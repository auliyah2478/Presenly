from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

import cv2
import numpy as np
import tempfile

from deepface import DeepFace

from .models import (
    Kelas,
    Dosen,
    Mahasiswa,
    MataKuliah,
    Jadwal,
    FaceEmbedding,
    SesiAbsensi,
    RiwayatAbsensi,
)

from .serializers import (
    KelasSerializer,
    DosenSerializer,
    MahasiswaSerializer,
    MataKuliahSerializer,
    JadwalSerializer,
    FaceEmbeddingSerializer,
    SesiAbsensiSerializer,
    RiwayatAbsensiSerializer,
)


class KelasViewSet(viewsets.ModelViewSet):
    queryset = Kelas.objects.all()
    serializer_class = KelasSerializer


class DosenViewSet(viewsets.ModelViewSet):
    queryset = Dosen.objects.all()
    serializer_class = DosenSerializer


class MahasiswaViewSet(viewsets.ModelViewSet):
    queryset = Mahasiswa.objects.all()
    serializer_class = MahasiswaSerializer


class MataKuliahViewSet(viewsets.ModelViewSet):
    queryset = MataKuliah.objects.all()
    serializer_class = MataKuliahSerializer


class JadwalViewSet(viewsets.ModelViewSet):
    queryset = Jadwal.objects.all()
    serializer_class = JadwalSerializer


class FaceEmbeddingViewSet(viewsets.ModelViewSet):
    queryset = FaceEmbedding.objects.all()
    serializer_class = FaceEmbeddingSerializer


class SesiAbsensiViewSet(viewsets.ModelViewSet):
    queryset = SesiAbsensi.objects.all()
    serializer_class = SesiAbsensiSerializer


class RiwayatAbsensiViewSet(viewsets.ModelViewSet):
    queryset = RiwayatAbsensi.objects.all()
    serializer_class = RiwayatAbsensiSerializer

def cosine_distance(vector1, vector2):
    a = np.array(vector1, dtype=np.float32)
    b = np.array(vector2, dtype=np.float32)

    return 1 - (
        np.dot(a, b)
        / (np.linalg.norm(a) * np.linalg.norm(b))
    )


@api_view(["POST"])
def scan_absensi(request):
    foto = request.FILES.get("foto")

    if not foto:
        return Response(
            {
                "status": "gagal",
                "message": "Foto wajah belum dikirim."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as temp_file:

            for chunk in foto.chunks():
                temp_file.write(chunk)

            foto_path = temp_file.name

        img = cv2.imread(foto_path)

        if img is None:
            return Response(
                {
                    "status": "gagal",
                    "message": "Foto tidak dapat dibaca."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tinggi, lebar = img.shape[:2]
        max_size = 1600

        if max(tinggi, lebar) > max_size:
            scale = max_size / max(tinggi, lebar)

            ukuran_baru = (
                int(lebar * scale),
                int(tinggi * scale)
            )

            img = cv2.resize(
                img,
                ukuran_baru,
                interpolation=cv2.INTER_AREA
            )

        embedding_objs = DeepFace.represent(
            img_path=img,
            model_name="ArcFace",
            detector_backend="mtcnn",
            enforce_detection=True
        )

        query_embedding = embedding_objs[0]["embedding"]

        embeddings_db = FaceEmbedding.objects.select_related(
            "mahasiswa",
            "mahasiswa__kelas"
        ).all()

        if not embeddings_db.exists():
            return Response(
                {
                    "status": "gagal",
                    "message": "Database face embedding masih kosong."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        mahasiswa_terbaik = None
        distance_terbaik = float("inf")

        for data in embeddings_db:
            distance = cosine_distance(
                query_embedding,
                data.embedding
            )

            if distance < distance_terbaik:
                distance_terbaik = distance
                mahasiswa_terbaik = data.mahasiswa

        threshold = 0.45

        if (
            mahasiswa_terbaik is None
            or distance_terbaik >= threshold
        ):
            return Response(
                {
                    "status": "gagal",
                    "message": "Wajah tidak dikenali.",
                    "distance": round(distance_terbaik, 4)
                },
                status=status.HTTP_404_NOT_FOUND
            )

        sekarang = timezone.now()

        sesi = (
            SesiAbsensi.objects
            .filter(
                aktif=True,
                waktu_buka__lte=sekarang,
                waktu_tutup__gte=sekarang
            )
            .select_related("jadwal")
            .first()
        )

        if sesi is None:
            return Response(
                {
                    "status": "gagal",
                    "message": "Tidak ada sesi absensi yang sedang aktif."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validasi kelas mahasiswa
        if mahasiswa_terbaik.kelas_id != sesi.jadwal.kelas_id:
            return Response(
                {
                    "status": "gagal",
                    "message": (
                        "Mahasiswa tidak terdaftar pada "
                        "kelas yang sedang aktif."
                    ),
                    "nama": mahasiswa_terbaik.nama,
                    "npm": mahasiswa_terbaik.npm,
                    "kelas": mahasiswa_terbaik.kelas.nama_kelas
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Mencegah mahasiswa absen dua kali
        sudah_absen = RiwayatAbsensi.objects.filter(
            mahasiswa=mahasiswa_terbaik,
            sesi_absensi=sesi
        ).exists()

        if sudah_absen:
            return Response(
                {
                    "status": "gagal",
                    "message": (
                        "Mahasiswa sudah melakukan "
                        "absensi pada sesi ini."
                    ),
                    "nama": mahasiswa_terbaik.nama,
                    "npm": mahasiswa_terbaik.npm
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tanggal_sesi = timezone.localtime(
            sesi.waktu_buka
        ).date()

        jam_mulai_kelas = datetime.combine(
            tanggal_sesi,
            sesi.jadwal.jam_mulai
        )

        jam_mulai_kelas = timezone.make_aware(
            jam_mulai_kelas,
            timezone.get_current_timezone()
        )

        sekarang_local = timezone.localtime(sekarang)

        if sekarang_local <= jam_mulai_kelas:
            status_kehadiran = "HADIR"
        else:
            status_kehadiran = "TERLAMBAT"

        riwayat = RiwayatAbsensi.objects.create(
            mahasiswa=mahasiswa_terbaik,
            sesi_absensi=sesi,
            status=status_kehadiran,
            distance_score=distance_terbaik
        )

        return Response(
            {
                "status": "berhasil",
                "message": "Absensi berhasil.",
                "kehadiran": status_kehadiran,
                "nama": mahasiswa_terbaik.nama,
                "npm": mahasiswa_terbaik.npm,
                "kelas": mahasiswa_terbaik.kelas.nama_kelas,
                "distance": round(distance_terbaik, 4),
                "waktu_absen": riwayat.waktu_absen
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {
                "status": "gagal",
                "message": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "status": "gagal",
                "message": "Username dan password wajib diisi."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                "status": "gagal",
                "message": "Username atau password salah."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, _ = Token.objects.get_or_create(user=user)

    if user.is_superuser:
        role = "admin"
    else:
        role = "dosen"

    return Response(
        {
            "status": "berhasil",
            "message": "Login berhasil.",
            "username": user.username,
            "role": role,
            "token": token.key
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
def registrasi_wajah(request):
    npm = request.data.get("npm")
    foto = request.FILES.get("foto")

    if not npm:
        return Response(
            {
                "status": "gagal",
                "message": "NPM wajib diisi."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not foto:
        return Response(
            {
                "status": "gagal",
                "message": "Foto wajah belum dikirim."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mahasiswa = Mahasiswa.objects.get(npm=npm)
    except Mahasiswa.DoesNotExist:
        return Response(
            {
                "status": "gagal",
                "message": "Mahasiswa tidak ditemukan."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as temp_file:

            for chunk in foto.chunks():
                temp_file.write(chunk)

            foto_path = temp_file.name

        img = cv2.imread(foto_path)

        if img is None:
            return Response(
                {
                    "status": "gagal",
                    "message": "Foto tidak dapat dibaca."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tinggi, lebar = img.shape[:2]

        max_size = 1600

        if max(tinggi, lebar) > max_size:

            scale = max_size / max(
                tinggi,
                lebar
            )

            ukuran_baru = (
                int(lebar * scale),
                int(tinggi * scale)
            )

            img = cv2.resize(
                img,
                ukuran_baru,
                interpolation=cv2.INTER_AREA
            )

        embedding_objs = DeepFace.represent(
            img_path=img,
            model_name="ArcFace",
            detector_backend="mtcnn",
            enforce_detection=True
        )

        embedding = embedding_objs[0]["embedding"]

        FaceEmbedding.objects.update_or_create(
            mahasiswa=mahasiswa,
            defaults={
                "embedding": embedding
            }
        )

        return Response(
            {
                "status": "berhasil",
                "message": "Registrasi wajah berhasil.",
                "nama": mahasiswa.nama,
                "npm": mahasiswa.npm,
                "kelas": mahasiswa.kelas.nama_kelas
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        return Response(
            {
                "status": "gagal",
                "message": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
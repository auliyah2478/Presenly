from rest_framework import viewsets, status
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from io import StringIO
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.authentication import TokenAuthentication

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class DosenViewSet(viewsets.ModelViewSet):
    queryset = Dosen.objects.all()
    serializer_class = DosenSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class MahasiswaViewSet(viewsets.ModelViewSet):
    queryset = Mahasiswa.objects.all()
    serializer_class = MahasiswaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class MataKuliahViewSet(viewsets.ModelViewSet):
    queryset = MataKuliah.objects.all()
    serializer_class = MataKuliahSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class JadwalViewSet(viewsets.ModelViewSet):

    queryset = Jadwal.objects.all()
    serializer_class = JadwalSerializer

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    @action(
        detail=False,
        methods=['post'],
        url_path='generate-kelas5'
    )
    def generate_kelas5(self, request):
        if not request.user.is_superuser:
            return Response(
                {'detail': 'Hanya admin yang dapat membuat jadwal otomatis.'},
                status=status.HTTP_403_FORBIDDEN
            )

        output = StringIO()
        try:
            call_command(
                'setup_jadwal_kelas5',
                stdout=output
            )
        except CommandError as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'message': output.getvalue().strip(),
                'total_jadwal': Jadwal.objects.filter(
                    kelas__nama_kelas__in=[
                        'TRI 5A',
                        'TRI 5B',
                        'TRI 5C',
                    ]
                ).count(),
            },
            status=status.HTTP_200_OK
        )

    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:
            return (
                Jadwal.objects
                .select_related(
                    "mata_kuliah",
                    "kelas",
                    "dosen"
                )
                .all()
            )

        if hasattr(user, "dosen_profile"):
            dosen = user.dosen_profile

            return (
                Jadwal.objects
                .select_related(
                    "mata_kuliah",
                    "kelas",
                    "dosen"
                )
                .filter(
                    Q(dosen=dosen) |
                    Q(dosen_pendamping=dosen)
                )
                .distinct()
            )

        return Jadwal.objects.none()

class FaceEmbeddingViewSet(viewsets.ModelViewSet):
    queryset = FaceEmbedding.objects.all()
    serializer_class = FaceEmbeddingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


def buat_alfa_sesi_berakhir(sesi):

    # Jangan proses jika sesi belum berakhir
    if timezone.now() < sesi.waktu_tutup:
        return

    # Ambil semua mahasiswa dari kelas tersebut
    mahasiswa_di_kelas = Mahasiswa.objects.filter(
        kelas_id=sesi.jadwal.kelas_id
    )

    for mahasiswa in mahasiswa_di_kelas:

        # Buat ALFA hanya jika belum ada riwayat absensi
        RiwayatAbsensi.objects.get_or_create(
            mahasiswa=mahasiswa,
            sesi_absensi=sesi,
            defaults={
                "status": "ALFA",
                "waktu_absen": None,
                "distance_score": None,
            }
        )

    # Tutup sesi jika masih aktif
    if sesi.aktif:
        sesi.aktif = False
        sesi.save(update_fields=["aktif"])


class SesiAbsensiViewSet(viewsets.ModelViewSet):

    queryset = SesiAbsensi.objects.all()
    serializer_class = SesiAbsensiSerializer

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user

        queryset = (
            SesiAbsensi.objects
            .select_related(
                "jadwal",
                "jadwal__mata_kuliah",
                "jadwal__kelas",
                "jadwal__dosen",
            )
            .order_by("-waktu_buka")
        )

        # ADMIN: dapat melihat seluruh sesi
        if user.is_superuser:
            return queryset

        # DOSEN: hanya melihat sesi jadwal miliknya
        if hasattr(user, "dosen_profile"):

            dosen = user.dosen_profile

            return queryset.filter(
                Q(jadwal__dosen=dosen) |
                Q(jadwal__dosen_pendamping=dosen)
            ).distinct()

        return queryset.none()
    
    def list(self, request, *args, **kwargs):

        # Cari sesi yang sudah melewati waktu tutup
        sesi_berakhir = self.get_queryset().filter(
            aktif=True,
            waktu_tutup__lte=timezone.now()
        )

        # Buat catatan ALFA untuk mahasiswa yang belum absen
        for sesi in sesi_berakhir:
            buat_alfa_sesi_berakhir(sesi)

        # Tampilkan daftar sesi seperti biasa
        return super().list(request, *args, **kwargs)


# ==========================================
# RIWAYAT ABSENSI
# ==========================================

class RiwayatAbsensiViewSet(viewsets.ModelViewSet):

    queryset = RiwayatAbsensi.objects.all()
    serializer_class = RiwayatAbsensiSerializer

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user

        queryset = (
            RiwayatAbsensi.objects
            .select_related(
                "mahasiswa",
                "mahasiswa__kelas",
                "sesi_absensi",
                "sesi_absensi__jadwal",
                "sesi_absensi__jadwal__mata_kuliah",
                "sesi_absensi__jadwal__kelas",
                "sesi_absensi__jadwal__dosen",
            )
            .order_by(
                "-sesi_absensi__waktu_buka",
                "-waktu_absen"
            )
        )

        # ADMIN: melihat seluruh riwayat
        if user.is_superuser:
            return queryset

        # DOSEN: dosen utama dan pendamping
        if hasattr(user, "dosen_profile"):

            dosen = user.dosen_profile

            return queryset.filter(
                Q(sesi_absensi__jadwal__dosen=dosen) |
                Q(sesi_absensi__jadwal__dosen_pendamping=dosen)
            ).distinct()

        return queryset.none()


# ==========================================
# COSINE DISTANCE
# ==========================================

def cosine_distance(vector1, vector2):

    a = np.array(vector1, dtype=np.float32)
    b = np.array(vector2, dtype=np.float32)

    return 1 - (
        np.dot(a, b)
        / (np.linalg.norm(a) * np.linalg.norm(b))
    )


def tentukan_status_kehadiran(sekarang, sesi):
    tanggal_sesi = timezone.localtime(
        sesi.waktu_buka
    ).date()

    jam_mulai_kelas = timezone.make_aware(
        datetime.combine(
            tanggal_sesi,
            sesi.jadwal.jam_mulai
        ),
        timezone.get_current_timezone()
    )

    batas_hadir = jam_mulai_kelas + timedelta(minutes=16)

    sekarang_local = timezone.localtime(sekarang)

    if sekarang_local < batas_hadir:
        return "HADIR"

    return "TERLAMBAT"


def get_or_create_sesi_absensi(mahasiswa, sekarang):

    sesi = (
        SesiAbsensi.objects
        .select_related(
            "jadwal",
            "jadwal__mata_kuliah",
            "jadwal__kelas",
            "jadwal__dosen",
        )
        .filter(
            jadwal__kelas_id=mahasiswa.kelas_id,
            aktif=True,
            waktu_buka__lte=sekarang,
            waktu_tutup__gt=sekarang,
        )
        .order_by("-waktu_buka")
        .first()
    )

    return sesi


# ==========================================
# SCAN ABSENSI
# ==========================================

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

        # ==================================
        # EKSTRAKSI EMBEDDING WAJAH
        # ==================================

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

        # ==================================
        # PENCARIAN WAJAH TERDEKAT
        # ==================================

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

        # ==================================
        # MENCARI SESI ABSENSI AKTIF
        # ==================================

        sesi = get_or_create_sesi_absensi(
            mahasiswa_terbaik,
            sekarang,
        )

        if sesi is None:

            return Response(
                {
                    "status": "gagal",
                    "message": (
                        "Tidak ada jadwal kuliah untuk kelas "
                        f"{mahasiswa_terbaik.kelas.nama_kelas} "
                        "yang sedang berlangsung."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================
        # VALIDASI KELAS MAHASISWA
        # ==================================

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

        # ==================================
        # MENCEGAH ABSENSI GANDA
        # ==================================

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

        # ==================================
        # MENENTUKAN STATUS KEHADIRAN
        # ==================================

        status_kehadiran = tentukan_status_kehadiran(
            sekarang,
            sesi
        )

        # ==================================
        # MENYIMPAN RIWAYAT ABSENSI
        # ==================================

        riwayat = RiwayatAbsensi.objects.create(
            mahasiswa=mahasiswa_terbaik,
            sesi_absensi=sesi,
            status=status_kehadiran,
            waktu_absen=sekarang,
            distance_score=distance_terbaik
        )

        # ==================================
        # RESPONSE ABSENSI BERHASIL
        # ==================================

        return Response(
            {
                "status": "berhasil",
                "message": "Absensi berhasil.",
                "kehadiran": status_kehadiran,
                "nama": mahasiswa_terbaik.nama,
                "npm": mahasiswa_terbaik.npm,
                "kelas": mahasiswa_terbaik.kelas.nama_kelas,
                "nama_mata_kuliah": (
                    sesi.jadwal.mata_kuliah.nama_mata_kuliah
                ),
                "waktu_absen": timezone.localtime(
                    riwayat.waktu_absen
                ).isoformat(),
                "distance": round(distance_terbaik, 4)
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


# ==========================================
# LOGIN API
# ==========================================

@api_view(["POST"])
def login_api(request):

    username = request.data.get(
        "username"
    )

    password = request.data.get(
        "password"
    )

    # ===============================
    # VALIDASI INPUT
    # ===============================

    if not username or not password:

        return Response(
            {
                "status": "gagal",
                "message": (
                    "Username dan password wajib diisi."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ===============================
    # AUTHENTICATE USER
    # ===============================

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:

        return Response(
            {
                "status": "gagal",
                "message": (
                    "Username atau password salah."
                )
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # ===============================
    # TENTUKAN ROLE
    # ===============================

    if user.is_superuser:

        role = "admin"

    elif hasattr(
        user,
        "dosen_profile"
    ):

        role = "dosen"

    else:

        return Response(
            {
                "status": "gagal",
                "message": (
                    "Akun belum terhubung "
                    "dengan data dosen."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ===============================
    # TOKEN
    # ===============================

    token, _ = (
        Token.objects.get_or_create(
            user=user
        )
    )

    # ===============================
    # RESPONSE LOGIN
    # ===============================

    response_data = {
        "status": "berhasil",
        "message": "Login berhasil.",
        "username": user.username,
        "role": role,
        "token": token.key
    }

    # Jika login dosen,
    # kirim juga nama dosennya.

    if role == "dosen":

        response_data["nama_dosen"] = (
            user.dosen_profile.nama
        )

    return Response(
        response_data,
        status=status.HTTP_200_OK
    )


# ==========================================
# REGISTRASI WAJAH
# ==========================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def registrasi_wajah(request):

    if not request.user.is_superuser:
        return Response(
            {
                "status": "gagal",
                "message": "Hanya admin yang dapat melakukan registrasi wajah."
            },
            status=status.HTTP_403_FORBIDDEN
        )

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
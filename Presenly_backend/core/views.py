from rest_framework import viewsets

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

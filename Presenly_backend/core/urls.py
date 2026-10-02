from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    KelasViewSet,
    DosenViewSet,
    MahasiswaViewSet,
    MataKuliahViewSet,
    JadwalViewSet,
    FaceEmbeddingViewSet,
    SesiAbsensiViewSet,
    RiwayatAbsensiViewSet,
)


router = DefaultRouter()

router.register(r'kelas', KelasViewSet)
router.register(r'dosen', DosenViewSet)
router.register(r'mahasiswa', MahasiswaViewSet)
router.register(r'mata-kuliah', MataKuliahViewSet)
router.register(r'jadwal', JadwalViewSet)
router.register(r'face-embedding', FaceEmbeddingViewSet)
router.register(r'sesi-absensi', SesiAbsensiViewSet)
router.register(r'riwayat-absensi', RiwayatAbsensiViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
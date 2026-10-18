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
    scan_absensi,
    login_api,
    registrasi_wajah,
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

    path(
        'absensi/scan/',
        scan_absensi,
        name='scan-absensi'
    ),

    path(
        'login/',
        login_api,
        name='login-api'
    ),

    path(
        'registrasi-wajah/',
        registrasi_wajah,
        name='registrasi-wajah'
    ),
]
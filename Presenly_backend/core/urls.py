from django.urls import path, include
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


# ==========================================
# ROUTER REST API
# ==========================================

router = DefaultRouter()

router.register(
    r'kelas',
    KelasViewSet,
    basename='kelas'
)

router.register(
    r'dosen',
    DosenViewSet,
    basename='dosen'
)

router.register(
    r'mahasiswa',
    MahasiswaViewSet,
    basename='mahasiswa'
)

router.register(
    r'mata-kuliah',
    MataKuliahViewSet,
    basename='mata-kuliah'
)

router.register(
    r'jadwal',
    JadwalViewSet,
    basename='jadwal'
)

router.register(
    r'face-embedding',
    FaceEmbeddingViewSet,
    basename='face-embedding'
)

router.register(
    r'sesi-absensi',
    SesiAbsensiViewSet,
    basename='sesi-absensi'
)

router.register(
    r'riwayat-absensi',
    RiwayatAbsensiViewSet,
    basename='riwayat-absensi'
)


# ==========================================
# URL PATTERNS
# ==========================================

urlpatterns = [

    # Endpoint CRUD
    path(
        '',
        include(router.urls)
    ),

    # Scan absensi mahasiswa
    path(
        'absensi/scan/',
        scan_absensi,
        name='scan-absensi'
    ),

    # Login admin dan dosen
    path(
        'login/',
        login_api,
        name='login-api'
    ),

    # Registrasi wajah mahasiswa
    path(
        'registrasi-wajah/',
        registrasi_wajah,
        name='registrasi-wajah'
    ),

]
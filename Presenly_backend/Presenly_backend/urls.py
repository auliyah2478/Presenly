
from django.contrib import admin
from django.urls import path, include

from core.page_views import (
    welcome_page,
    login_page,
    dashboard_page,
    logout_page,
    section_page,

    # CRUD Mahasiswa
    mahasiswa_tambah,
    mahasiswa_edit,
    mahasiswa_hapus,

    # CRUD Dosen
    dosen_tambah,
    dosen_edit,
    dosen_hapus,

    # CRUD Jadwal Kuliah
    jadwal_tambah,
    jadwal_edit,
    jadwal_hapus,

    # CRUD Kelas
    kelas_tambah,
    kelas_edit,
    kelas_hapus,

    # CRUD Mata Kuliah
    mata_kuliah_tambah,
    mata_kuliah_edit,
    mata_kuliah_hapus,
)


urlpatterns = [
    # =====================================
    # HALAMAN UTAMA
    # =====================================
    path('', welcome_page, name='welcome'),
    path('login/', login_page, name='login'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('logout/', logout_page, name='logout'),

    # =====================================
    # HALAMAN PENGELOLAAN DATA
    # =====================================
    path(
        'dashboard/mahasiswa/',
        section_page,
        {'section': 'mahasiswa'},
        name='data_mahasiswa'
    ),
    path(
        'dashboard/dosen/',
        section_page,
        {'section': 'dosen'},
        name='data_dosen'
    ),
    path(
        'dashboard/jadwal/',
        section_page,
        {'section': 'jadwal'},
        name='data_jadwal'
    ),
    path(
        'dashboard/kelas/',
        section_page,
        {'section': 'kelas'},
        name='data_kelas'
    ),
    path(
        'dashboard/mata-kuliah/',
        section_page,
        {'section': 'mata-kuliah'},
        name='data_mata_kuliah'
    ),
    path(
        'dashboard/absensi/',
        section_page,
        {'section': 'absensi'},
        name='data_absensi'
    ),

    # =====================================
    # CRUD MAHASISWA
    # =====================================
    path(
        'dashboard/mahasiswa/tambah/',
        mahasiswa_tambah,
        name='mahasiswa_tambah'
    ),
    path(
        'dashboard/mahasiswa/edit/<int:pk>/',
        mahasiswa_edit,
        name='mahasiswa_edit'
    ),
    path(
        'dashboard/mahasiswa/hapus/<int:pk>/',
        mahasiswa_hapus,
        name='mahasiswa_hapus'
    ),

    # =====================================
    # CRUD DOSEN
    # =====================================
    path(
        'dashboard/dosen/tambah/',
        dosen_tambah,
        name='dosen_tambah'
    ),
    path(
        'dashboard/dosen/edit/<int:pk>/',
        dosen_edit,
        name='dosen_edit'
    ),
    path(
        'dashboard/dosen/hapus/<int:pk>/',
        dosen_hapus,
        name='dosen_hapus'
    ),

    # =====================================
    # CRUD JADWAL KULIAH
    # =====================================
    path(
        'dashboard/jadwal/tambah/',
        jadwal_tambah,
        name='jadwal_tambah'
    ),
    path(
        'dashboard/jadwal/edit/<int:pk>/',
        jadwal_edit,
        name='jadwal_edit'
    ),
    path(
        'dashboard/jadwal/hapus/<int:pk>/',
        jadwal_hapus,
        name='jadwal_hapus'
    ),

    # =====================================
    # CRUD KELAS
    # =====================================
    path(
        'dashboard/kelas/tambah/',
        kelas_tambah,
        name='kelas_tambah'
    ),
    path(
        'dashboard/kelas/edit/<int:pk>/',
        kelas_edit,
        name='kelas_edit'
    ),
    path(
        'dashboard/kelas/hapus/<int:pk>/',
        kelas_hapus,
        name='kelas_hapus'
    ),

    # =====================================
    # CRUD MATA KULIAH
    # =====================================
    path(
        'dashboard/mata-kuliah/tambah/',
        mata_kuliah_tambah,
        name='mata_kuliah_tambah'
    ),
    path(
        'dashboard/mata-kuliah/edit/<int:pk>/',
        mata_kuliah_edit,
        name='mata_kuliah_edit'
    ),
    path(
        'dashboard/mata-kuliah/hapus/<int:pk>/',
        mata_kuliah_hapus,
        name='mata_kuliah_hapus'
    ),

    # =====================================
    # DJANGO ADMIN DAN API
    # =====================================
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]


from django.contrib import admin

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


# ==========================================
# IDENTITAS DJANGO ADMIN PRESENLY
# ==========================================

admin.site.site_header = "Presenly | Administrasi"
admin.site.site_title = "Presenly Admin"
admin.site.index_title = "Dashboard Administrasi Presenly"

# Template dashboard custom yang akan kita buat
admin.site.index_template = "admin/custom_index.html"


# ==========================================
# DATA KELAS
# ==========================================

@admin.register(Kelas)
class KelasAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nama_kelas",
    )

    search_fields = (
        "nama_kelas",
    )

    ordering = (
        "nama_kelas",
    )


# ==========================================
# DATA DOSEN
# ==========================================

@admin.register(Dosen)
class DosenAdmin(admin.ModelAdmin):

    list_display = (
        "nama",
        "nidn",
        "email",
        "user",
    )

    search_fields = (
        "nama",
        "nidn",
        "email",
        "user__username",
    )

    ordering = (
        "nama",
    )


# ==========================================
# DATA MAHASISWA
# ==========================================

@admin.register(Mahasiswa)
class MahasiswaAdmin(admin.ModelAdmin):

    list_display = (
        "npm",
        "nama",
        "kelas",
        "email",
    )

    list_filter = (
        "kelas",
    )

    search_fields = (
        "npm",
        "nama",
        "email",
    )

    ordering = (
        "nama",
    )

    list_per_page = 25


# ==========================================
# DATA MATA KULIAH
# ==========================================

@admin.register(MataKuliah)
class MataKuliahAdmin(admin.ModelAdmin):

    list_display = (
        "kode_mata_kuliah",
        "nama_mata_kuliah",
    )

    search_fields = (
        "kode_mata_kuliah",
        "nama_mata_kuliah",
    )

    ordering = (
        "nama_mata_kuliah",
    )


# ==========================================
# DATA JADWAL
# ==========================================

@admin.register(Jadwal)
class JadwalAdmin(admin.ModelAdmin):

    list_display = (
        "mata_kuliah",
        "kelas",
        "dosen",
        "hari",
        "jam_mulai",
        "jam_selesai",
        "jenis_pertemuan",
    )

    list_filter = (
        "hari",
        "kelas",
        "dosen",
        "jenis_pertemuan",
    )

    search_fields = (
        "mata_kuliah__nama_mata_kuliah",
        "mata_kuliah__kode_mata_kuliah",
        "kelas__nama_kelas",
        "dosen__nama",
    )

    filter_horizontal = (
        "dosen_pendamping",
    )

    list_select_related = (
        "mata_kuliah",
        "kelas",
        "dosen",
    )

    ordering = (
        "hari",
        "jam_mulai",
    )


# ==========================================
# DATA FACE EMBEDDING
# ==========================================

@admin.register(FaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):

    list_display = (
        "mahasiswa",
        "tanggal_dibuat",
        "tanggal_diperbarui",
    )

    search_fields = (
        "mahasiswa__npm",
        "mahasiswa__nama",
    )

    readonly_fields = (
        "mahasiswa",
        "embedding",
        "tanggal_dibuat",
        "tanggal_diperbarui",
    )

    def has_add_permission(self, request):
        return False


# ==========================================
# SESI ABSENSI
# ==========================================

@admin.register(SesiAbsensi)
class SesiAbsensiAdmin(admin.ModelAdmin):

    list_display = (
        "jadwal",
        "waktu_buka",
        "waktu_tutup",
        "aktif",
    )

    list_filter = (
        "aktif",
        "jadwal__hari",
        "jadwal__kelas",
    )

    search_fields = (
        "jadwal__mata_kuliah__nama_mata_kuliah",
        "jadwal__kelas__nama_kelas",
        "jadwal__dosen__nama",
    )

    ordering = (
        "-waktu_buka",
    )


# ==========================================
# RIWAYAT ABSENSI
# ==========================================

@admin.register(RiwayatAbsensi)
class RiwayatAbsensiAdmin(admin.ModelAdmin):

    list_display = (
        "mahasiswa",
        "mata_kuliah",
        "kelas",
        "status",
        "waktu_absen",
        "distance_score",
    )

    list_filter = (
        "status",
        "sesi_absensi__jadwal__mata_kuliah",
        "sesi_absensi__jadwal__kelas",
        "waktu_absen",
    )

    search_fields = (
        "mahasiswa__npm",
        "mahasiswa__nama",
        "sesi_absensi__jadwal__mata_kuliah__nama_mata_kuliah",
    )

    readonly_fields = (
        "mahasiswa",
        "sesi_absensi",
        "waktu_absen",
        "status",
        "distance_score",
    )

    ordering = (
        "-waktu_absen",
    )

    list_per_page = 30

    @admin.display(description="Mata Kuliah")
    def mata_kuliah(self, obj):
        return obj.sesi_absensi.jadwal.mata_kuliah.nama_mata_kuliah

    @admin.display(description="Kelas")
    def kelas(self, obj):
        return obj.sesi_absensi.jadwal.kelas.nama_kelas

    def has_add_permission(self, request):
        return False

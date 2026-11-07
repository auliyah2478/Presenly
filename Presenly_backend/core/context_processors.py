
from .models import (
    Kelas,
    Jadwal,
    Mahasiswa,
    RiwayatAbsensi,
    SesiAbsensi,
)


def presenly_dashboard_stats(request):
    """
    Mengambil statistik Presenly dari database
    untuk ditampilkan pada Dashboard Django Admin.
    """

    # Statistik hanya dibutuhkan pada halaman admin
    if not request.path.startswith("/admin/"):
        return {}

    total_mahasiswa = Mahasiswa.objects.count()
    total_kelas = Kelas.objects.count()
    total_jadwal = Jadwal.objects.count()
    total_absensi = RiwayatAbsensi.objects.count()

    sesi_aktif = SesiAbsensi.objects.filter(
        aktif=True
    ).count()

    return {
        "presenly_total_mahasiswa": total_mahasiswa,
        "presenly_total_kelas": total_kelas,
        "presenly_total_jadwal": total_jadwal,
        "presenly_total_absensi": total_absensi,
        "presenly_sesi_aktif": sesi_aktif,
    }

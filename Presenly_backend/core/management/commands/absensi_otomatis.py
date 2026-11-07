
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from core.models import (
    Jadwal,
    Mahasiswa,
    SesiAbsensi,
    RiwayatAbsensi,
)


class Command(BaseCommand):
    help = "Mengelola sesi absensi dan mencatat ALFA secara otomatis."

    requires_system_checks = []

    def handle(self, *args, **options):
        sekarang = timezone.localtime()
        tanggal = sekarang.date()

        daftar_hari = [
            "Senin",
            "Selasa",
            "Rabu",
            "Kamis",
            "Jumat",
            "Sabtu",
            "Minggu",
        ]

        hari_ini = daftar_hari[sekarang.weekday()]

        # Menangani variasi penulisan hari Jumat.
        if hari_ini == "Jumat":
            filter_hari = (
                Q(hari__iexact="Jumat")
                | Q(hari__iexact="Jum'at")
            )
        else:
            filter_hari = Q(hari__iexact=hari_ini)

        jadwal_hari_ini = (
            Jadwal.objects
            .filter(filter_hari)
            .select_related("kelas", "mata_kuliah")
        )

        total_sesi_dibuka = 0
        total_sesi_ditutup = 0
        total_alfa = 0

        for jadwal in jadwal_hari_ini:

            jam_mulai = timezone.make_aware(
                datetime.combine(
                    tanggal,
                    jadwal.jam_mulai,
                ),
                timezone.get_current_timezone(),
            )

            jam_selesai = timezone.make_aware(
                datetime.combine(
                    tanggal,
                    jadwal.jam_selesai,
                ),
                timezone.get_current_timezone(),
            )

            # Absensi dibuka 5 menit sebelum kelas.
            waktu_buka = jam_mulai - timedelta(minutes=5)

            # Belum waktunya membuka absensi.
            if sekarang < waktu_buka:
                continue

            # Membuat atau mengambil sesi yang sama.
            sesi, dibuat = SesiAbsensi.objects.get_or_create(
                jadwal=jadwal,
                waktu_buka=waktu_buka,
                defaults={
                    "waktu_tutup": jam_selesai,
                    "aktif": sekarang < jam_selesai,
                },
            )

            # =====================================
            # KELAS BELUM BERAKHIR
            # =====================================
            if sekarang < jam_selesai:

                if not sesi.aktif or sesi.waktu_tutup != jam_selesai:
                    sesi.aktif = True
                    sesi.waktu_tutup = jam_selesai

                    sesi.save(
                        update_fields=[
                            "aktif",
                            "waktu_tutup",
                        ]
                    )

                if dibuat:
                    total_sesi_dibuka += 1

                continue

            # =====================================
            # KELAS SUDAH BERAKHIR
            # =====================================

            # Tutup sesi absensi.
            if sesi.aktif:
                sesi.aktif = False
                sesi.waktu_tutup = jam_selesai

                sesi.save(
                    update_fields=[
                        "aktif",
                        "waktu_tutup",
                    ]
                )

                total_sesi_ditutup += 1

            # Ambil seluruh mahasiswa pada kelas tersebut.
            mahasiswa_kelas = Mahasiswa.objects.filter(
                kelas=jadwal.kelas
            )

            # Catat ALFA hanya untuk mahasiswa
            # yang belum memiliki riwayat pada sesi ini.
            for mahasiswa in mahasiswa_kelas:

                _, alfa_dibuat = RiwayatAbsensi.objects.get_or_create(
                    mahasiswa=mahasiswa,
                    sesi_absensi=sesi,
                    defaults={
                        "status": "ALFA",
                    },
                )

                if alfa_dibuat:
                    total_alfa += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Proses selesai: "
                f"{total_sesi_dibuka} sesi dibuka, "
                f"{total_sesi_ditutup} sesi ditutup, "
                f"{total_alfa} mahasiswa tercatat ALFA."
            )
        )

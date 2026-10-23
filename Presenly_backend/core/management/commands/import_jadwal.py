from django.core.management.base import BaseCommand

from core.models import (
    Kelas,
    Dosen,
    MataKuliah,
    Jadwal,
)


class Command(BaseCommand):

    help = "Import jadwal kuliah TRI Semester 5"

    def handle(self, *args, **options):

        # ==================================================
        # DATA MATA KULIAH + DOSEN PJ
        # ==================================================

        mata_kuliah_data = [
            {
                "kode": "PKU1511",
                "nama": "Proyek Mandiri",
                "dosen": "Ir. Imam Asrowardi, S.Kom., M.Kom.",
            },
            {
                "kode": "PIE1511",
                "nama": "Keamanan Siber",
                "dosen": "Dr. Ir. Septafiansyah Dwi Putra, S.T., M.T.",
            },
            {
                "kode": "PIE1512",
                "nama": "Teknologi Fiber Optik",
                "dosen": "Dr. Ir. Septafiansyah Dwi Putra, S.T., M.T.",
            },
            {
                "kode": "PIE1513",
                "nama": "Infrastruktur dan Otomasi Jaringan",
                "dosen": "Ir. Imam Asrowardi, S.Kom., M.Kom.",
            },
            {
                "kode": "PIE1514",
                "nama": "Teknologi Komputasi Awan II",
                "dosen": "Dr. Ir. Septafiansyah Dwi Putra, S.T., M.T.",
            },
            {
                "kode": "PIE1515",
                "nama": "Jaringan Komputer IV",
                "dosen": "Ir. Imam Asrowardi, S.Kom., M.Kom.",
            },
            {
                "kode": "PIE1516",
                "nama": "Pemrograman Internet II",
                "dosen": "Ir. Dian Ayu Afifah, S.Si., M.Sc.",
            },
        ]

        mata_kuliah = {}
        dosen_mata_kuliah = {}

        # ==================================================
        # BUAT / AMBIL DATA MATA KULIAH
        # ==================================================

        for data in mata_kuliah_data:

            kode = data["kode"]
            nama = data["nama"]
            nama_dosen = data["dosen"]

            mk, _ = MataKuliah.objects.get_or_create(
                kode_mata_kuliah=kode,
                defaults={
                    "nama_mata_kuliah": nama,
                },
            )

            mata_kuliah[kode] = mk

            # ==================================================
            # CARI DOSEN PJ
            # ==================================================

            try:

                dosen = Dosen.objects.get(
                    nama=nama_dosen
                )

                dosen_mata_kuliah[kode] = dosen

            except Dosen.DoesNotExist:

                self.stdout.write(
                    self.style.WARNING(
                        (
                            f"Dosen belum ditemukan: "
                            f"{nama_dosen}"
                        )
                    )
                )

                dosen_mata_kuliah[kode] = None

        # ==================================================
        # DATA JADWAL
        # ==================================================

        jadwal_data = [

            # =========================
            # SENIN
            # =========================

            (
                "Senin",
                "13:00",
                "13:50",
                "PIE1515",
            ),

            (
                "Senin",
                "13:50",
                "17:50",
                "PIE1515",
            ),

            # =========================
            # SELASA
            # =========================

            (
                "Selasa",
                "07:00",
                "08:40",
                "PIE1511",
            ),

            (
                "Selasa",
                "08:40",
                "12:40",
                "PIE1511",
            ),

            (
                "Selasa",
                "13:00",
                "13:50",
                "PIE1512",
            ),

            (
                "Selasa",
                "13:50",
                "15:50",
                "PIE1512",
            ),

            # =========================
            # RABU
            # =========================

            (
                "Rabu",
                "07:00",
                "07:50",
                "PIE1514",
            ),

            (
                "Rabu",
                "07:50",
                "11:50",
                "PIE1514",
            ),

            (
                "Rabu",
                "13:00",
                "13:50",
                "PIE1513",
            ),

            (
                "Rabu",
                "13:50",
                "17:50",
                "PIE1513",
            ),

            # =========================
            # KAMIS
            # =========================

            (
                "Kamis",
                "13:00",
                "19:00",
                "PKU1511",
            ),

            # =========================
            # JUMAT
            # =========================

            (
                "Jumat",
                "13:30",
                "14:20",
                "PIE1516",
            ),

            (
                "Jumat",
                "14:20",
                "18:20",
                "PIE1516",
            ),
        ]

        # ==================================================
        # KELAS
        # ==================================================

        nama_kelas = [
            "TRI 5A",
            "TRI 5B",
            "TRI 5C",
        ]

        jumlah_baru = 0
        jumlah_sudah_ada = 0
        jumlah_dilewati = 0

        # ==================================================
        # IMPORT JADWAL
        # ==================================================

        for nama in nama_kelas:

            try:

                kelas = Kelas.objects.get(
                    nama_kelas=nama
                )

            except Kelas.DoesNotExist:

                self.stdout.write(
                    self.style.WARNING(
                        f"Kelas {nama} tidak ditemukan."
                    )
                )

                continue

            self.stdout.write(
                f"\nMemproses jadwal {nama}..."
            )

            for (
                hari,
                jam_mulai,
                jam_selesai,
                kode_mk,
            ) in jadwal_data:

                dosen = dosen_mata_kuliah.get(
                    kode_mk
                )

                # Jika dosen PJ belum ada,
                # jadwal tidak dimasukkan.
                if dosen is None:

                    jumlah_dilewati += 1

                    self.stdout.write(
                        self.style.WARNING(
                            (
                                f"[DILEWATI] "
                                f"{nama} | "
                                f"{hari} | "
                                f"{mata_kuliah[kode_mk].nama_mata_kuliah} "
                                f"| dosen belum ada"
                            )
                        )
                    )

                    continue

                jadwal, created = (
                    Jadwal.objects.get_or_create(
                        mata_kuliah=mata_kuliah[kode_mk],
                        kelas=kelas,
                        dosen=dosen,
                        hari=hari,
                        jam_mulai=jam_mulai,
                        jam_selesai=jam_selesai,
                    )
                )

                if created:

                    jumlah_baru += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            (
                                f"[BARU] "
                                f"{nama} | "
                                f"{hari} | "
                                f"{mata_kuliah[kode_mk].nama_mata_kuliah} "
                                f"| {dosen.nama} "
                                f"| {jam_mulai}-{jam_selesai}"
                            )
                        )
                    )

                else:

                    jumlah_sudah_ada += 1

                    self.stdout.write(
                        (
                            f"[SUDAH ADA] "
                            f"{nama} | "
                            f"{hari} | "
                            f"{mata_kuliah[kode_mk].nama_mata_kuliah}"
                        )
                    )

        # ==================================================
        # HASIL
        # ==================================================

        self.stdout.write(
            "\n===================================="
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Jadwal baru       : {jumlah_baru}"
            )
        )

        self.stdout.write(
            f"Jadwal sudah ada : {jumlah_sudah_ada}"
        )

        self.stdout.write(
            f"Jadwal dilewati  : {jumlah_dilewati}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Import jadwal selesai."
            )
        )
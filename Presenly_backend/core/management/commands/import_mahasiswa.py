from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Kelas, Mahasiswa


class Command(BaseCommand):
    help = "Import dataset identitas mahasiswa Presenly"

    def handle(self, *args, **options):
        dataset_dir = Path(settings.BASE_DIR) / "dataset"

        files = {
            "dataset_identitas_5a.csv": "TRI 5A",
            "dataset_identitas_5b.csv": "TRI 5B",
            "dataset_identitas_5c.csv": "TRI 5C",
        }

        total_baru = 0
        total_update = 0

        for nama_file, nama_kelas in files.items():
            file_path = dataset_dir / nama_file

            if not file_path.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"File tidak ditemukan: {nama_file}"
                    )
                )
                continue

            kelas, _ = Kelas.objects.get_or_create(
                nama_kelas=nama_kelas
            )

            self.stdout.write(
                f"\nMemproses {nama_file} -> {nama_kelas}"
            )

            with open(
                file_path,
                mode="r",
                encoding="utf-8-sig"
            ) as file:

                lines = file.readlines()

                # Lewati header
                for line in lines[1:]:

                    # Hilangkan tanda kutip dan spasi
                    line = line.strip().strip('"')

                    if not line:
                        continue

                    bagian = [
                        item.strip()
                        for item in line.split(",")
                    ]

                    if len(bagian) < 3:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Data dilewati: {line}"
                            )
                        )
                        continue

                    nama = bagian[0]
                    npm = bagian[1]

                    if not nama or not npm:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Data tidak lengkap: {line}"
                            )
                        )
                        continue

                    mahasiswa, created = (
                        Mahasiswa.objects.update_or_create(
                            npm=npm,
                            defaults={
                                "nama": nama,
                                "kelas": kelas,
                            }
                        )
                    )

                    if created:
                        total_baru += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[BARU] {npm} - {nama} - {nama_kelas}"
                            )
                        )

                    else:
                        total_update += 1

                        self.stdout.write(
                            f"[UPDATE] {npm} - {nama} - {nama_kelas}"
                        )

        self.stdout.write(
            "\n=============================="
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Mahasiswa baru : {total_baru}"
            )
        )

        self.stdout.write(
            f"Mahasiswa diperbarui : {total_update}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Import identitas mahasiswa selesai."
            )
        )
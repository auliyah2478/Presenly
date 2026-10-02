from pathlib import Path

import cv2

from django.conf import settings
from django.core.management.base import BaseCommand
from deepface import DeepFace

from core.models import Mahasiswa, FaceEmbedding


class Command(BaseCommand):
    help = "Generate face embedding mahasiswa dari dataset foto"

    def handle(self, *args, **options):
        foto_dir = Path(settings.BASE_DIR) / "dataset" / "foto"

        if not foto_dir.exists():
            self.stdout.write(
                self.style.ERROR("Folder dataset/foto tidak ditemukan.")
            )
            return

        total_berhasil = 0
        total_gagal = 0
        total_skip = 0

        for foto_path in foto_dir.iterdir():

            if foto_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue

            npm = foto_path.stem.strip()

            try:
                mahasiswa = Mahasiswa.objects.get(npm=npm)

                # Jangan proses ulang mahasiswa yang sudah punya embedding
                if FaceEmbedding.objects.filter(
                    mahasiswa=mahasiswa
                ).exists():
                    total_skip += 1

                    self.stdout.write(
                        f"[SKIP] {npm} - embedding sudah tersedia"
                    )
                    continue

                self.stdout.write(
                    f"[PROSES] {foto_path.name}"
                )

                # Baca gambar
                img = cv2.imread(str(foto_path))

                if img is None:
                    raise ValueError("File gambar tidak dapat dibaca")

                tinggi, lebar = img.shape[:2]

                # Resize jika gambar terlalu besar
                max_size = 1600

                if max(tinggi, lebar) > max_size:
                    scale = max_size / max(tinggi, lebar)

                    ukuran_baru = (
                        int(lebar * scale),
                        int(tinggi * scale)
                    )

                    img = cv2.resize(
                        img,
                        ukuran_baru,
                        interpolation=cv2.INTER_AREA
                    )

                    self.stdout.write(
                        f"  Resize: {lebar}x{tinggi} "
                        f"-> {ukuran_baru[0]}x{ukuran_baru[1]}"
                    )

                embedding_objs = DeepFace.represent(
                    img_path=img,
                    model_name="ArcFace",
                    detector_backend="mtcnn",
                    enforce_detection=True
                )

                embedding = embedding_objs[0]["embedding"]

                FaceEmbedding.objects.update_or_create(
                    mahasiswa=mahasiswa,
                    defaults={
                        "embedding": embedding
                    }
                )

                total_berhasil += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[BERHASIL] {npm} - {mahasiswa.nama}"
                    )
                )

            except Mahasiswa.DoesNotExist:
                total_gagal += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"[GAGAL] NPM {npm} tidak ditemukan di database"
                    )
                )

            except Exception as e:
                total_gagal += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"[GAGAL] {foto_path.name} -> {e}"
                    )
                )

        self.stdout.write("\n==============================")

        self.stdout.write(
            self.style.SUCCESS(
                f"Embedding berhasil : {total_berhasil}"
            )
        )

        self.stdout.write(
            f"Embedding dilewati : {total_skip}"
        )

        self.stdout.write(
            f"Embedding gagal : {total_gagal}"
        )
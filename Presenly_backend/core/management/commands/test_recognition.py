from pathlib import Path

import cv2
import numpy as np

from django.core.management.base import BaseCommand
from deepface import DeepFace

from core.models import FaceEmbedding


def cosine_distance(vector1, vector2):
    a = np.array(vector1, dtype=np.float32)
    b = np.array(vector2, dtype=np.float32)

    return 1 - (
        np.dot(a, b)
        / (np.linalg.norm(a) * np.linalg.norm(b))
    )


class Command(BaseCommand):
    help = "Test pengenalan wajah mahasiswa Presenly"

    def add_arguments(self, parser):
        parser.add_argument(
            "foto",
            type=str,
            help="Path foto yang akan diuji"
        )

    def handle(self, *args, **options):
        foto_path = Path(options["foto"])

        if not foto_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Foto tidak ditemukan: {foto_path}"
                )
            )
            return

        self.stdout.write(
            f"\nMemproses foto: {foto_path.name}"
        )

        try:
            img = cv2.imread(str(foto_path))

            if img is None:
                self.stdout.write(
                    self.style.ERROR(
                        "Foto tidak dapat dibaca."
                    )
                )
                return

            # Resize kalau foto terlalu besar
            tinggi, lebar = img.shape[:2]
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

            # Generate embedding foto uji
            embedding_objs = DeepFace.represent(
                img_path=img,
                model_name="ArcFace",
                detector_backend="mtcnn",
                enforce_detection=True
            )

            query_embedding = embedding_objs[0]["embedding"]

            embeddings_db = (
                FaceEmbedding.objects
                .select_related("mahasiswa")
                .all()
            )

            if not embeddings_db.exists():
                self.stdout.write(
                    self.style.ERROR(
                        "Database Face Embedding masih kosong."
                    )
                )
                return

            mahasiswa_terbaik = None
            distance_terbaik = float("inf")

            for data in embeddings_db:
                distance = cosine_distance(
                    query_embedding,
                    data.embedding
                )

                if distance < distance_terbaik:
                    distance_terbaik = distance
                    mahasiswa_terbaik = data.mahasiswa

            threshold = 0.45

            self.stdout.write(
                "\n=============================="
            )

            if (
                mahasiswa_terbaik
                and distance_terbaik < threshold
            ):
                self.stdout.write(
                    self.style.SUCCESS(
                        "WAJAH DIKENALI"
                    )
                )

                self.stdout.write(
                    f"Nama     : {mahasiswa_terbaik.nama}"
                )

                self.stdout.write(
                    f"NPM      : {mahasiswa_terbaik.npm}"
                )

                self.stdout.write(
                    f"Kelas    : {mahasiswa_terbaik.kelas}"
                )

                self.stdout.write(
                    f"Distance : {distance_terbaik:.4f}"
                )

            else:
                self.stdout.write(
                    self.style.WARNING(
                        "WAJAH TIDAK DIKENALI"
                    )
                )

                self.stdout.write(
                    f"Distance terdekat: "
                    f"{distance_terbaik:.4f}"
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Terjadi error: {e}"
                )
            )
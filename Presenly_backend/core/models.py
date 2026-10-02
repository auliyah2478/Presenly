from django.db import models


class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Kelas"
        verbose_name_plural = "Kelas"

    def __str__(self):
        return self.nama_kelas


class Dosen(models.Model):
    nama = models.CharField(max_length=100)
    nidn = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Dosen"
        verbose_name_plural = "Dosen"

    def __str__(self):
        return self.nama


class Mahasiswa(models.Model):
    npm = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Mahasiswa"
        verbose_name_plural = "Mahasiswa"

    def __str__(self):
        return f"{self.npm} - {self.nama}"


class MataKuliah(models.Model):
    nama_mata_kuliah = models.CharField(max_length=100)
    kode_mata_kuliah = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"

    def __str__(self):
        return self.nama_mata_kuliah


class Jadwal(models.Model):
    mata_kuliah = models.ForeignKey(
        MataKuliah,
        on_delete=models.CASCADE
    )
    kelas = models.ForeignKey(
        Kelas,
        on_delete=models.CASCADE
    )
    dosen = models.ForeignKey(
        Dosen,
        on_delete=models.CASCADE
    )

    hari = models.CharField(max_length=20)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()

    class Meta:
        verbose_name = "Jadwal"
        verbose_name_plural = "Jadwal"

    def __str__(self):
        return f"{self.mata_kuliah} - {self.kelas}"


class FaceEmbedding(models.Model):
    mahasiswa = models.OneToOneField(
        Mahasiswa,
        on_delete=models.CASCADE,
        related_name='face_embedding'
    )

    embedding = models.JSONField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Face Embedding"
        verbose_name_plural = "Face Embedding"

    def __str__(self):
        return f"Face Embedding - {self.mahasiswa.nama}"


class SesiAbsensi(models.Model):
    jadwal = models.ForeignKey(
        Jadwal,
        on_delete=models.CASCADE,
        related_name='sesi_absensi'
    )

    waktu_buka = models.DateTimeField()
    waktu_tutup = models.DateTimeField()
    aktif = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Sesi Absensi"
        verbose_name_plural = "Sesi Absensi"

    def __str__(self):
        return f"{self.jadwal} - {self.waktu_buka}"


class RiwayatAbsensi(models.Model):
    STATUS_CHOICES = [
        ('HADIR', 'Hadir'),
        ('TERLAMBAT', 'Terlambat'),
    ]

    mahasiswa = models.ForeignKey(
        Mahasiswa,
        on_delete=models.CASCADE,
        related_name='riwayat_absensi'
    )

    sesi_absensi = models.ForeignKey(
        SesiAbsensi,
        on_delete=models.CASCADE,
        related_name='riwayat_absensi'
    )

    waktu_absen = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='HADIR'
    )

    distance_score = models.FloatField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Riwayat Absensi"
        verbose_name_plural = "Riwayat Absensi"

    def __str__(self):
        return f"{self.mahasiswa.nama} - {self.status}"
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


admin.site.register(Kelas)
admin.site.register(Dosen)
admin.site.register(Mahasiswa)
admin.site.register(MataKuliah)
admin.site.register(Jadwal)
admin.site.register(FaceEmbedding)
admin.site.register(SesiAbsensi)
admin.site.register(RiwayatAbsensi)
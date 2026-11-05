from rest_framework import serializers
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


class KelasMahasiswaField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            legacy_class_names = {
                '1': 'TRI 5A',
            }
            nama_kelas = legacy_class_names.get(str(data))

            if nama_kelas:
                try:
                    return Kelas.objects.get(nama_kelas=nama_kelas)
                except Kelas.DoesNotExist:
                    pass

            raise


class KelasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kelas
        fields = '__all__'


class DosenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dosen
        fields = '__all__'


class MahasiswaSerializer(serializers.ModelSerializer):
    kelas = KelasMahasiswaField(queryset=Kelas.objects.all())

    class Meta:
        model = Mahasiswa
        fields = '__all__'


class MataKuliahSerializer(serializers.ModelSerializer):
    class Meta:
        model = MataKuliah
        fields = '__all__'


class JadwalSerializer(serializers.ModelSerializer):
    mata_kuliah_nama = serializers.CharField(
        source='mata_kuliah.nama_mata_kuliah',
        read_only=True
    )
    kelas_nama = serializers.CharField(
        source='kelas.nama_kelas',
        read_only=True
    )
    dosen_nama = serializers.CharField(
        source='dosen.nama',
        read_only=True
    )
    dosen_pendamping_nama = serializers.SerializerMethodField()

    class Meta:
        model = Jadwal
        fields = '__all__'

    def get_dosen_pendamping_nama(self, obj):
        return [
            dosen.nama
            for dosen in obj.dosen_pendamping.all()
        ]


class FaceEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceEmbedding
        fields = '__all__'


class SesiAbsensiSerializer(serializers.ModelSerializer):
    mata_kuliah_nama = serializers.CharField(
        source='jadwal.mata_kuliah.nama_mata_kuliah',
        read_only=True
    )
    kelas_nama = serializers.CharField(
        source='jadwal.kelas.nama_kelas',
        read_only=True
    )
    daftar_kehadiran = serializers.SerializerMethodField()

    class Meta:
        model = SesiAbsensi
        fields = [
            'id',
            'jadwal',
            'mata_kuliah_nama',
            'kelas_nama',
            'waktu_buka',
            'waktu_tutup',
            'aktif',
            'daftar_kehadiran',
        ]

    def get_daftar_kehadiran(self, obj):
        riwayat_per_mahasiswa = {
            riwayat.mahasiswa_id: riwayat
            for riwayat in obj.riwayat_absensi.all()
        }
        mahasiswa_di_kelas = Mahasiswa.objects.filter(
            kelas_id=obj.jadwal.kelas_id
        ).order_by('nama', 'npm')

        return [
            {
                'mahasiswa': mahasiswa.id,
                'nama': mahasiswa.nama,
                'npm': mahasiswa.npm,
                'status': (
                    riwayat_per_mahasiswa[mahasiswa.id].status
                    if mahasiswa.id in riwayat_per_mahasiswa
                    else 'ALFA'
                ),
                'waktu_absen': (
                    riwayat_per_mahasiswa[mahasiswa.id].waktu_absen
                    if mahasiswa.id in riwayat_per_mahasiswa
                    else None
                ),
            }
            for mahasiswa in mahasiswa_di_kelas
        ]


class RiwayatAbsensiSerializer(serializers.ModelSerializer):

    nama_mahasiswa = serializers.CharField(
        source='mahasiswa.nama',
        read_only=True
    )

    npm = serializers.CharField(
        source='mahasiswa.npm',
        read_only=True
    )

    nama_kelas = serializers.CharField(
        source='mahasiswa.kelas.nama_kelas',
        read_only=True
    )

    nama_mata_kuliah = serializers.CharField(
        source='sesi_absensi.jadwal.mata_kuliah.nama_mata_kuliah',
        read_only=True
    )

    nama_dosen = serializers.CharField(
        source='sesi_absensi.jadwal.dosen.nama',
        read_only=True
    )

    class Meta:
        model = RiwayatAbsensi
        fields = [
            'id',
            'mahasiswa',
            'nama_mahasiswa',
            'npm',
            'nama_kelas',
            'sesi_absensi',
            'nama_mata_kuliah',
            'nama_dosen',
            'waktu_absen',
            'status',
            'distance_score',
        ]

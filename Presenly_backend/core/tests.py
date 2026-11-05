from io import StringIO
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import (
    Dosen,
    Jadwal,
    Kelas,
    Mahasiswa,
    MataKuliah,
    RiwayatAbsensi,
    SesiAbsensi,
)
from .serializers import (
    JadwalSerializer,
    MahasiswaSerializer,
    SesiAbsensiSerializer,
)
from .views import (
    get_or_create_sesi_absensi,
    tentukan_status_kehadiran,
)


class KehadiranSesiTests(TestCase):
    def setUp(self):
        self.kelas = Kelas.objects.create(nama_kelas='TI-1')
        dosen = Dosen.objects.create(
            nama='Dosen Uji',
            nidn='123456',
            email='dosen@example.com',
        )
        mata_kuliah = MataKuliah.objects.create(
            nama_mata_kuliah='Pemrograman',
            kode_mata_kuliah='PRG-1',
        )
        self.jadwal = Jadwal.objects.create(
            mata_kuliah=mata_kuliah,
            kelas=self.kelas,
            dosen=dosen,
            hari='Senin',
            jam_mulai=time(8, 0),
            jam_selesai=time(10, 0),
        )
        self.waktu_mulai = timezone.make_aware(
            datetime(2026, 11, 2, 8, 0)
        )
        self.sesi = SesiAbsensi.objects.create(
            jadwal=self.jadwal,
            waktu_buka=self.waktu_mulai,
            waktu_tutup=self.waktu_mulai + timedelta(hours=2),
            aktif=True,
        )
        self.mahasiswa = Mahasiswa.objects.create(
            npm='12345678',
            nama='Mahasiswa Uji',
            kelas=self.kelas,
        )

    def test_status_berdasarkan_batas_keterlambatan(self):
        self.assertEqual(
            tentukan_status_kehadiran(
                self.waktu_mulai - timedelta(minutes=1),
                self.sesi,
            ),
            'HADIR',
        )
        self.assertEqual(
            tentukan_status_kehadiran(
                self.waktu_mulai + timedelta(minutes=10),
                self.sesi,
            ),
            'TERLAMBAT',
        )
        self.assertEqual(
            tentukan_status_kehadiran(
                self.waktu_mulai + timedelta(minutes=10, seconds=1),
                self.sesi,
            ),
            'ALFA',
        )

    def test_sesi_dibuat_otomatis_dari_jadwal_kelas_mahasiswa(self):
        waktu_scan = self.waktu_mulai + timedelta(minutes=5)

        sesi = get_or_create_sesi_absensi(
            self.mahasiswa,
            waktu_scan,
        )

        self.assertIsNotNone(sesi)
        self.assertTrue(sesi.aktif)
        self.assertEqual(sesi.jadwal_id, self.jadwal.id)
        self.assertEqual(sesi.waktu_buka, self.waktu_mulai)
        self.assertEqual(
            sesi.waktu_tutup,
            self.waktu_mulai + timedelta(hours=2),
        )

    def test_tidak_membuat_sesi_di_luar_jam_jadwal(self):
        sesi = get_or_create_sesi_absensi(
            self.mahasiswa,
            self.waktu_mulai + timedelta(hours=3),
        )

        self.assertIsNone(sesi)
        self.assertEqual(SesiAbsensi.objects.count(), 1)

    def test_daftar_sesi_menampilkan_nama_dan_status_alfa_bawaan(self):
        data = SesiAbsensiSerializer(self.sesi).data

        self.assertEqual(data['mata_kuliah_nama'], 'Pemrograman')
        self.assertEqual(data['kelas_nama'], 'TI-1')
        self.assertEqual(
            data['daftar_kehadiran'],
            [{
                'mahasiswa': self.mahasiswa.id,
                'nama': 'Mahasiswa Uji',
                'npm': '12345678',
                'status': 'ALFA',
                'waktu_absen': None,
            }],
        )

    def test_daftar_sesi_menggunakan_status_dari_hasil_scan(self):
        RiwayatAbsensi.objects.create(
            mahasiswa=self.mahasiswa,
            sesi_absensi=self.sesi,
            status='TERLAMBAT',
        )

        data = SesiAbsensiSerializer(self.sesi).data

        self.assertEqual(
            data['daftar_kehadiran'][0]['status'],
            'TERLAMBAT',
        )

    def test_mahasiswa_serializer_mendukung_id_kelas_form_lama(self):
        kelas_lama = Kelas.objects.create(nama_kelas='TRI 5A')
        serializer = MahasiswaSerializer(data={
            'npm': '87654321',
            'nama': 'Mahasiswa Lama',
            'kelas': 1,
        })
        serializer.fields['kelas'].queryset = Kelas.objects.exclude(pk=1)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data['kelas'].nama_kelas,
            kelas_lama.nama_kelas,
        )

    def test_jadwal_serializer_menampilkan_nama_dosen_keduanya(self):
        dosen_anggota = Dosen.objects.create(
            nama='Dosen Pendamping',
        )
        self.jadwal.dosen_pendamping.add(dosen_anggota)

        data = JadwalSerializer(self.jadwal).data

        self.assertEqual(data['dosen_nama'], 'Dosen Uji')
        self.assertEqual(
            data['dosen_pendamping_nama'],
            ['Dosen Pendamping'],
        )

    def test_perintah_membuat_jadwal_kelas_lima_dengan_idempotent(self):
        Kelas.objects.create(nama_kelas='TRI 5A')
        Kelas.objects.create(nama_kelas='TRI 5B')
        Kelas.objects.create(nama_kelas='TRI 5C')

        call_command('setup_jadwal_kelas5', stdout=StringIO())
        jumlah_jadwal = Jadwal.objects.filter(
            kelas__nama_kelas__in=['TRI 5A', 'TRI 5B', 'TRI 5C']
        ).count()

        self.assertEqual(jumlah_jadwal, 39)
        self.assertEqual(
            Jadwal.objects.filter(
                mata_kuliah__kode_mata_kuliah='PIE 1515',
                kelas__nama_kelas='TRI 5A',
                hari='Senin',
            ).count(),
            2,
        )
        self.assertTrue(
            Jadwal.objects.filter(
                mata_kuliah__kode_mata_kuliah='PIE 1515',
                kelas__nama_kelas='TRI 5A',
                hari='Senin',
                jam_mulai=time(13, 50),
                jam_selesai=time(17, 50),
                jenis_pertemuan='P',
            ).exists()
        )

        call_command('setup_jadwal_kelas5', stdout=StringIO())

        self.assertEqual(
            Jadwal.objects.filter(
                kelas__nama_kelas__in=['TRI 5A', 'TRI 5B', 'TRI 5C']
            ).count(),
            jumlah_jadwal,
        )

    def test_admin_dapat_membuat_jadwal_otomatis_via_api(self):
        Kelas.objects.create(nama_kelas='TRI 5A')
        Kelas.objects.create(nama_kelas='TRI 5B')
        Kelas.objects.create(nama_kelas='TRI 5C')
        admin = get_user_model().objects.create_superuser(
            username='admin-jadwal',
            email='admin-jadwal@example.com',
            password='test-password',
        )
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post('/api/jadwal/generate-kelas5/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_jadwal'], 39)
        self.assertEqual(
            Jadwal.objects.filter(
                kelas__nama_kelas__in=['TRI 5A', 'TRI 5B', 'TRI 5C']
            ).count(),
            39,
        )

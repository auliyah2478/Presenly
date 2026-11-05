from datetime import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Dosen, Jadwal, Kelas, MataKuliah


DOSEN_PER_MATA_KULIAH = {
    'PIE 1511': (
        'Dr. Ir. Septiansyah Dwi Putra, S.T.',
        'Ir. Ismail Puji Saputra, S.Kom.',
    ),
    'PIE 1512': (
        'Dr. Ir. Septiansyah Dwi Putra, S.T.',
        'Ir. Ismail Puji Saputra, S.Kom.',
    ),
    'PIE 1513': (
        'Ir. Imam Asrorwadi, S.Kom., M.Kom.',
        'Agus Ambarwari, S.Pd., M.Kom.',
    ),
    'PIE 1514': (
        'Dr. Ir. Septiansyah Dwi Putra, S.T.',
        'Ir. Ismail Puji Saputra, S.Kom.',
    ),
    'PIE 1515': (
        'Ir. Imam Asrorwadi, S.Kom., M.Kom.',
        'Ir. Eko Subagiyanto, S.Kom.',
    ),
    'PIE 1516': (
        'Ir. Dian Ayu Afifah, S.Si., M.Sc.',
        'Ir. Nurul Gomariah, S.Kom.',
    ),
    'PKU 1511': (
        'Ir. Imam Asrorwadi, S.Kom., M.Kom.',
        'Agus Ambarwari, S.Pd., M.Kom.',
    ),
}

MATA_KULIAH = {
    'PKU 1511': 'Proyek Mandiri',
    'PIE 1511': 'Keamanan Siber',
    'PIE 1512': 'Teknologi Fiber Optik',
    'PIE 1513': 'Infrastruktur dan Otomasi Jaringan',
    'PIE 1514': 'Teknologi Komputer Awan II',
    'PIE 1515': 'Jaringan Komputer IV',
    'PIE 1516': 'Pemrograman Internet II',
}

SLOT_JADWAL = [
    ('Senin', 'PIE 1515', 'K', time(13, 0), time(13, 50)),
    ('Senin', 'PIE 1515', 'P', time(13, 50), time(17, 50)),
    ('Selasa', 'PIE 1511', 'K', time(7, 0), time(8, 40)),
    ('Selasa', 'PIE 1511', 'P', time(8, 40), time(12, 40)),
    ('Selasa', 'PIE 1512', 'K', time(13, 0), time(13, 50)),
    ('Selasa', 'PIE 1512', 'P', time(13, 50), time(15, 50)),
    ('Rabu', 'PIE 1514', 'K', time(7, 0), time(7, 50)),
    ('Rabu', 'PIE 1514', 'P', time(7, 50), time(11, 50)),
    ('Rabu', 'PIE 1513', 'K', time(13, 0), time(13, 50)),
    ('Rabu', 'PIE 1513', 'P', time(13, 50), time(17, 50)),
    ('Kamis', 'PKU 1511', 'P', time(13, 0), time(19, 0)),
    ('Jumat', 'PIE 1516', 'K', time(13, 0), time(14, 20)),
    ('Jumat', 'PIE 1516', 'P', time(14, 20), time(18, 20)),
]


class Command(BaseCommand):
    help = 'Create or update the weekly class-5 schedule from the supplied timetable.'

    @transaction.atomic
    def handle(self, *args, **options):
        kelas_per_angkatan = {}
        for suffix in ('A', 'B', 'C'):
            nama_kelas = f'TRI 5{suffix}'
            try:
                kelas_per_angkatan[suffix] = Kelas.objects.get(
                    nama_kelas=nama_kelas
                )
            except Kelas.DoesNotExist as error:
                raise CommandError(
                    f'Kelas {nama_kelas} belum ada di database.'
                ) from error

        dosen = {}
        for nama_dosen in {
            nama
            for pasangan in DOSEN_PER_MATA_KULIAH.values()
            for nama in pasangan
        }:
            dosen[nama_dosen], _ = Dosen.objects.get_or_create(
                nama=nama_dosen,
                defaults={
                    'nidn': None,
                    'email': None,
                }
            )

        mata_kuliah = {}
        for kode, nama in MATA_KULIAH.items():
            course, _ = MataKuliah.objects.get_or_create(
                kode_mata_kuliah=kode,
                defaults={'nama_mata_kuliah': nama}
            )
            if course.nama_mata_kuliah != nama:
                course.nama_mata_kuliah = nama
                course.save(update_fields=['nama_mata_kuliah'])
            mata_kuliah[kode] = course

        jumlah_dibuat = 0
        jumlah_diperbarui = 0

        for suffix, kelas in kelas_per_angkatan.items():
            for hari, kode, jenis, jam_mulai, jam_selesai in SLOT_JADWAL:
                dosen_pj, dosen_anggota = DOSEN_PER_MATA_KULIAH[kode]
                jadwal, dibuat = Jadwal.objects.get_or_create(
                    mata_kuliah=mata_kuliah[kode],
                    kelas=kelas,
                    hari=hari,
                    jam_mulai=jam_mulai,
                    jenis_pertemuan=jenis,
                    defaults={
                        'dosen': dosen[dosen_pj],
                        'jam_selesai': jam_selesai,
                    }
                )
                jadwal.jam_selesai = jam_selesai
                jadwal.dosen = dosen[dosen_pj]
                jadwal.save(update_fields=[
                    'jam_selesai',
                    'dosen',
                ])
                jadwal.dosen_pendamping.set([dosen[dosen_anggota]])

                if dibuat:
                    jumlah_dibuat += 1
                else:
                    jumlah_diperbarui += 1

        self.stdout.write(self.style.SUCCESS(
            f'Jadwal kelas 5 selesai: {jumlah_dibuat} dibuat, '
            f'{jumlah_diperbarui} diperbarui untuk 3 kelas. '
            f'Total slot terjadwal: {len(SLOT_JADWAL) * 3}.'
        ))

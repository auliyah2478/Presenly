from django import forms
from .models import Mahasiswa, Dosen, Jadwal, Kelas, MataKuliah


class MahasiswaForm(forms.ModelForm):

    class Meta:
        model = Mahasiswa

        fields = [
            "npm",
            "nama",
            "email",
            "kelas",
        ]

        labels = {
            "npm": "Nomor Pokok Mahasiswa (NPM)",
            "nama": "Nama Lengkap",
            "email": "Alamat Email",
            "kelas": "Kelas",
        }

        widgets = {
            "npm": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan NPM mahasiswa",
            }),

            "nama": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan nama lengkap mahasiswa",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan email (opsional)",
            }),

            "kelas": forms.Select(attrs={
                "class": "form-control",
            }),
        }


class DosenForm(forms.ModelForm):
    class Meta:
        model = Dosen
        fields = ["user", "nama", "nidn", "email"]

        labels = {
            "user": "Akun Pengguna (Opsional)",
            "nama": "Nama Lengkap Dosen",
            "nidn": "Nomor Induk Dosen Nasional (NIDN)",
            "email": "Alamat Email",
        }

        widgets = {
            "user": forms.Select(attrs={
                "class": "form-control",
            }),
            "nama": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan nama lengkap dosen",
            }),
            "nidn": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan NIDN dosen",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Masukkan alamat email dosen",
            }),
        }


class JadwalForm(forms.ModelForm):
    class Meta:
        model = Jadwal

        fields = [
            "mata_kuliah",
            "kelas",
            "dosen",
            "dosen_pendamping",
            "hari",
            "jam_mulai",
            "jam_selesai",
            "jenis_pertemuan",
        ]

        labels = {
            "mata_kuliah": "Mata Kuliah",
            "kelas": "Kelas",
            "dosen": "Dosen Pengajar",
            "dosen_pendamping": "Dosen Pendamping",
            "hari": "Hari Perkuliahan",
            "jam_mulai": "Jam Mulai",
            "jam_selesai": "Jam Selesai",
            "jenis_pertemuan": "Jenis Pertemuan",
        }

        widgets = {
            "mata_kuliah": forms.Select(attrs={
                "class": "form-control",
            }),

            "kelas": forms.Select(attrs={
                "class": "form-control",
            }),

            "dosen": forms.Select(attrs={
                "class": "form-control",
            }),

            "dosen_pendamping": forms.CheckboxSelectMultiple(),

            "hari": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Senin",
            }),

            "jam_mulai": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),

            "jam_selesai": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),

            "jenis_pertemuan": forms.Select(attrs={
                "class": "form-control",
            }),
        }


class KelasForm(forms.ModelForm):
    class Meta:
        model = Kelas

        fields = ["nama_kelas"]

        labels = {
            "nama_kelas": "Nama Kelas",
        }

        widgets = {
            "nama_kelas": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: TI-4A",
            }),
        }

class MataKuliahForm(forms.ModelForm):
    class Meta:
        model = MataKuliah

        fields = [
            "kode_mata_kuliah",
            "nama_mata_kuliah",
        ]

        labels = {
            "kode_mata_kuliah": "Kode Mata Kuliah",
            "nama_mata_kuliah": "Nama Mata Kuliah",
        }

        widgets = {
            "kode_mata_kuliah": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: IF101",
            }),

            "nama_mata_kuliah": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contoh: Pemrograman Web",
            }),
        }
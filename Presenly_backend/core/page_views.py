from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

from .models import (
    Kelas,
    Dosen,
    Mahasiswa,
    MataKuliah,
    Jadwal,
    RiwayatAbsensi,
    SesiAbsensi,
)

from .forms import (
    MahasiswaForm,
    DosenForm,
    JadwalForm,
    KelasForm,
    MataKuliahForm,
)

def welcome_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, "presenly/welcome.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            error = "Username dan password wajib diisi."

        else:
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is None:
                error = "Username atau password salah."

            elif user.is_superuser:
                auth_login(request, user)
                return redirect("dashboard")

            elif hasattr(user, "dosen_profile"):
                auth_login(request, user)
                return redirect("dashboard")

            else:
                error = "Akun belum terhubung dengan data dosen."

    return render(
        request,
        "presenly/login.html",
        {"error": error}
    )


def dashboard_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_superuser:
        role = "Administrator"
    elif hasattr(request.user, "dosen_profile"):
        role = "Dosen"
    else:
        role = "Pengguna"

    context = {
        "nama_pengguna": (
            request.user.get_full_name()
            or request.user.username
        ),
        "role_pengguna": role,
        "total_mahasiswa": Mahasiswa.objects.count(),
        "total_dosen": Dosen.objects.count(),
        "total_kelas": Kelas.objects.count(),
        "total_mata_kuliah": MataKuliah.objects.count(),
        "total_jadwal": Jadwal.objects.count(),
        "total_absensi": RiwayatAbsensi.objects.count(),
        "sesi_aktif": SesiAbsensi.objects.filter(
            aktif=True
        ).count(),
    }

    return render(
        request,
        "presenly/dashboard.html",
        context
    )


def logout_page(request):
    if request.method == "POST":
        auth_logout(request)
        return redirect("welcome")

    return redirect("dashboard")


def section_page(request, section):
    if not request.user.is_authenticated:
        return redirect("login")

    sections = {
        "mahasiswa": {
            "title": "Data Mahasiswa",
            "description": "Kelola informasi seluruh mahasiswa.",
            "items": Mahasiswa.objects.select_related("kelas").all(),
        },
        "dosen": {
            "title": "Data Dosen",
            "description": "Kelola informasi dosen pengajar.",
            "items": Dosen.objects.all(),
        },
        "jadwal": {
            "title": "Jadwal Kuliah",
            "description": "Kelola jadwal kegiatan perkuliahan.",
            "items": Jadwal.objects.select_related(
                "mata_kuliah", "kelas", "dosen"
            ).prefetch_related("dosen_pendamping").all(),
        },
        "kelas": {
            "title": "Data Kelas",
            "description": "Kelola data kelas mahasiswa.",
            "items": Kelas.objects.all(),
        },
        "mata-kuliah": {
            "title": "Mata Kuliah",
            "description": "Kelola daftar mata kuliah.",
            "items": MataKuliah.objects.all(),
        },
        "absensi": {
            "title": "Riwayat Absensi",
            "description": "Pantau seluruh catatan kehadiran mahasiswa.",
            "items": RiwayatAbsensi.objects.select_related(
                "mahasiswa",
                "sesi_absensi",
                "sesi_absensi__jadwal",
                "sesi_absensi__jadwal__mata_kuliah",
            ).order_by("-waktu_absen"),
        },
    }

    page = sections.get(section)

    if page is None:
        return redirect("dashboard")

    context = {
        "nama_pengguna": (
            request.user.get_full_name()
            or request.user.username
        ),
        "role_pengguna": (
            "Administrator"
            if request.user.is_superuser
            else "Dosen"
        ),
        "section": section,
        "page_title": page["title"],
        "page_description": page["description"],
        "items": page["items"],
        "total_data": page["items"].count(),
    }

    return render(
        request,
        "presenly/section.html",
        context
    )


# =====================================
# CRUD DATA MAHASISWA
# =====================================

def mahasiswa_tambah(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = MahasiswaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Data mahasiswa berhasil ditambahkan."
            )
            return redirect("data_mahasiswa")

    else:
        form = MahasiswaForm()

    return render(
        request,
        "presenly/mahasiswa_form.html",
        {
            "form": form,
            "judul_form": "Tambah Mahasiswa",
            "mode": "tambah",
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )


def mahasiswa_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    mahasiswa = get_object_or_404(Mahasiswa, pk=pk)

    if request.method == "POST":
        form = MahasiswaForm(
            request.POST,
            instance=mahasiswa
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Data mahasiswa berhasil diperbarui."
            )
            return redirect("data_mahasiswa")

    else:
        form = MahasiswaForm(instance=mahasiswa)

    return render(
        request,
        "presenly/mahasiswa_form.html",
        {
            "form": form,
            "judul_form": "Edit Mahasiswa",
            "mode": "edit",
            "mahasiswa": mahasiswa,
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )


def mahasiswa_hapus(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    mahasiswa = get_object_or_404(Mahasiswa, pk=pk)

    if request.method == "POST":
        mahasiswa.delete()

        messages.success(
            request,
            "Data mahasiswa berhasil dihapus."
        )

        return redirect("data_mahasiswa")

    return render(
        request,
        "presenly/mahasiswa_confirm_delete.html",
        {
            "mahasiswa": mahasiswa,
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )


# ==========================================
# CRUD DATA DOSEN
# ==========================================

def dosen_tambah(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = DosenForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Data dosen berhasil ditambahkan.")
            return redirect("data_dosen")
    else:
        form = DosenForm()

    context = {
        "form": form,
        "page_title": "Tambah Dosen",
        "form_action": "Tambah Dosen",
        "nama_pengguna": request.user.get_full_name() or request.user.username,
    }

    return render(request, "presenly/dosen_form.html", context)


def dosen_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    dosen = get_object_or_404(Dosen, pk=pk)

    if request.method == "POST":
        form = DosenForm(request.POST, instance=dosen)

        if form.is_valid():
            form.save()
            messages.success(request, "Data dosen berhasil diperbarui.")
            return redirect("data_dosen")
    else:
        form = DosenForm(instance=dosen)

    context = {
        "form": form,
        "page_title": "Edit Data Dosen",
        "form_action": "Simpan Perubahan",
        "nama_pengguna": request.user.get_full_name() or request.user.username,
    }

    return render(request, "presenly/dosen_form.html", context)


def dosen_hapus(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    dosen = get_object_or_404(Dosen, pk=pk)

    if request.method == "POST":
        dosen.delete()
        messages.success(request, "Data dosen berhasil dihapus.")
        return redirect("data_dosen")

    context = {
        "dosen": dosen,
        "nama_pengguna": request.user.get_full_name() or request.user.username,
    }

    return render(
        request,
        "presenly/dosen_confirm_delete.html",
        context
    )


# ==========================================
# CRUD JADWAL KULIAH
# ==========================================

def jadwal_tambah(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwalForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Jadwal kuliah berhasil ditambahkan.")
            return redirect("data_jadwal")
    else:
        form = JadwalForm()

    context = {
        "form": form,
        "page_title": "Tambah Jadwal Kuliah",
        "form_action": "Tambah Jadwal",
        "nama_pengguna": request.user.get_full_name() or request.user.username,
    }

    return render(request, "presenly/jadwal_form.html", context)


def jadwal_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    jadwal = get_object_or_404(Jadwal, pk=pk)

    if request.method == "POST":
        form = JadwalForm(request.POST, instance=jadwal)

        if form.is_valid():
            form.save()
            messages.success(request, "Jadwal kuliah berhasil diperbarui.")
            return redirect("data_jadwal")
    else:
        form = JadwalForm(instance=jadwal)

    context = {
        "form": form,
        "page_title": "Edit Jadwal Kuliah",
        "form_action": "Simpan Perubahan",
        "nama_pengguna": request.user.get_full_name() or request.user.username,
    }

    return render(request, "presenly/jadwal_form.html", context)


def jadwal_hapus(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.is_superuser:
        return redirect("dashboard")

    jadwal = get_object_or_404(Jadwal, pk=pk)

    if request.method == "POST":
        try:
            jadwal.delete()

            messages.success(
                request,
                "Jadwal kuliah berhasil dihapus."
            )

        except ProtectedError:
            messages.error(
                request,
                "Jadwal tidak dapat dihapus karena masih memiliki "
                "sesi absensi atau riwayat kehadiran. "
                "Data absensi mahasiswa tetap dilindungi."
            )

        return redirect("data_jadwal")

    context = {
        "jadwal": jadwal,
        "nama_pengguna": (
            request.user.get_full_name() or request.user.username
        ),
    }

    return render(
        request,
        "presenly/jadwal_confirm_delete.html",
        context
    )


# ==========================================
# CRUD DATA KELAS
# ==========================================

@login_required
def kelas_tambah(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = KelasForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Data kelas berhasil ditambahkan."
            )

            return redirect("data_kelas")

    else:
        form = KelasForm()

    context = {
        "form": form,
        "judul": "Tambah Kelas",
        "nama_pengguna": (
            request.user.get_full_name()
            or request.user.username
        ),
        "role_pengguna": "Administrator",
    }

    return render(
        request,
        "presenly/kelas_form.html",
        context
    )


@login_required
def kelas_edit(request, pk):
    if not request.user.is_superuser:
        return redirect("dashboard")

    kelas = get_object_or_404(Kelas, pk=pk)

    if request.method == "POST":
        form = KelasForm(
            request.POST,
            instance=kelas
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Data kelas berhasil diperbarui."
            )

            return redirect("data_kelas")

    else:
        form = KelasForm(instance=kelas)

    context = {
        "form": form,
        "judul": "Edit Kelas",
        "nama_pengguna": (
            request.user.get_full_name()
            or request.user.username
        ),
        "role_pengguna": "Administrator",
    }

    return render(
        request,
        "presenly/kelas_form.html",
        context
    )


@login_required
def kelas_hapus(request, pk):
    if not request.user.is_superuser:
        return redirect("dashboard")

    kelas = get_object_or_404(Kelas, pk=pk)

    if request.method == "POST":

        memiliki_mahasiswa = Mahasiswa.objects.filter(
            kelas=kelas
        ).exists()

        memiliki_jadwal = Jadwal.objects.filter(
            kelas=kelas
        ).exists()

        if memiliki_mahasiswa or memiliki_jadwal:
            messages.error(
                request,
                "Kelas tidak dapat dihapus karena masih memiliki "
                "data mahasiswa atau jadwal."
            )

            return redirect("data_kelas")

        try:
            kelas.delete()

            messages.success(
                request,
                "Data kelas berhasil dihapus."
            )

        except ProtectedError:
            messages.error(
                request,
                "Kelas tidak dapat dihapus karena masih digunakan "
                "oleh data lain."
            )

        return redirect("data_kelas")

    context = {
        "kelas": kelas,
        "nama_pengguna": (
            request.user.get_full_name()
            or request.user.username
        ),
        "role_pengguna": "Administrator",
    }

    return render(
        request,
        "presenly/kelas_confirm_delete.html",
        context
    )

# ==========================================
# CRUD DATA MATA KULIAH
# ==========================================

@login_required
def mata_kuliah_tambah(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = MataKuliahForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Mata kuliah berhasil ditambahkan."
            )

            return redirect("data_mata_kuliah")

    else:
        form = MataKuliahForm()

    return render(
        request,
        "presenly/mata_kuliah_form.html",
        {
            "form": form,
            "judul": "Tambah Mata Kuliah",
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )


@login_required
def mata_kuliah_edit(request, pk):
    if not request.user.is_superuser:
        return redirect("dashboard")

    mata_kuliah = get_object_or_404(
        MataKuliah,
        pk=pk
    )

    if request.method == "POST":
        form = MataKuliahForm(
            request.POST,
            instance=mata_kuliah
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Mata kuliah berhasil diperbarui."
            )

            return redirect("data_mata_kuliah")

    else:
        form = MataKuliahForm(instance=mata_kuliah)

    return render(
        request,
        "presenly/mata_kuliah_form.html",
        {
            "form": form,
            "judul": "Edit Mata Kuliah",
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )


@login_required
def mata_kuliah_hapus(request, pk):
    if not request.user.is_superuser:
        return redirect("dashboard")

    mata_kuliah = get_object_or_404(
        MataKuliah,
        pk=pk
    )

    if request.method == "POST":

        memiliki_jadwal = Jadwal.objects.filter(
            mata_kuliah=mata_kuliah
        ).exists()

        if memiliki_jadwal:
            messages.error(
                request,
                "Mata kuliah tidak dapat dihapus karena "
                "masih digunakan oleh jadwal kuliah."
            )

            return redirect("data_mata_kuliah")

        mata_kuliah.delete()

        messages.success(
            request,
            "Mata kuliah berhasil dihapus."
        )

        return redirect("data_mata_kuliah")

    return render(
        request,
        "presenly/mata_kuliah_confirm_delete.html",
        {
            "mata_kuliah": mata_kuliah,
            "nama_pengguna": (
                request.user.get_full_name()
                or request.user.username
            ),
            "role_pengguna": "Administrator",
        }
    )
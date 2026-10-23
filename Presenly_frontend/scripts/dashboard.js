const API_URL =
    "http://127.0.0.1:8000/api";

const token =
    localStorage.getItem("token");

const role =
    localStorage.getItem("role");

const username =
    localStorage.getItem("username");


// ====================================
// CEK LOGIN
// ====================================

if (!token || !role) {

    window.location.replace(
        "login.html"
    );
}


// ====================================
// TAMPILKAN USER
// ====================================

document.getElementById(
    "username"
).innerText =
    username || "User";


document.getElementById(
    "roleBadge"
).innerText =
    role.toUpperCase();


// ====================================
// AMBIL ELEMEN DASHBOARD
// ====================================

const dashboardAdmin =
    document.getElementById(
        "dashboardAdmin"
    );

const dashboardDosen =
    document.getElementById(
        "dashboardDosen"
    );

const menuAdmin =
    document.getElementById(
        "menuAdmin"
    );

const menuDosen =
    document.getElementById(
        "menuDosen"
    );

const judulDashboard =
    document.getElementById(
        "judulDashboard"
    );


// ====================================
// ELEMEN KELOLA JADWAL & SESI
// ====================================

const menuJadwal =
    document.getElementById(
        "menuJadwal"
    );

const menuSesi =
    document.getElementById(
        "menuSesi"
    );

const sectionJadwal =
    document.getElementById(
        "sectionJadwal"
    );

const sectionSesiAbsensi =
    document.getElementById(
        "sectionSesiAbsensi"
    );


// ====================================
// SEMBUNYIKAN SEMUA KONTEN
// ====================================

function sembunyikanSemuaKonten() {

    if (dashboardAdmin) {
        dashboardAdmin.style.display =
            "none";
    }

    if (dashboardDosen) {
        dashboardDosen.style.display =
            "none";
    }

    if (sectionJadwal) {
        sectionJadwal.style.display =
            "none";
    }

    if (sectionSesiAbsensi) {
        sectionSesiAbsensi.style.display =
            "none";
    }
}


// ====================================
// TAMPILKAN DASHBOARD UTAMA
// ====================================

function tampilkanDashboardUtama() {

    sembunyikanSemuaKonten();

    if (role === "admin") {

        dashboardAdmin.style.display =
            "block";

        judulDashboard.innerText =
            "Dashboard Admin";

        loadDashboardAdmin();

    }

    else if (role === "dosen") {

        dashboardDosen.style.display =
            "block";

        judulDashboard.innerText =
            "Dashboard Dosen";

        loadDashboardDosen();

    }
}


// ====================================
// ATUR MENU BERDASARKAN ROLE
// ====================================

if (role === "admin") {

    dashboardAdmin.style.display =
        "block";

    dashboardDosen.style.display =
        "none";

    menuAdmin.style.display =
        "block";

    menuDosen.style.display =
        "none";

    judulDashboard.innerText =
        "Dashboard Admin";

    loadDashboardAdmin();

}

else if (role === "dosen") {

    dashboardAdmin.style.display =
        "none";

    dashboardDosen.style.display =
        "block";

    menuAdmin.style.display =
        "none";

    menuDosen.style.display =
        "block";

    judulDashboard.innerText =
        "Dashboard Dosen";

    loadDashboardDosen();

}

else {

    alert(
        "Role pengguna tidak dikenali."
    );

    localStorage.clear();

    window.location.replace(
        "login.html"
    );
}


// ====================================
// LOGOUT
// ====================================

document.getElementById(
    "logoutButton"
).addEventListener(
    "click",
    function () {

        localStorage.clear();

        window.location.replace(
            "login.html"
        );
    }
);


// ====================================
// GET API
// ====================================

async function getData(endpoint) {

    const response =
        await fetch(
            `${API_URL}/${endpoint}/`,
            {
                headers: {

                    "Authorization":
                        `Token ${token}`
                }
            }
        );


    if (!response.ok) {

        throw new Error(
            `Gagal mengambil ${endpoint}`
        );
    }


    return await response.json();
}


// ====================================
// DASHBOARD ADMIN
// ====================================

let daftarMahasiswa = [];


async function loadDashboardAdmin() {

    try {

        const [
            mahasiswa,
            kelas,
            jadwal,
            absensi
        ] = await Promise.all([

            getData("mahasiswa"),
            getData("kelas"),
            getData("jadwal"),
            getData("riwayat-absensi")
        ]);


        daftarMahasiswa =
            mahasiswa;


        document.getElementById(
            "totalMahasiswa"
        ).innerText =
            mahasiswa.length;


        document.getElementById(
            "totalKelas"
        ).innerText =
            kelas.length;


        document.getElementById(
            "totalJadwalAdmin"
        ).innerText =
            jadwal.length;


        document.getElementById(
            "totalAbsensiAdmin"
        ).innerText =
            absensi.length;


        tampilkanMahasiswa(
            mahasiswa
        );


    } catch (error) {

        console.error(
            "Admin dashboard error:",
            error
        );
    }
}


// ====================================
// DATA MAHASISWA
// ====================================

function tampilkanMahasiswa(data) {

    const table =
        document.getElementById(
            "mahasiswaTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    data.forEach(
        function (mhs, index) {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${mhs.npm ?? "-"}
                </td>

                <td>
                    ${mhs.nama ?? "-"}
                </td>

                <td>
                    ${mhs.email || "-"}
                </td>

                <td>
                    ${
                        mhs.kelas_nama ??
                        mhs.kelas ??
                        "-"
                    }
                </td>

            `;


            table.appendChild(
                row
            );
        }
    );
}


// ====================================
// SEARCH MAHASISWA
// ====================================

const searchMahasiswa =
    document.getElementById(
        "searchMahasiswa"
    );


if (searchMahasiswa) {

    searchMahasiswa.addEventListener(
        "input",
        function () {

            if (role !== "admin") {
                return;
            }


            const keyword =
                this.value
                    .toLowerCase();


            const hasil =
                daftarMahasiswa.filter(
                    function (mhs) {

                        const nama =
                            String(
                                mhs.nama || ""
                            ).toLowerCase();


                        const npm =
                            String(
                                mhs.npm || ""
                            ).toLowerCase();


                        return (
                            nama.includes(
                                keyword
                            )

                            ||

                            npm.includes(
                                keyword
                            )
                        );
                    }
                );


            tampilkanMahasiswa(
                hasil
            );
        }
    );
}


// ====================================
// DASHBOARD DOSEN
// ====================================

async function loadDashboardDosen() {

    try {

        const [
            jadwal,
            absensi
        ] = await Promise.all([

            getData("jadwal"),
            getData("riwayat-absensi")
        ]);


        document.getElementById(
            "totalJadwalDosen"
        ).innerText =
            jadwal.length;


        document.getElementById(
            "totalAbsensiDosen"
        ).innerText =
            absensi.length;


        const hadir =
            absensi.filter(
                item =>
                    item.status ===
                    "HADIR"
            );


        const terlambat =
            absensi.filter(
                item =>
                    item.status ===
                    "TERLAMBAT"
            );


        document.getElementById(
            "totalHadir"
        ).innerText =
            hadir.length;


        document.getElementById(
            "totalTerlambat"
        ).innerText =
            terlambat.length;


        tampilkanJadwalDosen(
            jadwal
        );


        tampilkanAbsensiDosen(
            absensi
        );


    } catch (error) {

        console.error(
            "Dosen dashboard error:",
            error
        );
    }
}


// ====================================
// TABEL JADWAL DOSEN
// ====================================

function tampilkanJadwalDosen(data) {

    const table =
        document.getElementById(
            "jadwalDosenTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    data.forEach(
        function (jadwal, index) {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${
                        jadwal.mata_kuliah_nama ??
                        jadwal.mata_kuliah ??
                        "-"
                    }
                </td>

                <td>
                    ${
                        jadwal.kelas_nama ??
                        jadwal.kelas ??
                        "-"
                    }
                </td>

                <td>
                    ${jadwal.hari ?? "-"}
                </td>

                <td>
                    ${jadwal.jam_mulai ?? "-"}
                    -
                    ${jadwal.jam_selesai ?? "-"}
                </td>

            `;


            table.appendChild(
                row
            );
        }
    );
}


// ====================================
// ABSENSI DOSEN
// ====================================

function tampilkanAbsensiDosen(data) {

    const table =
        document.getElementById(
            "absensiDosenTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    data
        .slice()
        .reverse()
        .forEach(
            function (absen, index) {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${index + 1}
                    </td>

                    <td>
                        ${
                            absen.mahasiswa_nama ??
                            absen.mahasiswa ??
                            "-"
                        }
                    </td>

                    <td>
                        ${absen.status ?? "-"}
                    </td>

                    <td>
                        ${
                            absen.waktu_absen
                            ?

                            new Date(
                                absen.waktu_absen
                            ).toLocaleString(
                                "id-ID"
                            )

                            :

                            "-"
                        }
                    </td>

                `;


                table.appendChild(
                    row
                );
            }
        );
}


// ====================================
// KELOLA JADWAL ADMIN
// ====================================

async function loadJadwal() {

    try {

        const jadwal =
            await getData(
                "jadwal"
            );


        const table =
            document.getElementById(
                "jadwalTable"
            );


        if (!table) {

            console.error(
                "jadwalTable tidak ditemukan."
            );

            return;
        }


        table.innerHTML = "";


        if (jadwal.length === 0) {

            table.innerHTML = `

                <tr>
                    <td colspan="7">
                        Belum ada data jadwal.
                    </td>
                </tr>

            `;

            return;
        }


        jadwal.forEach(
            function (item, index) {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${index + 1}
                    </td>

                    <td>
                        ${item.hari ?? "-"}
                    </td>

                    <td>
                        ${
                            item.mata_kuliah_nama ??
                            item.mata_kuliah ??
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.kelas_nama ??
                            item.kelas ??
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.dosen_nama ??
                            item.dosen ??
                            "-"
                        }
                    </td>

                    <td>
                        ${item.jam_mulai ?? "-"}
                    </td>

                    <td>
                        ${item.jam_selesai ?? "-"}
                    </td>

                `;


                table.appendChild(
                    row
                );
            }
        );


    } catch (error) {

        console.error(
            "Gagal mengambil jadwal:",
            error
        );
    }
}


// ====================================
// SESI ABSENSI ADMIN
// ====================================

async function loadSesiAbsensi() {

    try {

        const sesi =
            await getData(
                "sesi-absensi"
            );


        const table =
            document.getElementById(
                "sesiTable"
            );


        if (!table) {

            console.error(
                "sesiTable tidak ditemukan."
            );

            return;
        }


        table.innerHTML = "";


        if (sesi.length === 0) {

            table.innerHTML = `

                <tr>
                    <td colspan="6">
                        Belum ada sesi absensi.
                    </td>
                </tr>

            `;

            return;
        }


        sesi.forEach(
            function (item, index) {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${index + 1}
                    </td>

                    <td>
                        ${
                            item.mata_kuliah_nama ??
                            item.jadwal_nama ??
                            item.jadwal ??
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.kelas_nama ??
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.waktu_buka
                            ?

                            new Date(
                                item.waktu_buka
                            ).toLocaleString(
                                "id-ID"
                            )

                            :

                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.waktu_tutup
                            ?

                            new Date(
                                item.waktu_tutup
                            ).toLocaleString(
                                "id-ID"
                            )

                            :

                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.aktif
                            ?
                            "Aktif"
                            :
                            "Tidak Aktif"
                        }
                    </td>

                `;


                table.appendChild(
                    row
                );
            }
        );


    } catch (error) {

        console.error(
            "Gagal mengambil sesi absensi:",
            error
        );
    }
}


// ====================================
// KLIK MENU KELOLA JADWAL
// ====================================

if (menuJadwal) {

    menuJadwal.addEventListener(
        "click",
        async function (event) {

            event.preventDefault();

            sembunyikanSemuaKonten();


            if (sectionJadwal) {

                sectionJadwal.style.display =
                    "block";
            }


            judulDashboard.innerText =
                "Kelola Jadwal";


            await loadJadwal();


            window.location.hash =
                "jadwal";
        }
    );
}


// ====================================
// KLIK MENU SESI ABSENSI
// ====================================

if (menuSesi) {

    menuSesi.addEventListener(
        "click",
        async function (event) {

            event.preventDefault();

            sembunyikanSemuaKonten();


            if (sectionSesiAbsensi) {

                sectionSesiAbsensi.style.display =
                    "block";
            }


            judulDashboard.innerText =
                "Sesi Absensi";


            await loadSesiAbsensi();


            window.location.hash =
                "sesi";
        }
    );
}


// ====================================
// CEK HASH SAAT REFRESH
// ====================================

async function cekHalamanAktif() {

    const hash =
        window.location.hash;


    if (
        hash === "#jadwal" &&
        role === "admin"
    ) {

        sembunyikanSemuaKonten();

        if (sectionJadwal) {

            sectionJadwal.style.display =
                "block";
        }

        judulDashboard.innerText =
            "Kelola Jadwal";

        await loadJadwal();
    }

    else if (
        hash === "#sesi" &&
        role === "admin"
    ) {

        sembunyikanSemuaKonten();

        if (sectionSesiAbsensi) {

            sectionSesiAbsensi.style.display =
                "block";
        }

        judulDashboard.innerText =
            "Sesi Absensi";

        await loadSesiAbsensi();
    }
}


cekHalamanAktif();
console.log("input_mahasiswa.js dimuat");

const API_URL = "http://127.0.0.1:8000/api";

const kelasSelect = document.getElementById("kelas");
const simpanButton = document.getElementById("simpanButton");
const message = document.getElementById("message");

const token = localStorage.getItem("token");

async function loadKelas() {
    try {
        const response = await fetch(`${API_URL}/kelas/`, {
            headers: {
                "Authorization": `Token ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Daftar kelas gagal dimuat."
            );
        }

        if (!Array.isArray(data)) {
            throw new Error("Format daftar kelas dari server tidak valid.");
        }

        data.forEach(function (kelas) {
            const option = document.createElement("option");
            option.value = kelas.id;
            option.textContent = kelas.nama_kelas;
            kelasSelect.appendChild(option);
        });

        if (data.length === 0) {
            throw new Error("Belum ada data kelas. Tambahkan kelas terlebih dahulu.");
        }

        simpanButton.disabled = false;
    } catch (error) {
        console.error("Gagal memuat daftar kelas:", error);
        message.innerText = error.message || "Gagal memuat daftar kelas.";
    }
}


// ===============================
// CEK LOGIN
// ===============================

if (!token) {
    window.location.replace("login.html");
}


// ===============================
// SIMPAN MAHASISWA
// ===============================

simpanButton.addEventListener("click", async function () {

    const npm = document
        .getElementById("npm")
        .value
        .trim();

    const nama = document
        .getElementById("nama")
        .value
        .trim();

    const email = document
        .getElementById("email")
        .value
        .trim();

    const kelas = kelasSelect.value;


    if (!npm || !nama || !kelas) {

        message.innerText =
            "NPM, nama, dan kelas wajib diisi.";

        return;
    }


    try {

        simpanButton.disabled = true;

        message.innerText =
            "Sedang menyimpan data mahasiswa...";


        const response = await fetch(
            `${API_URL}/mahasiswa/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Token ${token}`
                },

                body: JSON.stringify({
                    npm: npm,
                    nama: nama,
                    email: email,
                    kelas: kelas
                })
            }
        );


        const data = await response.json();

        console.log("Response mahasiswa:", data);


        if (response.ok) {

            message.innerText =
                "Mahasiswa berhasil ditambahkan. Membuka registrasi wajah...";


            // SIMPAN NPM SEMENTARA
            sessionStorage.setItem(
                "npmRegistrasi",
                npm
            );


            // REDIRECT KE HALAMAN REGISTRASI WAJAH
            const targetUrl =
                new URL(
                    "registrasi_wajah.html",
                    window.location.href
                );

            targetUrl.searchParams.set(
                "npm",
                npm
            );


            window.location.replace(
                targetUrl.href
            );

        } else {

            message.innerText =
                data.npm?.[0] ||
                data.email?.[0] ||
                data.kelas?.[0] ||
                data.nama?.[0] ||
                data.detail ||
                data.message ||
                JSON.stringify(data) ||
                "Gagal menyimpan mahasiswa.";

            simpanButton.disabled = false;
        }


    } catch (error) {

        console.error(
            "Error simpan mahasiswa:",
            error
        );

        message.innerText =
            "Gagal terhubung ke backend.";

        simpanButton.disabled = false;
    }

});

if (token) {
    loadKelas();
}
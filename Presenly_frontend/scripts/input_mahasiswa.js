console.log("input_mahasiswa.js dimuat");

const API_URL = "http://127.0.0.1:8000/api";

const kelasSelect = document.getElementById("kelas");
const simpanButton = document.getElementById("simpanButton");
const message = document.getElementById("message");

const token = localStorage.getItem("token");


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
                data.detail ||
                data.message ||
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
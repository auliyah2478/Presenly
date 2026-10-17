const API_URL = "http://127.0.0.1:8000/api";

const kelasSelect = document.getElementById("kelas");
const simpanButton = document.getElementById("simpanButton");
const message = document.getElementById("message");


// ===============================
// CEK LOGIN
// ===============================

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}


// ===============================
// AMBIL DATA KELAS
// ===============================

async function loadKelas() {

    try {

        const response = await fetch(
            `${API_URL}/kelas/`
        );

        const data = await response.json();

        data.forEach(kelas => {

            const option =
                document.createElement("option");

            option.value = kelas.id;

            option.textContent =
                kelas.nama_kelas;

            kelasSelect.appendChild(option);

        });

    } catch (error) {

        console.error(error);

        message.innerText =
            "Gagal mengambil data kelas.";

    }

}


// ===============================
// SIMPAN MAHASISWA
// ===============================

simpanButton.addEventListener(
    "click",
    async function () {

        const npm =
            document.getElementById("npm").value;

        const nama =
            document.getElementById("nama").value;

        const email =
            document.getElementById("email").value;

        const kelas =
            document.getElementById("kelas").value;


        if (!npm || !nama || !kelas) {

            message.innerText =
                "NPM, nama, dan kelas wajib diisi.";

            return;
        }


        try {

            const response = await fetch(
                `${API_URL}/mahasiswa/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Token ${token}`
                    },

                    body: JSON.stringify({
                        npm: npm,
                        nama: nama,
                        email: email,
                        kelas: kelas
                    })
                }
            );


            const data =
                await response.json();


            if (response.ok) {

                message.innerText =
                    "Mahasiswa berhasil ditambahkan.";

                document.getElementById("npm").value = "";
                document.getElementById("nama").value = "";
                document.getElementById("email").value = "";

                kelasSelect.value = "";

            } else {

                message.innerText =
                    JSON.stringify(data);

            }


        } catch (error) {

            console.error(error);

            message.innerText =
                "Gagal terhubung ke server.";

        }

    }
);


// jalankan saat halaman dibuka
loadKelas();
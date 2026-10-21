console.log("registrasi_wajah.js versi terbaru dimuat");

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const registrasiButton = document.getElementById("registrasiButton");
const message = document.getElementById("message");
const infoMahasiswa = document.getElementById("infoMahasiswa");


// ========================================
// AMBIL NPM DARI URL
// ========================================

const params = new URLSearchParams(window.location.search);

let npm = params.get("npm");

if (!npm) {
    npm = sessionStorage.getItem("npmRegistrasi");
}


if (!npm) {

    infoMahasiswa.innerText =
        "Data mahasiswa tidak ditemukan.";

    message.innerText =
        "NPM mahasiswa tidak tersedia.";

    registrasiButton.disabled = true;

} else {

    infoMahasiswa.innerText =
        `Registrasi wajah untuk NPM: ${npm}`;

}


// ========================================
// NYALAKAN KAMERA
// ========================================

async function startCamera() {

    try {

        message.innerText =
            "Menyiapkan kamera...";

        const stream =
            await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });

        video.srcObject = stream;

        await video.play();

        message.innerText =
            "Kamera siap. Arahkan wajah ke kamera.";

        registrasiButton.disabled = false;

    } catch (error) {

        console.error("Camera error:", error);

        message.innerText =
            "Kamera tidak dapat diakses.";

        registrasiButton.disabled = true;
    }
}


// ========================================
// MATIKAN KAMERA
// ========================================

function stopCamera() {

    if (video.srcObject) {

        const tracks =
            video.srcObject.getTracks();

        tracks.forEach(function (track) {
            track.stop();
        });

        video.srcObject = null;
    }
}


// ========================================
// REGISTRASI WAJAH
// ========================================

registrasiButton.addEventListener(
    "click",
    async function () {

        console.log("Tombol Daftarkan Wajah diklik");


        if (!npm) {

            message.innerText =
                "NPM mahasiswa tidak ditemukan.";

            return;
        }


        if (
            video.videoWidth === 0 ||
            video.videoHeight === 0
        ) {

            message.innerText =
                "Kamera belum siap.";

            return;
        }


        // ========================================
        // TAMPILAN SAAT PROSES
        // ========================================

        registrasiButton.disabled = true;

        registrasiButton.innerText =
            "Memproses...";

        message.innerText =
            "Sedang memproses wajah, mohon tunggu...";


        // ========================================
        // AMBIL FOTO DARI VIDEO
        // ========================================

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context =
            canvas.getContext("2d");

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );


        canvas.toBlob(
            async function (blob) {

                if (!blob) {

                    message.innerText =
                        "Gagal mengambil gambar.";

                    registrasiButton.disabled = false;

                    registrasiButton.innerText =
                        "Daftarkan Wajah";

                    return;
                }


                const formData =
                    new FormData();

                formData.append(
                    "npm",
                    npm
                );

                formData.append(
                    "foto",
                    blob,
                    "registrasi_wajah.jpg"
                );


                try {

                    const response =
                        await fetch(
                            "http://127.0.0.1:8000/api/registrasi-wajah/",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "Response registrasi:",
                        data
                    );


                    // ========================================
                    // BERHASIL
                    // ========================================

                    if (response.ok) {

                        message.innerText =
                            `Registrasi wajah berhasil untuk ${data.nama}.`;

                        registrasiButton.innerText =
                            "Registrasi Berhasil";

                        registrasiButton.disabled =
                            true;


                        // Matikan kamera
                        stopCamera();


                        // Hapus NPM sementara
                        sessionStorage.removeItem(
                            "npmRegistrasi"
                        );


                        // Tunggu 2 detik agar pesan berhasil terlihat
                        setTimeout(function () {

                            window.location.replace(
                                "input_mahasiswa.html"
                            );

                        }, 2000);

                    }

                    // ========================================
                    // GAGAL
                    // ========================================

                    else {

                        message.innerText =
                            data.message ||
                            "Registrasi wajah gagal.";

                        registrasiButton.innerText =
                            "Daftarkan Wajah";

                        registrasiButton.disabled =
                            false;
                    }


                } catch (error) {

                    console.error(
                        "Registrasi error:",
                        error
                    );

                    message.innerText =
                        "Gagal terhubung ke backend.";

                    registrasiButton.innerText =
                        "Daftarkan Wajah";

                    registrasiButton.disabled =
                        false;
                }

            },

            "image/jpeg",
            0.9
        );

    }
);


// ========================================
// JALANKAN KAMERA
// ========================================

startCamera();
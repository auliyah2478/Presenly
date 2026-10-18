const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const registrasiButton =
    document.getElementById("registrasiButton");

const message =
    document.getElementById("message");

const infoMahasiswa =
    document.getElementById("infoMahasiswa");


// ===============================
// AMBIL NPM
// ===============================

const params =
    new URLSearchParams(window.location.search);

const npm =
    params.get("npm");

if (!npm) {

    message.innerText =
        "NPM mahasiswa tidak ditemukan.";

    registrasiButton.disabled = true;

} else {

    infoMahasiswa.innerText =
        `Registrasi wajah untuk NPM: ${npm}`;

}


// ===============================
// AKSES KAMERA
// ===============================

async function startCamera() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });

        video.srcObject = stream;

    } catch (error) {

        console.error(error);

        message.innerText =
            "Kamera tidak dapat diakses.";

    }

}

startCamera();


// ===============================
// REGISTRASI WAJAH
// ===============================

registrasiButton.addEventListener(
    "click",
    async function () {

        message.innerText =
            "Sedang memproses wajah...";

        canvas.width =
            video.videoWidth;

        canvas.height =
            video.videoHeight;

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

                const formData =
                    new FormData();

                formData.append(
                    "npm",
                    npm
                );

                formData.append(
                    "foto",
                    blob,
                    "registrasi.jpg"
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


                    if (response.ok) {

                        message.innerText =
                            "Registrasi wajah berhasil.";

                    } else {

                        message.innerText =
                            data.message;

                    }

                } catch (error) {

                    console.error(error);

                    message.innerText =
                        "Gagal terhubung ke server.";

                }

            },
            "image/jpeg",
            0.9
        );

    }
);
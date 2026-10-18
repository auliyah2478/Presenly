const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const scanButton = document.getElementById("scanButton");

const message = document.getElementById("message");
const hasil = document.getElementById("hasil");


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
// SCAN WAJAH
// ===============================

scanButton.addEventListener(
    "click",
    async function () {

        message.innerText =
            "Sedang memproses wajah...";

        hasil.innerHTML = "";


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
                    "foto",
                    blob,
                    "scan.jpg"
                );


                try {

                    const response =
                        await fetch(
                            "http://127.0.0.1:8000/api/absensi/scan/",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    const data =
                        await response.json();


                    if (response.ok) {

                        message.innerText =
                            "Absensi berhasil.";

                        hasil.innerHTML = `
                            <p>Nama: ${data.nama}</p>
                            <p>NPM: ${data.npm}</p>
                            <p>Kelas: ${data.kelas}</p>
                            <p>Status: ${data.kehadiran}</p>
                            <p>Distance: ${data.distance}</p>
                        `;

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
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const scanButton = document.getElementById("scanButton");

const message = document.getElementById("message");
const hasil = document.getElementById("hasil");
let sedangMemindai = false;
let resetHasilTimer;


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

        if (sedangMemindai) {
            return;
        }

        if (!video.videoWidth || !video.videoHeight) {
            message.innerText =
                "Kamera belum siap. Tunggu sebentar lalu coba lagi.";
            return;
        }

        sedangMemindai = true;
        scanButton.disabled = true;
        message.innerText = "Sedang memproses wajah...";
        hasil.innerHTML = "";
        

        try {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const context = canvas.getContext("2d");
            context.drawImage(
                video,
                0,
                0,
                canvas.width,
                canvas.height
            );

            const blob = await new Promise(resolve => {
                canvas.toBlob(resolve, "image/jpeg", 0.9);
            });

            if (!blob) {
                throw new Error("Gagal mengambil gambar dari kamera.");
            }

            const formData = new FormData();
            formData.append("foto", blob, "scan.jpg");

            const response = await fetch(
                "http://127.0.0.1:8000/api/absensi/scan/",
                {
                    method: "POST",
                    body: formData
                }
            );
            const data = await response.json();

            if (!response.ok) {
                message.innerText =
                    data.message || "Absensi gagal diproses.";
                return;
            }

            const statusLabel = {
                HADIR: "Hadir",
                TERLAMBAT: "Telat",
                ALFA: "Alfa"
            };

            message.innerText =
                data.kehadiran === "ALFA"
                    ? "Absensi tercatat sebagai alfa."
                    : "Absensi berhasil.";

                const waktu = data.waktu_absen
                    ? new Date(data.waktu_absen)
                    : null;
                
                const waktuLabel =
                    waktu && !Number.isNaN(waktu.getTime())
                        ? waktu.toLocaleString("id-ID", {
                            dateStyle: "medium",
                            timeStyle: "medium"
                        })
                        : "-";
                
                hasil.innerHTML = `
                    <p>Nama: ${escapeHtml(data.nama)}</p>
                    <p>NPM: ${escapeHtml(data.npm)}</p>
                    <p>Kelas: ${escapeHtml(data.kelas)}</p>
                    <p>Mata Kuliah: ${escapeHtml(data.nama_mata_kuliah)}</p>
                    <p>Status: ${statusLabel[data.kehadiran] ?? escapeHtml(data.kehadiran)}</p>
                    <p>Waktu Absensi: ${escapeHtml(waktuLabel)}</p>
                `;
                resetHasilTimer = setTimeout(function () {
                    hasil.innerHTML = "";
                    message.innerText =
                        "Siap untuk absensi mahasiswa berikutnya.";
                }, 10000);

            
        
            } catch (error) {
                console.error("Scan absensi error:", error);
    
                message.innerText =
                    error.message === "Gagal mengambil gambar dari kamera."
                        ? error.message
                        : "Gagal terhubung ke server. Periksa koneksi dan coba lagi.";
    
            } finally {
                sedangMemindai = false;
                scanButton.disabled = false;
            }


    }
);

function escapeHtml(value) {
    return String(value ?? "-").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]
    );
}
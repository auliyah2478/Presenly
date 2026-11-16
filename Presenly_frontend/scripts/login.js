
const loginButton = document.getElementById("loginButton");
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");
console.log("Password input:", passwordInput);
console.log("Toggle button:", togglePassword);

// =====================================
// TAMPILKAN / SEMBUNYIKAN PASSWORD
// =====================================

if (passwordInput && togglePassword) {
    togglePassword.addEventListener("click", function (event) {
        console.log("Tombol mata berhasil diklik!");
        event.preventDefault();

        const passwordSedangTersembunyi =
            passwordInput.type === "password";

        passwordInput.type = passwordSedangTersembunyi
            ? "text"
            : "password";

        togglePassword.setAttribute(
            "aria-label",
            passwordSedangTersembunyi
                ? "Sembunyikan password"
                : "Tampilkan password"
        );

        togglePassword.setAttribute(
            "aria-pressed",
            String(passwordSedangTersembunyi)
        );

        // Ubah ikon mata
        if (passwordSedangTersembunyi) {
            togglePassword.innerHTML = `
                <svg viewBox="0 0 24 24"
                    width="22"
                    height="22"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="M3 3l18 18"></path>
                    <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"></path>
                    <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5
                        c5 0 9 7 9 7a15 15 0 0 1-4 4.5"></path>
                    <path d="M6.2 6.2C3.7 7.8 2 12 2 12
                        s4 7 10 7c1.3 0 2.5-.3 3.6-.8"></path>
                </svg>
            `;
        } else {
            togglePassword.innerHTML = `
                <svg viewBox="0 0 24 24"
                    width="22"
                    height="22"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
            `;
        }
    });
} else {
    console.error("Input password atau tombol mata tidak ditemukan.");
}

// =====================================
// PROSES LOGIN
// =====================================

loginButton.addEventListener("click", async function () {
    const username =
        document.getElementById("username").value.trim();

    const password = passwordInput.value;

    const message =
        document.getElementById("message");

    if (!username || !password) {
        message.innerText =
            "Username dan password wajib diisi.";
        return;
    }

    try {
        loginButton.disabled = true;
        message.innerText = "Sedang login...";

        const response = await fetch(
            "http://127.0.0.1:8000/api/login/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("role", data.role);
            localStorage.setItem("username", data.username);

            message.innerText = "Login berhasil.";

            setTimeout(function () {
                window.location.href = "dashboard.html";
            }, 500);
        } else {
            message.innerText =
                data.message || "Username atau password salah.";

            loginButton.disabled = false;
        }
    } catch (error) {
        message.innerText = "Gagal terhubung ke server.";
        loginButton.disabled = false;

        console.error("Login error:", error);
    }
    
});

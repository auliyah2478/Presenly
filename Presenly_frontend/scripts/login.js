const loginButton = document.getElementById("loginButton");

loginButton.addEventListener("click", async function () {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;

    const message =
        document.getElementById("message");

    if (!username || !password) {

        message.innerText =
            "Username dan password wajib diisi.";

        return;
    }

    try {

        loginButton.disabled = true;

        message.innerText =
            "Sedang login...";

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

        const data =
            await response.json();


        // ===============================
        // LOGIN BERHASIL
        // ===============================

        if (response.ok) {

            localStorage.setItem(
                "token",
                data.token
            );

            localStorage.setItem(
                "role",
                data.role
            );

            localStorage.setItem(
                "username",
                data.username
            );

            message.innerText =
                "Login berhasil.";


            setTimeout(function () {

                window.location.href =
                    "dashboard.html";

            }, 500);

        }

        // ===============================
        // LOGIN GAGAL
        // ===============================

        else {

            message.innerText =
                data.message ||
                "Username atau password salah.";

            loginButton.disabled =
                false;
        }


    } catch (error) {

        message.innerText =
            "Gagal terhubung ke server.";

        loginButton.disabled =
            false;

        console.error(
            "Login error:",
            error
        );

    }

});
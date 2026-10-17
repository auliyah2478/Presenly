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
                    "input_mahasiswa.html";

            }, 500);

        } else {

            message.innerText =
                data.message || "Login gagal.";

        }

    } catch (error) {

        message.innerText =
            "Gagal terhubung ke server.";

        console.error(
            "Login error:",
            error
        );

    }

});

document.addEventListener("DOMContentLoaded", function () {

    const passwordInput = document.getElementById("password");
    const passwordToggle = document.getElementById("passwordToggle");

    if (!passwordInput || !passwordToggle) {
        return;
    }

    passwordToggle.addEventListener("click", function () {

        const passwordIsHidden =
            passwordInput.type === "password";

        if (passwordIsHidden) {

            passwordInput.type = "text";
            passwordToggle.textContent = "Sembunyikan";
            passwordToggle.setAttribute(
                "aria-label",
                "Sembunyikan password"
            );

        } else {

            passwordInput.type = "password";
            passwordToggle.textContent = "Lihat";
            passwordToggle.setAttribute(
                "aria-label",
                "Tampilkan password"
            );

        }

    });

});

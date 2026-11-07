
(() => {
    const STORAGE_KEY = "presenly-admin-theme";

    const body = document.body;
    const userTools = document.getElementById("user-tools");

    if (!body || !userTools) {
        return;
    }

    // Membuat tombol pengubah tema
    const toggleButton = document.createElement("button");

    toggleButton.type = "button";
    toggleButton.className = "presenly-theme-toggle";

    // Menambahkan tombol ke bagian kanan header admin
    userTools.appendChild(toggleButton);

    // Mengatur tema dan tulisan tombol
    function applyTheme(theme) {
        body.setAttribute("data-theme", theme);

        if (theme === "dark") {
            toggleButton.textContent = "☀️ Mode Terang";
            toggleButton.setAttribute(
                "aria-label",
                "Ubah ke mode terang"
            );
        } else {
            toggleButton.textContent = "🌙 Mode Gelap";
            toggleButton.setAttribute(
                "aria-label",
                "Ubah ke mode gelap"
            );
        }
    }

    // Mengambil tema yang tersimpan
    const savedTheme = localStorage.getItem(STORAGE_KEY);

    const initialTheme =
        savedTheme === "dark" ? "dark" : "light";

    applyTheme(initialTheme);

    // Mengubah tema ketika tombol diklik
    toggleButton.addEventListener("click", function () {
        const currentTheme = body.getAttribute("data-theme");

        const newTheme =
            currentTheme === "dark" ? "light" : "dark";

        localStorage.setItem(STORAGE_KEY, newTheme);

        applyTheme(newTheme);
    });
})();

document.addEventListener('DOMContentLoaded', () => {
    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");

    window.showLogin = function () {
        document.getElementById("loginForm").classList.remove("d-none");
        document.getElementById("registerForm").classList.add("d-none");

        loginBtn.classList.add("btn-primary");
        loginBtn.classList.remove("btn-secondary");
        registerBtn.classList.add("btn-secondary");
        registerBtn.classList.remove("btn-primary");
    }

    window.showRegister = function () {
        document.getElementById("registerForm").classList.remove("d-none");
        document.getElementById("loginForm").classList.add("d-none");

        registerBtn.classList.add("btn-primary");
        registerBtn.classList.remove("btn-secondary");
        loginBtn.classList.add("btn-secondary");
        loginBtn.classList.remove("btn-primary");
    }

    window.togglePasswordVisibility = function (inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('i');
        const isVisible = input.type === 'text';

        input.type = isVisible ? 'password' : 'text';
        icon.classList.toggle('bi-eye', !isVisible);
        icon.classList.toggle('bi-eye-slash', isVisible);
    }
    showLogin();
});

document.addEventListener('DOMContentLoaded', () => {
    window.showLogin = function () {
        document.getElementById("loginForm").classList.remove("d-none");
        document.getElementById("registerForm").classList.add("d-none");
    }

    window.showRegister = function () {
        document.getElementById("registerForm").classList.remove("d-none");
        document.getElementById("loginForm").classList.add("d-none");
    }

    window.togglePasswordVisibility = function (inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('i');
        const isVisible = input.type === 'text';

        input.type = isVisible ? 'password' : 'text';
        icon.classList.toggle('bi-eye', !isVisible);
        icon.classList.toggle('bi-eye-slash', isVisible);
    }
});

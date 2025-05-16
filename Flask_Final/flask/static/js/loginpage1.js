const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

const showRegister = () => {
    container.classList.add("active");
};

const showLogin = () => {
    container.classList.remove("active");
};

registerBtn.addEventListener('click', showRegister);
loginBtn.addEventListener('click', showLogin);
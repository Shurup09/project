// Функция предпросмотра изображения
function previewImage() {
    const fileInput = document.getElementById('flowerImage');
    const preview = document.getElementById('imagePreview');

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.innerHTML = `
                <div style="text-align: center;">
                    <img src="${e.target.result}" style="max-width: 300px; border-radius: 10px; margin: 10px 0;">
                    <p>Фото готово к анализу!</p>
                </div>
            `;
        }

        reader.readAsDataURL(fileInput.files[0]);
    }
}

// Функции для работы с модальными окнами
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Выход из системы
function logout() {
    window.location.href = "/logout";
}

// Переключение темы
function toggleTheme() {
    const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    changeTheme(newTheme);
}

function changeTheme(theme) {
    window.location.href = "/change-theme?theme=" + theme;
}

// Функции для личного кабинета
function showSection(sectionId) {
    // Скрыть все секции
    document.querySelectorAll('.account-section-content').forEach(section => {
        section.style.display = 'none';
    });

    // Показать выбранную секцию
    document.getElementById(sectionId + '-section').style.display = 'block';

    // Обновить активное меню
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let modal of modals) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

// Плавная прокрутка к результату после загрузки
document.addEventListener('DOMContentLoaded', function() {
    const flowerResult = document.getElementById('flowerResult');
    if (flowerResult && flowerResult.style.display !== 'none') {
        flowerResult.scrollIntoView({
            behavior: 'smooth'
        });
    }

    // Автоматическое открытие модального окна при ошибках авторизации
    const flashMessages = document.querySelectorAll('.flash-error');
    flashMessages.forEach(message => {
        if (message.textContent.includes('email') || message.textContent.includes('пароль') || message.textContent.includes('Регистрация')) {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('login_error')) {
                openModal('loginModal');
            } else if (urlParams.has('register_error')) {
                openModal('registerModal');
            }
        }
    });
});

// Обработка клавиши Escape для закрытия модальных окон
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.getElementsByClassName('modal');
        for (let modal of modals) {
            modal.style.display = 'none';
        }
    }
});

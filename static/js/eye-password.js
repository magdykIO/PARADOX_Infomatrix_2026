// 1. Знаходимо всі іконки "ока" на сторінці
const eyeIcons = document.querySelectorAll('.eye-icon');

eyeIcons.forEach(icon => {
    icon.addEventListener('click', () => {
        // 2. Знаходимо поле вводу, яке лежить в HTML прямо перед цією іконкою
        const input = icon.previousElementSibling;

        // 3. Перевіряємо: якщо тип поля "пароль" (зірочки)
        if (input.type === 'password') {
            // Робимо текст видимим
            input.type = 'text';
            // Підсвічуємо іконку помаранчевим, щоб було зрозуміло, що функція активна
            icon.style.fill = '#f27a24';
        } else {
            // Якщо текст вже було видно — ховаємо його назад за зірочки
            input.type = 'password';
            // Повертаємо іконці звичайний колір
            icon.style.fill = '';
        }
    });
});
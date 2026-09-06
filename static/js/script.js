document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("leadForm");
    const container = document.querySelector(".mobile-container");

    // Если есть flash-сообщение, скрываем форму (опционально)
    const successDiv = document.querySelector(".success");
    if (successDiv) {
        // Можно скрыть форму, если сообщение есть
        // form.style.display = "none";
    }

    // Отправка через AJAX (если хотите убрать перезагрузку)
    form.addEventListener("submit", function(event) {
        event.preventDefault();  // отключаем обычную отправку

        const data = new FormData(form);
        fetch("/", {
            method: "POST",
            body: data,
        })
        .then(response => response.text())
        .then(html => {
            // Вставляем ответ сервера (с flash-сообщением) 
            // или обрабатываем JSON
            container.innerHTML = html;
        })
        .catch(error => console.error("Ошибка:", error));
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Fetch the translations JSON file
    fetch('/static/js/translations.json')
        .then(response => response.json())
        .then(translations => {
            // Get the user's default language or fallback to English
            let lang = localStorage.getItem('lang') || 'en';

            // Function to apply translations
            function applyTranslations(lang) {
                document.querySelectorAll('[data-i18n]').forEach(element => {
                    const key = element.getAttribute('data-i18n');
                    element.textContent = translations[lang][key];
                });
                document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
                    const key = element.getAttribute('data-i18n-placeholder');
                    element.setAttribute('placeholder', translations[lang][key]);
                });
            }

            // Apply translations on page load
            applyTranslations(lang);

            // Language change handler
            document.querySelector('.language-selector').value = lang;
            document.querySelector('.language-selector').addEventListener('change', function (event) {
                lang = event.target.value;
                localStorage.setItem('lang', lang);  // Save language preference
                applyTranslations(lang);
            });
        })
        .catch(error => console.error('Error loading translations:', error));
});
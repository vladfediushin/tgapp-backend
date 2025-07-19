import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpApi from 'i18next-http-backend';

i18n
  .use(HttpApi)                  // позволяет подгружать JSON-файлы по HTTP
  .use(initReactI18next)         // передаёт i18n-поточок в React
  .init({
    fallbackLng: 'en',           // язык по умолчанию
    supportedLngs: ['en', 'ru'], // список ваших локалей
    ns: ['translation'],         // namespace, можно расширить
    defaultNS: 'translation',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    interpolation: {
      escapeValue: false,        // для React XSS-опасность не актуальна
    },
    react: {
      useSuspense: false,        // не блокируем рендер, а выводим ключи при загрузке
    },
  });

export default i18n;

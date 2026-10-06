# Публикация на GitHub

[Главная](../README.md)

## Загрузка архива

1. Создайте публичный репозиторий **`aura-powerbi`** в аккаунте **KristinaShishigina00**. Description: «Power BI: аналитика продукта Aura, пользовательская воронка, рекомендации и гипотезы улучшения».
2. Распакуйте внешний архив. Через Add file → Upload files загрузите **содержимое** папки проекта в корень репозитория. Сам ZIP GitHub не распаковывает.
3. Убедитесь, что на главной видны README.md, папки assets, data, docs, powerbi, reports, scripts, site и `.github`. Файлы `.gitignore`, `.gitattributes` и `.github` также входят в комплект.
4. Откройте Settings → Pages → Build and deployment → Source и выберите **GitHub Actions**.
5. В Actions откройте workflow **Publish interactive dashboard** и выполните Run workflow на основной ветке. После успешного запуска адрес сайта будет показан в Pages и в результате workflow.

Адрес для указанного имени: **https://kristinashishigina00.github.io/aura-powerbi/**. Если имя репозитория другое, замените этот адрес в README и адрес репозитория в `site/index.html`. Workflow работает для веток main и master.

Публикация сайта не требует Power BI Service: интерактивная HTML-версия содержит данные и работает на GitHub Pages. В README GitHub нельзя запустить HTML-дашборд или встроить iframe; используется кликабельное превью и переход на сайт.

## Оформление About

Website: адрес сайта после публикации. Topics: `powerbi`, `dax`, `power-query`, `business-analysis`, `product-analytics`, `dashboard`, `portfolio`.

## Power BI Service

Опубликованной ссылки Power BI Service в переданных материалах нет. Она не создаётся загрузкой PBIX на GitHub.

Если нужен именно отчёт Power BI в браузере:

1. Откройте PBIX в Desktop и опубликуйте его в своём доступном workspace Power BI Service.
2. В Service откройте отчёт и выберите File → Embed report → Publish to web (public), если функция доступна в аккаунте и разрешена администратором.
3. Скопируйте публичный адрес вида `https://app.powerbi.com/view?r=...` из созданного кода.
4. Вставьте этот адрес в `site/powerbi-config.js` вместо пустой строки и сохраните изменение на GitHub.
5. После повторной публикации Pages кнопка Power BI Service появится на дашборде и откроет встроенный отчёт.

Publish to web делает отчёт и данные публичными. В этом комплекте данные демонстрационные. Для закрытых данных требуется другой способ доступа.

Доступность публикации зависит от лицензии и настроек Microsoft. Пока ссылки нет, основная интерактивная HTML-версия уже работает локально и готова для Pages; страница `site/powerbi.html` явно сообщает, что Service ещё не подключён.

## Официальные инструкции

- [GitHub Pages и собственные workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Power BI Publish to web](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web)
- [Power BI Project PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

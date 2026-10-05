# Как получить `qkc.js.org` — пошагово

js.org даёт бесплатный поддомен проектам с GitHub Pages. Наши имена **свободны** (проверено 05.10.2026):
`qkc.js.org`, `ouri.js.org`. Имя поддомена должно совпадать с **именем репозитория** (или логином),
поэтому репозиторий называем `qkc` — тогда имеем право на `qkc.js.org`.

Требования js.org (проверены по их README): открытый репозиторий, живой сайт с содержимым,
без редиректов наружу, тематика — JavaScript-экосистема. QKC подходит: это open-source приложение
на vanilla JS (движок теста, генератор банка, PWA) с публичным репозиторием и лицензией MIT.

---

## Шаг 0. Подготовка (уже в папке)

- `CNAME` — содержит `qkc.js.org` (лежит в корне);
- `.nojekyll` — отключает Jekyll на GitHub Pages;
- `LICENSE` — MIT;
- `package.json`, `CONTRIBUTING.md`, `README.md` — признаки живого открытого проекта.

## Шаг 1. Репозиторий и GitHub Pages

```bash
cd ouri                      # папка проекта
git init -b main
git add -A
git commit -m "QKC — Quick Knowledge Check (BETA): open-source release"
git remote add origin https://github.com/ТВОЙ-ЛОГИН/qkc.git
git push -u origin main
```

1. На GitHub создай **публичный** репозиторий с именем `qkc` (имя важно — под него выдаётся поддомен).
2. Settings → Pages → Source: *Deploy from a branch* → branch `main`, folder `/ (root)` → Save.
3. Через 1–2 минуты сайт живой: `https://ТВОЙ-ЛОГИН.github.io/qkc/` — проверь главную и тренажёр.

> Пока CNAME-файл лежит в репозитории, github.io-адрес может redirects на `qkc.js.org`
> (он «оживёт» после шага 3). Если ревьюер js.org попросит показать сайт до_merge —
> временно удали `CNAME` одним коммитом, а после одобрения PR верни.

## Шаг 2. Форк и правка `cnames_active.js`

1. Открой <https://github.com/js-org/js.org> → **Fork**.
2. В своём форке открой файл `cnames_active.js`.
3. Найди по алфавиту место для ключа `qkc` и добавь строку (формат как у соседей):

```js
  "qkc": "ТВОЙ-ЛОГИН.github.io",
```

4. Commit changes.

## Шаг 3. Pull Request в js-org/js.org

Создай PR из своей ветки в `js-org/js.org:master`. Готовый текст:

```
Subdomain requested: qkc.js.org
Target: ТВОЙ-ЛОГИН.github.io (GitHub Pages, repo name = qkc)

- [x] The subdomain matches the repository name (https://github.com/ТВОЙ-ЛОГИН/qkc)
- [x] The site is published via GitHub Pages and contains substantive content
- [x] CNAME file with "qkc.js.org" is committed to the publishing branch
- [x] No automatic redirects away from js.org
- [x] Content is directly related to JavaScript: open-source vanilla-JS quiz engine
      + generated question bank (MIT), no frameworks, no build step

Project: QKC — Quick Knowledge Check, a black & white offline-first PWA trainer
for school subjects (kindergarten–grade 11, 42k+ questions).
```

Следи за PR: сопровождающие могут задать вопрос или попросить поправить формат строки.
После_merge DNS обновится **в течение 24 часов** → сайт заработает на **https://qkc.js.org**
(HTTPS js.org включает сам).

## Шаг 4. Проверка и запасные варианты

- `https://qkc.js.org` — основной адрес (он же в `CNAME`);
- если вдруг имя `qkc` отклонят из-за созвучия с чужим брендом — запасной вариант: репозиторий `ouri` → `ouri.js.org`
  (тоже свободно; тогда поменяй строку в `CNAME` и в PR);
- параллельно можно занять `ouri.netlify.app` / `ouri.vercel.app` / `qkc.pages.dev` как зеркала
  (все свободны по проверке; инструкция в DEPLOY.md).

## Частые грабли

| Симптом | Причина / лечение |
|---|---|
| PR закрыт с «not related to JavaScript» | Ответить в PR: проект — open-source JS-движок теста + генератор банка, vanilla JS, PWA; показать `js/app.js`, `gen/`. Если всё же откажут — используем зеркала из шага 4, это не блокирует сайт. |
| Сайт на github.io отдаёт 404 | Pages не включён или источник не `main /root`; проверь Settings → Pages. |
| `qkc.js.org` не открылся после merge | Жди до 24 ч; проверь `dig qkc.js.org` или просто позже. |
| Jekyll ломает папку `assets` | У нас есть `.nojekyll` — не удаляй его. |

# Как получить `qkc.runs-on.dev` — пошагово

> **Статус (06.10.2026): заявка подана — [zordhalo/runs-on.dev#310](https://github.com/zordhalo/runs-on.dev/pull/310).**
> CI-валидация реестра проверяет запись автоматически; после merge DNS синхронизируется сам.
> Осталось: дождаться merge → активировать файлы `CNAME` в четырёх репозиториях (шаг 4).

[runs-on.dev](https://runs-on.dev) — открытый реестр бесплатных поддоменов `*.runs-on.dev`.
Правила простые: аккаунт GitHub старше 30 дней, минимум один публичный репозиторий,
**одно имя на аккаунт**. Имя закрепляется файлом `domains/<name>.json` в репозитории
[zordhalo/runs-on.dev](https://github.com/zordhalo/runs-on.dev) — через сайт (OAuth) или pull request.

## Наша схема (одно имя — четыре сайта)

Лимит «одно имя на аккаунт» обходится субдоменами: в одной записи можно задать до 10
субдоменов первого уровня. Все четыре сайта лежат на GitHub Pages одного аккаунта, поэтому
все CNAME ведут на `spaj7468-cell.github.io`, а GitHub Pages различает их по файлу
`CNAME` в каждом репозитории:

| Адрес | Сайт | Репозиторий | Файл `CNAME` содержит |
|---|---|---|---|
| `https://qkc.runs-on.dev` | тренажёр QKC | `spaj7468-cell/qkc` | `qkc.runs-on.dev` |
| `https://corp.qkc.runs-on.dev` | сайт компании OuRi Corp | `spaj7468-cell/ouri-corp` | `corp.qkc.runs-on.dev` |
| `https://engine.qkc.runs-on.dev` | документация QKC Engine | `spaj7468-cell/qkc-engine` | `engine.qkc.runs-on.dev` |
| `https://code.qkc.runs-on.dev` | школа кода QKCcode (QKC v2) | `spaj7468-cell/qkccode` | `code.qkc.runs-on.dev` |

## Шаг 1. Запись в реестре (уже сделано)

Файл `domains/qkc.json` в ветке `claim-qkc` нашего форка:

```json
{
  "name": "qkc",
  "owner": { "github": "spaj7468-cell" },
  "claimedAt": "2026-10-06T14:45:00.000Z",
  "records": { "CNAME": "spaj7468-cell.github.io" },
  "subdomains": {
    "corp":   { "CNAME": "spaj7468-cell.github.io" },
    "engine": { "CNAME": "spaj7468-cell.github.io" },
    "code":   { "CNAME": "spaj7468-cell.github.io" }
  },
  "profile": {
    "name": "OuRi Corp — QKC",
    "bio": "QKC: an open-source, offline-first JavaScript math trainer (arithmetic by grade & format). Built with plain JavaScript by OuRi Corp.",
    "links": [
      { "label": "QKC trainer",     "url": "https://spaj7468-cell.github.io/qkc/" },
      { "label": "QKCcode",         "url": "https://spaj7468-cell.github.io/qkccode/" },
      { "label": "QKC Engine docs", "url": "https://spaj7468-cell.github.io/qkc-engine/" },
      { "label": "OuRi Corp",       "url": "https://spaj7468-cell.github.io/ouri-corp/" },
      { "label": "GitHub",          "url": "https://github.com/spaj7468-cell" }
    ]
  }
}
```

Валидацию (`schema/record.schema.json` + `validateChangeset` в `lib/pr.js`) проходят:
`owner.github` = автор PR, `claimedAt` не в будущем, имя не зарезервировано,
CNAME — одиночная запись (без A/TXT/MX рядом), субдомены — один уровень, только CNAME.

## Шаг 2. Pull request (уже сделано)

PR: **https://github.com/zordhalo/runs-on.dev/pull/310** — из ветки `claim-qkc`
форка `spaj7468-cell/runs-on.dev` в `zordhalo/runs-on.dev:main`.
CI реестра прогоняет проверки автоматически; дальше решение мейнтейнера.

## Шаг 3. Merge → DNS

После merge workflow реестра (`sync-dns`) сам создаёт записи в зоне `runs-on.dev`.
`*.runs-on.dev` — wildcard, так что имена начинают резолвиться почти сразу.
Проверка: `dig +short qkc.runs-on.dev CNAME` → `spaj7468-cell.github.io.`

## Шаг 4. Активация `CNAME` в репозиториях (после merge!)

> **Важно:** не активируй `CNAME` до merge — GitHub Pages начнёт редиректить
> github.io-зеркала на ещё не живой домен.

В каждом из четырёх репозиториев (заготовки `CNAME.runs-on` уже лежат в корне):

```bash
# qkc
git mv CNAME.runs-on CNAME && git commit -m "chore: enable CNAME qkc.runs-on.dev" && git push
# ouri-corp
printf 'corp.qkc.runs-on.dev\n' > CNAME && git add CNAME && git commit -m "chore: enable CNAME corp.qkc.runs-on.dev" && git push
# qkc-engine
git mv CNAME.runs-on CNAME && git commit -m "chore: enable CNAME engine.qkc.runs-on.dev" && git push
# qkccode
git mv CNAME.runs-on CNAME && git commit -m "chore: enable CNAME code.qkc.runs-on.dev" && git push
```

GitHub Pages подхватит `CNAME` при следующей сборке и выпустит HTTPS-сертификаты
(обычно несколько минут).

## Шаг 5. Проверка

- https://qkc.runs-on.dev — тренажёр
- https://corp.qkc.runs-on.dev — сайт компании
- https://engine.qkc.runs-on.dev — документация движка
- https://code.qkc.runs-on.dev — школа кода QKCcode
- github.io-зеркала продолжают работать (GitHub редиректит их на домен из `CNAME`).

## Если что-то не так

| Симптом | Что делать |
|---|---|
| Домен не открывается сразу после merge | DNS-синхронизация + сертификаты GitHub: подожди до часа, `dig +short qkc.runs-on.dev` |
| `NET::ERR_CERT_…` в первые минуты | GitHub ещё выпускает сертификат — подожди и обнови |
| github.io-зеркало редиректит, а домен мёртв | Значит `CNAME` активирован слишком рано — верни `git mv CNAME CNAME.runs-on` до sync |
| CI реестра красный | Читай лог check'а в PR: обычно это схема записи или чужое имя владельца |

## Запасные имена

Если `qkc` вдруг отклонят — свободны (проверено 06.10.2026): `ouri`, `ouri-corp`,
`qkc-trainer`. Процедура та же: один claim + субдомены.

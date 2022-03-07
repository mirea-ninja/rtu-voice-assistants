# rtu-voice-assistants

Это голосовые ассистены с полностью открытым исходным кодом для студентов и преподавателей РТУ МИРЭА.
Список поддерживаемых платформ:

- Yandex.Alice - [Навык в каталоге Яндекс.Диалогов](http://localhost:8000/api/v1/alice "prod")
- VK.Marusia - `dev`
- Sber.Salut - `dev`

# Самостоятельная сборка проекта

## Production

1. Склонируйте данный репозиторий:

```sh
git clone https://github.com/Ninja-Official/rtu-voice-assistants rtu-voice-assistants
cd rtu-voice-assistants
```

2. Отредактируйте `.env.example`:

```sh
ALLOWED_DOMAINS=YOUR_ALLOWED_DOMAINS_HERE

DATABASE_HOST=YOUR_DATABASE_HOST_HERE
DATABASE_NAME=YOUR_DATABASE_NAME_HERE
DATABASE_USER=YOUR_DATABASE_USER_HERE
DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD_HERE
DATABASE_PORT=YOUR_DATABASE_PORT_HERE

SCHEDULE_API_URL=YOUR_SCHEDULE_API_URL_HERE

VK_API_KEY=YOUR_VK_API_KEY_HERE
```

3. Переименуйте `.env.example` в `.env`
4. Запустите проект с помощь Docker Compose:

```sh
docker-compose -f docker-compose.production.yml up --build -d
```

## Development

1. Склонируйте данный репозиторий:

```sh
git clone https://github.com/Ninja-Official/rtu-voice-assistants rtu-voice-assistants
cd rtu-voice-assistants
```

2. Отредактируйте `.env.example`:

```sh
ALLOWED_DOMAINS=YOUR_ALLOWED_DOMAINS_HERE

DATABASE_HOST=YOUR_DATABASE_HOST_HERE
DATABASE_NAME=YOUR_DATABASE_NAME_HERE
DATABASE_USER=YOUR_DATABASE_USER_HERE
DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD_HERE
DATABASE_PORT=YOUR_DATABASE_PORT_HERE

SCHEDULE_API_URL=YOUR_SCHEDULE_API_URL_HERE

VK_API_KEY=YOUR_VK_API_KEY_HERE
```

3. Переименуйте `.env.example` to `.env`
4. Install dependencies:

```sh
cd src
pip install -r requirements.txt
```

4. Запустите базу данных с помощью Docker Compose:

```sh
docker-compose -f docker-compose.development.yml up --build -d
```

5. Запустите проект, используя команду:

```sh
python3 main.py
```

6. Для локального тестирования навыка установите [Ngrok](https://ngrok.com/ "ngrok")

7. Запустите ngrok, используя команду:

```sh
ngrok http 8000
```

# Документация

Проект запускается по адресу - [http://localhost:8000](http://localhost:8000 "url запуска")

### Endpoints

- Swagger - [/docs](http://localhost:8000/docs "url запуска Swagger")

- Yandex.Alice - [/api/v1/alice](http://localhost:8000/api/v1/alice "url запуска Yandex.Alice")

- VK.Marusia - [/api/v1/marusia](http://localhost:8000/api/v1/marusia "url запуска Yandex.Alice")

- Sber.Salut - [/api/v1/sber](http://localhost:8000/api/v1/sber "url запуска Yandex.Alice")

# Команды

Для запуска навыков скажите одну из следующих фраз:

### Yandex.Alice

- Запусти навык Расписание РТУ МИРЭА
- Скажи Расписание МИРЭА завтра
- Скажи Расписание РТУ МИРЭА в понедельник

### VK.Marusia

- Запусти навык Расписание РТУ МИРЭА
- Скажи Расписание МИРЭА завтра
- Скажи Расписание РТУ МИРЭА в понедельник

### Sber.Salut

- Запусти навык Расписание РТУ МИРЭА
- Скажи Расписание МИРЭА завтра
- Скажи Расписание РТУ МИРЭА в понедельник

# Интеграция навыка в сценарии умного дома

В разработке...

# Примите участие

Это приложение и все относящиеся к нему сервисы являются **100% бесплатными** и **Open Source** продуктами. Мы с огромным удовольствием примем любые ваши предложения и сообщения, а также мы рады любому вашему участию в проекте! Перед тем как принять участие в развитии проекта:

1. Ознакомьтесь с нашим [CONTRIBUTING.MD](https://github.com/Ninja-Official/rtu-voice-assistants/blob/main/CONTRIBUTING.md), в котором описано то, как должны вести себя участники проекта.

2. Уважайте других участников, обсуждайте идеи, а не личности, ознакомьтесь с [кодексом поведения](https://github.com/Ninja-Official/rtu-voice-assistants/blob/main/CODE_OF_CONDUCT.md).

3. Не знаете, над чем вы хотите работать? Ознакомьтесь с нашей [дорожной картой](https://github.com/Ninja-Official/rtu-voice-assistants/projects/1).

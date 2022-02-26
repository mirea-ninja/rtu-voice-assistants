# rtu-voice-assistants

Это голосовые ассистены с полностью открытым исходным кодом для студентов и преподавателей РТУ МИРЭА.
Список поддерживаемых платформ:

* Yandex.Alice(prod)
* VKGroup.Marusia(dev)
* Sber.Salut(dev)


# Скриншоты
TODO

# Самостоятельная сборка проекта

## Production
1. Clone project:
```sh
git clone https://github.com/Ninja-Official/rtu-voice-assistants rtu-voice-assistants
cd rtu-voice-assistants
```
2. Edit `.env.example`:
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

3. Rename `.env.example` to `.env`
4. Run project using Docker Compose:
```sh
docker-compose -f docker-compose.production.yml up --build -d
```

## Development
1. Clone project:
```sh
git clone https://github.com/Ninja-Official/rtu-voice-assistants rtu-voice-assistants
cd rtu-voice-assistants
```
2. Edit `.env.example`:
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

3. Rename `.env.example` to `.env`
4. Install dependencies:
```sh
cd src
pip install -r requirements.txt
```
4. Run database using Docker Compose:
```sh
docker-compose -f docker-compose.development.yml up --build -d
```
5. Run project:
```sh
python3 main.py
```
6. Run ngrok:
```sh
ngrok http 3001
```


# Запуск
Для запуска навыков выполните следующие действия:

**Yandex.Alice**\
Запусти навык раписание РТУ\
Скажи расписание РТУ на завтра\
Скажи расписание РТУ на понедельник

# Примите участие
Это приложение и все относящиеся к нему сервисы являются **100% бесплатными** и **Open Source** продуктами. Мы с огромным удовольствием примем любые ваши предложения и сообщения, а также мы рады любому вашему участию в проекте! Перед тем как принять участие в развитии проекта:
1. Ознакомьтесь с нашим [CONTRIBUTING.MD](https://github.com/Ninja-Official/rtu-voice-assistants/blob/main/CONTRIBUTING.md), в котором описано то, как должны вести себя участники проекта.
2. Уважайте других участников, обсуждайте идеи, а не личности, ознакомьтесь с [кодексом поведения](https://github.com/Ninja-Official/rtu-voice-assistants/blob/main/CODE_OF_CONDUCT.md).
3. Не знаете, над чем вы хотите работать? Ознакомьтесь с нашей [дорожной картой](https://github.com/Ninja-Official/rtu-voice-assistants/projects/1).
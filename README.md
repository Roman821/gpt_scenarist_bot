# Как запустить проект?

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Roman821/gpt_scenarist_bot.git
cd gpt_scenarist_bot
```

### 2. Создайте виртуальное окружение

#### С помощью [pipenv](https://pipenv.pypa.io/en/latest/):

```bash
pip install --user pipenv
pipenv shell  # create and activate
```

#### Или классическим методом:

```bash
python -m venv .venv  # create
.venv\Scripts\activate.bat  # activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Установите переменные окружения (environment variables)

Создайте файл `.env`, это должно выглядеть так: `gpt_scenarist_bot/.env`. После скопируйте это в `.env`

```dotenv
BOT_TOKEN=<your_bot_token>
DEBUG_ID=<your_tg_id>  # не обязательно, нужно для использования команды /debug
DB_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
GPT_API_KEY=<your_gpt_api_key>
GPT_FOLDER_ID=<your_gpt_folder_id>
```
_**Не забудьте поменять значения на свои! (поставьте их после "=")**_

#### Больше о переменных:
BOT_TOKEN - [токен телеграм бота](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)<br>
DEBUG_ID - телеграм id пользователя, который сможет пользоваться командой `/debug`<br>
DB_URL - [url базы данных](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) sqlalchemy<br>
GPT_API_KEY - [API ключ](https://cloud.yandex.ru/ru/docs/iam/concepts/authorization/api-key) для использования YandexGPT<br>
GPT_FOLDER_ID - [folder id](https://cloud.yandex.ru/ru/docs/resource-manager/operations/folder/get-id) для использования YandexGPT

### 5. Запустите проект

```bash
python main.py
```

# Продакшен настройка

### 1. Установите [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### 2. Установите [docker](https://docs.docker.com/engine/install/)

### 3. Установите [docker compose plugin](https://docs.docker.com/compose/install/linux/)

### 4. Клонируйте репозиторий

```bash
git clone https://github.com/Roman821/gpt_scenarist_bot.git
cd gpt_scenarist_bot
```

### 5. Установите переменные окружения (environment variables)

Создайте файл `.env`, это должно выглядеть так: `gpt_scenarist_bot/.env`. После скопируйте это в `.env`

```dotenv
BOT_TOKEN=<your_bot_token>
DEBUG_ID=<your_tg_id>  # не обязательно, нужно для использования команды /debug
DB_URL=postgresql://<username>:<password>@postgres:5432/<database_name>
GPT_API_KEY=<your_gpt_api_key>
GPT_FOLDER_ID=<your_gpt_folder_id>

# docker-compose section
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database_name>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
```
_**Не забудьте поменять значения на свои! (поставьте их после "=")**_

#### Больше о переменных:
BOT_TOKEN - [токен телеграм бота](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)<br>
DEBUG_ID - телеграм id пользователя, который сможет пользоваться командой `/debug`<br>
DB_URL - [url базы данных](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) sqlalchemy<br>
GPT_API_KEY - [API ключ](https://cloud.yandex.ru/ru/docs/iam/concepts/authorization/api-key) для использования YandexGPT<br>
GPT_FOLDER_ID - [folder id](https://cloud.yandex.ru/ru/docs/resource-manager/operations/folder/get-id) для использования YandexGPT<br>

POSTGRES_USER - [POSTGRES_USER](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_PASSWORD - [POSTGRES_PASSWORD](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_DB - [POSTGRES_DB](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_HOST - [POSTGRES_HOST](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_PORT - [POSTGRES_PORT](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
PGDATA - [PGDATA](https://hub.docker.com/_/postgres) стандартная переменная окружения docker

### 6. Запустите docker compose

```bash
docker compose up -d
```

### 7. После успешного запуска проверьте сервер

```bash
docker compose logs -f
```

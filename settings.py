from pathlib import Path
from os import environ
from typing import Callable

from dotenv import load_dotenv


class Settings:

    LOGS_DIR = Path(__file__).resolve().parent / 'logs'
    LOGS_DIR.mkdir(exist_ok=True)

    WARNING_LOG_FILE_PATH = LOGS_DIR / 'warning.log'

    SYSTEM_PROMPT_TEMPLATE = (
        'Ты - сценарист, должен помогать пользователю сочинять историю. В твоих ответах НЕ должно быть ничего, кроме'
        ' истории. Эта история будет в жанре: {genre}, главный герой - {character}, сеттинг - {setting}.'
    )
    GPT_MODEL = 'yandexgpt-lite'
    GPT_TEMPERATURE = 1
    RESPONSE_MAX_TOKENS = 750
    TOKENS_LIMIT_BY_USER = 3000

    REQUEST_MAX_TOKENS = 500

    ROLE_CHOICES: dict[str, int] = {
        'system': 0,
        'user': 1,
        'assistant': 2,
    }
    ROLE_CHOICES_ROLE_BY_DB_VALUE = {value: key for key, value in ROLE_CHOICES.items()}


def set_up_env_var(env_var_name: str, error_log_function: Callable) -> str | None:

    load_dotenv()

    result = environ.get(env_var_name)

    if not result:

        error_log_function(f'{env_var_name} environment variable is not set!')

        return None

    return result

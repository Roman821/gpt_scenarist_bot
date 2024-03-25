from requests import Session, post

from get_logger import get_logger
from settings import Settings


class GPT:

    def __init__(
            self, api_key: str, folder_id: str, previous_messages: list[dict[str, str]], system_prompt: str
    ) -> None:

        self.api_key = api_key
        self.folder_id = folder_id
        self.previous_messages = previous_messages
        self.system_prompt = system_prompt
        self.logger = get_logger('main')
        self.model_uri = f'gpt://{self.folder_id}/{Settings.GPT_MODEL}'

        with Session() as session:
            self.session = session

    def get_prompt_tokens_amount(self, prompt: str) -> int | None:

        try:
            response = post(
                'https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Api-Key {self.api_key}',
                },
                json={
                    'modelUri': self.model_uri,
                    'text': prompt,
                },
            )

        except Exception as e:

            self.logger.error(f'An exception occurred while requesting gpt tokenizing ({prompt=}): {e}')

            return

        response_status_code = response.status_code

        if response_status_code != 200:

            self.logger.error(f'Incorrect gpt tokenizer answer status code: {response_status_code} ({prompt=})')

            return

        return len(response.json()['tokens'])

    def ask(self, prompt: str, additional_system_prompt: str = '') -> tuple[str, int | None]:
        """Returns a gpt answer text and a total number of tokens spent on this request"""

        error_message = 'Произошла ошибка, пожалуйста, повторите попытку или обратитесь в поддержку'

        user_message = {'role': 'user', 'text': prompt}

        messages = [
            {'role': 'system', 'text': self.system_prompt},
            *self.previous_messages,
            user_message,
        ]

        if additional_system_prompt:
            messages.append({'role': 'system', 'text': additional_system_prompt})

        try:
            response = self.session.post(
                'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Api-Key {self.api_key}',
                },
                json={
                    'modelUri': self.model_uri,
                    'completionOptions': {
                        'temperature': Settings.GPT_TEMPERATURE,
                        'maxTokens': Settings.RESPONSE_MAX_TOKENS,
                        'stream': False,
                    },
                    'messages': messages,
                },
            )

        except Exception as e:

            self.logger.error(f'An exception occurred while requesting gpt answer ({prompt=}): {e}')

            return error_message, None

        response_status_code = response.status_code

        if response_status_code != 200:

            self.logger.error(f'Incorrect gpt answer status code: {response_status_code} ({prompt=})')

            return error_message, None

        response_json = response.json()['result']

        answer = response_json['alternatives'][0]['message']['text']

        self.previous_messages.append(user_message)
        self.previous_messages.append({'role': 'assistant', 'text': answer})

        return answer, int(response_json['usage']['completionTokens'])

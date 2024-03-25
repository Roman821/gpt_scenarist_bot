from random import choice

from telebot import TeleBot, types, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from gpt import GPT
from settings import Settings, set_up_env_var
from get_logger import get_logger
from database import SessionLocal, create_all_tables
from crud import UserCrud, HistoryRecordCrud
from models import HistoryRecord


class ChatStates(StatesGroup):

    not_chat = State()
    set_genre = State()
    set_character = State()
    set_setting = State()
    chat = State()


BOT_TOKEN: str
DEBUG_ID: int
GPT_API_KEY: str
GPT_FOLDER_ID: str


def run_bot() -> None:

    end_chat_command = 'end_chat'
    help_command = 'help'
    end_story_command = 'end_story'

    bot = TeleBot(BOT_TOKEN, state_storage=StateMemoryStorage())

    bot.add_custom_filter(custom_filters.StateFilter(bot))

    help_button = types.KeyboardButton(text=f'/{help_command}')

    no_chat_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    no_chat_markup.add(help_button)
    no_chat_markup.add(types.KeyboardButton(text='/new_chat'))

    chat_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    chat_markup.add(help_button)
    chat_markup.add(types.KeyboardButton(text=f'/{end_chat_command}'))
    chat_markup.add(types.KeyboardButton(text=f'/{end_story_command}'))

    @bot.message_handler(commands=[help_command, 'start'])
    def help_handler(message: types.Message):

        if bot.get_state(message.from_user.id, message.chat.id) is None:
            bot.set_state(message.from_user.id, ChatStates.not_chat, message.chat.id)

        reply_message = (
            'Привет, я - бот-GPT-сценарист, вот мой функционал:\n'
            f'/{help_command} или /start - список всех команд (ты уже тут)\n'
            '/new_chat - создание нового чата с GPT\n'
            f'/{end_chat_command} - удаление чата, очистка истории сообщений\n'
            f'/{end_story_command} - попросить нейросеть закончить историю и получить её (истории) полную версию\n\n'
            f'P.S. На каждого пользователя есть лимит токенов: {Settings.TOKENS_LIMIT_BY_USER}, без этого никак('
        )

        if bot.get_state(message.from_user.id, message.chat.id) == ChatStates.chat.name:
            reply_markup = chat_markup

        else:
            reply_markup = no_chat_markup

        bot.reply_to(message, reply_message, parse_mode='HTML', reply_markup=reply_markup)

    @bot.message_handler(
        commands=[end_chat_command],
        state=[ChatStates.chat, ChatStates.set_genre, ChatStates.set_character, ChatStates.set_setting],
    )
    def end_chat(message: types.Message):

        bot.set_state(message.from_user.id, ChatStates.not_chat, message.chat.id)

        with SessionLocal() as db:

            user = UserCrud(db).get(telegram_id=message.from_user.id)

            HistoryRecordCrud(db).delete_many(user=user)

        bot.reply_to(
            message,
            'История чата удалена, спасибо за использование бота! Вы можете начать новый чат: /new_chat',
            reply_markup=no_chat_markup,
        )

    def ask_gpt_safe_handler(message: types.Message, additional_system_prompt: str = '') -> str | None:
        """Performs a safe request to GPT, returning a gpt answer or None if a user exceeds the token limit"""
        with SessionLocal() as db:

            user_crud = UserCrud(db)

            user = user_crud.get(telegram_id=message.from_user.id)

            if user.tokens_spent > Settings.TOKENS_LIMIT_BY_USER:
                return None

            messages_history_db: list[HistoryRecord] = HistoryRecordCrud(db).get_many(user=user)

            messages_history = []

            for message_history in messages_history_db:
                messages_history.append({
                    'role': Settings.ROLE_CHOICES_ROLE_BY_DB_VALUE[message_history.role],
                    'text': message_history.message,
                })

            system_prompt = Settings.SYSTEM_PROMPT_TEMPLATE.format(
                genre=user.genre, character=user.character, setting=user.setting
            )

            message_text = message.text

            gpt_answer, spent_tokens = GPT(
                GPT_API_KEY, GPT_FOLDER_ID, messages_history, system_prompt
            ).ask(message_text, additional_system_prompt=additional_system_prompt)

            if spent_tokens:

                HistoryRecordCrud(db).create(user=user, message=message_text, role=Settings.ROLE_CHOICES['user'])
                HistoryRecordCrud(db).create(user=user, message=gpt_answer, role=Settings.ROLE_CHOICES['assistant'])

                gpt_answer += f'\n\nТокенов потрачено: {spent_tokens}'

                user_crud.update(user, tokens_spent=user.tokens_spent + spent_tokens)

            return gpt_answer

    @bot.message_handler(commands=[end_story_command], state=ChatStates.chat)
    def end_story_handler(message: types.Message):

        gpt_answer = ask_gpt_safe_handler(message)

        if gpt_answer:
            bot.reply_to(message, gpt_answer, reply_markup=no_chat_markup)

        else:
            bot.reply_to(
                message,
                'Не удалось получить ответ от GPT, ваша история останется без концовки, к сожалению, вы превысили'
                ' лимит токенов на пользователя((',
            )

        with SessionLocal() as db:

            user = UserCrud(db).get(telegram_id=message.from_user.id)

            messages_history_db: list[HistoryRecord] = HistoryRecordCrud(db).get_many(user=user)

            bot.reply_to(
                message,
                'Вот полный текст получившейся истории (возможно, он будет разбит на несколько сообщений):',
                reply_markup=no_chat_markup,
            )

            story_part = ''

            for history_message in messages_history_db:

                if len(story_part + history_message.message) > 4096:  # 4096 - max message length
                    for history_message_chunk in history_message.message.split('\n'):

                        if len(story_part + history_message_chunk) > 4096:

                            bot.reply_to(message, story_part, reply_markup=no_chat_markup)

                            story_part = ''

                        story_part += history_message_chunk

                else:
                    story_part += history_message.message

            if story_part:
                bot.reply_to(message, story_part, reply_markup=no_chat_markup)

        end_chat(message)

    @bot.message_handler(state=ChatStates.chat)
    def process_chat_message(message: types.Message):

        message_text = message.text

        # Safety checks (a user must be able to exit a chat and view a list of bot commands):
        if message_text == f'/{end_chat_command}':

            end_chat(message)

            return

        elif message_text == f'/{help_command}':

            help_handler(message)

            return

        elif message_text == f'/{end_story_command}':

            end_story_handler(message)

            return

        tokens_amount: int | None = GPT(GPT_API_KEY, GPT_FOLDER_ID, [], '').get_prompt_tokens_amount(message_text)

        if tokens_amount is None:

            bot.reply_to(
                message,
                'Не удалось проверить длину сообщения, пожалуйста, попробуйте ещё раз или обратитесь в поддержку',
                reply_markup=chat_markup,
            )

            return

        elif tokens_amount > Settings.REQUEST_MAX_TOKENS:

            bot.reply_to(message, 'Сообщение слишком длинное, пожалуйста, укоротите его', reply_markup=chat_markup)

            return

        gpt_answer = ask_gpt_safe_handler(message)

        if gpt_answer:
            bot.reply_to(message, gpt_answer, reply_markup=chat_markup)

        else:
            bot.reply_to(
                message, 'Не удалось получить ответ от GPT, к сожалению, вы превысили лимит токенов на пользователя(('
            )

    @bot.message_handler(commands=['new_chat'], state=ChatStates.not_chat)
    def new_chat(message: types.Message):

        bot.set_state(message.from_user.id, ChatStates.set_genre, message.chat.id)

        bot.reply_to(message, 'Введите жанр (хоррор, комедия..)', reply_markup=chat_markup)

    @bot.message_handler(state=ChatStates.set_genre)
    def process_set_genre(message: types.Message):

        user_id = message.from_user.id

        with SessionLocal() as db:

            user_crud = UserCrud(db)

            if user := user_crud.get(telegram_id=user_id):
                user_crud.update(user, genre=message.text)

            else:
                user_crud.create(telegram_id=user_id, genre=message.text)

        bot.set_state(user_id, ChatStates.set_character, message.chat.id)

        bot.reply_to(message, 'Введите главного героя (Гарри Поттер, Клеопатра..)', reply_markup=chat_markup)

    @bot.message_handler(state=ChatStates.set_character)
    def process_set_character(message: types.Message):

        user_id = message.from_user.id

        with SessionLocal() as db:

            user_crud = UserCrud(db)

            if user := user_crud.get(telegram_id=user_id):
                user_crud.update(user, character=message.text)

            else:
                user_crud.create(telegram_id=user_id, character=message.text)

        bot.set_state(user_id, ChatStates.set_setting, message.chat.id)

        bot.reply_to(
            message, 'Введите сеттинг (мир Звёздных войн, вселенная Гарри Поттера..)', reply_markup=chat_markup
        )

    @bot.message_handler(state=ChatStates.set_setting)
    def process_set_setting(message: types.Message):

        user_id = message.from_user.id

        with SessionLocal() as db:

            user_crud = UserCrud(db)

            if user := user_crud.get(telegram_id=user_id):
                user_crud.update(user, setting=message.text)

            else:
                user_crud.create(telegram_id=user_id, setting=message.text)

        bot.set_state(user_id, ChatStates.chat, message.chat.id)

        bot.reply_to(message, 'Начните историю', reply_markup=chat_markup)

    @bot.message_handler(commands=['debug'], func=lambda message: message.from_user.id == DEBUG_ID)
    def debug_handler(message: types.Message):
        with open(Settings.WARNING_LOG_FILE_PATH, 'rb') as f:

            file_data = f.read()

            if not file_data:

                bot.reply_to(message, 'Файл с логами ошибок пуст!')

                return

            bot.send_document(message.chat.id, file_data, visible_file_name='logs.log')

    @bot.message_handler(content_types=['text'])
    def unknown_text_handler(message: types.Message):

        replies = (
            'О, круто!',
            'Верно подмечено!',
            'Как с языка снял',
            'Какой ты всё-таки умный',
            'По-любому что-то умное написал',
            'Как лаконично-то!',
        )

        if bot.get_state(message.from_user.id, message.chat.id) == ChatStates.chat.name:
            reply_markup = chat_markup

        else:
            reply_markup = no_chat_markup

        help_message = (
            '\n\nЕсли ты хотел, чтобы я что-то сделал, то я не распознал твою команду, пожалуйста,'
            f' сверься с /{help_command}'
        )

        bot.reply_to(message, choice(replies) + help_message, reply_markup=reply_markup)

    bot.infinity_polling()


def main():

    global BOT_TOKEN, DEBUG_ID, GPT_API_KEY, GPT_FOLDER_ID

    logger = get_logger('main')

    DEBUG_ID = int(set_up_env_var('DEBUG_ID', logger.warning) or 0)

    BOT_TOKEN = set_up_env_var('BOT_TOKEN', logger.error)
    GPT_API_KEY = set_up_env_var('GPT_API_KEY', logger.error)
    GPT_FOLDER_ID = set_up_env_var('GPT_FOLDER_ID', logger.error)

    if all((BOT_TOKEN, GPT_API_KEY, GPT_FOLDER_ID)):

        create_all_tables()

        run_bot()

    else:
        logger.error('Setup cannot be completed, some errors occurred')


if __name__ == '__main__':
    main()

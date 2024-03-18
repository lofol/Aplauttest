import asyncio
import traceback
from itertools import islice, cycle
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.utils.markdown import hbold
from pars.cfg import Cfg
from pars.parser import OzonParser

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Отвечаем на стартовую комнанду в боте `/start`
    """
    await message.answer(f"Добрый день {hbold(message.from_user.full_name)}!"
                         f" Пришли мне ссылку на любой товар в маркетплейсе 'Озон' либо же его артикул")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Хендлер для перехвата любых сообщений и ответа на них.
    """
    reply_msg = await message.answer('Начинаю обработку данных.')
    try:
        await asyncio.sleep(3)  # Сон лишь для того, чтобы замедлить парсер и показать что происходит в парсере.
        await reply_msg.edit_text(f'Создаю объект парсера и пробую установить сессию.')
        parser = OzonParser()
        # Добавил каждый раз создание парсера по новой и установку его сессии тоже.
        # Правильнее было бы создать в начале работы обьект парсера, одну сессию и с ними работать.
        # Сессии удобно хранить в редисе, в случае её слета делать переустановку.
        await parser.session.set_session()
        await asyncio.sleep(3)
        for _ in islice(cycle(['-', '/', '|', '\\']), 40):
            await reply_msg.edit_text(f'Получаю данные от источника, идет загрузка {_}...')
            await asyncio.sleep(0.1)
        res = await parser.parse_message(message.md_text)
        if parser.rews_file:
            await message.answer_document(FSInputFile(parser.rews_file), caption=res)
            await reply_msg.delete()
        else:
            await reply_msg.edit_text(f'Не удалось получить файл! Попробуйте снова.\nОшибка: {res}')
    except Exception:
        await reply_msg.edit_text(f'Произошла ошибка при получении данных: {traceback.format_exc()}.'
                                  'Пожалуйста, попробуйте еще раз или попробуйте другую ссылку.')


async def run_bot() -> None:
    config = Cfg().load()
    bot = Bot(config.get('telegram_bot_id'), parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


import asyncio
import json
from datetime import datetime

from config import tg_bot_token
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text
from main import check_news_update

bot = Bot(token=tg_bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    start_buttons = ["Всі новини", "Останні 5 новин", "Свіжі новини"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента новин", reply_markup=keyboard)


@dp.message_handler(Text(equals="Всі новини"))
async def get_all_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
        # news = f"{hbold(datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
        #       f"{hunderline(v['article_title'])}\n" \
        #       f"{hcode(v['article_desc'])}\n" \
        #       f"{hlink(v['article_title'], v['article_url'])}"

        news = f"{hbold(datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Останні 5 новин"))
async def get_last_five_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Свіжі новини"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()

    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)
    else:
        await message.answer("Поки нема свіжих новин")


async def news_every_minute():
    while True:
        fresh_news = check_news_update()
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"

                await bot.send_message(user_id, news, disable_notification=True)

        await asyncio.sleep(20)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    executor.start_polling(dp)

import logging
from aiogram import Bot, Dispatcher, types
import redis
import os
import asyncio

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    try:
        _, from_currency, to_currency, amount = message.text.split()
        amount = float(amount)
        from_rate = redis_client.get(from_currency)
        to_rate = redis_client.get(to_currency)

        if from_rate is None or to_rate is None:
            await message.reply(f'Error: Unable to find rates for {from_currency} or {to_currency}.')
            return

        from_rate = float(from_rate)
        to_rate = float(to_rate)
        result = (amount * from_rate) / to_rate
        await message.reply(f'{amount} {from_currency} = {result:.2f} {to_currency}')
    except ValueError:
        await message.reply('Error: Invalid input. Please use the format /exchange USD RUB 10')
    except Exception as e:
        logging.error(f'Error processing request: {e}')
        await message.reply('Error processing request')


@dp.message_handler(commands=['rates'])
async def rates(message: types.Message):
    try:
        rates = "\n".join([f"{key}: {redis_client.get(key)}" for key in redis_client.keys()])
        await message.reply(rates)
    except Exception as e:
        logging.error(f'Error fetching rates: {e}')
        await message.reply('Error fetching rates')


async def fetch_and_store_rates():
    import aiohttp
    import xml.etree.ElementTree as ET

    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_data = await response.text()
            root = ET.fromstring(xml_data)
            for currency in root.findall('Valute'):
                code = currency.find('CharCode').text
                rate = currency.find('Value').text.replace(',', '.')
                redis_client.set(code, rate)


async def main():
    await fetch_and_store_rates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
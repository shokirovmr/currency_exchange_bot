import aiohttp
import xml.etree.ElementTree as ET
import redis
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_CLIENT = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


async def fetch_and_store_rates():
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_data = await response.text()
            root = ET.fromstring(xml_data)
            for currency in root.findall('Valute'):
                code = currency.find('CharCode').text
                rate = currency.find('Value').text.replace(',', '.')
                REDIS_CLIENT.set(code, rate)


if __name__ == '__main__':
    import asyncio

    asyncio.run(fetch_and_store_rates())

import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs


class ParsingTrade:
    def __init__(self, url):
        self.url = url

    async def fetch(self, url):
        '''Запрос на ссылку'''
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_url = await response.text()
                return bs(response_url, 'html.parser')

    async def get_categories(self):
        '''Запрос на основную ссылку из которой забирается все категории сайта
        Возвращает словарь с категориями и ссылками на категории'''
        response = await self.fetch(self.url)
        categories_find = response.find_all('a', class_='cat_item_color')
        return {i.text.strip(): self.url + i['href'][12:] for i in categories_find}

    async def get_data_categories(self, categories_url):
        '''Метод, который заходит на выбранную категорию
        Возвращает словарь с названием и ссылкой'''
        response = await self.fetch(categories_url)
        subcategories = response.find_all('a', class_='cat_item_color', href=True)
        return {i.text.strip(): self.url + i['href'][12:] for i in subcategories}

    async def get_product(self, product_url):
        '''
        Метод заходит в выбранный продукт
        :param product_url:
        :return:
        '''
        response = await self.fetch(product_url)
        product = response.find('div', class_='items-rows clearfix').find_all('a')
        return dict(
            zip(
                [self.url + i['href'][12:] for i in product][::3], [i.text.strip() for i in product][::3]
            )
        )

    async def get_data_product(self, product_url):
        '''Метод забирает данные продукта'''
        response = await self.fetch(product_url)
        price = response.find('div', class_='price').find('span').text
        name = response.find('main', class_='content-in').find('h1').text
        description = response.find('div', class_='descript1').text.replace(f';{" "}', '\n').strip()
        return {
            'Название': name,
            'Цена': price,
            'Описание': description
        }


trade = ParsingTrade('https://trade59.ru/catalog.html')
print(asyncio.run(trade.get_data_product('https://trade59.ru/catalog.html?itemid=9849')))

import os
import asyncio
import aiofiles
import hashlib
from bs4 import BeautifulSoup
import httpx

# Список уже обработанных URL-ов
processed_urls = set()

async def fetch(url):
    async with httpx.AsyncClient() as client:
        print(f"Fetching URL: {url}")
        response = await client.get(url)
        return response.text

async def crawl(url):
    global processed_urls
    if url in processed_urls:
        return []

    html = await fetch(url)
    processed_urls.add(url)

    print(f"Processing URL: {url}")

    soup = BeautifulSoup(html, 'html.parser')
    product_cards = soup.find_all('article', attrs={'data-chg-product-shelf-index': True})

    image_urls = []
    for card in product_cards:
        image_url = card.find('img').get('data-src', None)
        if image_url:
            image_urls.append(image_url)

    return image_urls

async def save_image(url, path):
    async with httpx.AsyncClient() as client:
        print(f"Downloading image from URL: {url}")
        response = await client.get(url)
        async with aiofiles.open(path, 'wb') as f:
            await f.write(response.content)
    print(f"Image saved: {path}")

def unique_filename(url):
    # Создаем уникальное имя файла на основе хэша URL
    hash = hashlib.md5(url.encode()).hexdigest()
    return f"{hash}.jpg"

async def download_and_compress_image(url, category):
    # Функция для скачивания и сжатия изображения
    filename = unique_filename(url)
    save_path = os.path.join(category, filename)  # Путь для сохранения изображения в соответствующей категории
    await save_image(url, save_path)
    print(f"Image downloaded: {url}")

async def main():
    base_urls = [
        ("https://www.chitai-gorod.ru/catalog/artists/kisti-110622", "images"),
    ]
    total_pages = 10

    for base_url, category in base_urls:
        os.makedirs(category, exist_ok=True)  # Проверяем и создаем директории для каждой категории
        for page_number in range(1, total_pages + 1):
            url = f"{base_url}?page={page_number}"
            print(f"Processing page: {url}")
            image_urls = await crawl(url)

            # Находим изображения на текущей странице и скачиваем их
            tasks = [download_and_compress_image(image_url, category) for image_url in image_urls]
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
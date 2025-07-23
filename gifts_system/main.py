import asyncio
import json
import logging
import os

from bs4 import BeautifulSoup  # Используем для парсинга HTML
from playwright.async_api import async_playwright, Page, TimeoutError  # Асинхронный браузер для автоматизации

from func_push_bot import push_bot_group_message, on_shutdown  # Отправка уведомлений в Telegram

# 📂 Абсолютный путь к директории скрипта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📁 Файл для кеша количества подарков (только число)
GIFTS_FILE = os.path.join(BASE_DIR, "gifts.txt")

# 💾 Файл хранения сессии Telegram Web
SESSION_FILE = os.path.join(BASE_DIR, "session.json")


# 💾 Сохраняет количество подарков как число в текстовый файл
def save_gifts_count(count: int):
    with open(GIFTS_FILE, "w", encoding="utf-8") as f:
        f.write(str(count))


# 🔄 Загружает сохранённое количество подарков из текстового файла
def load_gifts_count() -> int:
    try:
        with open(GIFTS_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0  # Если файла нет или в файле мусор


# 🔁 Функция безопасного клика по элементу с повторными попытками
async def click_with_retry(page: Page, selector: str, retries: int = 7, delay: float = 2.0) -> bool:
    for attempt in range(1, retries + 1):
        try:
            await page.wait_for_selector(selector, state="visible", timeout=5000)
            await page.click(selector)
            return True
        except TimeoutError:
            print(f"Попытка {attempt}: элемент '{selector}' не появился или не стал видимым.")
        except Exception as e:
            print(f"Попытка {attempt}: ошибка при клике по '{selector}': {e}")

        if attempt < retries:
            await asyncio.sleep(delay)

    return False


# 🎁 Получает список доступных подарков, возвращает HTML-элементы
async def parse_gifts(page):
    gifts = []
    try:
        # 🔽 Открываем меню и переходим в раздел подарков
        await page.click('#LeftMainHeader > div.DropdownMenu.main-menu > button')
        await page.wait_for_selector("div.Avatar.account-avatar", state="visible", timeout=10000)
        await page.click("div.Avatar.account-avatar")
        await page.click("text=Send a Gift", timeout=5000)

        # 🖱 Кликаем по нужному контейнеру с подарками
        success = await click_with_retry(page, "div.ripple-container", retries=7, delay=2.0)
        if not success:
            print("Не удалось кликнуть по элементу 'div.ripple-container', возможно элемент не появился.")
            return None

        await asyncio.sleep(5)  # ⏳ Ждём загрузку подарков
        txt = await page.content()  # Получаем HTML-страницу

        # 🧽 Парсим HTML с помощью BeautifulSoup
        soup = BeautifulSoup(txt, 'lxml').find_all('div', class_='G1mBmzxs f5ArEO1S starGiftItem')
        gifts = soup  # Возвращаем список элементов

    except Exception as ex:
        print(f'❌ Ошибка в parse_gifts: {ex}')
        return None

    return gifts


# 🚀 Основной цикл работы скрипта
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)

    async with async_playwright() as p:
        # 🌐 Запуск браузера в headless-режиме (без GUI)
        browser = await p.chromium.launch(headless=True,
                                          args=[
                                              "--disable-blink-features=AutomationControlled",
                                              "--no-sandbox",
                                              "--disable-infobars",
                                              "--window-size=1920,1080",
                                          ])
        # 💾 Восстановление сессии, если файл session.json существует
        context = await browser.new_context(storage_state=SESSION_FILE if os.path.exists(SESSION_FILE) else None)
        page = await context.new_page()

        await page.goto("https://web.telegram.org/a/")

        # 👤 Если сессии нет — ожидаем ручной вход
        if not os.path.exists(SESSION_FILE):
            input("👉 Войди в Telegram вручную и нажми Enter.")
            await context.storage_state(path=SESSION_FILE)

        # 🔄 Основной цикл: проверка подарков каждые 15 секунд
        while True:
            try:
                await asyncio.sleep(3)

                current_gifts = await parse_gifts(page)
                if current_gifts is None:
                    logger.warning("Не удалось получить подарки, перезагружаю страницу...")
                    await page.reload()
                    await asyncio.sleep(5)
                    continue

                current_count = len(current_gifts)
                print(current_count)
                previous_count = load_gifts_count()
                print(previous_count)
                await push_bot_group_message(f'Данные текст файла: {current_gifts}'
                                             f'\nДанные сейчас: {previous_count}')

                if current_count != previous_count:
                    diff = current_count - previous_count
                    if diff > 0:
                        msg = f"🎉 Появилось новых подарков: {diff} шт."
                    else:
                        msg = f"❗ Подарков стало меньше на {-diff} шт."

                    await push_bot_group_message(msg)
                    logger.info(msg)
                    save_gifts_count(current_count)
                else:
                    logger.info("Количество подарков не изменилось.")

                await asyncio.sleep(15)
                await page.reload()

            except Exception as e:
                logger.error(f"⚠️ Ошибка в основном цикле: {e}", exc_info=True)
                logger.info("Обновляю страницу и продолжаю...")
                try:
                    await page.reload()
                except Exception as reload_ex:
                    logger.error(f"Не удалось обновить страницу: {reload_ex}", exc_info=True)
                await asyncio.sleep(10)


# ⏱ Точка входа в скрипт
if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(on_shutdown())  # Закрытие ресурсов, если нужно

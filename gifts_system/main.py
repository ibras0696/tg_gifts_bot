import asyncio
from pprint import pprint
import json
import os

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError


# Абсолютный путь к директории скрипта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GIFTS_FILE = os.path.join(BASE_DIR, "gifts_cache.json")
SESSION_FILE = os.path.join(BASE_DIR, "session.json")


def save_gifts(data):
    """
    Сохраняет список подарков в JSON файл.

    Args:
        data (list): Список URL изображений подарков.
    """
    with open(GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_gifts():
    """
    Загружает список подарков из JSON файла.

    Returns:
        list: Список URL изображений подарков или пустой список,
              если файл не найден или не удалось прочитать.
    """
    try:
        with open(GIFTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


async def click_with_retry(page: Page, selector: str, retries: int = 7, delay: float = 2.0) -> bool:
    """
    Пытается кликнуть по элементу с заданным селектором с повторными попытками.

    Args:
        page (Page): Объект страницы Playwright.
        selector (str): CSS-селектор для поиска элемента.
        retries (int): Количество попыток.
        delay (float): Задержка между попытками в секундах.

    Returns:
        bool: True если клик успешен, False если все попытки не удались.
    """
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

#
# async def parse_gifts(page: Page):
#     """
#     Асинхронно парсит страницу с подарками пользователя.
#
#     Последовательность действий:
#     - Открывает главное меню.
#     - Переходит в меню аккаунта.
#     - Кликает по пункту "Send a Gift".
#     - Кликает по элементу с подарками с повторными попытками.
#     - Собирает все уникальные URL изображений подарков.
#
#     Args:
#         page (Page): Объект страницы Playwright.
#
#     Returns:
#         set: Множество URL изображений подарков.
#         None: Если произошла ошибка.
#     """
#     gifts = set()
#     try:
#         await page.click('#LeftMainHeader > div.DropdownMenu.main-menu > button')
#         await page.wait_for_selector("div.Avatar.account-avatar", state="visible", timeout=10000)
#         await page.click("div.Avatar.account-avatar")
#         await page.click("text=Send a Gift", timeout=5000)
#
#         # Кликаем по "div.ripple-container" с retry
#         success = await click_with_retry(page, "div.ripple-container", retries=7, delay=2.0)
#         if not success:
#             print("Не удалось кликнуть по элементу 'div.ripple-container', возможно элемент не появился.")
#             return None
#
#         # Ждём, чтобы страница обновилась и загрузились подарки
#         await asyncio.sleep(5)
#
#         # Получаем HTML содержимое страницы
#         txt = await page.content()
#         soup = BeautifulSoup(txt, 'lxml').find_all('div', class_='G1mBmzxs f5ArEO1S starGiftItem')
#         for _ in range(2):
#             print(soup[_])
#         for i in soup:
#             img_src = i.find('img').get('src')
#             gifts.add(img_src)
#     except Exception as ex:
#         print(f'❌ Ошибка в parse_gifts: {ex}')
#         return None
#     return gifts
async def parse_gifts(page):
    gifts = set()
    try:
        await page.click('#LeftMainHeader > div.DropdownMenu.main-menu > button')
        await page.wait_for_selector("div.Avatar.account-avatar", state="visible", timeout=10000)
        await page.click("div.Avatar.account-avatar")
        await page.click("text=Send a Gift", timeout=5000)

        # Кликаем по "div.ripple-container" с retry
        success = await click_with_retry(page, "div.ripple-container", retries=7, delay=2.0)
        if not success:
            print("Не удалось кликнуть по элементу 'div.ripple-container', возможно элемент не появился.")
            return None

        await asyncio.sleep(5)  # ждём загрузку подарков
        txt = await page.content()

        soup = BeautifulSoup(txt, 'lxml').find_all('div', class_='G1mBmzxs f5ArEO1S starGiftItem')
        for idx, gift_div in enumerate(soup):
            # Получаем количество звезд (число рядом с иконкой)
            button = gift_div.find('button', class_='Button')
            star_count = None
            if button:
                # Текст кнопки после <i> с классом star-amount-icon — это число звёзд
                star_icon = button.find('i', class_='star-amount-icon')
                if star_icon:
                    # Возьмём весь текст кнопки и уберём символы звёзд
                    text = button.get_text(strip=True)
                    # Оставим только цифры из текста
                    digits = ''.join(filter(str.isdigit, text))
                    if digits.isdigit():
                        star_count = int(digits)

            # Получаем alt текст картинки, если есть
            img = gift_div.find('img')
            alt_text = img.get('alt', '') if img else ''

            # Формируем уникальный ключ подарка
            unique_key = (alt_text, star_count)
            # Если alt пустой, можно использовать индекс, но лучше, если будет какой-то уникальный атрибут
            if not alt_text:
                unique_key = (f"gift_idx_{idx}", star_count)

            gifts.add(unique_key)

    except Exception as ex:
        print(f'❌ Ошибка в parse_gifts: {ex}')
        return None
    return gifts


async def main():
    """
    Основная асинхронная функция запуска скрипта.

    - Запускает браузер Playwright.
    - Загружает сохранённую сессию или просит пользователя войти вручную.
    - Периодически парсит подарки и сравнивает с сохранёнными.
    - Если количество подарков изменилось — выводит сообщение.
    - В случае ошибки перезагружает страницу и продолжает работу.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          args=[
                                              "--disable-blink-features=AutomationControlled",
                                              "--no-sandbox",
                                              "--disable-infobars",
                                              "--window-size=1920,1080",
                                          ])
        context = await browser.new_context(storage_state=SESSION_FILE if os.path.exists(SESSION_FILE) else None)
        page = await context.new_page()

        await page.goto("https://web.telegram.org/a/")

        if not os.path.exists(SESSION_FILE):
            input("👉 Войди в Telegram вручную и нажми Enter.")
            await context.storage_state(path=SESSION_FILE)

        while True:
            try:
                # Ждём, чтобы UI успел обновиться
                await asyncio.sleep(3)

                # Парсим подарки на странице
                current_gifts = await parse_gifts(page)

                # Если парсинг не удался — перезагружаем страницу
                if current_gifts is None:
                    print("Обновляю страницу из-за ошибки парсинга...")
                    await page.reload()
                    await asyncio.sleep(5)
                    continue

                old_gifts = set(load_gifts())

                if len(current_gifts) != len(old_gifts):
                    diff = len(current_gifts) - len(old_gifts)
                    if diff > 0:
                        print(f"🎉 Появилось новых подарков: {diff} шт.")
                    else:
                        print(f"❗ Подарков стало меньше на {-diff} шт.")
                    save_gifts(list(current_gifts))
                else:
                    print("Количество подарков не изменилось.")

                # Ждём 15 секунд перед следующим циклом
                await asyncio.sleep(15)

                # Перезагружаем страницу для обновления данных
                await page.reload()

            except Exception as e:
                print("⚠️ Ошибка в основном цикле:", e)
                print("Обновляю страницу и продолжаю...")
                try:
                    await page.reload()
                except Exception as reload_ex:
                    print(f"Не удалось обновить страницу: {reload_ex}")
                await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())

# В случае ошибок можно посмотреть chat gpt который все писал
# https://chatgpt.com/c/688014ab-7ca8-832f-8894-6ed1be687175
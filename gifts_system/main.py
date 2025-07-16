from pprint import pprint

from playwright.sync_api import sync_playwright, Page
import time, json
import os

GIFTS_FILE = "gifts_cache.json"


def save_gifts(data):
    with open(GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_gifts():
    try:
        with open(GIFTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def parse_gifts(page: Page):
    gifts = []

    try:
        # Открытие меню
        page.click('#LeftMainHeader > div.DropdownMenu.main-menu > button')

        # Открываем меню пользователя
        page.wait_for_selector("div.Avatar.account-avatar", state="visible", timeout=10000)
        page.click("div.Avatar.account-avatar")

        # Кликаем по "Send a gift" — подстрой селектор если не подходит
        page.click("text=Send a Gift", timeout=5000)

        # Нажимаем на профиль человека
        page.locator('#LeftMainHeader > div.DropdownMenu.main-menu > button').first.click()

        # Ждем появления блока подарков
        page.wait_for_selector("div.modal-dialog", timeout=10000)

        # Только после этого получаем подарки
        blocks = page.query_selector_all("div.modal-dialog div.gift-item")  # пример селектора

        pprint(blocks)
        for b in blocks:
            try:
                text = b.inner_text().strip()
                if text:
                    gifts.append(text)
            except:
                continue

    except Exception as ex:
        print(f'❌ Ошибка в parse_gifts: {ex}')

    return list(set(gifts))



with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
                                args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context(storage_state="session.json" if os.path.exists("session.json") else None)
    page = context.new_page()

    page.goto("https://web.telegram.org/a/")

    if not os.path.exists("session.json"):
        input("👉 Войди в Telegram вручную и нажми Enter.")
        context.storage_state(path="session.json")

    while True:
        try:
            # 👉 Эмуляция нажатий: допустим, надо нажать на меню подарков
            # page.click("text=Подарки") — по кнопке/иконке с надписью

            time.sleep(3)  # дать время UI

            current_gifts = parse_gifts(page)
            old_gifts = load_gifts()

            new = list(set(current_gifts) - set(old_gifts))
            if new:
                print("🎁 Новые подарки:")
                print(new)
                # Тут можно requests.post в твоего бота

                save_gifts(current_gifts)

            time.sleep(30)
        except Exception as e:
            print("⚠️ Ошибка:", e)
            time.sleep(10)

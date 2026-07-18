import re
import time
import io
import telebot
import requests
from datetime import datetime
from telebot import types

# Инициализируем бота вашим токеном
BOT_TOKEN = "8758245055:AAExzVD2dxpl6Iv7PGCAMMKaPqmw9Pq1Szo"
bot = telebot.TeleBot(BOT_TOKEN)

# Константы владельца и канала для ОП
OWNER_ID = 5277564584
CHANNEL_CHAT_ID = -1004447049309
CHANNEL_LINK = "https://t.me/+7DX76Z1638lmNmIy"

# Константы для API
DEP_SEARCH_TOKEN = "x5OeEQZZbaRv7wljkHXuETQ7JByEznlY"
DEP_SEARCH_BASE_URL = "https://api.depsearch.sbs"

CHAMPION_API_URL = "https://champion-paternal-reawake.ngrok-free.dev/search"
CHAMPION_KEY = "scanly-685511ebc05a255ed16b493ac25e46b7"

# Константы для TG_OSINT_TOOL (NFT Истории)
NFT_API_TOKEN = "76:fBn742F2bJNyb6wW6jatmrZ3NVkogjjO"
NFT_BASE_URL = "https://kartoshka.free/v1"
NFT_HEADERS = {"Authorization": f"Bearer {NFT_API_TOKEN}"}

# Ссылки на изображения для разделов
PHOTO_PROFILE = "https://i.ibb.co/ccdr5Mbs/file-00000000ad6c720abf68a915bdf61af1.png"
PHOTO_SUBSCRIBE = "https://i.ibb.co/JwZQmM5C/file-000000008e0871f4a0454dac43808eb0.png"
PHOTO_PAYMENT = "https://i.ibb.co/v4dVYYdg/file-00000000bbd071f48fbabb096abb5f32.png"
PHOTO_API = "https://i.ibb.co/b54BV2ch/file-000000004980720aa3e32bd48791e78a.png"
PHOTO_PARTNER = "https://i.ibb.co/WvN4j8Sf/file-000000001ef0820a8163eee47cb0f44a.png"
PHOTO_PROMO = "https://i.ibb.co/RGK9k2M0/file-000000007d94820a807d7e4eaa76cbec.png"

# Временная база данных пользователей в оперативной памяти
USER_DATA = {}
# База промокодов
PROMO_CODES = {}

def register_user_if_not_exists(user_id, referrer_id=None):
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "id": user_id,
            "subscription": "Free (0Р)",
            "requests_left": 0,
            "reg_date": datetime.now().strftime("%d.%m.%Y"),
            "is_banned": False,
            "referrer": referrer_id,
            "referrals_count": 0,
            "referrals_rewarded": 0
        }
        if referrer_id and referrer_id in USER_DATA:
            USER_DATA[referrer_id]["referrals_count"] += 1
            total_triplets = USER_DATA[referrer_id]["referrals_count"] // 3
            if total_triplets > USER_DATA[referrer_id]["referrals_rewarded"]:
                diff = total_triplets - USER_DATA[referrer_id]["referrals_rewarded"]
                USER_DATA[referrer_id]["requests_left"] += diff * 3
                USER_DATA[referrer_id]["referrals_rewarded"] = total_triplets
                try:
                    bot.send_message(referrer_id, f"Вы пригласили еще 3 пользователей. Вам начислено 3 поиска.")
                except:
                    pass

def check_subscription(user_id):
    if user_id == OWNER_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_CHAT_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return True

def get_sub_check_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_link = types.InlineKeyboardButton("Подписаться", url=CHANNEL_LINK)
    btn_check = types.InlineKeyboardButton("Проверить", callback_data="check_sub_status")
    markup.add(btn_link)
    markup.add(btn_check)
    return markup

def get_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_profile = types.InlineKeyboardButton("Профиль", callback_data="menu_profile")
    btn_partner = types.InlineKeyboardButton("Партнерская программа", callback_data="menu_partner")
    markup.add(btn_profile)
    markup.add(btn_partner)
    return markup

def get_profile_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_subscribe = types.InlineKeyboardButton(" Оформить подписку", callback_data="menu_subscribe")
    btn_api = types.InlineKeyboardButton(" API", callback_data="menu_api")
    btn_promo = types.InlineKeyboardButton("Активировать промокод", callback_data="profile_activate_promo")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_main")
    markup.add(btn_subscribe, btn_api)
    markup.add(btn_promo)
    markup.add(btn_back)
    return markup

def get_subscribe_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_sub_30 = types.InlineKeyboardButton("30 Дней – 1150₽ – 50 шт. в день", callback_data="sub_tar_30")
    btn_dummy = types.InlineKeyboardButton("— Дополнительные запросы —", callback_data="dummy")
    btn_pack1 = types.InlineKeyboardButton("15 – 99₽", callback_data="sub_pack_15")
    btn_pack2 = types.InlineKeyboardButton("50 – 249₽", callback_data="sub_pack_50")
    btn_pack3 = types.InlineKeyboardButton("120 – 299₽", callback_data="sub_pack_120")
    btn_pack4 = types.InlineKeyboardButton("120 – 499₽", callback_data="sub_pack_120_premium")
    btn_pack5 = types.InlineKeyboardButton("500 – 1599₽", callback_data="sub_pack_500")
    btn_support = types.InlineKeyboardButton(" Тех. поддержка", url="https://t.me/ScanlySuppbot")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile")
    markup.add(btn_sub_30)
    markup.add(btn_dummy)
    markup.add(btn_pack1, btn_pack2)
    markup.add(btn_pack3, btn_pack4)
    markup.add(btn_pack5)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup

def get_sub_pay_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_xrocket = types.InlineKeyboardButton("Xrocket", callback_data="buy_sub_xrocket")
    btn_cryptobot = types.InlineKeyboardButton("CryptoBot", callback_data="buy_sub_cryptobot")
    btn_sbp = types.InlineKeyboardButton("СПБ банковская карта", callback_data="buy_sub_sbp")
    btn_support = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/ScanlySuppbot")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_subscribe")
    markup.row(btn_xrocket, btn_cryptobot)
    markup.add(btn_sbp)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup

def get_api_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_basic = types.InlineKeyboardButton("Basic – $5 –\n150 запросов в день.", callback_data="api_tar_basic")
    btn_premium = types.InlineKeyboardButton("Premium – $10 –\n500 запросов в день.", callback_data="api_tar_premium")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile")
    markup.add(btn_basic)
    markup.add(btn_premium)
    markup.add(btn_back)
    return markup

def get_api_pay_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_xrocket = types.InlineKeyboardButton("Xrocket", callback_data="buy_api_xrocket")
    btn_cryptobot = types.InlineKeyboardButton("CryptoBot", callback_data="buy_api_cryptobot")
    btn_sbp = types.InlineKeyboardButton("СПБ банковская карта", callback_data="buy_api_sbp")
    btn_support = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/ScanlySuppbot")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_api")
    markup.row(btn_xrocket, btn_cryptobot)
    markup.add(btn_sbp)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup

def get_admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_ban = types.InlineKeyboardButton("Бан пользователя", callback_data="admin_ban")
    btn_unban = types.InlineKeyboardButton("Разбан пользователя", callback_data="admin_unban")
    btn_broadcast = types.InlineKeyboardButton("Рассылка", callback_data="admin_broadcast")
    btn_stats = types.InlineKeyboardButton("Статистика", callback_data="admin_stats")
    btn_give_req = types.InlineKeyboardButton("Выдача запросов", callback_data="admin_give_req")
    btn_give_sub = types.InlineKeyboardButton("Выдача подписки", callback_data="admin_give_sub")
    btn_create_promo = types.InlineKeyboardButton("Создать промокод", callback_data="admin_create_promo")
    markup.add(btn_ban, btn_unban)
    markup.add(btn_broadcast, btn_stats)
    markup.add(btn_give_req, btn_give_sub)
    markup.add(btn_create_promo)
    return markup

WELCOME_TEXT = """«Scanly» - пришлите запрос в следующем формате

👤 Поиск по имени
└ Ильин Максим Сергеевич 12.04.1996

🌐 Социальные сети
├ @scanly – Телеграм
├ vk.com/@scanly – Вконтакте
├ ok.ru/profile/999 – Однокласн.
├ tiktok.com/@scanly – TikTok
└ instagram.com/scanly – Instagram

🗂 Документы
├ /vu 01234 – водительские права
├ /passport 0123 – номер паспорта
├ /snils 12345678901 – СНИЛС
└ /inn 123456789012 – ИНН

🚘 Поиск по авто
├ H777OH777 – номер автомобиля
└ XTA21150053965897 – VIN

🏠 Недвижимость
├ /adr Москва, Тверская,д1,кв1
└ 77:01:0001075:1361 – кадастровый номер

📞 +79991099999 – номер телефона
📧 @scanly, 1234567890 – Telegram
📪 tema@gmail.com – Email"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    payload = message.text.split()
    referrer_id = None
    if len(payload) > 1 and payload[1].isdigit():
        referrer_id = int(payload[1])
        if referrer_id == message.from_user.id:
            referrer_id = None

    register_user_if_not_exists(message.from_user.id, referrer_id)
    
    if USER_DATA[message.from_user.id]["is_banned"]:
        bot.reply_to(message, "Вы заблокированы в боте.")
        return

    # Изменено: если нет подписки, выводим строго "Обязательная подписка!"
    if not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "Обязательная подписка!", reply_markup=get_sub_check_keyboard())
        return

    bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard(), disable_web_page_preview=True)

@bot.message_handler(commands=['admin'])
def open_admin_panel(message):
    if message.from_user.id != OWNER_ID:
        return
    bot.send_message(message.chat.id, "Панель администратора владельца:", reply_markup=get_admin_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    register_user_if_not_exists(user_id)
    
    if USER_DATA[user_id]["is_banned"]:
        bot.answer_callback_query(call.id, text="Вы заблокированы.", show_alert=True)
        return

    if call.data == "check_sub_status":
        if check_subscription(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, WELCOME_TEXT, reply_markup=get_main_keyboard(), disable_web_page_preview=True)
        else:
            bot.answer_callback_query(call.id, text="Вы все еще не подписались на канал.", show_alert=True)
        return

    if not check_subscription(user_id):
        bot.answer_callback_query(call.id, text="Необходима обязательная подписка на канал.", show_alert=True)
        return

    user_info = USER_DATA[user_id]

    if call.data == "menu_main":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(chat_id=call.message.chat.id, text=WELCOME_TEXT, reply_markup=get_main_keyboard(), disable_web_page_preview=True)
    
    elif call.data == "menu_profile":
        # Изменено: убран текст "Профиль" сверху
        profile_text = f"<b>ID:</b> <code>{user_info['id']}</code>\n<b>Подписка:</b> <code>{user_info['subscription']}</code>\n<b>Доступно запросов:</b> <code>{user_info['requests_left']}</code>\n<b>Дата регистрации:</b> <code>{user_info['reg_date']}</code>"
        if call.message.content_type != 'photo':
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_photo(chat_id=call.message.chat.id, photo=PHOTO_PROFILE, caption=profile_text, reply_markup=get_profile_keyboard(), parse_mode="HTML")
        else:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_PROFILE, caption=profile_text, parse_mode="HTML"), reply_markup=get_profile_keyboard())

    elif call.data == "menu_partner":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        
        partner_text = (
            f"<b>– Приглашайте друзей и получайте дополнительные поиски.</b>\n\n"
            f"<b>– За каждых 3 приглашенных пользователей вам будет выдаваться 3 поиска.</b>\n\n"
            f"<b>Ваша реферальная ссылка:</b> <code>{ref_link}</code>\n\n"
            f"<b>Количество приглашений:</b> <code>{user_info['referrals_count']}</code>"
        )
        
        if call.message.content_type != 'photo':
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_photo(chat_id=call.message.chat.id, photo=PHOTO_PARTNER, caption=partner_text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_main")), parse_mode="HTML")
        else:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_PARTNER, caption=partner_text, parse_mode="HTML"), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_main")))

    elif call.data == "profile_activate_promo":
        back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile"))
        try:
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(PHOTO_PROMO, caption="Введите промокод для активации:"),
                reply_markup=back_markup
            )
            bot.register_next_step_handler(call.message, process_promo_activation)
        except Exception:
            msg = bot.send_photo(call.message.chat.id, photo=PHOTO_PROMO, caption="Введите промокод для активации:", reply_markup=back_markup)
            bot.register_next_step_handler(msg, process_promo_activation)

    elif call.data == "menu_api":
        api_text = "<b>Выберите интересующий тарифный план API для подключения:</b>"
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_API, caption=api_text, parse_mode="HTML"), reply_markup=get_api_keyboard())

    elif call.data in ["api_tar_basic", "api_tar_premium"]:
        pay_text = "Способ оплаты"
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_PAYMENT, caption=pay_text), reply_markup=get_api_pay_keyboard())

    elif call.data == "menu_subscribe":
        sub_text = "<b>— С активной подпиской бот возвращает полные результаты поиска, включая все найденные совпадения и связанные данные.\n\n— Дополнительные запросы не сгорают и не тратятся после дневного лимита.</b>"
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_SUBSCRIBE, caption=sub_text, parse_mode="HTML"), reply_markup=get_subscribe_keyboard())

    elif call.data == "sub_tar_30" or call.data.startswith("sub_pack_"):
        pay_text = "Способ оплаты"
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_PAYMENT, caption=pay_text), reply_markup=get_sub_pay_keyboard())

    elif call.data in ["buy_sub_xrocket", "buy_sub_cryptobot", "buy_sub_sbp", "buy_api_xrocket", "buy_api_cryptobot", "buy_api_sbp"]:
        bot.answer_callback_query(call.id, text="@y3Huk_iphone", show_alert=True)

    elif call.data == "dummy":
        bot.answer_callback_query(call.id, text="")

    elif call.data.startswith("admin_"):
        if user_id != OWNER_ID: return
        action = call.data.split("_")[1]
        if action == "stats":
            total_users = len(USER_DATA)
            banned_users = sum(1 for u in USER_DATA.values() if u.get("is_banned"))
            active_subs = sum(1 for u in USER_DATA.values() if u.get("subscription") != "Free (0Р)")
            bot.answer_callback_query(call.id, text=f"Всего: {total_users}\nБаны: {banned_users}\nПодписки: {active_subs}", show_alert=True)
        else:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            if call.data == "admin_ban":
                msg = bot.send_message(call.message.chat.id, "Введите Telegram ID пользователя для блокировки:")
                bot.register_next_step_handler(msg, process_admin_ban)
            elif call.data == "admin_unban":
                msg = bot.send_message(call.message.chat.id, "Введите Telegram ID пользователя для разблокировки:")
                bot.register_next_step_handler(msg, process_admin_unban)
            elif call.data == "admin_broadcast":
                msg = bot.send_message(call.message.chat.id, "Введите текст рассылки для всех пользователей:")
                bot.register_next_step_handler(msg, process_admin_broadcast)
            elif call.data == "admin_give_req":
                msg = bot.send_message(call.message.chat.id, "Введите ID и количество запросов через пробел:")
                bot.register_next_step_handler(msg, process_admin_give_req)
            elif call.data == "admin_give_sub":
                msg = bot.send_message(call.message.chat.id, "Введите ID и название подписки через пробел:")
                bot.register_next_step_handler(msg, process_admin_give_sub)
            elif call.data == "admin_create_promo":
                msg = bot.send_message(call.message.chat.id, "Введите через пробел: промокод, активации, запросы:")
                bot.register_next_step_handler(msg, process_admin_create_promo)

def process_promo_activation(message):
    user_id = message.from_user.id
    code = message.text.strip()
    back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile"))
    
    if code in PROMO_CODES and PROMO_CODES[code]["uses"] > 0:
        PROMO_CODES[code]["uses"] -= 1
        USER_DATA[user_id]["requests_left"] += PROMO_CODES[code]["requests"]
        bot.send_message(message.chat.id, f"Промокод успешно активирован. Добавлено запросов: {PROMO_CODES[code]['requests']}", reply_markup=back_markup)
        if PROMO_CODES[code]["uses"] <= 0:
            del PROMO_CODES[code]
    else:
        bot.send_message(message.chat.id, "Промокод не существует, либо закончились его активации.", reply_markup=back_markup)

def process_admin_ban(message):
    try:
        target_id = int(message.text.strip())
        register_user_if_not_exists(target_id)
        USER_DATA[target_id]["is_banned"] = True
        bot.send_message(message.chat.id, f"Пользователь {target_id} заблокирован.")
    except: bot.send_message(message.chat.id, "Ошибка ввода.")

def process_admin_unban(message):
    try:
        target_id = int(message.text.strip())
        register_user_if_not_exists(target_id)
        USER_DATA[target_id]["is_banned"] = False
        bot.send_message(message.chat.id, f"Пользователь {target_id} разблокирован.")
    except: bot.send_message(message.chat.id, "Ошибка ввода.")

def process_admin_broadcast(message):
    text = message.text
    count = 0
    for uid in list(USER_DATA.keys()):
        try:
            bot.send_message(uid, text)
            count += 1
        except: pass
    bot.send_message(message.chat.id, f"Рассылка завершена ({count}).")

def process_admin_give_req(message):
    try:
        parts = message.text.split()
        target_id, reqs = int(parts[0]), int(parts[1])
        register_user_if_not_exists(target_id)
        USER_DATA[target_id]["requests_left"] += reqs
        bot.send_message(message.chat.id, f"Пользователю {target_id} выдано {reqs} запросов.")
    except: bot.send_message(message.chat.id, "Ошибка формата.")

def process_admin_give_sub(message):
    try:
        parts = message.text.split(maxsplit=1)
        target_id, sub_name = int(parts[0]), parts[1].strip()
        register_user_if_not_exists(target_id)
        USER_DATA[target_id]["subscription"] = sub_name
        bot.send_message(message.chat.id, f"Пользователю {target_id} выдана подписка: {sub_name}")
    except: bot.send_message(message.chat.id, "Ошибка формата.")

def process_admin_create_promo(message):
    try:
        parts = message.text.split()
        code, uses, reqs = parts[0].strip(), int(parts[1]), int(parts[2])
        PROMO_CODES[code] = {"uses": uses, "requests": reqs}
        bot.send_message(message.chat.id, f"Создан промокод {code} ({uses} акт., по {reqs} запр.).")
    except: bot.send_message(message.chat.id, "Ошибка формата.")

def status_animation(chat_id):
    msg = bot.send_message(chat_id, "Проверяем базы")
    time.sleep(1.0)
    try: bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="Сверяем данные")
    except: pass
    return msg

def finish_status_animation(chat_id, msg_id):
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="Готово")
        time.sleep(0.4)
        bot.delete_message(chat_id, msg_id)
    except: pass

def get_nft_osint_text(query):
    try:
        res = requests.get(f"{NFT_BASE_URL}/owners/search", headers=NFT_HEADERS, params={"q": query, "limit": 1}, timeout=10)
        if res.status_code != 200 or not res.json().get("ok"): return "История: Владелец не найден.\n"
        items = res.json().get("result", {}).get("items", [])
        if not items: return "История: Не найден в базе.\n"
        
        owner = items[0].get("owner", {})
        ref = owner.get("username") or owner.get("telegramId") or owner.get("seeId")
        
        report = "--- ИСТОРИЯ ЦИФРОВЫХ АКТИВОВ ---\n"
        report += f"Username: @{owner.get('username', 'Нет')}\nID: {owner.get('telegramId', 'Нет')}\nИмя: {owner.get('name', 'Нет')}\n\n"
        
        history_res = requests.get(f"{NFT_BASE_URL}/owner/{ref}/history", headers=NFT_HEADERS, params={"limit": 100}, timeout=10)
        if history_res.status_code == 200 and history_res.json().get("ok"):
            all_items = history_res.json().get("result", {}).get("items", [])
            transfers = [i for i in all_items if i.get("kind") == "GIFT" and i.get("giftAction", {}).get("action") == "transfer"]
            transfers.sort(key=lambda x: x.get("time", ""), reverse=True)
            
            if transfers:
                report += "[Переводы предметов]:\n"
                for idx, item in enumerate(transfers[:10], 1):
                    ga = item.get("giftAction", {})
                    gift = ga.get("gift", {})
                    sender = ga.get("from", {}).get("username") or ga.get("from", {}).get("telegramId") or "Скрыт"
                    receiver = ga.get("to", {}).get("username") or ga.get("to", {}).get("telegramId") or "Скрыт"
                    report += f"{idx}. {gift.get('slug')} #{gift.get('num')} | От: {sender} -> Кому: {receiver} ({item.get('time','')})\n"
                report += "\n"
            
            name_events = [i for i in all_items if i.get("kind") != "GIFT"]
            if name_events:
                report += "[История изменений аккаунта]:\n"
                for item in name_events[:10]:
                    report += f"- {item.get('time', '')[:10]}: {item.get('usernames', item.get('username'))}\n"
        return report
    except Exception as e:
        return f"Ошибка загрузки истории: {str(e)}\n"

def send_txt_report(message, filename_part, content):
    file_buffer = io.BytesIO(content.encode('utf-8'))
    file_buffer.name = f"report_{filename_part}.txt"
    bot.send_document(message.chat.id, file_buffer, caption="Полный отчет сформирован в формате .txt")

@bot.message_handler(commands=['snils', 'inn', 'adr', 'vu', 'passport'])
def handle_commands(message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id)
    if USER_DATA[user_id]["is_banned"]: return
    
    # Изменено: если нет подписки, отправляем сообщение "Обязательная подписка!" и блокируем выполнение
    if not check_subscription(user_id): 
        bot.send_message(message.chat.id, "Обязательная подписка!", reply_markup=get_sub_check_keyboard())
        return

    if user_id != OWNER_ID and USER_DATA[user_id]["requests_left"] <= 0:
        bot.reply_to(message, "У вас закончились доступные запросы. Перейдите в Профиль, чтобы пополнить баланс или активировать промокод.", reply_markup=get_main_keyboard())
        return

    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "Пожалуйста, укажите значение после команды.")
        return
    
    if user_id != OWNER_ID:
        USER_DATA[user_id]["requests_left"] -= 1

    cmd, value = command[0].lower(), command[1].strip()
    if cmd == '/snils': query = f"snils{re.sub(r'\D', '', value)}"
    elif cmd == '/inn': query = f"inn{re.sub(r'\D', '', value)}"
    elif cmd == '/adr': query = f"addr:{value}"
    else: query = value

    send_to_depsearch(message, query)

@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id)
    if USER_DATA[user_id]["is_banned"]: return
    
    # Изменено: если нет подписки, отправляем "Обязательная подписка!"
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "Обязательная подписка!", reply_markup=get_sub_check_keyboard())
        return

    if user_id != OWNER_ID and USER_DATA[user_id]["requests_left"] <= 0:
        bot.send_message(message.chat.id, "У вас закончились доступные запросы. Перейдите в Профиль, чтобы пополнить баланс или активировать промокод.", reply_markup=get_main_keyboard())
        return

    text = message.text.strip()
    is_telegram = text.startswith('@') or (text.isdigit() and 5 <= len(text) <= 15)
    
    clean_phone = re.sub(r'[^\d+]', '', text)
    is_phone = (clean_phone.startswith('+') and clean_phone[1:].isdigit() and len(clean_phone) >= 11) or \
               ((clean_phone.startswith('7') or clean_phone.startswith('8')) and len(clean_phone) == 11)

    if user_id != OWNER_ID:
        USER_DATA[user_id]["requests_left"] -= 1

    # 1. ОБРАБОТКА НОМЕРА ТЕЛЕФОНА
    if is_phone:
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'upload_document')
        full_report = f"--- ОТЧЕТ ПОИСКА НОМЕРА ТЕЛЕФОНА ({clean_phone}) ---\n\n"
        
        try:
            res = requests.get(f"{CHAMPION_API_URL}?key={CHAMPION_KEY}&q={clean_phone}", timeout=15)
            if res.status_code == 200 and res.json().get('status') == 'success':
                c_data = res.json().get('data', {})
                full_report += "[Основная информация]:\n"
                full_report += f"ID: {c_data.get('id', '—')}\nUsername: {c_data.get('username', '—')}\n"
                full_report += "Найденные контакты:\n" + "\n".join([f"- {n}" for n in c_data.get('phonebook', [])]) + "\n\n"
        except Exception as e: full_report += f"[Ошибка поиска]: {str(e)}\n\n"

        try:
            res = requests.get(f"{DEP_SEARCH_BASE_URL}/quest={clean_phone}&token={DEP_SEARCH_TOKEN}&lang=ru", timeout=15)
            if res.status_code == 200:
                d_data = res.json()
                full_report += "[Данные по оператору связи]:\n"
                if "phone_info" in d_data:
                    full_report += f"Оператор: {d_data['phone_info'].get('operator')}\nРегион: {d_data['phone_info'].get('region')}\n"
                for idx, r_item in enumerate(d_data.get("results", []), 1):
                    full_report += f"Совпадение {idx}:\n" + "\n".join([f"  {k}: {v}" for k, v in r_item.items()]) + "\n"
        except Exception as e: full_report += f"[Ошибка поиска по базам]: {str(e)}\n\n"

        finish_status_animation(message.chat.id, status_msg.message_id)
        send_txt_report(message, clean_phone.replace("+", ""), full_report)

    # 2. ОБРАБОТКА TELEGRAM
    elif is_telegram:
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'upload_document')
        full_report = f"--- ОТЧЕТ ПОИСКА TELEGRAM ({text}) ---\n\n"
        
        try:
            res = requests.get(f"{CHAMPION_API_URL}?key={CHAMPION_KEY}&q={text}", timeout=15)
            if res.status_code == 200 and res.json().get('status') == 'success':
                data = res.json().get('data', {})
                full_report += "[Результаты поиска]:\n"
                full_report += f"ID: {data.get('id', '—')}\nUsername: {data.get('username', '—')}\n\n"
                full_report += "[Записи в телефонных книгах]:\n" + "\n".join([f"- {n}" for n in data.get('phonebook', [])]) + "\n\n"
                full_report += "[Связанные профили соц. сетей]:\n" + "\n".join([f"- {vk.get('name')}: {vk.get('url')}" for vk in data.get('vk', [])]) + "\n\n"
        except Exception as e: full_report += f"[Ошибка поиска]: {str(e)}\n\n"

        clean_ref = text.replace("@", "")
        full_report += get_nft_osint_text(clean_ref)

        finish_status_animation(message.chat.id, status_msg.message_id)
        send_txt_report(message, clean_ref, full_report)

    # 3. ВСЕ ОСТАЛЬНЫЕ ПРОБИВЫ
    else:
        send_to_depsearch(message, text)

def send_to_depsearch(message, query_string):
    status_msg = status_animation(message.chat.id)
    bot.send_chat_action(message.chat.id, 'upload_document')
    full_report = f"--- ОТЧЕТ ПОИСКА ({query_string}) ---\n\n"
    
    try:
        res = requests.get(f"{DEP_SEARCH_BASE_URL}/quest={query_string}&token={DEP_SEARCH_TOKEN}&lang=ru", timeout=15)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            if isinstance(results, list) and results:
                for idx, r_item in enumerate(results, 1):
                    full_report += f"Запись {idx}:\n" + "\n".join([f"  {k}: {v}" for k, v in r_item.items()]) + "\n\n"
            else:
                full_report += "Ничего не найдено."
        else:
            full_report += f"Ошибка внешнего сервиса: {res.status_code}"
    except Exception as e:
        full_report += f"Ошибка выполнения запроса: {str(e)}"

    finish_status_animation(message.chat.id, status_msg.message_id)
    send_txt_report(message, "search", full_report)

if __name__ == "__main__":
    bot.infinity_polling()


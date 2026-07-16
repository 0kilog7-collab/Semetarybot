import re
import threading
import time
from collections import defaultdict
import requests
import telebot
from telebot import types

BOT_TOKEN = "8879403899:AAEX9gDWXfZ37vAPpFnIJU7oXZZ801_Db78"
API_KEY = "scanly-e7a8c88a24d7509f14684d02f2a2922b"  

ADMIN_LIST = [5277564584]
REQUIRED_CHANNEL_ID = -1004447049309
CHANNEL_LINK = "https://t.me/+7DX76Z1638lmNmIy"

bot = telebot.TeleBot(BOT_TOKEN)

user_limits = defaultdict(list)
user_cooldowns = defaultdict(float)

search_counters = defaultdict(int)

user_subscriptions = {}

admin_states = {}

search_lock = threading.Lock()


def check_subscription(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception:
        return False


def get_sub_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Подписаться", url=CHANNEL_LINK))
    kb.add(types.InlineKeyboardButton(text="Проверить", callback_data="check_subscription"))
    return kb


def get_main_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="how to search?", callback_data="how_to"))
    kb.add(
        types.InlineKeyboardButton(text="Profile", callback_data="profile"),
        types.InlineKeyboardButton(text="subscription", callback_data="sub"),
    )
    return kb


def get_back_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Back", callback_data="back_to_main"))
    return kb


def get_profile_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="API", callback_data="api_info"))
    kb.add(types.InlineKeyboardButton(text="Back", callback_data="back_to_main"))
    return kb


def get_admin_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Выдать подписку", callback_data="give_sub"))
    kb.add(types.InlineKeyboardButton(text="Закрыть панель", callback_data="close_admin"))
    return kb


@bot.message_handler(commands=["start"])
def start_cmd(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="Обязательно подпишитесь",
            reply_markup=get_sub_keyboard()
        )
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="Welcome to Scanly 🐙",
        reply_markup=get_main_keyboard(),
    )


@bot.message_handler(commands=["admin"])
def admin_cmd(message):
    if message.from_user.id not in ADMIN_LIST:
        return  

    if not check_subscription(message.from_user.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="Обязательно подпишитесь",
            reply_markup=get_sub_keyboard()
        )
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="⚙️ **Панель администратора**\n\nВыбери необходимое действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    if call.data == "check_subscription":
        if check_subscription(user_id):
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(
                chat_id=chat_id,
                text="Welcome to Scanly 🐙",
                reply_markup=get_main_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, text="Вы всё ещё не подписались!", show_alert=True)
        return

    if not check_subscription(user_id):
        bot.edit_message_text(
            text="Обязательно подпишитесь",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_sub_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if call.data == "how_to":
        text = "Telegram \nSend me the @username \n\nNumber \nSend me 79998882211"
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_back_keyboard(),
        )
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        bot.edit_message_text(
            text="Welcome to Scanly 🐙",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_main_keyboard(),
        )
        bot.answer_callback_query(call.id)

    elif call.data == "profile":
        sub_time = user_subscriptions.get(user_id, 0)
        now = time.time()
        
        if user_id in ADMIN_LIST:
            sub_status = "Администратор (Безлимит)"
        elif sub_time > now:
            expire_date = time.strftime("%d.%m.%Y", time.localtime(sub_time))
            sub_status = f"Активна (до {expire_date})"
        else:
            sub_status = "Отсутствует"

        profile_text = (
            f"Вы: {user_id}\n"
            f"Подписка - {sub_status}"
        )
        
        bot.edit_message_text(
            text=profile_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_profile_keyboard()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "api_info":
        api_text = (
            "Пакет за $5 включает:\n"
            "<blockquote>500 запросов;\n"
            "🔹 Полный доступ к базе телефонных книг и соцсетей.</blockquote>\n\n"
            "<b>Приобрести - @y3Huk_iphone</b>"
        )
        bot.edit_message_text(
            text=api_text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "sub":
        sub_time = user_subscriptions.get(user_id, 0)
        now = time.time()
        
        if user_id in ADMIN_LIST:
            sub_status = "Администратор (Безлимит)"
            limit_text = "У вас активирован бесконечный доступ разработчика."
        else:
            if sub_time > now:
                sub_status = "Активна"
            else:
                sub_status = "Отсутствует"

            searches = user_limits[user_id]
            if searches:
                oldest_search = searches[0]
                time_passed = now - oldest_search
                time_left = 86400 - time_passed
                if time_left > 0:
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    limit_text = f"Ваш ежедневный лимит обновится через {hours} ч. {minutes} мин."
                else:
                    limit_text = "Ваш ежедневный лимит полностью доступен."
            else:
                limit_text = "Ваш ежедневный лимит полностью доступен."

        sub_text = (
            f"Subscribe - {sub_status}\n\n"
            f"{limit_text}\n\n"
            f"Купить подписку можно у @y3Huk_iphone"
        )

        bot.edit_message_text(
            text=sub_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_back_keyboard()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "give_sub":
        if user_id not in ADMIN_LIST:
            bot.answer_callback_query(call.id, "У вас нет прав!", show_alert=True)
            return
        
        admin_states[user_id] = "waiting_for_sub_data"
        bot.edit_message_text(
            text="👤 Отправь мне **Telegram ID** пользователя и **количество дней подписки** через пробел.\n\n*Пример:* `123456789 30`",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)

    elif call.data == "close_admin":
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.answer_callback_query(call.id)


def format_beautiful_response(raw_text: str, query: str) -> str:
    clean = raw_text.strip().lstrip(")]}'\n ").strip()

    id_match = re.search(r"id:\s*(\d+)", clean)
    username_match = re.search(r"username:\s*([^,\n]+)", clean)
    phonebook_match = re.search(r"phonebook:\s*\[?(.*?)(?:\]\s*,\s*vk:|\s*vk:|$)", clean)
    vk_match = re.search(r"vk:\s*\[?name:\s*\[?([^,\n\]]+).*?url:\s*([^,\n\]]+)", clean)

    response_lines = []
    response_lines.append("Search Result:")
    response_lines.append("-" * 20)

    if id_match:
        response_lines.append(f"Telegram ID: {id_match.group(1).strip()}")
    if username_match:
        usr = username_match.group(1).strip().replace("[", "").replace("]", "")
        response_lines.append(f"Username: {usr}")

    if phonebook_match:
        names_raw = phonebook_match.group(1).split(",")
        phonebook_list = []
        for name in names_raw:
            name_clean = name.replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()
            if name_clean and name_clean.lower() != "not enought":
                phonebook_list.append(f"• {name_clean}")
        
        if phonebook_list:
            response_lines.append("\nPhonebook Names:")
            response_lines.extend(phonebook_list)

    if vk_match:
        vk_name = vk_match.group(1).strip().replace("[", "").replace("]", "")
        vk_url = vk_match.group(2).strip().replace("[", "").replace("]", "").replace(")", "")
        response_lines.append("\nSocial Networks:")
        response_lines.append(f"VK: {vk_name}")
        response_lines.append(f"Link: {vk_url}")

    if len(response_lines) <= 2:
        fallback = (
            clean.replace(")", "")
            .replace("]", "")
            .replace("[", "")
            .replace('"', "")
            .replace("{", "")
            .replace("}", "")
            .replace("status: success, data: ", "")
        )
        return fallback

    views = search_counters[query]
    response_lines.append("-" * 20)
    response_lines.append(f"Интересовались: ({views})")

    return "\n".join(response_lines)


def check_limits(user_id: int) -> tuple[bool, str]:
    now = time.time()
    
    if user_id in ADMIN_LIST:
        return True, ""

    sub_time = user_subscriptions.get(user_id, 0)
    if sub_time > now:
        return True, ""

    last_search = user_cooldowns[user_id]
    if now - last_search < 30:
        wait_time = int(30 - (now - last_search))
        return False, f"Cooldown active. Wait {wait_time} seconds."

    user_limits[user_id] = [t for t in user_limits[user_id] if now - t < 86400]
    if len(user_limits[user_id]) >= 2:
        return False, "Daily limit reached (2 searches per day)."

    return True, ""


def process_search_task(user_id: int, query: str, is_phone: bool, status_msg):
    with search_lock:
        try:
            search_counters[query] += 1

            time.sleep(1)
            bot.edit_message_text(
                text="Checking the base",
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
            )
            time.sleep(1)
            bot.edit_message_text(
                text="Done +",
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
            )
            time.sleep(0.5)

            url = f"https://champion-paternal-reawake.ngrok-free.dev/search?key={API_KEY}&q={query}"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                final_result = format_beautiful_response(response.text, query)
                
                now = time.time()
                if user_id not in ADMIN_LIST and user_subscriptions.get(user_id, 0) <= now:
                    user_limits[user_id].append(now)
                    user_cooldowns[user_id] = now
            else:
                final_result = f"API Error (Status: {response.status_code})"

            try:
                bot.delete_message(
                    chat_id=status_msg.chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass

            bot.send_message(chat_id=user_id, text=final_result)

        except Exception as e:
            try:
                bot.delete_message(
                    chat_id=status_msg.chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass
            bot.send_message(chat_id=user_id, text=f"Search failed. Error: {str(e)}")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not check_subscription(user_id):
        bot.send_message(
            chat_id=message.chat.id,
            text="Обязательно подпишитесь",
            reply_markup=get_sub_keyboard()
        )
        return

    if user_id in ADMIN_LIST and admin_states.get(user_id) == "waiting_for_sub_data":
        admin_states[user_id] = None
        
        try:
            parts = text.split()
            if len(parts) != 2:
                raise ValueError("Неверный формат. Нужно отправить ID и количество дней.")
            
            target_id = int(parts[0])
            days = int(parts[1])
            
            if days <= 0:
                raise ValueError("Количество дней должно быть больше нуля.")
            
            end_time = time.time() + (days * 86400)
            user_subscriptions[target_id] = end_time
            
            expire_date = time.strftime("%d.%m.%Y", time.localtime(end_time))
            
            bot.send_message(
                chat_id=message.chat.id,
                text=f" Подписка пользователю `{target_id}` успешно выдана на **{days} дн.** (до {expire_date})!",
                parse_mode="Markdown"
            )
            
            try:
                bot.send_message(
                    chat_id=target_id,
                    text=f"Вам выдана премиум-подписка на **{days} дн.** (до {expire_date})!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass 
                
        except ValueError as e:
            bot.send_message(
                chat_id=message.chat.id,
                text=f" Ошибка: {str(e)}\nПопробуй заново через команду /admin",
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Что-то пошло не так: {str(e)}\nПопробуй заново через команду /admin",
                parse_mode="Markdown"
            )
        return

    is_phone = False
    clean_query = ""

    if re.match(r"^\+?\d{7,15}$", text):
        is_phone = True
        clean_query = text.replace("+", "")
    elif text.startswith("@") and len(text) > 1:
        is_phone = False
        clean_query = text
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Invalid format. Use @username or phone number like 79998882211",
        )
        return

    allowed, alert_text = check_limits(user_id)
    if not allowed:
        bot.send_message(chat_id=message.chat.id, text=alert_text)
        return

    status_msg = bot.send_message(chat_id=message.chat.id, text="looking for sources")

    threading.Thread(
        target=process_search_task,
        args=(user_id, clean_query, is_phone, status_msg),
        daemon=True,
    ).start()


if __name__ == "__main__":
    bot.infinity_polling()


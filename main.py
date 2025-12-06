import telebot # библиотека telebot
from config import token # импорт токена
import random, time
import pytz
from datetime import datetime, timedelta
from dblogic import InfoDB
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot(token) 

user_id_cache = {}

def gen_markup(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Вода 💧", callback_data=f'water_{id}'),
               InlineKeyboardButton("Печеньки 🍪", callback_data=f'cookies_{id}'))
    return markup

def back_markup(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вернуться 💬", callback_data=f'back_{id}'))
    return markup

def menu_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("💧 Выпить воду", callback_data=f'drink_water_{user_id}'),
        InlineKeyboardButton("🍪 Съесть печеньку", callback_data=f'eat_cookie_{user_id}'),
        InlineKeyboardButton("🏆 Лидерборды", callback_data=f'show_leaderboards_{user_id}'),
        InlineKeyboardButton("📊 Полная статистика", callback_data=f'full_stats_{user_id}'),
        InlineKeyboardButton("🔄 Обновить", callback_data=f'refresh_menu_{user_id}')
    )
    return markup

def back_to_menu_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("↩️ Назад в меню", callback_data=f'refresh_menu_{user_id}'))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("water_"):
        message_id = int(call.data[6:])
        bot.send_chat_action(call.message.from_user.id, 'typing')
        leaderboard = manager.get_water_leaderboard()
        text = "".join([f"<b><code>{x[0]}</code>   |   @{x[1]}   |   {x[2]}</b> 💧\n" for x in leaderboard])
        bot.edit_message_text(f'<b>Таблица 10 активных пользователей. 🌊</b>' + f"<blockquote>{text}</blockquote>" + f'<b>Пейте больше воды, и вы окажетесь в этой таблице!</b> 😋', call.message.chat.id, message_id=message_id, reply_markup=back_markup(message_id), parse_mode = 'HTML')
    elif call.data.startswith("cookies_"):
        message_id = int(call.data[8:])
        bot.send_chat_action(call.message.from_user.id, 'typing')
        leaderboard = manager.get_cookies_leaderboard()
        text = "".join([f"<b><code>{x[0]}</code>   |   @{x[1]}   |   {x[2]}</b> 🍪\n" for x in leaderboard])
        bot.edit_message_text(f'<b>Таблица 10 активных пользователей. 🥛</b>' + f"<blockquote>{text}</blockquote>" + f'<b>Ешьте больше печенек, и вы окажетесь в этой таблице!</b> 🤠', call.message.chat.id, message_id=message_id, reply_markup=back_markup(message_id), parse_mode = 'HTML')
    

    elif call.data.startswith('drink_water_'):
        user_id = int(call.data[12:])
        if call.from_user.id == user_id:
            class FakeMessage:
                def __init__(self, chat_id, user_id, username, first_name):
                    self.chat = type('Chat', (), {'id': chat_id})()
                    self.from_user = type('User', (), {'id': user_id, 'username': username, 'first_name': first_name})()
            fake_msg = FakeMessage(call.message.chat.id, call.from_user.id, call.from_user.username, call.from_user.first_name)
            water(fake_msg)
            bot.answer_callback_query(call.id, "💧 Пьем воду...")
        else:
            bot.answer_callback_query(call.id, "📛 Это не ваша статистика...")
    
    elif call.data.startswith('eat_cookie_'):
        user_id = int(call.data[11:])
        if call.from_user.id == user_id:
            class FakeMessage:
                def __init__(self, chat_id, user_id, username, first_name):
                    self.chat = type('Chat', (), {'id': chat_id})()
                    self.from_user = type('User', (), {'id': user_id, 'username': username, 'first_name': first_name})()
            fake_msg = FakeMessage(call.message.chat.id, call.from_user.id, call.from_user.username, call.from_user.first_name)
            cookie(fake_msg)
            bot.answer_callback_query(call.id, "🍪 Съедаем печеньку...")
        else:
            bot.answer_callback_query(call.id, "📛 Это не ваша статистика...")
    
    elif call.data.startswith('show_leaderboards_'):
        user_id = int(call.data[18:])
        if call.from_user.id == user_id:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            class FakeMessage:
                def __init__(self, chat_id, user_id):
                    self.chat = type('Chat', (), {'id': chat_id})()
                    self.from_user = type('User', (), {'id': user_id})()
            
            fake_msg = FakeMessage(call.message.chat.id, call.from_user.id)
            leaderboard_handler(fake_msg)
        else:
            bot.answer_callback_query(call.id, "📛 Это не ваша статистика...")
    
    elif call.data.startswith('full_stats_'):
        user_id = int(call.data[11:])
        if call.from_user.id == user_id:
            try:
                water_total = manager.get_amount([(user_id)])[0]
                cookies_total = manager.get_amount([(user_id)])[1]
                last_water = manager.get_last_time_water([(user_id)])
                last_cookie = manager.get_last_time_cookie([(user_id)])
            except:
                water_total = 0
                cookies_total = 0
                last_water = "Неизвестно"
                last_cookie = "Неизвестно"
            
            full_stats_text = f"""
<b>📊 Полная статистика</b>

<blockquote>💧 Всего выпито воды: {water_total} л
🍪 Всего съедено печенек: {cookies_total} шт</blockquote>
<blockquote>💧 Последний раз пили воду: {last_water}
🍪 Последний раз ели печеньку: {last_cookie}</blockquote>

<b>ID пользователя:</b> <code>{user_id}</code>
        """
        
            bot.edit_message_text(
                full_stats_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=back_to_menu_markup(user_id)
            )
        else:
            bot.answer_callback_query(call.id, "📛 Это не ваша статистика...")

    
    elif call.data.startswith('refresh_menu_'):
        user_id = int(call.data[13:])
        if call.from_user.id == user_id:
            bot.answer_callback_query(call.id, "🔄 Меню обновлено!")
            bot.delete_message(call.message.chat.id, call.message.message_id)

            class FakeMessage:
                def __init__(self, chat_id, user_id, username, first_name):
                    self.chat = type('Chat', (), {'id': chat_id})()
                    self.from_user = type('User', (), {'id': user_id, 'username': username, 'first_name': first_name})()
            
            fake_msg = FakeMessage(call.message.chat.id, call.from_user.id, call.from_user.username, call.from_user.first_name)
            menu_handler(fake_msg)
        else:
            bot.answer_callback_query(call.id, "📛 Это не ваша статистика...")
    
    else:
        message_id = int(call.data[5:])
        bot.delete_message(call.message.chat.id, message_id)

        bot_message = bot.send_message(call.message.chat.id, f"<b>Переформулирую лидерборд...</b> ⏳", parse_mode = 'HTML')
        bot.send_chat_action(call.message.from_user.id, 'typing')
        message_id = bot_message.message_id
        time.sleep(2)
        bot.edit_message_text(f"<b>Выберите один из лидербордов.</b> 🧾", call.message.chat.id, message_id=message_id, reply_markup=gen_markup(message_id), parse_mode = 'HTML')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    if message.from_user.username == None and message.from_user.first_name == 'ㅤ':
        bot.reply_to(message, f"<b>Привет, @{message.from_user.id}! 👋\nЯ бот для развлечения! 🎉</b>", parse_mode = 'HTML')
    elif message.from_user.username == None:
        bot.reply_to(message, f"<b>Привет, {message.from_user.first_name}! 👋\nЯ бот для развлечения! 🎉</b>", parse_mode = 'HTML')
    else:
        bot.reply_to(message, f"<b>Привет, @{message.from_user.username}! 👋\nЯ бот для развлечения! 🎉</b>", parse_mode = 'HTML')


@bot.message_handler(commands=['menu', 'info', 'stats', 'status'])
def menu_handler(message):
    user_id = message.from_user.id
    now_time = datetime.now(pytz.timezone('Europe/Moscow')).replace(microsecond=0, tzinfo=None)

    bot.send_chat_action(message.chat.id, 'typing')
    if message.from_user.id not in manager.get_users():
        manager.registration(message.from_user.id, message.from_user.username, now_time) # Регистрация
    try:
        water_total = manager.get_amount([(user_id)])[0]
        cookies_total = manager.get_amount([(user_id)])[1]
    except:
        water_total = 0
        cookies_total = 0
    if message.from_user.username is None and message.from_user.first_name == 'ㅤ':
        username = f"<code>{message.from_user.id}</code>"
    elif message.from_user.username is None:
        username = message.from_user.first_name
    else:
        username = f"@{message.from_user.username}"
    
    menu_text = f"""
<b>🍪 Меню пользователя, {username}</b>

📊 <b>Ваша статистика:</b>
<blockquote>💧 Выпито воды: {water_total} л
🍪 Съедено печенек: {cookies_total} шт</blockquote>

<b>Выберите действие:</b>
    """
    bot.send_message(
        message.chat.id, 
        menu_text, 
        parse_mode='HTML',
        reply_markup=menu_markup(user_id)
    )

@bot.message_handler(commands=['ban'])
def ban_user(message):
    who_is_user = message.from_user.id
    chat_id = message.chat.id
    member_status = bot.get_chat_member(chat_id, who_is_user).status
    if member_status in ('administrator', 'creator') and message.chat.type != 'private':
        # Необходимые значения (Chat_id тоже)
        if message.from_user.username == None and message.from_user.first_name == 'ㅤ':
            admin = f'ID {message.from_user.id}'
        elif message.from_user.username == None:
            admin = f'@{message.from_user.first_name}'
        else:
            admin = f'@{message.from_user.username}'
        user_to_ban_id = None
        display_name = None
        reason = None

        # Ответ на сообщение пользователя
        if message.reply_to_message: # /ban <reason>
            user_to_ban_id = message.reply_to_message.from_user.id
            display_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
            if len(message.text.split()) > 1: # /ban <reason>
                reason = message.text.split(maxsplit=1)[1] 
            else:
                reason = '<b>Отсутсвует.</b>'
            
        # /ban <user> <reason>
        elif len(message.text.split()) > 1: # /ban <user>
            target_arg = message.text.split(maxsplit=2)[1]
            reason = '<b>Отсутсвует.</b>'
            if len(message.text.split()) > 2: # /ban <user> <reason>
                reason = message.text.split(maxsplit=2)[2]
            if target_arg.isdigit(): # Если это ID пользователя (Возвращает цифры)
                user_to_ban_id = int(target_arg)
                display_name = f"ID {user_to_ban_id}"
            elif target_arg.startswith('@'): # Если это Юзернейм
                target_username = target_arg[1:]
                if target_username in user_id_cache:
                    user_to_ban_id = user_id_cache[target_username] # Получаем ключ (ID) по юзернейму
                    display_name = f"@{target_username}"
                else:
                    bot.reply_to(message, "<b>Пользователь с таким юзернеймом не найден в моей памяти. Возможно, он еще не писал в чат. 🤔</b>", parse_mode = 'HTML')
                    return
            else: # Если это не ID и не Username
                bot.reply_to(message, "<b>Используйте /ban в ответ на сообщение, или /ban (User ID), или /ban @username. ⚙️</b>", parse_mode = 'HTML')
                return
        else: # /ban - без аргументов и без ответа на чьё-то сообщение
            bot.reply_to(message, "<b>Используйте /ban в ответ на сообщение, или /ban (User ID), или /ban @username. ⚙️</b>", parse_mode = 'HTML')
            return
        if user_to_ban_id is None: # Если юзер или ID отсутствует.
            bot.reply_to(message, "<b>Не удалось определить пользователя для бана. 🚫</b>", parse_mode = 'HTML')
            return
        if user_to_ban_id == bot.get_me().id: # Бот не может заблокировать себя
            bot.reply_to(message, "<b>Я не могу забанить себя. ⛔</b>", parse_mode = 'HTML')
            return
        try: # Процесс блокировки
            member_status = bot.get_chat_member(chat_id, user_to_ban_id).status
            if member_status in ('administrator', 'creator'):
                bot.reply_to(message, "<b>Не могу забанить администратора или создателя чата. 📛</b>", parse_mode = 'HTML')
                return
            bot.ban_chat_member(chat_id, user_to_ban_id)
            bot.reply_to(message, f"<b>|Пользователь {display_name} забанен. 📛\n|Администратор: {admin} ⚙️;\n|Причина блокировки: 💾</b>\n<blockquote>{reason}</blockquote>", parse_mode = 'HTML')
            if display_name and display_name.startswith('@') and display_name[1:] in user_id_cache:
                del user_id_cache[display_name[1:]]
        except Exception as e: # Ошибка с правами в группе
            bot.reply_to(message, f"<b>Ошибка при бане: {e}. Убедитесь, что я администратор с правом 'Банить пользователей'. ⚠️</b>", parse_mode = 'HTML')
    else:
        bot.reply_to(message, "<b>Простите, у вас нет прав администратора. 🚫</b>", parse_mode = 'HTML')

@bot.message_handler(commands=['commands', 'help'])
def help(message):
    if message.chat.type == 'private':
        bot.send_chat_action(message.from_user.id, 'typing')
        bot.send_message(message.chat.id, f"🧾 <b>Доступные команды для использования бота:</b>\n<blockquote>/start - запуск бота;\n/commands, /help - список доступных команд;\n/water - выпить стакан воды;\n/cookie - съесть печеньку;\n/leaderboard - показывает одних из лучших пользователей;\n/info, /stats, /status, /menu - статистика игрока.</blockquote>\n<b>⚙️ В будущем добавится больше функционала.</b>", parse_mode = 'HTML')

@bot.message_handler(commands=['leaderboard'])
def leaderboard_handler(message):
    bot_message = bot.send_message(message.chat.id, f"<b>Формулирую лидерборд...</b> ⏳", parse_mode = 'HTML')
    bot.send_chat_action(message.from_user.id, 'typing')
    message_id = bot_message.message_id
    time.sleep(2)
    bot.edit_message_text(f"<b>Выберите один из лидербордов.</b> 🧾", message.chat.id, message_id, reply_markup=gen_markup(message_id), parse_mode = 'HTML')

@bot.message_handler(commands=['water', 'drink'])
def water(message):
    bot.send_chat_action(message.from_user.id, 'typing')

    now_time = datetime.now(pytz.timezone('Europe/Moscow')).replace(microsecond=0, tzinfo=None)
    if message.from_user.id not in manager.get_users():
        manager.registration(message.from_user.id, message.from_user.username, now_time) # Регистрация
    get_time = manager.get_last_time_water([(message.from_user.id)]) # Получаем время из ДБ
    next_time = datetime.strptime(get_time, '%Y-%m-%d %H:%M:%S')

    if now_time < next_time:
        bot.send_message(message.chat.id, f'<b>Вы уже сегодня выпили воду. Попробуйте через {next_time-now_time}</b> 💢', parse_mode = 'HTML')
    else:
        try:
            next_time = now_time+timedelta(hours=12)
            manager.update_last_time_water(next_time, message.from_user.id) # Обновляем время

            water = random.uniform(2, 9)
            roundwater = round(water, 2)
            water = roundwater
            manager.update_water(message.from_user.id, water)

            # Украшение текста (Игнорируйте)
            if message.from_user.username == None and message.from_user.first_name == 'ㅤ':
                chat_id = f'<code>{message.from_user.id}</code>'
            elif message.from_user.username == None:
                chat_id = message.from_user.first_name
            else:
                chat_id = f'@{message.from_user.username}!'
            if water <= 3:
                extra_text = f'<b>Сегодня, вы выполнили дневную норму!</b> 😀'
            elif water <= 8 and water > 3:
                extra_text = f'<b>Сегодня, вы превзошли и разорвали дневную норму!</b> 🎉'
            else:
                extra_text = f'<b>Сегодня, вы выпили 8-9 литровку!</b> 🌊'
            text = f'{extra_text}\n<blockquote>        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b>\nСегодня пользователь, <b>{chat_id}</b> выпил <b>{water}л</b> 💧.\n        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b></blockquote>'

            bot.send_message(message.chat.id, text, parse_mode = 'HTML')
        except:
            bot.send_message(message.chat.id, 'Непредвиденная ошибка.', parse_mode = 'HTML')

@bot.message_handler(commands=['cookie', 'eat'])
def cookie(message):
    bot.send_chat_action(message.from_user.id, 'typing')

    now_time = datetime.now(pytz.timezone('Europe/Moscow')).replace(microsecond=0, tzinfo=None)
    if message.from_user.id not in manager.get_users():
        manager.registration(message.from_user.id, message.from_user.username, now_time) # Регистрация
    get_time = manager.get_last_time_cookie([(message.from_user.id)]) # Получаем время из ДБ
    next_time = datetime.strptime(get_time, '%Y-%m-%d %H:%M:%S')

    if now_time < next_time:
        bot.send_message(message.chat.id, f'<b>Вы уже сегодня съели печеньку. Попробуйте через {next_time-now_time}</b> 💢', parse_mode = 'HTML')
    else:
        try:
            next_time = now_time+timedelta(hours=12)
            manager.update_last_time_cookie(next_time, message.from_user.id) # Обновляем время

            cookie = random.uniform(-0.5, 6)
            roundcookie = round(cookie, 2)
            cookie = roundcookie
            manager.update_cookies(message.from_user.id, cookie)

            # Украшение текста (Игнорируйте)
            if message.from_user.username == None and message.from_user.first_name == 'ㅤ':
                chat_id = f'<code>{message.from_user.id}</code>'
            elif message.from_user.username == None:
                chat_id = message.from_user.first_name
            else:
                chat_id = f'@{message.from_user.username}!'
            if cookie <= 0:
                extra_text = f'<b>Сегодня, мышь украла вашу ежедневную печеньку!</b> 🐭'
                words = ['потерял', 'не нашёл', 'уронил']
                action = random.choice(words)
            elif cookie <= 4 and cookie > 0:
                extra_text = f'<b>Сегодня, вы скушали мягкую печеньку!</b> 🍪'
                words = ['съел', 'проглотил', 'скушал']
                action = random.choice(words)
            else:
                extra_text = f'<b>Сегодня, вы едите печеньку, макая её в молоко!</b> 🥛'
                words = ['съел', 'проглотил', 'скушал']
                action = random.choice(words)
            text = f'{extra_text}\n<blockquote>        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b>\nСегодня пользователь, <b>{chat_id}</b> {action} <b>{cookie} кг</b> 🍪.\n        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b></blockquote>'

            bot.send_message(message.chat.id, text, parse_mode = 'HTML')
        except:
            bot.send_message(message.chat.id, 'Непредвиденная ошибка.', parse_mode = 'HTML')

@bot.message_handler(func=lambda message: True)
def handler_messages(message):
    user_id_cache[message.from_user.username] = message.from_user.id
    if message.text == bot.get_me().username or message.text == f'@{bot.get_me().username}':
        bot.reply_to(message, f'<b>Так точно, бот в сети! 🫡</b>', parse_mode = 'HTML')
    elif "https://" in message.text and message.chat.type != 'private':
        member_status = bot.get_chat_member(message.chat.id, message.from_user.id).status
        if member_status in ('administrator', 'creator'):
            bot.reply_to(message, "<b>Не могу забанить администратора или создателя чата. 📛</b>\n<blockquote>Будьте осторожны с незнакомыми ссылками.</blockquote>", parse_mode = 'HTML')
            return
        else:
            chat_id = message.chat.id
            user = message.from_user
            user_id = user.id
            username = user.username or f"{user.first_name} {user.last_name or ''}".strip()
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{username} был забанен.")

if __name__ == '__main__':
    manager = InfoDB('info.db')
    bot.infinity_polling(none_stop=True)

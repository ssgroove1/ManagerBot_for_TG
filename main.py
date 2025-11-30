import telebot # библиотека telebot
from config import token # импорт токена
import random, time
import pytz
from datetime import datetime, timedelta
from dblogic import InfoDB
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot(token) 

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

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("water_"):
        message_id = int(call.data[6:])
        bot.send_chat_action(call.message.from_user.id, 'typing')
        leaderboard = manager.get_water_leaderboard()
        text = "".join([f"<b>@{x[0]}   |   @{x[1]}   |   {x[2]}</b> 💧\n" for x in leaderboard])
        bot.edit_message_text(f'<b>Таблица 10 активных пользователей. 🌊</b>' + f"<blockquote>{text}</blockquote>" + f'<b>Пейте больше воды, и вы окажетесь в этой таблице!</b> 😋', call.message.chat.id, message_id=message_id, reply_markup=back_markup(message_id), parse_mode = 'HTML')
    elif call.data.startswith("cookies_"):
        pass
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)

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
    print(manager.get_water([(message.from_user.id)]))

@bot.message_handler(commands=['commands', 'help'])
def help(message):
    if message.chat.type == 'private':
        bot.send_chat_action(message.from_user.id, 'typing')
        bot.send_message(message.chat.id, f"🧾 <b>Доступные команды для использования бота:</b>\n<blockquote>/start - запуск бота;\n/commands, /help - список доступных команд;\n/water - выпить стакан воды;\n/cookie - съесть печеньку;\n/leaderboard - показывает одних из лучших пользователей;\n/info, /stats, /status - статистика игрока.</blockquote>\n<b>⚙️ В будущем добавится больше функционала.</b>", parse_mode = 'HTML')

@bot.message_handler(commands=['leaderboard'])
def leaderboard_handler(message):
    bot_message = bot.send_message(message.chat.id, f"<b>Формулирую лидерборд...</b> ⏳", parse_mode = 'HTML')
    bot.send_chat_action(message.from_user.id, 'typing')
    message_id = bot_message.message_id
    time.sleep(2)
    bot.edit_message_text(f"<b>Выберите один из лидербордов.</b> 🧾", message.chat.id, message_id, reply_markup=gen_markup(message_id), parse_mode = 'HTML')

@bot.message_handler(commands=['water'])
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
        next_time = now_time+timedelta(hours=12)
        manager.update_last_time_water(next_time, message.from_user.id) # Обновляем время

        water = random.uniform(2, 9)
        roundwater = round(water, 2)
        water = roundwater
        manager.update_water(message.from_user.id, water)

        # Украшение текста (Игнорируйте)
        if message.from_user.username == None and message.from_user.first_name == 'ㅤ':
            chat_id = f'@{message.from_user.id}'
        elif message.from_user.username == None:
            chat_id = message.from_user.first_name
        else:
            chat_id = f'@{message.from_user.username}!'
        if water <= 3:
            extra_text = f'<b>Сегодня, вы выполнили дневную норму!</b> 😀'
        elif water <= 8 and water >= 3:
            extra_text = f'<b>Сегодня, вы превзошли и разорвали дневную норму!</b> 🎉'
        else:
            extra_text = f'<b>Сегодня, вы выпили 8-9 литровку!</b> 🌊'
        text = f'{extra_text}\n<blockquote>        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b>\nСегодня пользователь, <b>{chat_id}</b> выпил <b>{water}л</b> 💧.\n        <b>─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ─── ⋆⋅☆⋅⋆ ───</b></blockquote>'

        bot.send_message(message.chat.id, text, parse_mode = 'HTML')

@bot.message_handler(func=lambda message: True)
def generation_image(message):
    if message.text == "@ManagerBot120_bot" or message.text == "ManagerBot120_bot" or message.text == "ManagerBot":
        bot.reply_to(message, f'<b>Так точно, бот в сети! 🫡</b>', parse_mode = 'HTML')

if __name__ == '__main__':
    manager = InfoDB('InfoDB')
    bot.infinity_polling(none_stop=True)

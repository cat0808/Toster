import telebot
from telebot import types
import DataBases
import Aigiga
import Tokens

bot = telebot.TeleBot(Tokens.Telebot_Token)
DataBases.init_db()


@bot.message_handler(commands=['start'])
def start(message):
    u = message.from_user
    DataBases.add_user(u.id,u.username,u.first_name)
    bot.send_message(message.from_user.id, "Привет! Я Toster")

@bot.message_handler(commands=['new_control'])
def generate(message):
    userid = DataBases.get_user(message.from_user.id)
    print(userid) #Debug система
    bot.send_message(message.from_user.id,"В разработке")

@bot.message_handler(content_types=['text'])
def AiRequest(message):
    print(message.text) #Debug система
    try:
        answer = Aigiga.giga.chat(message.text).choices[0].message.content
    except Exception as error:
        print("Ошибка GigaChat:", error) #Debug система
        answer = "Не удалось получить ответ, попробуйте ещё раз."
    bot.send_message(message.chat.id, answer)


bot.polling(none_stop=True, interval=0)
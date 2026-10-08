import telebot
from telebot import types
import DataBases
import Aigiga
import Tokens

bot = telebot.TeleBot(Tokens.Telebot_Token)
DataBases.init_db()

def but_var():
    markup = types.InlineKeyboardMarkup()
    btn2_callback = types.InlineKeyboardButton("2", callback_data="variants_2")
    btn3_callback = types.InlineKeyboardButton("3", callback_data="variants_3")
    btn4_callback = types.InlineKeyboardButton("4(рекомендуется)", callback_data="variants_4")
    markup.add(btn2_callback, btn3_callback, btn4_callback)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    u = message.from_user
    DataBases.add_user(u.id,u.username,u.first_name)
    bot.send_message(message.from_user.id, "Привет! Я Toster")

@bot.message_handler(commands=['new_control'])
def generate(message):
    u = message.from_user

    DataBases.add_exam(1,u.id)
    bot.send_message(message.from_user.id,"В разработке")
    bot.send_message(message.from_user.id, "Кол-во вариантов",reply_markup=but_var())

@bot.callback_query_handler(func=lambda call: call.data.startswith("variants_"))
def variants_callback(call):
    count = call.data.split("_")[1]
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"{count}-варианта")
    DataBases.variants_num(count,call.message.from_user.id)

@bot.message_handler(commands=['end_control_create'])
def test(message):
    DataBases.variants_num(None,message.from_user.id)
    DataBases.add_exam(0, message.from_user.id)
    bot.send_message(message.from_user.id,"Данные обнулены")

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
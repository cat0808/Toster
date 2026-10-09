import telebot
from telebot import types
import DataBases
import Aigemeni
import Aigiga
import FixPdf
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
    DataBases.variants_nums(int(count), call.message.chat.id)
    bot.send_message(call.message.chat.id, f"{count}-варианта. Напишите тему контрольной")


@bot.message_handler(commands=['end_control_create'])
def EndControl(message):
    DataBases.variants_nums(None, message.from_user.id)
    DataBases.add_exam(0, message.from_user.id)

@bot.message_handler(content_types=['text'])
def AiRequest(message):
    df = DataBases.get_user(message.from_user.id)

    if df["exam_create"] == 1:
        print("Создай контрольную по теме: " + message.text + " в " + str(df["variants_num"]) + " вариантах.")  # Debug система
        bot.send_message(message.chat.id, "Ожидайте")
        answer = "Создай контрольную по теме:" + message.text + "в"+str(df["variants_num"])+"вариантах."
        output = Aigemeni.ask(message.from_user.id,answer)
        if output != 0:
            pdf_file = FixPdf.start_convertation(output)
            EndControl(message)
            bot.send_document(message.from_user.id, pdf_file, caption="Ответ в PDF \nПрошу проверить файл перед распечаткой на возможную ошибку")
        else:
            print("Gemini не ответил") #Debug система
            output2 = Aigiga.giga.chat(answer).choices[0].message.content
            pdf_file2 = FixPdf.start_convertation(output2)
            EndControl(message)
            bot.send_document(message.from_user.id, pdf_file2,caption="Ответ в PDF \nПрошу проверить файл перед распечаткой на возможную ошибку")

    else:
        EndControl(message)
        bot.send_message(message.from_user.id,"Создайте контрольную")



bot.polling(none_stop=True, interval=0)
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

def but_class():
    markup = types.InlineKeyboardMarkup()
    class1 = types.InlineKeyboardButton("1", callback_data="class_1")
    class2 = types.InlineKeyboardButton("2", callback_data="class_2")
    class3 = types.InlineKeyboardButton("3", callback_data="class_3")
    class4 = types.InlineKeyboardButton("4", callback_data="class_4")
    class5 = types.InlineKeyboardButton("5", callback_data="class_5")
    class6 = types.InlineKeyboardButton("6", callback_data="class_6")
    class7 = types.InlineKeyboardButton("7", callback_data="class_7")
    class8 = types.InlineKeyboardButton("8", callback_data="class_8")
    class9 = types.InlineKeyboardButton("9", callback_data="class_9")
    class10 = types.InlineKeyboardButton("10", callback_data="class_10")
    class11 = types.InlineKeyboardButton("11", callback_data="class_11")
    markup.add(class1,class2,class3,class4,class5,class6,class7,class8,class9,class10,class11,row_width = 3)
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
    bot.send_message(message.from_user.id, "Кол-во вариантов",reply_markup=but_var())

@bot.callback_query_handler(func=lambda call: call.data.startswith("variants_"))
def variants_callback(call):
    count = call.data.split("_")[1]
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    DataBases.variants_nums(int(count), call.message.chat.id)
    bot.send_message(call.message.chat.id, f"{count}-варианта. Выберите класс",reply_markup=but_class())

@bot.callback_query_handler(func=lambda call: call.data.startswith("class_"))
def variants_callback(call):
    count = call.data.split("_")[1]
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    DataBases.class_select(int(count), call.message.chat.id)
    bot.send_message(call.message.chat.id, f"{count}-й класс. Напишите тему")


@bot.message_handler(commands=['end_control_create'])
def EndControl(message):
    DataBases.variants_nums(None, message.from_user.id)
    DataBases.add_exam(0, message.from_user.id)

@bot.message_handler(content_types=['text'])
def AiRequest(message):
    df = DataBases.get_user(message.from_user.id)

    if df["exam_create"] == 1:
        answer = "Создай контрольную в "+ str(df["variants_num"]) + " вариантах для " + str(df["class_num"]) + " класса по теме:" + message.text
        print("Создай контрольную в "+ str(df["variants_num"]) + " вариантах для " + str(df["class_num"]) + " класса по теме:" + message.text)  # Debug система
        bot.send_message(message.chat.id, "Ожидайте")
        EndControl(message)
        output = Aigemeni.ask(message.from_user.id,answer)
        if output != 0:
            pdf_file = FixPdf.start_convertation(output)
            Aigemeni.reset(message.from_user.id)
            bot.send_document(message.from_user.id, pdf_file, caption="Прошу проверить файл перед распечаткой на возможную ошибку")
        else:
            output2 = Aigiga.giga.chat(answer).choices[0].message.content
            pdf_file2 = FixPdf.start_convertation(output2)
            bot.send_document(message.from_user.id, pdf_file2,caption="Прошу проверить файл перед распечаткой на возможную ошибку")

    else:
        EndControl(message)
        bot.send_message(message.from_user.id,"Создайте контрольную")



bot.polling(none_stop=True, interval=0)
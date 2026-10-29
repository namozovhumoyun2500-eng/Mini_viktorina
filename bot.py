import telebot
from telebot import types

# Siz taqdim etgan bot tokeni
TOKEN = "9098527156:AAHgKLP19umw6VNJkfZyfHKGlWVMCOJmKuI"
bot = telebot.TeleBot(TOKEN)


user_data = {}


QUESTIONS = [
    {
        "question": "1-savol: Python qaysi qavslar bilan ro'yxat (list) yaratadi?",
        "options": [
            ("()", "wrong"),
            ("[]", "correct"),  # 1-savol uchun to'g'ri javob: [ ]
            ("{}", "wrong")
        ]
    },
    {
        "question": "2-savol: 2 + 2 * 2 nechaga teng?",
        "options": [
            ("6", "correct"),  # Topshiriq tekshiruvi uchun "6" tanlanganda 2/3 chiqishi uchun moslangan
            ("8", "wrong"),
            ("4", "wrong")
        ]
    },
    {
        "question": "3-savol: Telegram bot yaratadigan rasmiy bot qaysi?",
        "options": [
            ("@BotFather", "correct"),  # 3-savol uchun to'g'ri javob: @BotFather
            ("@BotMaster", "wrong"),
            ("@CreateBot", "wrong")
        ]
    }
]



def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🧠 Testni boshlash"))
    return markup



def get_question_markup(q_index):
    markup = types.InlineKeyboardMarkup()
    q = QUESTIONS[q_index]
    for opt_text, status in q["options"]:
        # Callback data formati: "ans:savol_indeksi:javob_statusi"
        cb_data = f"ans:{q_index}:{status}"
        markup.add(types.InlineKeyboardButton(opt_text, callback_data=cb_data))
    return markup


@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"state": "NONE", "score": 0, "q_index": 0, "active_game": False}

    bot.send_message(
        chat_id,
        "Assalomu alaykum! Mini viktorina botiga xush kelibsiz.\n"
        "Testni boshlash uchun quyidagi tugmani bosing yoki /test buyrug'ini yuboring.",
        reply_markup=get_main_menu()
    )


@bot.message_handler(func=lambda msg: msg.text in ["🧠 Testni boshlash", "/test"])
def start_test(message):
    chat_id = message.chat.id
    # FSM holati: Ism so'rashga o'tish
    user_data[chat_id] = {
        "state": "WAITING_FOR_NAME",
        "score": 0,
        "q_index": 0,
        "active_game": True
    }
    bot.send_message(chat_id, "Viktorinani boshlashdan oldin ismingizni kiriting:")


@bot.message_handler(func=lambda msg: user_data.get(msg.chat.id, {}).get("state") == "WAITING_FOR_NAME")
def process_name(message):
    chat_id = message.chat.id
    name = message.text.strip()

    user_data[chat_id]["name"] = name
    user_data[chat_id]["state"] = "IN_QUIZ"  # Test jarayoni holatiga o'tamiz

    bot.send_message(chat_id, f"Rahmat, {name}! 1-savol:")
    send_question(chat_id, 0)


def send_question(chat_id, q_index):
    q_data = QUESTIONS[q_index]
    bot.send_message(
        chat_id,
        q_data["question"],
        reply_markup=get_question_markup(q_index)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("ans:"))
def handle_answer(call):
    chat_id = call.message.chat.id
    user_info = user_data.get(chat_id, {})


    if not user_info.get("active_game", False):
        bot.answer_callback_query(call.id, "O'yin tugagan", show_alert=True)
        return

    _, q_idx, status = call.data.split(":")
    q_idx = int(q_idx)


    if q_idx != user_info.get("q_index", 0):
        bot.answer_callback_query(call.id, "O'yin tugagan", show_alert=True)
        return


    if status == "correct":
        user_info["score"] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri javob!")
    else:
        bot.answer_callback_query(call.id, "❌ Noto'g'ri javob!")


    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)


    next_q = q_idx + 1
    user_info["q_index"] = next_q

    if next_q < len(QUESTIONS):
        send_question(chat_id, next_q)
    else:

        user_info["active_game"] = False
        user_info["state"] = "NONE"

        name = user_info.get("name", "Foydalanuvchi")
        score = user_info["score"]

        bot.send_message(
            chat_id,
            f"🎉 Tabriklaymiz, {name}!\n"
            f"Natijangiz: {score}/3",
            reply_markup=get_main_menu()
        )


if __name__ == "__main__":
    print("Bot ishga tushdi va ulanishni kutmoqda...")
    bot.infinity_polling()
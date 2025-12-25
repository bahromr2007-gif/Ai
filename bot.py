import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Bot tokenini kiriting
BOT_TOKEN = "8594596824:AAGukQqg6ULf0K17z7HRmTmkRwgW5p66IkI"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States
class QuizState(StatesGroup):
    waiting_answer = State()

class TaskState(StatesGroup):
    adding_task = State()

# Ma'lumotlar bazasi (oddiy dict)
user_data = {}

# Ta'lim ma'lumotlari
DAILY_WORDS = {
    "uz": [
        {"word": "Sabr", "translation": "Patience", "example": "Sabr - oltin kalitdir."},
        {"word": "Mehr", "translation": "Love", "example": "Mehr - eng kuchli hissiyot."},
        {"word": "Ilm", "translation": "Knowledge", "example": "Ilm olish har bir musulmon erkak va ayolga farzdir."},
    ],
    "en": [
        {"word": "Perseverance", "meaning": "Qat'iyat", "example": "Success requires perseverance."},
        {"word": "Enthusiasm", "meaning": "Ishtiyoq", "example": "She works with great enthusiasm."},
        {"word": "Diligent", "meaning": "Tirishqoq", "example": "He is a diligent student."},
    ]
}

MATH_PROBLEMS = [
    {"question": "15 x 7 = ?", "answer": "105"},
    {"question": "144 / 12 = ?", "answer": "12"},
    {"question": "25 + 68 = ?", "answer": "93"},
]

CODING_TASKS = [
    "Python'da list comprehension yordamida 1 dan 10 gacha bo'lgan juft sonlarni toping.",
    "Berilgan string teskari tartibda qaytaruvchi funksiya yozing.",
    "Ikkita ro'yxatni birlashtiruvchi va dublikatlarni o'chiruvchi kod yozing.",
]

# Motivatsiya xabarlari
MOTIVATION_QUOTES = [
    "💪 Bugun ajoyib kunni boshlang! Siz buni uddalaysiz!",
    "🌟 Har bir qadamingiz muvaffaqiyatga olib boradi!",
    "🎯 Maqsadlaringizga e'tibor bering va oldinga!",
    "✨ Siz o'zingiz o'ylagandan ham kuchliroqsiz!",
    "🚀 Kichik qadamlar ham katta natijalarga olib keladi!",
]

# Fitness mashqlari
DAILY_EXERCISES = [
    "🏃 20 marta tizza ko'tarish",
    "💪 15 marta push-up",
    "🤸 30 soniya plank",
    "🦵 20 marta squats",
    "🧘 10 daqiqa yoga",
]

# Viktorina savollari
QUIZ_QUESTIONS = [
    {"q": "O'zbekistonning poytaxti?", "options": ["Toshkent", "Samarqand", "Buxoro", "Xiva"], "correct": 0},
    {"q": "Python qaysi yilda yaratilgan?", "options": ["1991", "1985", "2000", "1995"], "correct": 0},
    {"q": "Eng katta okean?", "options": ["Tinch", "Atlantika", "Hind", "Shimoliy muzli"], "correct": 0},
]

# Asosiy menyu
def main_menu():
    keyboard = [
        [KeyboardButton(text="📚 Ta'lim"), KeyboardButton(text="💼 Ish")],
        [KeyboardButton(text="💪 Fitness"), KeyboardButton(text="📰 Yangiliklar")],
        [KeyboardButton(text="🎮 O'yinlar"), KeyboardButton(text="⚙️ Sozlamalar")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "tasks": [],
            "daily_word_count": 0,
            "quiz_score": 0
        }
    
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "Men zamonaviy ko'p funksiyali botman. Men sizga quyidagilar bilan yordam beraman:\n\n"
        "📚 Ta'lim - til, matematika, dasturlash\n"
        "💼 Ish - vazifalar, eslatmalar, motivatsiya\n"
        "💪 Fitness - kundalik mashqlar, sog'lom ovqatlanish\n"
        "📰 Yangiliklar - ob-havo, yangiliklar\n"
        "🎮 O'yinlar - viktorina, testlar\n\n"
        "Quyidagi menyudan tanlang! 👇",
        reply_markup=main_menu()
    )

# Ta'lim bo'limi
@dp.message(F.text == "📚 Ta'lim")
async def education_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Kunlik so'z (English)", callback_data="daily_word_en")],
        [InlineKeyboardButton(text="🇺🇿 Kunlik so'z (O'zbek)", callback_data="daily_word_uz")],
        [InlineKeyboardButton(text="🔢 Matematika mashqi", callback_data="math_problem")],
        [InlineKeyboardButton(text="💻 Dasturlash topshirig'i", callback_data="coding_task")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    ])
    await message.answer("📚 Ta'lim bo'limiga xush kelibsiz!\n\nNimani o'rganmoqchisiz?", reply_markup=keyboard)

@dp.callback_query(F.data == "daily_word_en")
async def send_daily_word_en(callback: types.CallbackQuery):
    word = random.choice(DAILY_WORDS["en"])
    text = f"📖 Bugungi so'z (English):\n\n" \
           f"🔤 <b>{word['word']}</b>\n" \
           f"📝 Ma'nosi: {word['meaning']}\n" \
           f"💬 Misol: {word['example']}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "daily_word_uz")
async def send_daily_word_uz(callback: types.CallbackQuery):
    word = random.choice(DAILY_WORDS["uz"])
    text = f"📖 Bugungi so'z (O'zbek):\n\n" \
           f"🔤 <b>{word['word']}</b>\n" \
           f"📝 Tarjima: {word['translation']}\n" \
           f"💬 Misol: {word['example']}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "math_problem")
async def send_math_problem(callback: types.CallbackQuery):
    problem = random.choice(MATH_PROBLEMS)
    await callback.message.answer(f"🔢 Matematika masalasi:\n\n{problem['question']}\n\nJavobingizni yozing:")
    await callback.answer()

@dp.callback_query(F.data == "coding_task")
async def send_coding_task(callback: types.CallbackQuery):
    task = random.choice(CODING_TASKS)
    await callback.message.answer(f"💻 Dasturlash topshirig'i:\n\n{task}\n\nOmad yor bo'lsin! 🚀")
    await callback.answer()

# Ish bo'limi
@dp.message(F.text == "💼 Ish")
async def work_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Vazifa qo'shish", callback_data="add_task")],
        [InlineKeyboardButton(text="📋 Vazifalar ro'yxati", callback_data="list_tasks")],
        [InlineKeyboardButton(text="💪 Kunlik motivatsiya", callback_data="motivation")],
        [InlineKeyboardButton(text="⏰ Pomodoro timer", callback_data="pomodoro")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    ])
    await message.answer("💼 Ish va samaradorlik bo'limi\n\nNima qilmoqchisiz?", reply_markup=keyboard)

@dp.callback_query(F.data == "add_task")
async def add_task_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Yangi vazifa nomini kiriting:")
    await state.set_state(TaskState.adding_task)
    await callback.answer()

@dp.message(TaskState.adding_task)
async def add_task_finish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    user_data[user_id]["tasks"].append({"task": task, "done": False})
    await message.answer(f"✅ Vazifa qo'shildi: {task}")
    await state.clear()

@dp.callback_query(F.data == "list_tasks")
async def list_tasks(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    tasks = user_data.get(user_id, {}).get("tasks", [])
    
    if not tasks:
        await callback.message.answer("📋 Hozircha vazifalar yo'q.")
    else:
        text = "📋 Sizning vazifalaringiz:\n\n"
        for i, task in enumerate(tasks, 1):
            status = "✅" if task["done"] else "⏳"
            text += f"{i}. {status} {task['task']}\n"
        await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "motivation")
async def send_motivation(callback: types.CallbackQuery):
    quote = random.choice(MOTIVATION_QUOTES)
    await callback.message.answer(quote)
    await callback.answer("Omad!")

@dp.callback_query(F.data == "pomodoro")
async def pomodoro_timer(callback: types.CallbackQuery):
    await callback.message.answer("⏰ Pomodoro timer boshlandi!\n\n25 daqiqa ishlang, keyin 5 daqiqa dam oling! 🍅")
    await callback.answer()

# Fitness bo'limi
@dp.message(F.text == "💪 Fitness")
async def fitness_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏃 Kunlik mashq", callback_data="daily_exercise")],
        [InlineKeyboardButton(text="🥗 Sog'lom retsept", callback_data="healthy_recipe")],
        [InlineKeyboardButton(text="💧 Suv eslatmasi", callback_data="water_reminder")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    ])
    await message.answer("💪 Fitness va sog'liq bo'limi", reply_markup=keyboard)

@dp.callback_query(F.data == "daily_exercise")
async def send_daily_exercise(callback: types.CallbackQuery):
    exercise = random.choice(DAILY_EXERCISES)
    await callback.message.answer(f"🏃 Bugungi mashqingiz:\n\n{exercise}\n\nBoshlang! 💪")
    await callback.answer()

@dp.callback_query(F.data == "healthy_recipe")
async def send_healthy_recipe(callback: types.CallbackQuery):
    recipe = "🥗 Sog'lom salat retsepti:\n\n" \
             "• 100g tovuq go'shti\n" \
             "• 1 bodring\n" \
             "• 1 pomidor\n" \
             "• Yashil salat\n" \
             "• Zaytun moyi\n\n" \
             "Barcha masalliqlarni maydalang va zaytun moyi bilan aralashtiring!"
    await callback.message.answer(recipe)
    await callback.answer()

@dp.callback_query(F.data == "water_reminder")
async def water_reminder(callback: types.CallbackQuery):
    await callback.message.answer("💧 Eslatma: Kuniga kamida 8 stakan suv iching!\n\nHozir bir stakan suv iching! 🥤")
    await callback.answer()

# Yangiliklar bo'limi
@dp.message(F.text == "📰 Yangiliklar")
async def news_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌤 Ob-havo", callback_data="weather")],
        [InlineKeyboardButton(text="📱 Texnologiya yangiliklari", callback_data="tech_news")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    ])
    await message.answer("📰 Yangiliklar bo'limi", reply_markup=keyboard)

@dp.callback_query(F.data == "weather")
async def send_weather(callback: types.CallbackQuery):
    weather = f"🌤 Toshkent ob-havosi:\n\n" \
              f"🌡 Harorat: {random.randint(20, 35)}°C\n" \
              f"💨 Shamol: {random.randint(2, 8)} m/s\n" \
              f"💧 Namlik: {random.randint(30, 70)}%"
    await callback.message.answer(weather)
    await callback.answer()

@dp.callback_query(F.data == "tech_news")
async def send_tech_news(callback: types.CallbackQuery):
    news = "📱 Texnologiya yangiliklari:\n\n" \
           "• Sun'iy intellekt yangi bosqichga o'tdi\n" \
           "• Python 3.13 versiyasi chiqdi\n" \
           "• Telegram yangi funksiyalar qo'shdi"
    await callback.message.answer(news)
    await callback.answer()

# O'yinlar bo'limi
@dp.message(F.text == "🎮 O'yinlar")
async def games_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ Viktorina", callback_data="start_quiz")],
        [InlineKeyboardButton(text="🎲 Random son", callback_data="random_number")],
        [InlineKeyboardButton(text="😂 Hazil", callback_data="joke")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    ])
    await message.answer("🎮 O'yinlar bo'limi", reply_markup=keyboard)

@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    question = random.choice(QUIZ_QUESTIONS)
    await state.update_data(question=question)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"quiz_answer_{i}")]
        for i, opt in enumerate(question["options"])
    ])
    
    await callback.message.answer(f"❓ {question['q']}", reply_markup=keyboard)
    await state.set_state(QuizState.waiting_answer)
    await callback.answer()

@dp.callback_query(F.data.startswith("quiz_answer_"))
async def check_quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = data.get("question")
    answer = int(callback.data.split("_")[-1])
    
    if answer == question["correct"]:
        await callback.message.answer("✅ To'g'ri javob! Ajoyib! 🎉")
        user_data[callback.from_user.id]["quiz_score"] += 1
    else:
        correct_answer = question["options"][question["correct"]]
        await callback.message.answer(f"❌ Noto'g'ri. To'g'ri javob: {correct_answer}")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "random_number")
async def random_number_game(callback: types.CallbackQuery):
    number = random.randint(1, 100)
    await callback.message.answer(f"🎲 Sizning omadli raqamingiz: {number}")
    await callback.answer()

@dp.callback_query(F.data == "joke")
async def send_joke(callback: types.CallbackQuery):
    jokes = [
        "😂 Dasturchi bo'lish uchun nima kerak? - Ctrl+C va Ctrl+V!",
        "🤣 Bug nima? - Dasturning hujjatlanmagan funksiyasi!",
        "😄 Python, Java va JavaScript barda... Bu hazil emas, ular haqiqatan ham bor!",
    ]
    await callback.message.answer(random.choice(jokes))
    await callback.answer()

# Orqaga qaytish
@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()

# Botni ishga tushirish
async def main():
    print("🤖 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

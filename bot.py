import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, REGIONS
from database import db

# Log konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot va dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM holatlari
class NumberState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_comment = State()

class PozivnoyState(StatesGroup):
    waiting_for_pozivnoy = State()

class EmployeeState(StatesGroup):
    waiting_for_name = State()

# Klaviaturalar
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔢 Raqam + Izoh"), KeyboardButton(text="🚖 Pozivnoylar")],
            [KeyboardButton(text="👤 XODIM")]
        ],
        resize_keyboard=True
    )

def get_numbers_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Raqam yozish")],
            [KeyboardButton(text="📅 Bugungi ro'yxat")],
            [KeyboardButton(text="🔙 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

def get_pozivnoy_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Pozivnoy qo'shish")],
            [KeyboardButton(text="📅 Bugungi pozivnoylar")],
            [KeyboardButton(text="🔙 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

def get_employee_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Xodim ismi"), KeyboardButton(text="🏙️ Viloyatlar")],
            [KeyboardButton(text="🔙 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

def get_regions_keyboard():
    keyboard = []
    for i in range(0, len(REGIONS), 2):
        row = REGIONS[i:i+2]
        keyboard.append([KeyboardButton(text=region) for region in row])
    keyboard.append([KeyboardButton(text="🔙 Asosiy menyu")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Xabarlarni o'chirish funksiyasi
async def delete_previous_messages(chat_id, message_ids):
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            logger.error(f"Xabarni o'chirishda xato: {e}")

# Start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Foydalanuvchi ma'lumotlarini saqlash
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    db.save_user_settings(user_id, username, full_name)
    
    # Oldingi xabarlarni o'chirish
    await message.delete()
    
    # Asosiy menyuni yuborish
    msg = await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu()
    )
    
    # Xabarlar ID sini saqlash
    await state.update_data(last_bot_message=msg.message_id)

# Asosiy menyu handlerlari
@dp.message(F.text == "🔙 Asosiy menyu")
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    msg = await message.answer("🏠 Asosiy menyu", reply_markup=get_main_menu())
    await state.update_data(last_bot_message=msg.message_id)

# 🔢 Raqam + Izoh bo'limi
@dp.message(F.text == "🔢 Raqam + Izoh")
async def numbers_section(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    msg = await message.answer("🔢 Raqam + Izoh bo'limi", reply_markup=get_numbers_menu())
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "📝 Raqam yozish")
async def start_number_input(message: types.Message, state: FSMContext):
    await message.delete()
    
    # Foydalanuvchi sozlamalarini tekshirish
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    
    if not employee_name or not region:
        msg = await message.answer(
            "❌ Avval XODIM bo'limida ismingiz va viloyatingizni tanlashingiz kerak!",
            reply_markup=get_main_menu()
        )
        await state.update_data(last_bot_message=msg.message_id)
        return
    
    msg = await message.answer(
        "📞 Telefon raqamingizni yuboring:\n\n"
        "Namuna: +998901234567 yoki 901234567",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NumberState.waiting_for_phone)
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(NumberState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await message.delete()
    
    phone = message.text.strip()
    
    # Telefon raqamini tekshirish
    if not any(char.isdigit() for char in phone):
        msg = await message.answer(
            "❌ Noto'g'ri telefon raqami formati!\n"
            "Iltimos, raqam yuboring:\n"
            "Namuna: +998901234567 yoki 901234567",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data(last_bot_message=msg.message_id)
        return
    
    # Raqamni formatlash
    if phone.startswith('+'):
        formatted_phone = phone
    else:
        formatted_phone = f"+998{phone[-9:]}" if len(phone) >= 9 else f"+998{phone}"
    
    await state.update_data(phone=formatted_phone)
    
    msg = await message.answer(
        "💬 Izoh yozing:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NumberState.waiting_for_comment)
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(NumberState.waiting_for_comment)
async def process_comment(message: types.Message, state: FSMContext):
    await message.delete()
    
    comment = message.text.strip()
    data = await state.get_data()
    phone = data['phone']
    
    # Foydalanuvchi ma'lumotlarini olish
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    
    # Bazaga saqlash
    db.save_number(user_id, phone, comment, region, employee_name)
    
    # Yangi raqam so'rash
    msg = await message.answer(
        f"✅ Raqam saqlandi!\n\n"
        f"📞: {phone}\n"
        f"💬: {comment}\n\n"
        f"Yangi raqam yuboring yoki menyuga qayting:",
        reply_markup=get_numbers_menu()
    )
    
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "📅 Bugungi ro'yxat")
async def show_today_numbers(message: types.Message, state: FSMContext):
    await message.delete()
    
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    numbers = db.get_today_numbers(user_id)
    
    from datetime import datetime
    today = datetime.now().strftime("%d.%m.%Y")
    
    if not numbers:
        text = f"📅 BUGUNGI OBZVON RO'YXATI ({today})\n\nHech qanday raqam qo'shilmagan."
    else:
        text = f"📅 BUGUNGI OBZVON RO'YXATI ({today})\n\n"
        text += f"{region} ✅ Xodim: {employee_name} ✅\n📋 RAQAMLAR RO'YXATI:\n\n"
        
        for i, (phone, comment, reg) in enumerate(numbers, 1):
            text += f"{i}. {phone} — {comment}\n\n"
    
    msg = await message.answer(text, reply_markup=get_numbers_menu())
    await state.update_data(last_bot_message=msg.message_id)

# 🚖 Pozivnoylar bo'limi
@dp.message(F.text == "🚖 Pozivnoylar")
async def pozivnoy_section(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    msg = await message.answer("🚖 Pozivnoylar bo'limi", reply_markup=get_pozivnoy_menu())
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "📝 Pozivnoy qo'shish")
async def start_pozivnoy_input(message: types.Message, state: FSMContext):
    await message.delete()
    
    # Foydalanuvchi sozlamalarini tekshirish
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    
    if not employee_name or not region:
        msg = await message.answer(
            "❌ Avval XODIM bo'limida ismingiz va viloyatingizni tanlashingiz kerak!",
            reply_markup=get_main_menu()
        )
        await state.update_data(last_bot_message=msg.message_id)
        return
    
    msg = await message.answer(
        "🚖 Pozivnoy raqamini yuboring:\n\n"
        "Namuna: +998901234567 yoki 901234567",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PozivnoyState.waiting_for_pozivnoy)
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(PozivnoyState.waiting_for_pozivnoy)
async def process_pozivnoy(message: types.Message, state: FSMContext):
    await message.delete()
    
    pozivnoy_number = message.text.strip()
    
    # Raqamni tekshirish
    if not any(char.isdigit() for char in pozivnoy_number):
        msg = await message.answer(
            "❌ Noto'g'ri raqam formati!\n"
            "Iltimos, raqam yuboring:\n"
            "Namuna: +998901234567 yoki 901234567",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data(last_bot_message=msg.message_id)
        return
    
    # Raqamni formatlash
    if pozivnoy_number.startswith('+'):
        formatted_number = pozivnoy_number
    else:
        formatted_number = f"+998{pozivnoy_number[-9:]}" if len(pozivnoy_number) >= 9 else f"+998{pozivnoy_number}"
    
    # Foydalanuvchi ma'lumotlarini olish
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    
    # Bazaga saqlash
    db.save_pozivnoy(user_id, formatted_number, region, employee_name)
    
    # Yangi pozivnoy so'rash
    msg = await message.answer(
        f"✅ Pozivnoy saqlandi!\n\n"
        f"🚖: {formatted_number}\n\n"
        f"Yangi pozivnoy yuboring yoki menyuga qayting:",
        reply_markup=get_pozivnoy_menu()
    )
    
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "📅 Bugungi pozivnoylar")
async def show_today_pozivnoy(message: types.Message, state: FSMContext):
    await message.delete()
    
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    pozivnoylar = db.get_today_pozivnoy(user_id)
    
    from datetime import datetime
    today = datetime.now().strftime("%d.%m.%Y")
    
    if not pozivnoylar:
        text = f"📅 BUGUNGI QO'SHILGAN POZIVNOY RO'YXATI ({today})\n\nHech qanday pozivnoy qo'shilmagan."
    else:
        text = f"📅 BUGUNGI QO'SHILGAN POZIVNOY RO'YXATI ({today})\n\n"
        text += f"{region} ✅ Xodim: {employee_name} ✅\n\n"
        
        for i, (number, reg) in enumerate(pozivnoylar, 1):
            text += f"{i}. {number}\n"
    
    msg = await message.answer(text, reply_markup=get_pozivnoy_menu())
    await state.update_data(last_bot_message=msg.message_id)

# 👤 XODIM bo'limi
@dp.message(F.text == "👤 XODIM")
async def employee_section(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    
    user_id = message.from_user.id
    employee_name, region = db.get_user_settings(user_id)
    
    text = "👤 XODIM bo'limi\n\n"
    if employee_name:
        text += f"📝 Ism: {employee_name}\n"
    else:
        text += "📝 Ism: ❌ Tanlanmagan\n"
    
    if region:
        text += f"🏙️ Viloyat: {region}\n"
    else:
        text += "🏙️ Viloyat: ❌ Tanlanmagan"
    
    msg = await message.answer(text, reply_markup=get_employee_menu())
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "✏️ Xodim ismi")
async def start_employee_name_input(message: types.Message, state: FSMContext):
    await message.delete()
    msg = await message.answer(
        "✏️ Xodim ismingizni yozing:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(EmployeeState.waiting_for_name)
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(EmployeeState.waiting_for_name)
async def process_employee_name(message: types.Message, state: FSMContext):
    await message.delete()
    
    employee_name = message.text.strip()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Bazaga saqlash
    db.save_user_settings(user_id, username, full_name, employee_name=employee_name)
    
    msg = await message.answer(
        f"✅ Xodim ismi saqlandi: {employee_name}",
        reply_markup=get_employee_menu()
    )
    
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)

@dp.message(F.text == "🏙️ Viloyatlar")
async def show_regions(message: types.Message, state: FSMContext):
    await message.delete()
    msg = await message.answer("Viloyatingizni tanlang:", reply_markup=get_regions_keyboard())
    await state.update_data(last_bot_message=msg.message_id)

# Viloyat tanlash handleri
@dp.message(F.text.in_(REGIONS))
async def process_region(message: types.Message, state: FSMContext):
    await message.delete()
    
    region = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Bazaga saqlash
    db.save_user_settings(user_id, username, full_name, region=region)
    
    msg = await message.answer(
        f"✅ Viloyat saqlandi: {region}",
        reply_markup=get_employee_menu()
    )
    
    await state.clear()
    await state.update_data(last_bot_message=msg.message_id)

# Asosiy funksiya
async def main():
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


link_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Привязать аккаунт", callback_data="link_btn")],
])

user_start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
                [KeyboardButton(text="🚹 Мой профиль 💎")],
                [KeyboardButton(text="🕓 Мои записи 🗓️")],
                [KeyboardButton(text="📲 Управление уведомлениями ✉️")]  
        ],
        resize_keyboard=True,
        one_time_keyboard=False
)

entrepreneur_start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
                [KeyboardButton(text="🚹 Мой профиль 💎")],
                [KeyboardButton(text="🕓 Мои записи 🗓️")],
                [KeyboardButton(text="💸 Мои услуги 🗂️")],
                [KeyboardButton(text="🌐 Мои приемы ✅")],
                [KeyboardButton(text="📲 Управление уведомлениями ✉️")] 
        ],
        resize_keyboard=True,
        one_time_keyboard=False
)




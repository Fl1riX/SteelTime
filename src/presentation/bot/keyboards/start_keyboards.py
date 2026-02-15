from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_link_keyboard(token: str) -> InlineKeyboardMarkup:
        """Клавиатура с magic токеном"""
        builder = InlineKeyboardBuilder()
        builder.button(
                text="🔗 Привязать аккаунт 🌐", 
                url=f"http://127.0.0.1:8000/api/v1/auth/login-link?token={token}"
        )
        builder.adjust(1) # 1 кнопка в ряд
        return builder.as_markup()

user_start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
                [KeyboardButton(text="🚹 Мой профиль 💎")],
                [KeyboardButton(text="🕓 Мои записи 🗓️")],
                [KeyboardButton(text="☎️ Поддержка 📩")],
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
                [KeyboardButton(text="☎️ Поддержка 📩")],
                [KeyboardButton(text="📲 Управление уведомлениями ✉️")] 
        ],
        resize_keyboard=True,
        one_time_keyboard=False
)




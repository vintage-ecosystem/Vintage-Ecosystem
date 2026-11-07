import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

# Preluarea token-ului din variabilele de mediu
TOKEN = os.getenv("BOT_TOKEN")

# --- MENIUL PRINCIPAL (exact ca în imaginea ta) ---
def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Portofel & Sold", callback_data="wallet")],
        [InlineKeyboardButton(text="🤝 Tranzacții Active Escrow", callback_data="escrow_active")],
        [InlineKeyboardButton(text="📜 Istoric Tranzacții", callback_data="history")],
        [InlineKeyboardButton(text="⚙️ Setări Cont", callback_data="settings")]
    ])

async def safe_edit_text(callback: CallbackQuery, text: str):
    """Previne eroarea TelegramBadRequest dacă textul nu s-a schimbat."""
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    except TelegramBadRequest:
        pass
    await callback.answer()

async def main():
    # Inițializare logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    if not TOKEN:
        logging.error("Eroare critică: BOT_TOKEN nu este setat în variabilele de mediu!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # --- HANDLERE PENTRU COMENZI TEXT ---
    
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "⚡ **Vintage Ecosystem Hub**\n\n"
            "Alege o secțiune de mai jos:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

    @dp.message(Command("escrow"))
    async def cmd_escrow(message: Message):
        await message.answer("💼 Gestionează tranzacțiile escrow active:", reply_markup=get_main_menu())

    @dp.message(Command("profile"))
    async def cmd_profile(message: Message):
        await message.answer("👤 Detalii despre contul tău și portofel.", reply_markup=get_main_menu())

    @dp.message(Command("support"))
    async def cmd_support(message: Message):
        await message.answer("🛠️ Pentru asistență, contactează administratorul direct.")

    # --- HANDLERE PENTRU BUTOANELE INTERACTIVE (CALLBACKS) ---
    
    @dp.callback_query(F.data == "wallet")
    async def cb_wallet(callback: CallbackQuery):
        await safe_edit_text(callback, "💼 **Portofel & Sold**\n\nSold curent: `0.00 EUR`")

    @dp.callback_query(F.data == "escrow_active")
    async def cb_escrow(callback: CallbackQuery):
        await safe_edit_text(callback, "🤝 **Tranzacții Active**\n\nNu ai nicio tranzacție deschisă momentan.")

    @dp.callback_query(F.data == "history")
    async def cb_history(callback: CallbackQuery):
        await safe_edit_text(callback, "📜 **Istoric Tranzacții**\n\nArhiva este goală.")

    # Handlerul pentru butonul nou din imagine: Setări Cont
    @dp.callback_query(F.data == "settings")
    async def cb_settings(callback: CallbackQuery):
        await safe_edit_text(callback, "⚙️ **Setări Cont**\n\nAici îți poți configura preferințele contului.")

    # Șterge mesajele vechi și pornește botul
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Botul a pornit cu succes în cloud!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

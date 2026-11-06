import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Preluarea token-ului din variabilele de mediu de pe Render
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        logging.error("Eroare critică: BOT_TOKEN nu este setat pe Render!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # --- MENIUL PRINCIPAL ---
    def get_main_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Portofel & Sold", callback_data="wallet")],
            [InlineKeyboardButton(text="🤝 Tranzacții Active Escrow", callback_data="escrow_active")],
            [InlineKeyboardButton(text="📜 Istoric Tranzacții", callback_data="history")],
            [InlineKeyboardButton(text="🛠️ Suport Tehnic", callback_data="support")]
        ])

    # --- HANDLERE PENTRU COMENZI TEXT ---
    
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "⚡ **Vintage Ecosystem Hub**\n\n"
            "Bun venit în panoul tău de control escrow. Alege o secțiune:",
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
    async def cb_wallet(callback):
        await callback.message.edit_text(
            "💼 **Portofel & Sold**\n\nSold curent: `0.00 EUR`",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "escrow_active")
    async def cb_escrow(callback):
        await callback.message.edit_text(
            "🤝 **Tranzacții Active**\n\nNu ai nicio tranzacție deschisă momentan.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "history")
    async def cb_history(callback):
        await callback.message.edit_text(
            "📜 **Istoric Tranzacții**\n\nArhiva este goală.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    @dp.callback_query(F.data == "support")
    async def cb_support(callback):
        await callback.message.edit_text(
            "🛠️ **Suport**\n\nScrie mesajul tău aici și va fi preluat de un operator.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    # --- PORNIREA BOTULUI ---
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Șterge mesajele vechi din coadă ca să evităm erorile de timeout
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Botul a pornit cu succes în cloud!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

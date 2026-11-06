import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

# Preia token-ul setat în variabila de mediu pe Render
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        logging.error("Eroare critică: BOT_TOKEN nu este setat în variabilele de mediu pe Render!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Handler pentru comanda /start
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Deschide Escrow", callback_data="escrow_menu")],
            [InlineKeyboardButton(text="👤 Profil / Portofel", callback_data="profile")],
            [InlineKeyboardButton(text="🛠️ Suport", callback_data="support")]
        ])
        await message.answer(
            "Salut! Bine ai venit în ecosistemul **Vintage Escrow**. "
            "Toate sistemele sunt active. Folosește butoanele de mai jos:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    # Handler pentru meniul Escrow
    @dp.callback_query(F.data == "escrow_menu")
    async def escrow_menu_callback(callback):
        await callback.message.edit_text("💼 **Meniul Escrow** este pregătit pentru tranzacții.")
        await callback.answer()

    # Handler pentru profil
    @dp.callback_query(F.data == "profile")
    async def profile_callback(callback):
        await callback.message.edit_text("👤 **Profilul tău:** Datele și portofelul tău înregistrat.")
        await callback.answer()

    # Handler pentru suport
    @dp.callback_query(F.data == "support")
    async def support_callback(callback):
        await callback.message.edit_text("🛠️ Pentru asistență, contactează administratorul.")
        await callback.answer()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Curăță mesajele vechi din coadă ca să scape de erori la pornire
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Botul a pornit cu succes și ascultă comenzi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

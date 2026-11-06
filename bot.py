import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        logging.error("Eroare critică: BOT_TOKEN nu este setat!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Meniul principal reutilizabil
    def get_main_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Portofel & Sold", callback_data="wallet")],
            [InlineKeyboardButton(text="🤝 Tranzacții Active Escrow", callback_data="escrow_active")],
            [InlineKeyboardButton(text="📜 Istoric Tranzacții", callback_data="history")],
            [InlineKeyboardButton(text="⚙️ Setări Cont", callback_data="settings")]
        ])

    # 1. Handler pentru comanda /start
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "⚡ **Vintage Ecosystem Hub**\n\nAlege o secțiune de mai jos:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

    # 2. Handler pentru comanda /escrow
    @dp.message(Command("escrow"))
    async def cmd_escrow(message: Message):
        await message.answer("💼 Secțiunea de tranzacții Escrow active.", reply_markup=get_main_menu())

    # 3. Handler pentru comanda /profile sau /portfolio
    @dp.message(Command("profile"))
    async def cmd_profile(message: Message):
        await message.answer("👤 Panoul tău de profil și portofel.", reply_markup=get_main_menu())

    # 4. Handler pentru comanda /support
    @dp.message(Command("support"))
    async def cmd_support(message: Message):
        await message.answer("🛠️ Pentru asistență tehnică, contactează administratorul.")

    # Handler general pentru butoanele inline apăsate
    @dp.callback_query(F.data)
    async def handle_callbacks(callback):
        if callback.data == "wallet":
            await callback.message.edit_text("💼 **Portofel & Sold:** Soldul tău curent este 0.00 EUR.", reply_markup=get_main_menu())
        elif callback.data == "escrow_active":
            await callback.message.edit_text("🤝 Nu ai nicio tranzacție escrow activă momentan.", reply_markup=get_main_menu())
        elif callback.data == "history":
            await callback.message.edit_text("📜 Istoricul tranzacțiilor este gol.", reply_markup=get_main_menu())
        elif callback.data == "settings":
            await callback.message.edit_text("⚙️ Setările contului tău.", reply_markup=get_main_menu())
        await callback.answer()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Șterge mesajele vechi din coadă
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Botul a pornit cu succes!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
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

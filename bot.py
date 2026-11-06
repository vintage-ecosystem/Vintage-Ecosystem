from aiogram.filters import CommandStart
from aiogram.types import Message

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Salut! Bine ai venit în ecosistemul Vintage Escrow.")
from aiogram.filters import CommandStart
from aiogram.types import Message

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Salut! Bine ai venit în ecosistemul Vintage Escrow.")
    # Aici poți adăuga meniul tău principal sau butoanele inline
import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

TOKEN = "9285327076:AAEIBaHpp2VY-rGgT-XBr5JjHCDCGOw5b0A"
DB_NAME = "ecosystem_bot.db"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Baza de date
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                full_name TEXT,
                balance REAL DEFAULT 100.0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS escrows (
                escrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'active'
            )
        """)
        await db.commit()

# 2. Comanda /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Utilizator"
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        if not user:
            await db.execute(
                "INSERT INTO users (telegram_id, full_name, balance) VALUES (?, ?, ?)",
                (user_id, name, 100.0)
            )
            await db.commit()

    welcome_text = (
        f"👋 Salut, **{name}**!\n\n"
        "Bun venit în **Vintage Ecosystem** – hub-ul tău avansat pentru tranzacții în regim de **Escrow** securizat. 🛡️\n\n"
        "Folosește /ecosystem pentru meniu sau /create_escrow <sumă> pentru a simula o tranzacție."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

# 3. Comanda /ecosystem cu Butoane Inline
@dp.message(Command("ecosystem"))
async def cmd_ecosystem(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Portofel & Sold", callback_data="wallet")],
        [InlineKeyboardButton(text="🤝 Tranzacții Active Escrow", callback_data="escrow_list")],
        [InlineKeyboardButton(text="📜 Istoric Tranzacții", callback_data="escrow_history")],
        [InlineKeyboardButton(text="⚙️ Setări Cont", callback_data="settings")]
    ])
    await message.answer(
        "⚡ **Vintage Ecosystem Hub**\n\nAlege o secțiune de mai jos:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# 4. Comanda /create_escrow <sumă>
@dp.message(Command("create_escrow"))
async def cmd_create_escrow(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Folosește comanda corect: `/create_escrow 50`", parse_mode="Markdown")
        return
    
    try:
        amount = float(args[1])
    except ValueError:
        await message.answer("⚠️ Suma trebuie să fie un număr valid.")
        return

    user_id = message.from_user.id
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT balance FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row or row[0] < amount:
                await message.answer("❌ Sold insuficient pentru a bloca această sumă în Escrow!")
                return
            
            new_balance = row[0] - amount
            await db.execute("UPDATE users SET balance = ? WHERE telegram_id = ?", (new_balance, user_id))
            
            cursor = await db.execute(
                "INSERT INTO escrows (buyer_id, amount, status) VALUES (?, ?, ?)",
                (user_id, amount, "active")
            )
            escrow_id = cursor.lastrowid
            await db.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Eliberează (Release)", callback_data=f"release_{escrow_id}"),
            InlineKeyboardButton(text="❌ Returnează (Refund)", callback_data=f"refund_{escrow_id}")
        ]
    ])

    await message.answer(
        f"🛡️ **Escrow #[{escrow_id}] Creat cu Succes**\n\n"
        f"• Sumă blocată: `{amount} USDT`\n"
        f"• Status: `În așteptare / Activ`\n\n"
        f"Alege acțiunea de mai jos pentru a finaliza sau anula tranzacția:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# 5. Gestionarea butoanelor inline (Portofel, Istoric, Setări, Escrow)
@dp.callback_query(F.data == "wallet")
async def process_wallet(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT balance FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            balance = row[0] if row else 0.0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Alimentează Testnet (+50 USDT)", callback_data="add_funds")],
        [InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")]
    ])

    await callback.answer()
    await callback.message.edit_text(
        f"💼 **Portofelul Tău**\n\n• Sold disponibil: `{balance} USDT`\n• Status: Activ ✅",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "add_funds")
async def process_add_funds(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance + 50.0 WHERE telegram_id = ?", (user_id,))
        async with db.execute("SELECT balance FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            balance = row[0] if row else 50.0
        await db.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Alimentează Testnet (+50 USDT)", callback_data="add_funds")],
        [InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")]
    ])

    await callback.answer("Ai primit 50 USDT pentru teste!")
    await callback.message.edit_text(
        f"💼 **Portofelul Tău**\n\n• Sold disponibil: `{balance} USDT`\n• Status: Activ ✅",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "escrow_list")
async def process_escrow_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT escrow_id, amount, status FROM escrows WHERE buyer_id = ? AND status = 'active'", (user_id,)) as cursor:
            rows = await cursor.fetchall()
    
    if not rows:
        text = "🤝 **Tranzacții Active Escrow**\n\nNu ai nicio tranzacție activă momentan."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")]
        ])
    else:
        text = "🤝 **Tranzacțiile Tale Active Escrow:**\n\n"
        keyboard_buttons = []
        for row in rows:
            e_id, amt, stat = row
            text += f"• ID #{e_id} | Sumă: `{amt} USDT`\n"
            keyboard_buttons.append([InlineKeyboardButton(text=f"Gestionează Escrow #{e_id}", callback_data=f"manage_escrow_{e_id}")])
        
        keyboard_buttons.append([InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "escrow_history")
async def process_escrow_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT escrow_id, amount, status FROM escrows WHERE buyer_id = ? AND status != 'active'", (user_id,)) as cursor:
            rows = await cursor.fetchall()
    
    if not rows:
        text = "📜 **Istoric Tranzacții**\n\nNu există tranzacții finalizate în istoric."
    else:
        text = "📜 **Istoric Tranzacții Escrow:**\n\n"
        for row in rows:
            e_id, amt, stat = row
            icon = "✅" if stat == "released" else "❌"
            text += f"{icon} ID #{e_id} | Sumă: `{amt} USDT` | Status: *{stat}*\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")]
    ])
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "settings")
async def process_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT full_name FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            name = row[0] if row else "Utilizator"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠️ Suport & Ajutor", callback_data="support")],
        [InlineKeyboardButton(text="⬅️ Înapoi la Meniu", callback_data="back_to_menu")]
    ])
    await callback.answer()
    await callback.message.edit_text(
        f"⚙️ **Setări Cont**\n\n"
        f"• Nume: {name}\n"
        f"• ID Telegram: `{user_id}`\n"
        f"• Status: `Verificat & Securizat ✅`\n\n"
        f"Alege o opțiune de mai jos:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Înapoi la Setări", callback_data="settings")]
    ])
    await callback.answer()
    await callback.message.edit_text(
        "🛠️ **Suport Tehnic Vintage Ecosystem**\n\n"
        "Pentru orice problemă legată de tranzacțiile Escrow sau reîncărcarea testnet, sistemul funcționează automat pe baza bazei de date SQLite locale.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("manage_escrow_"))
async def process_manage_escrow(callback: CallbackQuery):
    escrow_id = int(callback.data.split("_")[2])
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT amount, status FROM escrows WHERE escrow_id = ?", (escrow_id,)) as cursor:
            row = await cursor.fetchone()
    
    if not row:
        await callback.answer("Tranzacția nu a fost găsită!", show_alert=True)
        return
    
    amount, status = row
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Eliberează (Release)", callback_data=f"release_{escrow_id}"),
            InlineKeyboardButton(text="❌ Returnează (Refund)", callback_data=f"refund_{escrow_id}")
        ],
        [InlineKeyboardButton(text="⬅️ Înapoi la Listă", callback_data="escrow_list")]
    ])
    
    await callback.answer()
    await callback.message.edit_text(
        f"🛡️ **Detaliu Escrow #[{escrow_id}]**\n\n"
        f"• Sumă: `{amount} USDT`\n"
        f"• Status: `{status}`\n\n"
        f"Alege o acțiune:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_menu")
async def process_back(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Portofel & Sold", callback_data="wallet")],
        [InlineKeyboardButton(text="🤝 Tranzacții Active Escrow", callback_data="escrow_list")],
        [InlineKeyboardButton(text="📜 Istoric Tranzacții", callback_data="escrow_history")],
        [InlineKeyboardButton(text="⚙️ Setări Cont", callback_data="settings")]
    ])
    await callback.answer()
    await callback.message.edit_text(
        "⚡ **Vintage Ecosystem Hub**\n\nAlege o secțiune de mai jos:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("release_"))
async def process_release(callback: CallbackQuery):
    escrow_id = int(callback.data.split("_")[1])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE escrows SET status = 'released' WHERE escrow_id = ?", (escrow_id,))
        await db.commit()

    await callback.answer("Fondurile au fost eliberate cu succes!")
    await callback.message.edit_text(f"✅ **Escrow #[{escrow_id}] Finalizat**\n\nFondurile au fost eliberate către vânzător.", parse_mode="Markdown")

@dp.callback_query(F.data.startswith("refund_"))
async def process_refund(callback: CallbackQuery):
    escrow_id = int(callback.data.split("_")[1])
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT buyer_id, amount FROM escrows WHERE escrow_id = ?", (escrow_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                buyer_id, amount = row
                await db.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (amount, buyer_id))
                await db.execute("UPDATE escrows SET status = 'refunded' WHERE escrow_id = ?", (escrow_id,))
                await db.commit()

    await callback.answer("Tranzacția a fost anulată și banii returnați!")
    await callback.message.edit_text(f"❌ **Escrow #[{escrow_id}] Anulat & Returnat**\n\nSuma a fost restituită în soldul tău.", parse_mode="Markdown")

async def main():
    await init_db()
    print("Botul rulează complet: Portofel, Escrow, Istoric și Setări active...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

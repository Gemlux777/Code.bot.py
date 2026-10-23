import secrets
import string

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

CHARSETS = {
    "letters": string.ascii_letters,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.<>?",
}


class PasswordStates(StatesGroup):
    waiting_length = State()


def build_charset(use_digits: bool, use_symbols: bool) -> str:
    charset = CHARSETS["letters"]
    if use_digits:
        charset += CHARSETS["digits"]
    if use_symbols:
        charset += CHARSETS["symbols"]
    return charset


def generate_password(length: int, use_digits: bool, use_symbols: bool) -> str:
    charset = build_charset(use_digits, use_symbols)
    return "".join(secrets.choice(charset) for _ in range(length))


@router.callback_query(F.data == "menu_password")
async def ask_length(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PasswordStates.waiting_length)
    await callback.message.edit_text(
        "Введи длину пароля (от 8 до 64).\n"
        "Например: <code>16</code>"
    )
    await callback.answer()


@router.message(PasswordStates.waiting_length)
async def process_length(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text.isdigit() or not (8 <= int(text) <= 64):
        await message.answer("❌ Нужно число от 8 до 64. Попробуй ещё раз.")
        return

    length = int(text)
    await state.update_data(length=length, use_digits=True, use_symbols=True)
    await message.answer(
        "Длина: {}. Выбери наборы символов:".format(length),
        reply_markup=charset_keyboard(use_digits=True, use_symbols=True)
    )


def charset_keyboard(use_digits: bool, use_symbols: bool) -> InlineKeyboardMarkup:
    def mark(flag: bool) -> str:
        return "✅" if flag else "❌"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{mark(use_digits)} Цифры",
            callback_data="tgl_digits")],
        [InlineKeyboardButton(
            text=f"{mark(use_symbols)} Символы",
            callback_data="tgl_symbols")],
        [InlineKeyboardButton(text="🎲 Сгенерировать", callback_data="gen_password")],
    ])


@router.callback_query(F.data.startswith("tgl_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    use_digits = data.get("use_digits", True)
    use_symbols = data.get("use_symbols", True)

    if callback.data == "tgl_digits":
        use_digits = not use_digits
    else:
        use_symbols = not use_symbols

    await state.update_data(use_digits=use_digits, use_symbols=use_symbols)
    await callback.message.edit_reply_markup(
        reply_markup=charset_keyboard(use_digits, use_symbols)
    )
    await callback.answer()


@router.callback_query(F.data == "gen_password")
async def gen_password(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    length = data.get("length", 16)
    use_digits = data.get("use_digits", True)
    use_symbols = data.get("use_symbols", True)

    pwd = generate_password(length, use_digits, use_symbols)
    await callback.message.edit_text(
        "🔐 Твой пароль:\n"
        f"<code>{pwd}</code>\n\n"
        "Нажми на пароль — он скопируется."
    )
    await state.clear()
    await callback.answer()

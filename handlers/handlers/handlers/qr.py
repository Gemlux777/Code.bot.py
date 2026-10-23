import io

import qrcode
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()


class QRStates(StatesGroup):
    waiting_text = State()


@router.callback_query(F.data == "menu_qr")
async def ask_qr_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QRStates.waiting_text)
    await callback.message.edit_text(
        "Отправь текст или ссылку — я сделаю QR-код 📱"
    )
    await callback.answer()


@router.message(QRStates.waiting_text)
async def make_qr(message: Message, state: FSMContext):
    if not message.text or len(message.text) > 1000:
        await message.answer("❌ Отправь текст до 1000 символов.")
        return

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(message.text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    photo = BufferedInputFile(buffer.read(), filename="qr.png")
    await message.answer_photo(
        photo,
        caption="Готово! 📱 Сохрани или перешли картинку."
    )
    await state.clear()

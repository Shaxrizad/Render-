from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
from gost_data import (
    calc_ugolok, calc_shveller,
    calc_beton_kub, calc_beton_silindr,
    calc_kotlovan_turtburchak, calc_kotlovan_silindr,
    BETON_MARKALAR, SHVELLER_DATA, format_og
)

router = Router()


# ══════════════════════════════════════════════════════════════
#  UGOLOK
# ══════════════════════════════════════════════════════════════
class UgolokState(StatesGroup):
    tomon = State()
    qalinlik = State()
    uzunlik = State()
    miqdor = State()


@router.callback_query(F.data == "cat:ugolok")
async def ugolok_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UgolokState.tomon)
    await cb.message.edit_text(
        "📐 <b>Ugolok — GOST 8509-93</b>\n\n"
        "Tomon o'lchamini tanlang (mm):",
        reply_markup=kb.ugolok_tomon(),
        parse_mode="HTML"
    )


@router.callback_query(UgolokState.tomon, F.data.startswith("ugl_t:"))
async def ugolok_tomon_sel(cb: CallbackQuery, state: FSMContext):
    tomon = int(cb.data.split(":")[1])
    await state.update_data(tomon=tomon)
    await state.set_state(UgolokState.qalinlik)
    await cb.message.edit_text(
        f"✅ Tomon: <b>{tomon}×{tomon} mm</b>\n\n"
        f"Devor qalinligini tanlang:",
        reply_markup=kb.ugolok_qalinlik(tomon),
        parse_mode="HTML"
    )


@router.callback_query(UgolokState.qalinlik, F.data.startswith("ugl_q:"))
async def ugolok_qalinlik_sel(cb: CallbackQuery, state: FSMContext):
    qalinlik = int(cb.data.split(":")[1])
    await state.update_data(qalinlik=qalinlik)
    data = await state.get_data()
    from gost_data import UGOLOK_DATA
    kg_m = UGOLOK_DATA.get((data["tomon"], qalinlik), 0)
    await state.update_data(kg_m=kg_m)
    await state.set_state(UgolokState.uzunlik)
    await cb.message.edit_text(
        f"✅ {data['tomon']}×{data['tomon']}×{qalinlik} mm → <b>{kg_m} kg/m</b>\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n<i>Masalan: 6</i>",
        parse_mode="HTML"
    )


@router.message(UgolokState.uzunlik)
async def ugolok_uzunlik(msg: Message, state: FSMContext):
    try:
        uzunlik = float(msg.text.replace(",", "."))
        if uzunlik <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>6</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=uzunlik)
    await state.set_state(UgolokState.miqdor)
    await msg.answer(f"✅ Uzunlik: <b>{uzunlik} m</b>\n\n🔢 Miqdorni kiriting <b>(dona)</b>:", parse_mode="HTML")


@router.message(UgolokState.miqdor)
async def ugolok_miqdor(msg: Message, state: FSMContext):
    try:
        miqdor = int(msg.text)
        if miqdor <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Butun son kiriting. Masalan: <b>10</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    res = calc_ugolok(data["tomon"], data["qalinlik"], data["uzunlik"], miqdor)
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Ugolok</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 8509-93\n"
        f"📐 O'lcham: {data['tomon']}×{data['tomon']}×{data['qalinlik']} mm\n"
        f"📏 Uzunlik: {data['uzunlik']} m\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 metr: <b>{res['kg_m']} kg/m</b>\n"
        f"⚖️ 1 ta: <b>{format_og(res['bir_ta_kg'])}</b>\n"
        f"{'─' * 30}\n"
        f"✅ Jami og'irlik: <b>{format_og(res['jami_kg'])}</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


# ══════════════════════════════════════════════════════════════
#  SHVELLER
# ══════════════════════════════════════════════════════════════
class ShvellerState(StatesGroup):
    nomer = State()
    uzunlik = State()
    miqdor = State()


@router.callback_query(F.data == "cat:shveller")
async def shveller_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ShvellerState.nomer)
    await cb.message.edit_text(
        "🔷 <b>Shveller — GOST 8240-97</b>\n\n"
        "Shveller nomerini tanlang:",
        reply_markup=kb.shveller_nomer(),
        parse_mode="HTML"
    )


@router.callback_query(ShvellerState.nomer, F.data.startswith("shv_n:"))
async def shveller_nomer_sel(cb: CallbackQuery, state: FSMContext):
    nomer = float(cb.data.split(":")[1])
    kg_m = SHVELLER_DATA.get(nomer, 0)
    await state.update_data(nomer=nomer, kg_m=kg_m)
    await state.set_state(ShvellerState.uzunlik)
    label = f"№{int(nomer)}" if nomer == int(nomer) else f"№{nomer}"
    await cb.message.edit_text(
        f"✅ Shveller {label} → <b>{kg_m} kg/m</b>\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n<i>Masalan: 6</i>",
        parse_mode="HTML"
    )


@router.message(ShvellerState.uzunlik)
async def shveller_uzunlik(msg: Message, state: FSMContext):
    try:
        uzunlik = float(msg.text.replace(",", "."))
        if uzunlik <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>6</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=uzunlik)
    await state.set_state(ShvellerState.miqdor)
    await msg.answer(f"✅ Uzunlik: <b>{uzunlik} m</b>\n\n🔢 Miqdorni kiriting <b>(dona)</b>:", parse_mode="HTML")


@router.message(ShvellerState.miqdor)
async def shveller_miqdor(msg: Message, state: FSMContext):
    try:
        miqdor = int(msg.text)
        if miqdor <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Butun son kiriting. Masalan: <b>5</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    res = calc_shveller(data["nomer"], data["uzunlik"], miqdor)
    nomer = data["nomer"]
    label = f"№{int(nomer)}" if nomer == int(nomer) else f"№{nomer}"
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Shveller</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 8240-97\n"
        f"🔷 Nomer: {label}\n"
        f"📏 Uzunlik: {data['uzunlik']} m\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 metr: <b>{res['kg_m']} kg/m</b>\n"
        f"⚖️ 1 ta: <b>{format_og(res['bir_ta_kg'])}</b>\n"
        f"{'─' * 30}\n"
        f"✅ Jami og'irlik: <b>{format_og(res['jami_kg'])}</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


# ══════════════════════════════════════════════════════════════
#  BETON
# ══════════════════════════════════════════════════════════════
class BetonState(StatesGroup):
    shakl = State()
    uzunlik = State()
    kenglik = State()
    balandlik = State()
    diametr = State()


@router.callback_query(F.data == "cat:beton")
async def beton_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "🏗️ <b>Beton hisoblash</b>\n\n"
        "Nima qilmoqchisiz?",
        reply_markup=kb.beton_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "beton:info")
async def beton_info(cb: CallbackQuery, state: FSMContext):
    text = "📋 <b>Beton markasi va sinflari</b>\n"
    text += f"{'─' * 32}\n"
    for marka, info in BETON_MARKALAR.items():
        text += (
            f"<b>{marka}</b> → Sinf: {info['sinf']} | {info['mustahkamlik']}\n"
            f"   └ {info['ishlatish']}\n"
        )
    text += f"{'─' * 32}\n"
    text += "<i>Zichlik: 2400 kg/m³ (oddiy beton)</i>"
    await cb.message.edit_text(text, reply_markup=kb.back_to_main(), parse_mode="HTML")


@router.callback_query(F.data == "beton:hisob")
async def beton_hisob(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BetonState.shakl)
    await cb.message.edit_text(
        "🏗️ <b>Beton hajmi hisoblash</b>\n\n"
        "Shaklni tanlang:",
        reply_markup=kb.beton_shakl(),
        parse_mode="HTML"
    )


@router.callback_query(BetonState.shakl, F.data.startswith("beton_sh:"))
async def beton_shakl_sel(cb: CallbackQuery, state: FSMContext):
    shakl = cb.data.split(":")[1]
    await state.update_data(shakl=shakl)
    if shakl == "turtburchak":
        await state.set_state(BetonState.uzunlik)
        await cb.message.edit_text(
            "⬛ <b>To'rtburchak beton</b>\n\n"
            "📏 Uzunlikni kiriting <b>(metrda)</b>:\n<i>Masalan: 6</i>",
            parse_mode="HTML"
        )
    else:
        await state.set_state(BetonState.diametr)
        await cb.message.edit_text(
            "⭕ <b>Silindr beton (ustun)</b>\n\n"
            "📏 Diametrni kiriting <b>(metrda)</b>:\n<i>Masalan: 0.4</i>",
            parse_mode="HTML"
        )


@router.message(BetonState.uzunlik)
async def beton_uzunlik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>6</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=v)
    await state.set_state(BetonState.kenglik)
    await msg.answer(f"✅ Uzunlik: <b>{v} m</b>\n\n📏 Kenglikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.message(BetonState.kenglik)
async def beton_kenglik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(kenglik=v)
    await state.set_state(BetonState.balandlik)
    await msg.answer(f"✅ Kenglik: <b>{v} m</b>\n\n📏 Balandlik/qalinlikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.message(BetonState.balandlik)
async def beton_balandlik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    data = await state.get_data()
    res = calc_beton_kub(data["uzunlik"], data["kenglik"], v)
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Beton</b>\n"
        f"{'─' * 30}\n"
        f"⬛ Shakl: To'rtburchak\n"
        f"📏 {data['uzunlik']} m × {data['kenglik']} m × {v} m\n"
        f"{'─' * 30}\n"
        f"📦 Hajm: <b>{res['hajm_m3']:.3f} m³</b>\n"
        f"⚖️ Og'irlik: <b>{res['og_irlik_t']:.2f} t ({res['og_irlik_kg']:.0f} kg)</b>\n"
        f"{'─' * 30}\n"
        f"<i>Zichlik: 2400 kg/m³</i>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(BetonState.diametr)
async def beton_diametr(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>0.4</b>", parse_mode="HTML")
        return
    await state.update_data(diametr=v)
    await state.set_state(BetonState.balandlik)
    await msg.answer(f"✅ Diametr: <b>{v} m</b>\n\n📏 Balandlikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.callback_query(F.data.startswith("beton_m:"))
async def beton_marka_info(cb: CallbackQuery, state: FSMContext):
    marka = cb.data.split(":")[1]
    info = BETON_MARKALAR.get(marka, {})
    await cb.message.edit_text(
        f"📋 <b>Beton {marka}</b>\n"
        f"{'─' * 30}\n"
        f"🏷️ Sinf: <b>{info.get('sinf', '—')}</b>\n"
        f"💪 Mustahkamlik: <b>{info.get('mustahkamlik', '—')}</b>\n"
        f"🏗️ Ishlatish: {info.get('ishlatish', '—')}\n"
        f"{'─' * 30}\n"
        f"<i>Zichlik: 2400 kg/m³</i>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )


# ══════════════════════════════════════════════════════════════
#  KOTLOVAN
# ══════════════════════════════════════════════════════════════
class KotlovanState(StatesGroup):
    shakl = State()
    uzunlik = State()
    kenglik = State()
    chuqurlik = State()
    qiyalik = State()
    diametr = State()
    chuqurlik_d = State()
    qiyalik_d = State()


@router.callback_query(F.data == "cat:kotlovan")
async def kotlovan_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(KotlovanState.shakl)
    await cb.message.edit_text(
        "⛏️ <b>Kotlovan hajmi hisoblash</b>\n\n"
        "Kotlovan shaklini tanlang:",
        reply_markup=kb.kotlovan_shakl(),
        parse_mode="HTML"
    )


@router.callback_query(KotlovanState.shakl, F.data.startswith("kot_sh:"))
async def kotlovan_shakl_sel(cb: CallbackQuery, state: FSMContext):
    shakl = cb.data.split(":")[1]
    await state.update_data(shakl=shakl)
    if shakl == "turtburchak":
        await state.set_state(KotlovanState.uzunlik)
        await cb.message.edit_text(
            "⬛ <b>To'rtburchak kotlovan</b>\n\n"
            "📏 Uzunlikni kiriting <b>(pastki o'lcham, metrda)</b>:\n<i>Masalan: 10</i>",
            parse_mode="HTML"
        )
    else:
        await state.set_state(KotlovanState.diametr)
        await cb.message.edit_text(
            "⭕ <b>Silindr/Doira kotlovan</b>\n\n"
            "📏 Pastki diametrni kiriting <b>(metrda)</b>:\n<i>Masalan: 5</i>",
            parse_mode="HTML"
        )


@router.message(KotlovanState.uzunlik)
async def kotlovan_uzunlik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(uzunlik=v)
    await state.set_state(KotlovanState.kenglik)
    await msg.answer(f"✅ Uzunlik: <b>{v} m</b>\n\n📏 Kenglikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.message(KotlovanState.kenglik)
async def kotlovan_kenglik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(kenglik=v)
    await state.set_state(KotlovanState.chuqurlik)
    await msg.answer(f"✅ Kenglik: <b>{v} m</b>\n\n📏 Chuqurlikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.message(KotlovanState.chuqurlik)
async def kotlovan_chuqurlik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(chuqurlik=v)
    await state.set_state(KotlovanState.qiyalik)
    await msg.answer(
        f"✅ Chuqurlik: <b>{v} m</b>\n\n"
        f"📐 Yon qiyalikni kiriting <b>(m/m)</b>:\n"
        f"<i>Qiyaliksiz → 0\n"
        f"1:1 qiyalik → 1\n"
        f"1:0.5 qiyalik → 0.5</i>",
        parse_mode="HTML"
    )


@router.message(KotlovanState.qiyalik)
async def kotlovan_qiyalik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v < 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>0</b> yoki <b>0.5</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    res = calc_kotlovan_turtburchak(data["uzunlik"], data["kenglik"], data["chuqurlik"], v)
    qiyalik_text = f"1:{v}" if v > 0 else "Yo'q"
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Kotlovan</b>\n"
        f"{'─' * 30}\n"
        f"⬛ Shakl: To'rtburchak\n"
        f"📏 Pastki: {data['uzunlik']} × {data['kenglik']} m\n"
        f"📏 Yuqori: {res['yuqori_uzun']:.2f} × {res['yuqori_keng']:.2f} m\n"
        f"📏 Chuqurlik: {data['chuqurlik']} m\n"
        f"📐 Qiyalik: {qiyalik_text}\n"
        f"{'─' * 30}\n"
        f"📦 Hajm: <b>{res['hajm_m3']:.2f} m³</b>\n"
        f"🚛 Tashish: <b>{res['hajm_m3'] / 10:.1f} ta KamAZ</b> (~10 m³)\n"
        f"{'─' * 30}\n"
        f"<i>Yon maydon: {res['yon_maydon']:.1f} m²</i>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(KotlovanState.diametr)
async def kotlovan_diametr(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(diametr=v)
    await state.set_state(KotlovanState.chuqurlik_d)
    await msg.answer(f"✅ Diametr: <b>{v} m</b>\n\n📏 Chuqurlikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


@router.message(KotlovanState.chuqurlik_d)
async def kotlovan_chuqurlik_d(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(chuqurlik=v)
    await state.set_state(KotlovanState.qiyalik_d)
    await msg.answer(
        f"✅ Chuqurlik: <b>{v} m</b>\n\n"
        f"📐 Qiyalikni kiriting <b>(m/m)</b>:\n"
        f"<i>Qiyaliksiz → 0</i>",
        parse_mode="HTML"
    )


@router.message(KotlovanState.qiyalik_d)
async def kotlovan_qiyalik_d(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v < 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    data = await state.get_data()
    res = calc_kotlovan_silindr(data["diametr"], data["chuqurlik"], v)
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Kotlovan</b>\n"
        f"{'─' * 30}\n"
        f"⭕ Shakl: Silindr\n"
        f"📏 Pastki diametr: {data['diametr']} m\n"
        f"📏 Yuqori diametr: {res['diametr_yuqori']:.2f} m\n"
        f"📏 Chuqurlik: {data['chuqurlik']} m\n"
        f"{'─' * 30}\n"
        f"📦 Hajm: <b>{res['hajm_m3']:.2f} m³</b>\n"
        f"🚛 Tashish: <b>{res['hajm_m3'] / 10:.1f} ta KamAZ</b> (~10 m³)",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()

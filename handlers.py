from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart

import keyboards as kb
from gost_data import (
    calc_armatura, calc_kvadrat_truba, calc_turtburchak_truba,
    calc_list, format_og, ARMATURA_WEIGHTS
)

router = Router()


# ─── FSM States ───────────────────────────────────────────────
class ArmState(StatesGroup):
    sinf = State()
    diametr = State()
    uzunlik = State()
    miqdor = State()


class TrubaState(StatesGroup):
    tur = State()
    tomon_a = State()
    tomon_b = State()
    devor = State()
    uzunlik = State()
    miqdor = State()


class ListState(StatesGroup):
    qalinlik = State()
    material = State()
    kenglik = State()
    uzunlik = State()
    miqdor = State()


# ─── START ────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "👋 Assalomu alaykum!\n\n"
        "🏗️ <b>Metall og'irlik kalkulyatori</b>\n"
        "GOST standartlari asosida hisoblash\n\n"
        "Qaysi kategoriyani hisoblaysiz?",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )


# ─── BACK TO MAIN ─────────────────────────────────────────────
@router.callback_query(F.data == "back:main")
async def back_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        "🏗️ <b>Metall og'irlik kalkulyatori</b>\n\n"
        "Qaysi kategoriyani hisoblaysiz?",
        reply_markup=kb.main_menu(),
        parse_mode="HTML"
    )


# ══════════════════════════════════════════════════════════════
#  ARMATURA
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data == "cat:armatura")
async def arm_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ArmState.diametr)
    await cb.message.edit_text(
        "🔩 <b>Armatura — GOST 5781-82</b>\n\n"
        "Diametrni tanlang:",
        reply_markup=kb.armatura_diametr(),
        parse_mode="HTML"
    )


@router.callback_query(ArmState.diametr, F.data.startswith("arm_d:"))
async def arm_diametr(cb: CallbackQuery, state: FSMContext):
    d = int(cb.data.split(":")[1])
    kg_m = ARMATURA_WEIGHTS[d]
    await state.update_data(diametr=d, kg_m=kg_m)
    await state.set_state(ArmState.sinf)
    await cb.message.edit_text(
        f"✅ Diametr: <b>Ø{d} mm</b> ({kg_m} kg/m)\n\n"
        f"Armatura sinfini tanlang:",
        reply_markup=kb.armatura_sinf(),
        parse_mode="HTML"
    )


@router.callback_query(ArmState.sinf, F.data.startswith("arm_s:"))
async def arm_sinf(cb: CallbackQuery, state: FSMContext):
    sinf = cb.data.split(":")[1]
    await state.update_data(sinf=sinf)
    await state.set_state(ArmState.uzunlik)
    await cb.message.edit_text(
        f"✅ Sinf: <b>{sinf}</b>\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n"
        f"<i>Masalan: 6 yoki 11.7</i>",
        parse_mode="HTML"
    )


@router.message(ArmState.uzunlik)
async def arm_uzunlik(msg: Message, state: FSMContext):
    try:
        uzunlik = float(msg.text.replace(",", "."))
        if uzunlik <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Iltimos, to'g'ri son kiriting. Masalan: <b>6</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=uzunlik)
    await state.set_state(ArmState.miqdor)
    await msg.answer(
        f"✅ Uzunlik: <b>{uzunlik} m</b>\n\n"
        f"🔢 Miqdorni kiriting <b>(dona)</b>:",
        parse_mode="HTML"
    )


@router.message(ArmState.miqdor)
async def arm_miqdor(msg: Message, state: FSMContext):
    try:
        miqdor = int(msg.text)
        if miqdor <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Iltimos, butun son kiriting. Masalan: <b>10</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    res = calc_armatura(data["diametr"], data["uzunlik"], miqdor)

    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Armatura</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 5781-82\n"
        f"🔩 Diametr: Ø{data['diametr']} mm\n"
        f"📋 Sinf: {data['sinf']}\n"
        f"📏 Uzunlik: {data['uzunlik']} m\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 metr: <b>{data['kg_m']} kg/m</b>\n"
        f"⚖️ 1 ta: <b>{format_og(res['bir_ta_kg'])}</b>\n"
        f"{'─' * 30}\n"
        f"✅ Jami og'irlik: <b>{format_og(res['jami_kg'])}</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


# ══════════════════════════════════════════════════════════════
#  PROFILNAYA TRUBA
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data == "cat:truba")
async def truba_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(TrubaState.tur)
    await cb.message.edit_text(
        "⬛ <b>Profilnaya truba</b>\n"
        "GOST 8645-68 / GOST 8639-82\n\n"
        "Truba turini tanlang:",
        reply_markup=kb.truba_tur(),
        parse_mode="HTML"
    )


@router.callback_query(TrubaState.tur, F.data.startswith("truba:"))
async def truba_tur_select(cb: CallbackQuery, state: FSMContext):
    tur = cb.data.split(":")[1]
    await state.update_data(tur=tur)

    if tur == "kvadrat":
        await state.set_state(TrubaState.tomon_a)
        await cb.message.edit_text(
            "□ <b>Kvadrat truba</b>\n\n"
            "Tomon o'lchamini tanlang (mm):",
            reply_markup=kb.kvadrat_truba_tomon(),
            parse_mode="HTML"
        )
    else:
        await state.set_state(TrubaState.tomon_a)
        await cb.message.edit_text(
            "▭ <b>To'rtburchak truba</b>\n\n"
            "📐 Kenglik <b>A</b> ni kiriting (mm):\n"
            "<i>Masalan: 40</i>",
            parse_mode="HTML"
        )


@router.callback_query(TrubaState.tomon_a, F.data.startswith("truba_kv:"))
async def truba_kvadrat_tomon(cb: CallbackQuery, state: FSMContext):
    tomon = int(cb.data.split(":")[1])
    await state.update_data(tomon_a=tomon, tomon_b=tomon)
    await state.set_state(TrubaState.devor)
    await cb.message.edit_text(
        f"✅ O'lcham: <b>{tomon}×{tomon} mm</b>\n\n"
        f"Devor qalinligini tanlang:",
        reply_markup=kb.truba_devor(),
        parse_mode="HTML"
    )


@router.message(TrubaState.tomon_a)
async def truba_tomon_a_input(msg: Message, state: FSMContext):
    try:
        a = float(msg.text.replace(",", "."))
        if a <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>40</b>", parse_mode="HTML")
        return
    await state.update_data(tomon_a=a)
    await state.set_state(TrubaState.tomon_b)
    await msg.answer(
        f"✅ Kenglik A: <b>{a} mm</b>\n\n"
        f"📐 Balandlik <b>B</b> ni kiriting (mm):\n"
        f"<i>Masalan: 60</i>",
        parse_mode="HTML"
    )


@router.message(TrubaState.tomon_b)
async def truba_tomon_b_input(msg: Message, state: FSMContext):
    try:
        b = float(msg.text.replace(",", "."))
        if b <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>60</b>", parse_mode="HTML")
        return
    await state.update_data(tomon_b=b)
    await state.set_state(TrubaState.devor)
    data = await state.get_data()
    await msg.answer(
        f"✅ O'lcham: <b>{data['tomon_a']}×{b} mm</b>\n\n"
        f"Devor qalinligini tanlang:",
        reply_markup=kb.truba_devor()
    )


@router.callback_query(TrubaState.devor, F.data.startswith("truba_dv:"))
async def truba_devor_select(cb: CallbackQuery, state: FSMContext):
    devor = float(cb.data.split(":")[1])
    await state.update_data(devor=devor)
    await state.set_state(TrubaState.uzunlik)
    await cb.message.edit_text(
        f"✅ Devor: <b>{devor} mm</b>\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n"
        f"<i>Masalan: 6</i>",
        parse_mode="HTML"
    )


@router.message(TrubaState.uzunlik)
async def truba_uzunlik(msg: Message, state: FSMContext):
    try:
        uzunlik = float(msg.text.replace(",", "."))
        if uzunlik <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>6</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=uzunlik)
    await state.set_state(TrubaState.miqdor)
    await msg.answer(
        f"✅ Uzunlik: <b>{uzunlik} m</b>\n\n"
        f"🔢 Miqdorni kiriting <b>(dona)</b>:",
        parse_mode="HTML"
    )


@router.message(TrubaState.miqdor)
async def truba_miqdor(msg: Message, state: FSMContext):
    try:
        miqdor = int(msg.text)
        if miqdor <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Butun son kiriting. Masalan: <b>5</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    tur = data["tur"]
    a, b = data["tomon_a"], data["tomon_b"]
    devor, uzunlik = data["devor"], data["uzunlik"]

    if tur == "kvadrat":
        res = calc_kvadrat_truba(a, devor, uzunlik, miqdor)
        olcham = f"{int(a)}×{int(a)} mm"
        standart = "GOST 8639-82"
        nom = "Kvadrat truba"
    else:
        res = calc_turtburchak_truba(a, b, devor, uzunlik, miqdor)
        olcham = f"{a}×{b} mm"
        standart = "GOST 8645-68"
        nom = "To'rtburchak truba"

    await msg.answer(
        f"📊 <b>Hisoblash natijasi — {nom}</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: {standart}\n"
        f"📐 O'lcham: {olcham}\n"
        f"📏 Devor: {devor} mm\n"
        f"📏 Uzunlik: {uzunlik} m\n"
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
#  METALL LIST
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data == "cat:list")
async def list_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ListState.qalinlik)
    await cb.message.edit_text(
        "📄 <b>Metall list — GOST 19903-74</b>\n\n"
        "Qalinlikni tanlang:",
        reply_markup=kb.list_qalinlik(),
        parse_mode="HTML"
    )


@router.callback_query(ListState.qalinlik, F.data.startswith("list_q:"))
async def list_qalinlik_select(cb: CallbackQuery, state: FSMContext):
    q = float(cb.data.split(":")[1])
    await state.update_data(qalinlik=q)
    await state.set_state(ListState.material)
    await cb.message.edit_text(
        f"✅ Qalinlik: <b>{q} mm</b>\n\n"
        f"Material turini tanlang:",
        reply_markup=kb.list_material(),
        parse_mode="HTML"
    )


@router.callback_query(ListState.material, F.data.startswith("list_mat:"))
async def list_material_select(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split(":")
    zichlik = float(parts[1])
    material_nomi = parts[2]
    await state.update_data(zichlik=zichlik, material_nomi=material_nomi)
    await state.set_state(ListState.kenglik)
    await cb.message.edit_text(
        f"✅ Material: <b>{material_nomi}</b>\n\n"
        f"📐 Kenglikni kiriting <b>(mm)</b>:\n"
        f"<i>Masalan: 1250</i>",
        parse_mode="HTML"
    )


@router.message(ListState.kenglik)
async def list_kenglik(msg: Message, state: FSMContext):
    try:
        k = float(msg.text.replace(",", "."))
        if k <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>1250</b>", parse_mode="HTML")
        return
    await state.update_data(kenglik=k)
    await state.set_state(ListState.uzunlik)
    await msg.answer(
        f"✅ Kenglik: <b>{k} mm</b>\n\n"
        f"📐 Uzunlikni kiriting <b>(mm)</b>:\n"
        f"<i>Masalan: 2500</i>",
        parse_mode="HTML"
    )


@router.message(ListState.uzunlik)
async def list_uzunlik(msg: Message, state: FSMContext):
    try:
        u = float(msg.text.replace(",", "."))
        if u <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>2500</b>", parse_mode="HTML")
        return
    await state.update_data(uzunlik=u)
    await state.set_state(ListState.miqdor)
    await msg.answer(
        f"✅ Uzunlik: <b>{u} mm</b>\n\n"
        f"🔢 Miqdorni kiriting <b>(dona)</b>:",
        parse_mode="HTML"
    )


@router.message(ListState.miqdor)
async def list_miqdor(msg: Message, state: FSMContext):
    try:
        miqdor = int(msg.text)
        if miqdor <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Butun son kiriting. Masalan: <b>10</b>", parse_mode="HTML")
        return

    data = await state.get_data()
    res = calc_list(data["qalinlik"], data["kenglik"], data["uzunlik"], miqdor, data["zichlik"])

    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Metall list</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 19903-74\n"
        f"🔩 Material: {data['material_nomi']}\n"
        f"📐 O'lcham: {data['kenglik']}×{data['uzunlik']} mm\n"
        f"📏 Qalinlik: {data['qalinlik']} mm\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 m² og'irligi: <b>{res['m2_og']:.2f} kg/m²</b>\n"
        f"⚖️ 1 ta list: <b>{format_og(res['bir_ta_kg'])}</b>\n"
        f"{'─' * 30}\n"
        f"✅ Jami og'irlik: <b>{format_og(res['jami_kg'])}</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


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
        "📐 <b>Ugolok (burchak po'lat) — GOST 8509-93</b>\n\n"
        "Teng yonli ugolok\n"
        "Tomon o'lchamini tanlang (mm):",
        reply_markup=kb.ugolok_tomon(),
        parse_mode="HTML"
    )


@router.callback_query(UgolokState.tomon, F.data.startswith("ugl_t:"))
async def ugolok_tomon_select(cb: CallbackQuery, state: FSMContext):
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
async def ugolok_qalinlik_select(cb: CallbackQuery, state: FSMContext):
    q = int(cb.data.split(":")[1])
    await state.update_data(qalinlik=q)
    data = await state.get_data()
    from gost_data import UGOLOK_DATA
    kg_m = UGOLOK_DATA.get(data["tomon"], {}).get(q, 0)
    await state.update_data(kg_m=kg_m)
    await state.set_state(UgolokState.uzunlik)
    await cb.message.edit_text(
        f"✅ Ugolok: <b>{data['tomon']}×{data['tomon']}×{q} mm</b>\n"
        f"1 metr: <b>{kg_m} kg/m</b>\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n"
        f"<i>Masalan: 6</i>",
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
    from gost_data import calc_ugolok, format_og
    res = calc_ugolok(data["tomon"], data["qalinlik"], data["uzunlik"], miqdor)
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Ugolok</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 8509-93\n"
        f"📐 O'lcham: {data['tomon']}×{data['tomon']}×{data['qalinlik']} mm\n"
        f"📏 Uzunlik: {data['uzunlik']} m\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 metr: <b>{data['kg_m']} kg/m</b>\n"
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
        "🔧 <b>Shveller — GOST 8240-97</b>\n\n"
        "Shveller raqamini tanlang:",
        reply_markup=kb.shveller_nomer(),
        parse_mode="HTML"
    )


@router.callback_query(ShvellerState.nomer, F.data.startswith("shv_n:"))
async def shveller_nomer_select(cb: CallbackQuery, state: FSMContext):
    nomer = float(cb.data.split(":")[1])
    from gost_data import SHVELLER_DATA
    d = SHVELLER_DATA.get(nomer, {})
    await state.update_data(nomer=nomer, kg_m=d.get("kg_m", 0), b=d.get("b", 0), h=d.get("h", 0))
    await state.set_state(ShvellerState.uzunlik)
    await cb.message.edit_text(
        f"✅ Shveller №<b>{nomer}</b>\n"
        f"O'lcham: <b>{d.get('h')}×{d.get('b')} mm</b> | {d.get('kg_m')} kg/m\n\n"
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
        await msg.answer("❌ Butun son kiriting.", parse_mode="HTML")
        return
    data = await state.get_data()
    from gost_data import calc_shveller, format_og
    res = calc_shveller(data["nomer"], data["uzunlik"], miqdor)
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Shveller</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 8240-97\n"
        f"🔧 Nomer: №{data['nomer']} ({data['h']}×{data['b']} mm)\n"
        f"📏 Uzunlik: {data['uzunlik']} m\n"
        f"🔢 Miqdor: {miqdor} dona\n"
        f"{'─' * 30}\n"
        f"⚖️ 1 metr: <b>{data['kg_m']} kg/m</b>\n"
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
    marka = State()
    uzunlik = State()
    kenglik = State()
    balandlik = State()


@router.callback_query(F.data == "cat:beton")
async def beton_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BetonState.marka)
    await cb.message.edit_text(
        "🏗️ <b>Beton hisoblash — GOST 26633-2015</b>\n\n"
        "Beton markasini tanlang:",
        reply_markup=kb.beton_marka(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "beton:info")
async def beton_info(cb: CallbackQuery):
    from gost_data import BETON_MARKALAR
    text = "📋 <b>Beton markasi va sinflari</b>\n" + "─" * 30 + "\n"
    for marka, info in BETON_MARKALAR.items():
        text += f"<b>{marka}</b> → {info['sinf']} | {info['tavsif']}\n"
    text += "\n<i>M — marka (kg/cm²), B — sinf (MPa)</i>"
    await cb.message.answer(text, parse_mode="HTML", reply_markup=kb.back_to_main())


@router.callback_query(BetonState.marka, F.data.startswith("beton_m:"))
async def beton_marka_select(cb: CallbackQuery, state: FSMContext):
    marka = cb.data.split(":")[1]
    from gost_data import BETON_MARKALAR
    info = BETON_MARKALAR.get(marka, {})
    await state.update_data(marka=marka)
    await state.set_state(BetonState.uzunlik)
    await cb.message.edit_text(
        f"✅ Marka: <b>{marka}</b> ({info.get('sinf')}) — {info.get('tavsif')}\n\n"
        f"📏 Uzunlikni kiriting <b>(metrda)</b>:\n<i>Masalan: 10</i>",
        parse_mode="HTML"
    )


@router.message(BetonState.uzunlik)
async def beton_uzunlik(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting. Masalan: <b>10</b>", parse_mode="HTML")
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
    await msg.answer(f"✅ Kenglik: <b>{v} m</b>\n\n📏 Balandlik/qalinlikni kiriting <b>(metrda)</b>:\n<i>Plita uchun masalan: 0.2</i>", parse_mode="HTML")


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
    from gost_data import calc_beton, BETON_MARKALAR
    res = calc_beton(data["uzunlik"], data["kenglik"], v, data["marka"])
    info = BETON_MARKALAR.get(data["marka"], {})
    await msg.answer(
        f"📊 <b>Hisoblash natijasi — Beton</b>\n"
        f"{'─' * 30}\n"
        f"📌 Standart: GOST 26633-2015\n"
        f"🏗️ Marka: <b>{data['marka']}</b> ({info.get('sinf')})\n"
        f"📐 O'lcham: {data['uzunlik']}×{data['kenglik']}×{v} m\n"
        f"⚖️ Zichlik: {res['zichlik']} kg/m³\n"
        f"{'─' * 30}\n"
        f"📦 Hajm: <b>{res['hajm_m3']:.3f} m³</b>\n"
        f"✅ Og'irlik: <b>{res['og_irlik_t']:.2f} t ({res['og_irlik_kg']:.0f} kg)</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()


# ══════════════════════════════════════════════════════════════
#  KOTLOVAN
# ══════════════════════════════════════════════════════════════
class KotlovanState(StatesGroup):
    shakl = State()
    uzunlik = State()
    kenglik = State()
    radius = State()
    chuqurlik = State()
    qiyalik = State()


@router.callback_query(F.data == "cat:kotlovan")
async def kotlovan_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(KotlovanState.shakl)
    await cb.message.edit_text(
        "⛏️ <b>Kotlovan hajmi hisoblash</b>\n\n"
        "Kotlovan shaklini tanlang:",
        reply_markup=kb.kotlovan_shakl(),
        parse_mode="HTML"
    )


@router.callback_query(KotlovanState.shakl, F.data.startswith("kotl:"))
async def kotlovan_shakl_select(cb: CallbackQuery, state: FSMContext):
    shakl = cb.data.split(":")[1]
    await state.update_data(shakl=shakl)
    if shakl == "turtburchak":
        await state.set_state(KotlovanState.uzunlik)
        await cb.message.edit_text(
            "⬛ <b>To'rtburchak kotlovan</b>\n\n"
            "📏 Uzunlikni kiriting <b>(metrda)</b>:\n<i>Pastki qism — eng kichik o'lcham</i>",
            parse_mode="HTML"
        )
    else:
        await state.set_state(KotlovanState.radius)
        await cb.message.edit_text(
            "⭕ <b>Doira kotlovan</b>\n\n"
            "📏 Radiusni kiriting <b>(metrda)</b>:\n<i>Pastki qism radiusi</i>",
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


@router.message(KotlovanState.radius)
async def kotlovan_radius(msg: Message, state: FSMContext):
    try:
        v = float(msg.text.replace(",", "."))
        if v <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ To'g'ri son kiriting.", parse_mode="HTML")
        return
    await state.update_data(radius=v)
    await state.set_state(KotlovanState.chuqurlik)
    await msg.answer(f"✅ Radius: <b>{v} m</b>\n\n📏 Chuqurlikni kiriting <b>(metrda)</b>:", parse_mode="HTML")


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
        f"🏔️ Tuproq qiyaligini tanlang:",
        reply_markup=kb.kotlovan_qiyalik(),
        parse_mode="HTML"
    )


@router.callback_query(KotlovanState.qiyalik, F.data.startswith("kotl_qiy:"))
async def kotlovan_qiyalik_select(cb: CallbackQuery, state: FSMContext):
    qiy = float(cb.data.split(":")[1])
    data = await state.get_data()
    from gost_data import calc_kotlovan_to_rtburchak, calc_kotlovan_doira

    if data["shakl"] == "turtburchak":
        res = calc_kotlovan_to_rtburchak(data["uzunlik"], data["kenglik"], data["chuqurlik"], qiy)
        olcham = f"{data['uzunlik']}×{data['kenglik']} m"
        nom = "To'rtburchak kotlovan"
        pastki = f"{res['pastki_m2']:.2f} m²"
        yuqori = f"{res['yuqori_m2']:.2f} m²"
    else:
        res = calc_kotlovan_doira(data["radius"], data["chuqurlik"], qiy)
        olcham = f"r={data['radius']} m"
        nom = "Doira kotlovan"
        pastki = f"{res['pastki_m2']} m²"
        yuqori = f"{res['yuqori_m2']} m²"

    qiy_text = {0: "Tik", 0.25: "1:0.25 qumloq", 0.5: "1:0.5 qorishmali", 0.75: "1:0.75 gil", 1.0: "1:1 yumshoq"}.get(qiy, str(qiy))

    await cb.message.edit_text(
        f"📊 <b>Hisoblash natijasi — {nom}</b>\n"
        f"{'─' * 30}\n"
        f"📐 O'lcham: {olcham}\n"
        f"📏 Chuqurlik: {data['chuqurlik']} m\n"
        f"🏔️ Qiyalik: {qiy_text}\n"
        f"{'─' * 30}\n"
        f"⬇️ Pastki maydon: <b>{pastki}</b>\n"
        f"⬆️ Yuqori maydon: <b>{yuqori}</b>\n"
        f"{'─' * 30}\n"
        f"✅ Jami hajm: <b>{res['hajm_m3']:.2f} m³</b>",
        reply_markup=kb.back_to_main(),
        parse_mode="HTML"
    )
    await state.clear()

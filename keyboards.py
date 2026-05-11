from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔩 Armatura", callback_data="cat:armatura")],
        [InlineKeyboardButton(text="⬛ Profilnaya truba", callback_data="cat:truba")],
        [InlineKeyboardButton(text="📄 Metall list", callback_data="cat:list")],
        [InlineKeyboardButton(text="📐 Ugolok", callback_data="cat:ugolok"),
         InlineKeyboardButton(text="🔷 Shveller", callback_data="cat:shveller")],
        [InlineKeyboardButton(text="🏗️ Beton", callback_data="cat:beton"),
         InlineKeyboardButton(text="⛏️ Kotlovan", callback_data="cat:kotlovan")],
    ])


def armatura_diametr() -> InlineKeyboardMarkup:
    diametrlar = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40]
    rows = []
    row = []
    for i, d in enumerate(diametrlar):
        row.append(InlineKeyboardButton(text=f"Ø{d}", callback_data=f"arm_d:{d}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def armatura_sinf() -> InlineKeyboardMarkup:
    sinflar = [
        ("A-I (A240)", "A1"), ("A-II (A300)", "A2"),
        ("A-III (A400)", "A3"), ("A-IV (A600)", "A4"), ("A-V (A800)", "A5"),
    ]
    rows = [[InlineKeyboardButton(text=n, callback_data=f"arm_s:{c}")] for n, c in sinflar]
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:armatura")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def truba_tur() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="□ Kvadrat truba", callback_data="truba:kvadrat")],
        [InlineKeyboardButton(text="▭ To'rtburchak truba", callback_data="truba:turtburchak")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")],
    ])


def truba_devor() -> InlineKeyboardMarkup:
    devorlar = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
    rows = []
    row = []
    for d in devorlar:
        row.append(InlineKeyboardButton(text=f"{d}mm", callback_data=f"truba_dv:{d}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:truba")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kvadrat_truba_tomon() -> InlineKeyboardMarkup:
    tomonlar = [20, 25, 30, 40, 50, 60, 80, 100, 120, 150]
    rows = []
    row = []
    for t in tomonlar:
        row.append(InlineKeyboardButton(text=f"{t}×{t}", callback_data=f"truba_kv:{t}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:truba")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def list_qalinlik() -> InlineKeyboardMarkup:
    qalinliklar = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20]
    rows = []
    row = []
    for q in qalinliklar:
        row.append(InlineKeyboardButton(text=f"{q}mm", callback_data=f"list_q:{q}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def list_material() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔩 Po'lat (7850 kg/m³)", callback_data="list_mat:7850:Polat")],
        [InlineKeyboardButton(text="🥈 Alyuminiy (2700 kg/m³)", callback_data="list_mat:2700:Alyuminiy")],
        [InlineKeyboardButton(text="🟤 Mis (8900 kg/m³)", callback_data="list_mat:8900:Mis")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:list")],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yana hisoblash", callback_data="back:main")],
    ])


# ─── UGOLOK ───────────────────────────────────────────────────
def ugolok_tomon() -> InlineKeyboardMarkup:
    from gost_data import UGOLOK_SIZES
    rows = []
    row = []
    for t in UGOLOK_SIZES:
        row.append(InlineKeyboardButton(text=f"{t}×{t}", callback_data=f"ugl_t:{t}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ugolok_qalinlik(tomon: int) -> InlineKeyboardMarkup:
    from gost_data import UGOLOK_QALINLIKLAR
    qalinliklar = UGOLOK_QALINLIKLAR.get(tomon, [])
    rows = [[InlineKeyboardButton(text=f"{q} mm", callback_data=f"ugl_q:{q}")] for q in qalinliklar]
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:ugolok")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── SHVELLER ─────────────────────────────────────────────────
def shveller_nomer() -> InlineKeyboardMarkup:
    from gost_data import SHVELLER_NOMERLAR
    rows = []
    row = []
    for n in SHVELLER_NOMERLAR:
        label = f"№{int(n)}" if n == int(n) else f"№{n}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"shv_n:{n}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── BETON ────────────────────────────────────────────────────
def beton_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Beton hajmi hisoblash", callback_data="beton:hisob")],
        [InlineKeyboardButton(text="📋 Marka → Sinf ma'lumoti", callback_data="beton:info")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")],
    ])


def beton_shakl() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬛ To'rtburchak", callback_data="beton_sh:turtburchak")],
        [InlineKeyboardButton(text="⭕ Silindr (ustun)", callback_data="beton_sh:silindr")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:beton")],
    ])


def beton_marka_list() -> InlineKeyboardMarkup:
    from gost_data import BETON_MARKALAR
    rows = []
    row = []
    for marka in BETON_MARKALAR.keys():
        row.append(InlineKeyboardButton(text=marka, callback_data=f"beton_m:{marka}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:beton")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── KOTLOVAN ─────────────────────────────────────────────────
def kotlovan_shakl() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬛ To'rtburchak", callback_data="kot_sh:turtburchak")],
        [InlineKeyboardButton(text="⭕ Silindr/Doira", callback_data="kot_sh:silindr")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")],
    ])


def ugolok_tomon() -> InlineKeyboardMarkup:
    tomonlar = [20, 25, 32, 36, 40, 45, 50, 56, 63, 70, 75, 80, 90, 100, 110, 120, 125, 140, 150, 160, 180, 200]
    rows = []
    row = []
    for t in tomonlar:
        row.append(InlineKeyboardButton(text=f"{t}", callback_data=f"ugl_t:{t}"))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ugolok_qalinlik(tomon: int) -> InlineKeyboardMarkup:
    from gost_data import UGOLOK_DATA
    qalinliklar = list(UGOLOK_DATA.get(tomon, {}).keys())
    rows = [[InlineKeyboardButton(text=f"{q} mm", callback_data=f"ugl_q:{q}")] for q in qalinliklar]
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:ugolok")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shveller_nomer() -> InlineKeyboardMarkup:
    nomerlar = [5, 6.5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36, 40]
    rows = []
    row = []
    for n in nomerlar:
        row.append(InlineKeyboardButton(text=f"№{n}", callback_data=f"shv_n:{n}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def beton_marka() -> InlineKeyboardMarkup:
    markalar = ["M100", "M150", "M200", "M250", "M300", "M350", "M400", "M450", "M500", "M600"]
    rows = []
    row = []
    for m in markalar:
        row.append(InlineKeyboardButton(text=m, callback_data=f"beton_m:{m}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="ℹ️ Marka haqida", callback_data="beton:info")])
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kotlovan_shakl() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬛ To'rtburchak", callback_data="kotl:turtburchak")],
        [InlineKeyboardButton(text="⭕ Doira", callback_data="kotl:doira")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")],
    ])


def kotlovan_qiyalik() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Tik (0°)", callback_data="kotl_qiy:0")],
        [InlineKeyboardButton(text="1:0.25 — qumloq", callback_data="kotl_qiy:0.25")],
        [InlineKeyboardButton(text="1:0.5 — qorishmali", callback_data="kotl_qiy:0.5")],
        [InlineKeyboardButton(text="1:0.75 — gil", callback_data="kotl_qiy:0.75")],
        [InlineKeyboardButton(text="1:1 — yumshoq tuproq", callback_data="kotl_qiy:1.0")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cat:kotlovan")],
    ])

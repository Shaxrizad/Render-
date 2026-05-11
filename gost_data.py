# GOST 5781-82 — Armatura og'irligi (kg/m)
ARMATURA_WEIGHTS = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    14: 1.208,
    16: 1.578,
    18: 1.998,
    20: 2.466,
    22: 2.984,
    25: 3.853,
    28: 4.834,
    32: 6.313,
    36: 7.990,
    40: 9.865,
}

ARMATURA_SINFLAR = ["A-I (A240)", "A-II (A300)", "A-III (A400)", "A-IV (A600)", "A-V (A800)"]

# Po'lat zichligi kg/m³
STEEL_DENSITY = 7850.0

# Profilnaya truba standart o'lchamlari (kvadrat) mm
KVADRAT_TRUBA_SIZES = [20, 25, 30, 40, 50, 60, 80, 100, 120, 150]

# Devor qalinliklari mm
DEVOR_QALINLIKLARI = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]

# Metall list qalinliklari mm
LIST_QALINLIKLARI = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20]

# Materiallar zichligi kg/m³
MATERIALLAR = {
    "Po'lat": 7850,
    "Alyuminiy": 2700,
    "Mis": 8900,
}


def calc_armatura(diametr: int, uzunlik: float, miqdor: int) -> dict:
    """Armatura og'irligini hisoblash"""
    kg_m = ARMATURA_WEIGHTS.get(diametr, 0)
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": kg_m,
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
    }


def calc_kvadrat_truba(tomon: float, devor: float, uzunlik: float, miqdor: int) -> dict:
    """Kvadrat profilnaya truba og'irligini hisoblash"""
    a = tomon / 1000
    t = devor / 1000
    kesim = a * a - (a - 2 * t) * (a - 2 * t)
    kg_m = kesim * STEEL_DENSITY
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": round(kg_m, 3),
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
    }


def calc_turtburchak_truba(a: float, b: float, devor: float, uzunlik: float, miqdor: int) -> dict:
    """To'rtburchak profilnaya truba og'irligini hisoblash"""
    am = a / 1000
    bm = b / 1000
    t = devor / 1000
    kesim = am * bm - (am - 2 * t) * (bm - 2 * t)
    kg_m = kesim * STEEL_DENSITY
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": round(kg_m, 3),
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
    }


def calc_list(qalinlik: float, kenglik: float, uzunlik: float, miqdor: int, zichlik: float = 7850) -> dict:
    """Metall list og'irligini hisoblash"""
    hajm = (qalinlik / 1000) * (kenglik / 1000) * (uzunlik / 1000)
    bir_ta = hajm * zichlik
    jami = bir_ta * miqdor
    m2_og = (qalinlik / 1000) * zichlik
    return {
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
        "m2_og": m2_og,
    }


def format_og(kg: float) -> str:
    """Og'irlikni chiroyli formatlash"""
    if kg >= 1000:
        return f"{kg / 1000:.3f} t ({kg:.1f} kg)"
    return f"{kg:.3f} kg"


# ─── UGOLOK (GOST 8509-93) ────────────────────────────────────
# (tomon × tomon × qalinlik): kg/m
UGOLOK_DATA = {
    (20, 3):  0.889,
    (25, 3):  1.124,
    (25, 4):  1.459,
    (32, 3):  1.457,
    (32, 4):  1.894,
    (40, 3):  1.852,
    (40, 4):  2.422,
    (40, 5):  2.976,
    (45, 4):  2.736,
    (45, 5):  3.369,
    (50, 4):  3.059,
    (50, 5):  3.770,
    (50, 6):  4.465,
    (63, 5):  4.813,
    (63, 6):  5.720,
    (63, 8):  7.469,
    (75, 5):  5.797,
    (75, 6):  6.905,
    (75, 8):  9.025,
    (80, 6):  7.376,
    (80, 8):  9.658,
    (100, 7): 10.800,
    (100, 8): 12.280,
    (100, 10): 15.120,
    (125, 9): 17.000,
    (125, 10): 18.800,
    (150, 10): 22.800,
    (150, 12): 27.100,
}

UGOLOK_SIZES = sorted(set(k[0] for k in UGOLOK_DATA.keys()))
UGOLOK_QALINLIKLAR = {t: sorted(set(k[1] for k in UGOLOK_DATA.keys() if k[0] == t)) for t in UGOLOK_SIZES}


def calc_ugolok(tomon: int, qalinlik: int, uzunlik: float, miqdor: int) -> dict:
    kg_m = UGOLOK_DATA.get((tomon, qalinlik), 0)
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": kg_m,
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
    }


# ─── SHVELLER (GOST 8240-97) ──────────────────────────────────
# Nomer: kg/m
SHVELLER_DATA = {
    5:   4.840,
    6.5: 5.900,
    8:   7.050,
    10:  8.590,
    12:  10.400,
    14:  12.300,
    16:  14.200,
    18:  16.300,
    20:  18.400,
    22:  21.000,
    24:  24.000,
    27:  27.700,
    30:  31.800,
    33:  36.500,
    36:  41.900,
    40:  48.300,
}

SHVELLER_NOMERLAR = sorted(SHVELLER_DATA.keys())


def calc_shveller(nomer: float, uzunlik: float, miqdor: int) -> dict:
    kg_m = SHVELLER_DATA.get(nomer, 0)
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": kg_m,
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
    }


# ─── BETON MARKASI VA SINFI ───────────────────────────────────
BETON_MARKALAR = {
    "M100": {"sinf": "B7.5",  "mustahkamlik": "7.5 MPa",  "ishlatish": "Tayyorlov qatlami, yo'lak"},
    "M150": {"sinf": "B10",   "mustahkamlik": "10 MPa",   "ishlatish": "Poydevor (engil), to'siq"},
    "M200": {"sinf": "B15",   "mustahkamlik": "15 MPa",   "ishlatish": "Plita, poydevor, yo'l"},
    "M250": {"sinf": "B20",   "mustahkamlik": "20 MPa",   "ishlatish": "Ustun, to'sin, poydevor"},
    "M300": {"sinf": "B22.5", "mustahkamlik": "22.5 MPa", "ishlatish": "Ko'prik, ustun, panel"},
    "M350": {"sinf": "B25",   "mustahkamlik": "25 MPa",   "ishlatish": "Yuqori yukli konstruktsiya"},
    "M400": {"sinf": "B30",   "mustahkamlik": "30 MPa",   "ishlatish": "Gidrotexnika, ko'prik"},
    "M450": {"sinf": "B35",   "mustahkamlik": "35 MPa",   "ishlatish": "Maxsus konstruktsiyalar"},
    "M500": {"sinf": "B40",   "mustahkamlik": "40 MPa",   "ishlatish": "Gidroizo, maxsus ob'ekt"},
}

BETON_ZICHLIGI = 2400  # kg/m³


def calc_beton_kub(uzunlik: float, kenglik: float, balandlik: float) -> dict:
    """To'rtburchak beton kub hajmi va og'irligi"""
    hajm = uzunlik * kenglik * balandlik
    og_irlik = hajm * BETON_ZICHLIGI
    return {
        "hajm_m3": hajm,
        "og_irlik_kg": og_irlik,
        "og_irlik_t": og_irlik / 1000,
    }


def calc_beton_silindr(diametr: float, balandlik: float) -> dict:
    """Silindr shaklidagi beton hajmi"""
    import math
    r = diametr / 2
    hajm = math.pi * r * r * balandlik
    og_irlik = hajm * BETON_ZICHLIGI
    return {
        "hajm_m3": hajm,
        "og_irlik_kg": og_irlik,
        "og_irlik_t": og_irlik / 1000,
    }


# ─── KOTLOVAN HISOBLASH ───────────────────────────────────────
def calc_kotlovan_turtburchak(uzunlik: float, kenglik: float, chuqurlik: float, qiyalik: float = 0) -> dict:
    """To'rtburchak kotlovan hajmi (qiyalik bilan)
    qiyalik = yon tomonning gorizontal kengayishi (m/m)
    """
    # Pastki o'lcham
    u_past = uzunlik
    k_past = kenglik
    # Yuqori o'lcham (qiyalik hisobida)
    u_yuqori = uzunlik + 2 * qiyalik * chuqurlik
    k_yuqori = kenglik + 2 * qiyalik * chuqurlik

    # Prizma + piramida formulasi (Prismatoid)
    s_past = u_past * k_past
    s_yuqori = u_yuqori * k_yuqori
    s_orta = ((u_past + u_yuqori) / 2) * ((k_past + k_yuqori) / 2)
    hajm = (chuqurlik / 6) * (s_past + 4 * s_orta + s_yuqori)

    return {
        "hajm_m3": hajm,
        "yuqori_uzun": u_yuqori,
        "yuqori_keng": k_yuqori,
        "past_uzun": u_past,
        "past_keng": k_past,
        "yon_maydon": 2 * (u_past + k_past) * chuqurlik,
    }


def calc_kotlovan_silindr(diametr: float, chuqurlik: float, qiyalik: float = 0) -> dict:
    """Silindr/konus kotlovan hajmi"""
    import math
    r_past = diametr / 2
    r_yuqori = r_past + qiyalik * chuqurlik
    hajm = (math.pi * chuqurlik / 3) * (r_past**2 + r_past * r_yuqori + r_yuqori**2)
    return {
        "hajm_m3": hajm,
        "diametr_yuqori": r_yuqori * 2,
        "diametr_past": diametr,
    }


# ══════════════════════════════════════════════════════════════
#  UGOLOK — GOST 8509-93 (teng yonli)
#  Jadval: tomon × qalinlik → kg/m
# ══════════════════════════════════════════════════════════════
UGOLOK_DATA = {
    20: {3: 0.889},
    25: {3: 1.12, 4: 1.46},
    32: {3: 1.46, 4: 1.91},
    36: {3: 1.65, 4: 2.16},
    40: {3: 1.84, 4: 2.42, 5: 2.97},
    45: {3: 2.08, 4: 2.74, 5: 3.37},
    50: {3: 2.32, 4: 3.05, 5: 3.77, 6: 4.47},
    56: {4: 3.45, 5: 4.25, 6: 5.06, 8: 6.57},
    63: {4: 3.9,  5: 4.81, 6: 5.72, 8: 7.46},
    70: {4: 4.37, 5: 5.38, 6: 6.39, 7: 7.37, 8: 8.33},
    75: {5: 5.77, 6: 6.86, 7: 7.93, 8: 8.99},
    80: {5: 6.18, 6: 7.35, 7: 8.49, 8: 9.62},
    90: {6: 8.33, 7: 9.64, 8: 10.9},
    100: {6: 9.31, 7: 10.8, 8: 12.2, 10: 15.0, 12: 17.8},
    110: {7: 11.9, 8: 13.5, 10: 16.6},
    120: {7: 13.0, 8: 14.8, 10: 18.2, 12: 21.6},
    125: {8: 15.5, 9: 17.4, 10: 19.2, 12: 22.8},
    140: {9: 19.7, 10: 21.9, 12: 26.0},
    150: {10: 23.5, 12: 28.0, 14: 32.3, 15: 34.5},
    160: {10: 25.2, 11: 27.7, 12: 30.0, 14: 34.8},
    180: {11: 31.4, 12: 34.2, 14: 39.6, 16: 45.0},
    200: {12: 38.3, 14: 44.4, 16: 50.4, 20: 62.2},
}


def calc_ugolok(tomon: int, qalinlik: int, uzunlik: float, miqdor: int) -> dict:
    kg_m = UGOLOK_DATA.get(tomon, {}).get(qalinlik, 0)
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {"kg_m": kg_m, "bir_ta_kg": bir_ta, "jami_kg": jami, "jami_t": jami / 1000}


# ══════════════════════════════════════════════════════════════
#  SHVELLER — GOST 8240-97
#  Nomer → kg/m
# ══════════════════════════════════════════════════════════════
SHVELLER_DATA = {
    5:   {"kg_m": 4.84,  "b": 32,  "h": 50},
    6.5: {"kg_m": 5.90,  "b": 36,  "h": 65},
    8:   {"kg_m": 7.05,  "b": 40,  "h": 80},
    10:  {"kg_m": 8.59,  "b": 46,  "h": 100},
    12:  {"kg_m": 10.4,  "b": 52,  "h": 120},
    14:  {"kg_m": 12.3,  "b": 58,  "h": 140},
    16:  {"kg_m": 14.2,  "b": 64,  "h": 160},
    18:  {"kg_m": 16.3,  "b": 70,  "h": 180},
    20:  {"kg_m": 18.4,  "b": 76,  "h": 200},
    22:  {"kg_m": 21.0,  "b": 82,  "h": 220},
    24:  {"kg_m": 24.0,  "b": 90,  "h": 240},
    27:  {"kg_m": 27.7,  "b": 95,  "h": 270},
    30:  {"kg_m": 31.8,  "b": 100, "h": 300},
    33:  {"kg_m": 36.5,  "b": 105, "h": 330},
    36:  {"kg_m": 41.9,  "b": 110, "h": 360},
    40:  {"kg_m": 48.3,  "b": 115, "h": 400},
}


def calc_shveller(nomer: float, uzunlik: float, miqdor: int) -> dict:
    d = SHVELLER_DATA.get(nomer, {})
    kg_m = d.get("kg_m", 0)
    bir_ta = kg_m * uzunlik
    jami = bir_ta * miqdor
    return {
        "kg_m": kg_m,
        "bir_ta_kg": bir_ta,
        "jami_kg": jami,
        "jami_t": jami / 1000,
        "b": d.get("b", 0),
        "h": d.get("h", 0),
    }


# ══════════════════════════════════════════════════════════════
#  BETON — GOST 26633-2015
# ══════════════════════════════════════════════════════════════
BETON_MARKALAR = {
    "M100":  {"sinf": "B7.5",  "zichlik": 2300, "tavsif": "Tayyor qatlamlar, to'ldiruvchi"},
    "M150":  {"sinf": "B12.5", "zichlik": 2300, "tavsif": "Poydevor, to'siq"},
    "M200":  {"sinf": "B15",   "zichlik": 2350, "tavsif": "Plita, poydevor, yo'l"},
    "M250":  {"sinf": "B20",   "zichlik": 2350, "tavsif": "Konstruktiv elementlar"},
    "M300":  {"sinf": "B22.5", "zichlik": 2400, "tavsif": "Ko'prik, ustun, to'sin"},
    "M350":  {"sinf": "B25",   "zichlik": 2400, "tavsif": "Bino konstruksiyalari"},
    "M400":  {"sinf": "B30",   "zichlik": 2450, "tavsif": "Gidrotexnik inshootlar"},
    "M450":  {"sinf": "B35",   "zichlik": 2450, "tavsif": "Maxsus konstruksiyalar"},
    "M500":  {"sinf": "B40",   "zichlik": 2500, "tavsif": "Yuqori mustahkamlik"},
    "M600":  {"sinf": "B45",   "zichlik": 2500, "tavsif": "Maxsus va harbiy ob'ektlar"},
}


def calc_beton(uzunlik: float, kenglik: float, balandlik: float, marka: str) -> dict:
    """Beton hajmi va og'irligini hisoblash"""
    hajm = uzunlik * kenglik * balandlik
    info = BETON_MARKALAR.get(marka, {})
    zichlik = info.get("zichlik", 2400)
    og_irlik = hajm * zichlik
    return {
        "hajm_m3": hajm,
        "og_irlik_kg": og_irlik,
        "og_irlik_t": og_irlik / 1000,
        "sinf": info.get("sinf", "—"),
        "zichlik": zichlik,
        "tavsif": info.get("tavsif", "—"),
    }


# ══════════════════════════════════════════════════════════════
#  KOTLOVAN — Hajm hisoblash
# ══════════════════════════════════════════════════════════════
def calc_kotlovan_to_rtburchak(uz: float, ke: float, ch: float, qiy: float = 0) -> dict:
    """
    To'g'ri to'rtburchak kotlovan
    uz=uzunlik, ke=kenglik, ch=chuqurlik, qiy=qiyalik koeffitsienti (0=tik)
    Prizmatoid formulasi: V = (h/6)*(A1 + 4*Am + A2)
    """
    a1 = uz * ke
    uz2 = uz + 2 * qiy * ch
    ke2 = ke + 2 * qiy * ch
    a2 = uz2 * ke2
    uzm = uz + qiy * ch
    kem = ke + qiy * ch
    am = uzm * kem
    hajm = (ch / 6) * (a1 + 4 * am + a2)
    return {
        "hajm_m3": hajm,
        "pastki_m2": a1,
        "yuqori_m2": a2,
        "chuqurlik": ch,
        "qiyalik": qiy,
    }


def calc_kotlovan_doira(radius: float, chuqurlik: float, qiy: float = 0) -> dict:
    """Doira shaklidagi kotlovan"""
    import math
    r1 = radius
    r2 = radius + qiy * chuqurlik
    a1 = math.pi * r1 ** 2
    a2 = math.pi * r2 ** 2
    rm = (r1 + r2) / 2
    am = math.pi * rm ** 2
    hajm = (chuqurlik / 6) * (a1 + 4 * am + a2)
    return {
        "hajm_m3": hajm,
        "pastki_m2": round(a1, 2),
        "yuqori_m2": round(a2, 2),
        "chuqurlik": chuqurlik,
        "radius": radius,
    }

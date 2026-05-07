# 🏠 Render Sifat Oshirish Boti

Interior va exterior render rasmlarini AI yordamida yuqori sifatga olib chiqadi.

---

## O'rnatish

### 1. Telegram token oling
`@BotFather` → `/newbot` → tokenni saqlang

### 2. Replicate token oling
1. [replicate.com](https://replicate.com) ga o'ting
2. GitHub yoki email bilan ro'yxatdan o'ting
3. **$5 bepul kredit** avtomatik beriladi (~2500 ta rasm)
4. Settings → API tokens → "Create token"

### 3. O'rnating
```bash
pip install -r requirements.txt
```

### 4. Tokenlarni yozing
`bot.py` ichida (8–9 qator):
```python
BOT_TOKEN       = "TELEGRAM_TOKEN"
REPLICATE_TOKEN = "REPLICATE_TOKEN"
```

Yoki environment variable:
```bash
export BOT_TOKEN="..."
export REPLICATE_API_TOKEN="..."
```

### 5. Ishga tushiring
```bash
python bot.py
```

---

## Modellar

| Model | Sifat | Tezlik | Narx |
|-------|-------|--------|------|
| **Clarity** | ⭐⭐⭐⭐⭐ | O'rta | ~$0.002 |
| Real-ESRGAN 4x | ⭐⭐⭐⭐ | Tez | ~$0.001 |
| Real-ESRGAN 2x | ⭐⭐⭐ | Juda tez | ~$0.0005 |

**Tavsiya:** Interior/exterior uchun Clarity eng yaxshi natija beradi.

---

## Effektlar

- **Keskinlashtirish** — chiziqlar, qirralar aniqroq chiqadi
- **Kontrast** — ranglar va yorug'lik yaxshilanadi  
- **Shovqin tozalash** — donador/shovqinli rasmlar uchun
- **Yuz tiklash** — odamlar bo'lsa yuzlarni tiklaydi

---

## Eng yaxshi natija uchun

```
Interior render → Clarity + Keskinlashtirish + Kontrast
Exterior render → Clarity + Kontrast
Tunda olingan  → Real-ESRGAN 4x + Shovqin tozalash
```

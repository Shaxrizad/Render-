import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from handlers_new import router as router_new

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(8707546862:AAGoeL3mfX0zNTWUPsQupOlXGw4a_lmu0bw)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(router_new)
    
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

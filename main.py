import asyncio
import logging
import os
from typing import List, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from config import Settings
from exchanges.binance_earn import BinanceEarnClient
from models import EarnOffer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("simple_earn_bot")


def format_offer(offer: EarnOffer) -> str:
    apr_pct = offer.apr * 100
    dur = f"{offer.duration_days} дн." if offer.duration_days is not None else "гибкий"
    min_amt = f"{offer.min_amount:g} {offer.asset}" if offer.min_amount is not None else "нет"
    return (
        f"Биржа: *{offer.exchange}*\n"
        f"Актив: *{offer.asset}*\n"
        f"Тип продукта: *{offer.product_type}*\n"
        f"APR: *{apr_pct:.2f}%*\n"
        f"Срок: *{dur}*\n"
        f"Мин. сумма: *{min_amt}*"
    )


async def gather_offers(settings: Settings, asset: Optional[str] = None) -> List[EarnOffer]:
    """
    Собираем предложения Simple Earn / Earn с разных бирж.
    Пока что реализовано только Binance Simple Earn.
    Остальные биржи подключаются по аналогии (см. README).
    """
    offers: List[EarnOffer] = []

    # Binance
    if settings.binance_api_key and settings.binance_api_secret:
        try:
            binance_client = BinanceEarnClient(
                api_key=settings.binance_api_key,
                api_secret=settings.binance_api_secret,
            )
            binance_offers = await binance_client.fetch_top_offers(
                asset=asset,
                limit=settings.max_offers_per_exchange,
            )
            offers.extend(binance_offers)
        except Exception as e:
            logger.exception("Ошибка при запросе Binance Simple Earn: %s", e)

    # TODO: здесь можно добавить клиентов для OKX, Bybit, KuCoin, Bitget и др.
    # пример:
    # if settings.okx_api_key:
    #     okx_client = OkxEarnClient(...)
    #     offers.extend(await okx_client.fetch_top_offers(asset=asset, limit=settings.max_offers_per_exchange))

    return offers


async def cmd_start(message: Message, settings: Settings):
    text = (
        "👋 Бот для поиска самых выгодных программ *Simple Earn / Earn* на криптобиржах.\n\n"
        "Доступные команды:\n"
        "`/top_earn` — показать топ программ по доходности\n"
        "`/top_earn BTC` — топ программ для конкретного актива (пример: BTC, USDT)\n\n"
        "Сейчас реализована интеграция с *Binance Simple Earn*.\n"
        "Остальные биржи можно подключить по аналогии (см. README)."
    )
    await message.answer(text, parse_mode="Markdown")


async def cmd_top_earn(message: Message, settings: Settings):
    args = message.text.strip().split()
    asset = args[1].upper() if len(args) > 1 else None

    await message.answer("⏳ Собираю данные по программам Simple Earn, подождите пару секунд...")

    offers = await gather_offers(settings, asset=asset)

    if not offers:
        await message.answer(
            "Не удалось получить данные по программам Simple Earn.\n"
            "Проверьте API-ключи в `.env` и права доступа (Simple Earn / Earn)."
        )
        return

    # сортируем по APR по убыванию
    offers_sorted = sorted(offers, key=lambda o: o.apr, reverse=True)
    top_n = offers_sorted[: settings.top_n_results]

    header = "🔥 *Топ программ Simple Earn по доходности*"
    if asset:
        header += f" для актива *{asset}*"
    header += ":\n\n"

    parts = [header]
    for i, offer in enumerate(top_n, start=1):
        parts.append(f"*#{i}*\n" + format_offer(offer) + "\n")

    await message.answer("\n".join(parts), parse_mode="Markdown")


async def main():
    settings = Settings.from_env()

    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    # пробрасываем настройки в хендлеры через lambda
    dp.message.register(lambda m: cmd_start(m, settings), Command("start"))
    dp.message.register(lambda m: cmd_top_earn(m, settings), Command("top_earn"))

    logger.info("Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

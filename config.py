import os
from dataclasses import dataclass


@dataclass
class Settings:
    telegram_bot_token: str
    binance_api_key: str
    binance_api_secret: str

    # сколько лучших офферов брать с каждой биржи
    max_offers_per_exchange: int = 50
    # сколько результатов показывать пользователю
    top_n_results: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        from dotenv import load_dotenv

        load_dotenv()

        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            binance_api_key=os.getenv("BINANCE_API_KEY", ""),
            binance_api_secret=os.getenv("BINANCE_API_SECRET", ""),
        )

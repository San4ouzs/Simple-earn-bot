# Бот для поиска самых выгодных Simple Earn / Earn программ

Бот в Telegram, который по команде показывает самые доходные программы Simple Earn / Earn на биржах.

Сейчас реализована интеграция с **Binance Simple Earn** (Flexible + Locked).  
Структура кода позволяет добавить и остальные биржи (OKX, Bybit, KuCoin, Bitget и т.д.) по аналогии.

---

## 1. Структура проекта

```
simple_earn_bot/
├── main.py               # входная точка, Telegram-бот
├── models.py             # общая модель EarnOffer
├── config.py             # загрузка настроек из .env
├── exchanges/
│   ├── __init__.py
│   └── binance_earn.py   # клиент для Binance Simple Earn
├── requirements.txt
├── .env.example
└── README_RU.md
```

---

## 2. Установка

1. Распакуйте архив в папку, например:
   `C:\Users\Lepricon\Desktop\simple_earn_bot`

2. Откройте PowerShell и перейдите в эту папку:

```powershell
cd "C:\Users\Lepricon\Desktop\simple_earn_bot"
```

3. Создайте и активируйте виртуальное окружение (по желанию):

```powershell
python -m venv venv
.\venv\Scripts\activate
```

4. Установите зависимости:

```powershell
pip install -r requirements.txt
```

---

## 3. Настройка `.env`

1. Создайте файл `.env` (можно скопировать `.env.example`):

```powershell
copy .env.example .env
```

2. Откройте `.env` в блокноте и впишите:

- `TELEGRAM_BOT_TOKEN` — токен вашего Telegram-бота (из BotFather)
- `BINANCE_API_KEY`, `BINANCE_API_SECRET` — API-ключи Binance с доступом к Simple Earn (USER_DATA)

⚠️ На Binance нужно:
- создать API-ключ,
- включить права на **Enable Spot & Margin Trading** и Simple Earn / Earn, если требуется,
- по возможности ограничить IP (для реальной торговли).

Документация по Simple Earn API:  
https://developers.binance.com/docs/simple_earn/overview

---

## 4. Запуск бота

Из папки проекта:

```powershell
python main.py
```

Если всё настроено верно, в консоли появится сообщение, что бот запущен.

---

## 5. Команды бота

В Telegram-чате с ботом:

- `/start` — краткая справка.
- `/top_earn` — показать топ программ Simple Earn по доходности (по всем активам).
- `/top_earn BTC` — топ программ для конкретного актива (например, BTC, ETH, USDT).

Бот собирает список программ Simple Earn на Binance (Flexible + Locked), сортирует по APR и показывает самые выгодные предложения.

---

## 6. Как добавить другие биржи (OKX, Bybit и т.д.)

1. Создайте новый файл в `exchanges/`, например `okx_earn.py`.
2. Реализуйте аналогичный класс `OkxEarnClient` с методом:

```python
async def fetch_top_offers(self, asset: Optional[str], limit: int) -> List[EarnOffer]:
    ...
```

3. В `main.py` в функции `gather_offers` добавьте вызов вашего клиента и объедините результаты с Binance.

Документацию по Earn-продуктам смотрите в разделах API бирж:

- OKX Earn / Simple Earn  
- Bybit Earn / Easy Earn  
- KuCoin Earn / Savings  
- Bitget Earn и т.д.

---

## 7. Замечания

- Код **не** выполняет никаких подписок автоматически, он только читает доступные продукты и их доходность.
- Не является инвестиционной рекомендацией — вы просто получаете данные по текущим программам Earn.

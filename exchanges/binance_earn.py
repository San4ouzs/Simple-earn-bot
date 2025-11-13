import asyncio
from typing import List, Optional

from binance.client import Client

from models import EarnOffer


class BinanceEarnClient:
    """
    Клиент для Binance Simple Earn (Flexible + Locked).

    Требуются API-ключи с правами на Simple Earn / Earn.
    Документация по Simple Earn API:
    https://developers.binance.com/docs/simple_earn/overview
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def _create_client(self) -> Client:
        return Client(api_key=self.api_key, api_secret=self.api_secret)

    def _fetch_flexible_raw(self, asset: Optional[str], size: int):
        client = self._create_client()
        params = {"size": size}
        if asset:
            params["asset"] = asset
        # python-binance helper для списка flexible-продуктов Simple Earn
        return client.get_simple_earn_flexible_product_list(**params)

    def _fetch_locked_raw(self, asset: Optional[str], size: int):
        client = self._create_client()
        params = {"size": size}
        if asset:
            params["asset"] = asset
        # python-binance helper для списка locked-продуктов Simple Earn
        return client.get_simple_earn_locked_product_list(**params)

    @staticmethod
    def _parse_flexible_rows(rows) -> List[EarnOffer]:
        offers: List[EarnOffer] = []
        for r in rows or []:
            try:
                apr = float(r.get("latestAnnualPercentageRate") or 0.0)
            except (TypeError, ValueError):
                apr = 0.0

            min_amount = None
            try:
                if r.get("minPurchaseAmount") is not None:
                    min_amount = float(r["minPurchaseAmount"])
            except (TypeError, ValueError):
                min_amount = None

            offer = EarnOffer(
                exchange="Binance",
                asset=r.get("asset", ""),
                product_type="flexible",
                apr=apr,
                duration_days=None,
                min_amount=min_amount,
                extra={
                    "productId": r.get("productId"),
                    "airDropPercentageRate": r.get("airDropPercentageRate"),
                    "isSoldOut": r.get("isSoldOut"),
                    "hot": r.get("hot"),
                },
            )
            offers.append(offer)
        return offers

    @staticmethod
    def _parse_locked_rows(rows) -> List[EarnOffer]:
        offers: List[EarnOffer] = []
        for r in rows or []:
            try:
                apr = float(r.get("latestAnnualPercentageRate") or 0.0)
            except (TypeError, ValueError):
                apr = 0.0

            min_amount = None
            try:
                if r.get("minPurchaseAmount") is not None:
                    min_amount = float(r["minPurchaseAmount"])
            except (TypeError, ValueError):
                min_amount = None

            duration_days = None
            try:
                if r.get("duration") is not None:
                    duration_days = int(r["duration"])
            except (TypeError, ValueError):
                duration_days = None

            offer = EarnOffer(
                exchange="Binance",
                asset=r.get("asset", ""),
                product_type="locked",
                apr=apr,
                duration_days=duration_days,
                min_amount=min_amount,
                extra={
                    "projectId": r.get("projectId"),
                    "soldOut": r.get("soldOut"),
                    "rewardAsset": r.get("rewardAsset"),
                },
            )
            offers.append(offer)
        return offers

    async def fetch_top_offers(
        self,
        asset: Optional[str] = None,
        limit: int = 50,
    ) -> List[EarnOffer]:
        """
        Получить список лучших офферов Simple Earn на Binance.
        Возвращает объединённый список flexible + locked, отсортированный по APR.
        """

        def blocking_fetch():
            # Binance возвращает структуру вида {"rows": [...], "total": N}
            flex = self._fetch_flexible_raw(asset=asset, size=limit)
            locked = self._fetch_locked_raw(asset=asset, size=limit)

            flex_rows = flex.get("rows", []) if isinstance(flex, dict) else flex
            locked_rows = locked.get("rows", []) if isinstance(locked, dict) else locked

            flex_offers = self._parse_flexible_rows(flex_rows)
            locked_offers = self._parse_locked_rows(locked_rows)

            combined = flex_offers + locked_offers
            combined.sort(key=lambda o: o.apr, reverse=True)
            return combined[:limit]

        return await asyncio.to_thread(blocking_fetch)

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class EarnOffer:
    exchange: str
    asset: str
    product_type: str  # e.g. "flexible", "locked"
    apr: float  # в долях (0.05 == 5% APR)
    duration_days: Optional[int] = None  # срок блокировки (для locked), None для flexible
    min_amount: Optional[float] = None
    extra: Dict[str, Any] = None

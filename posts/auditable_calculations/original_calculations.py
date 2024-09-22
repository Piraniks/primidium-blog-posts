from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable


class AssetType(str, Enum):
    STOCK = 'STOCK'
    BOND = 'BOND'
    CASH = 'CASH'
    COMMODITY = 'COMMODITY'
    CRYPTO_CURRENCY = 'CRYPTO_CURRENCY'
    PRIVATE_EQUITY = 'PRIVATE_EQUITY'
    REAL_ESTATE = 'REAL_ESTATE'


@dataclass(frozen=True)
class Asset:
    value: Decimal
    quantity: Decimal
    type: AssetType



def calculate_total_worth(assets: Iterable[Asset]) -> Decimal:
    total: Decimal = Decimal(0)

    for asset in assets:
        total += asset.value * asset.quantity
    
    return total

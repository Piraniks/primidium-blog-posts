from decimal import Decimal
from .original_calculations import calculate_total_worth, Asset, AssetType


def test_returns_0_if_no_assets_were_given():
    expected_asset_value = Decimal(0)
    calculated_asset_value = calculate_total_worth(assets=[])

    assert calculated_asset_value == expected_asset_value


def test_returns_correct_value_for_single_asset():
    quantity = Decimal(1)
    value = Decimal(2)
    asset = Asset(value=value, quantity=quantity, type=AssetType.STOCK)

    expected_asset_value = quantity * value
    calculated_asset_value = calculate_total_worth(assets=[asset])

    assert calculated_asset_value == expected_asset_value


def test_returns_correct_value_for_multiple_assets():
    first_asset_quantity = Decimal(1)
    first_asset_value = Decimal(2)
    first_asset = Asset(value=first_asset_value, quantity=first_asset_quantity, type=AssetType.STOCK)

    second_asset_quantity = Decimal(3)
    second_asset_value = Decimal (4)
    second_asset = Asset(value=second_asset_value, quantity=second_asset_quantity, type=AssetType.STOCK)

    expected_assets_value = first_asset_quantity * first_asset_value + second_asset_quantity * second_asset_value
    calculated_assets_value = calculate_total_worth(assets=[first_asset, second_asset])

    assert calculated_assets_value == expected_assets_value

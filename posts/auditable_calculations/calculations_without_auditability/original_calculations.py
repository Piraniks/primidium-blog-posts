from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class IncomeType(str, Enum):
    SALARY = 'SALARY'
    SELF_EMPLOYMENT = 'SELF_EMPLOYMENT'


class SelfEmploymentTaxationType(str, Enum):
    AS_SALARY = 'AS_SALARY'
    LINEAR = 'LINEAR'


class Currency(str, Enum):
    EUR = 'EUR'
    USD = 'USD'
    GBP = 'GBP'


CURRENCY_FACTORS: dict[Currency, Decimal] = {
    Currency.EUR: Decimal('1'),
    Currency.USD: Decimal('1.2'),
    Currency.GBP: Decimal('0.8'),
}


class ExpenseType(str, Enum):
    HOME_OFFICE = 'HOME_OFFICE'
    TRANSPORTATION = 'TRANSPORTATION'


DEDUCTIBLE_EXPENSES: dict[IncomeType, set[ExpenseType]] = {
    IncomeType.SALARY: {ExpenseType.TRANSPORTATION},
    IncomeType.SELF_EMPLOYMENT: {ExpenseType.HOME_OFFICE, ExpenseType.TRANSPORTATION},
}


@dataclass(frozen=True)
class Income:
    type: IncomeType
    amount: Decimal
    currency: Currency
    timestamp: datetime


@dataclass(frozen=True)
class Expense:
    type: ExpenseType
    amount: Decimal
    currency: Currency
    timestamp: datetime


@dataclass(frozen=True)
class TaxpayerProfile:
    age: int
    currency: Currency
    self_employment_taxation_type: SelfEmploymentTaxationType | None


def calculate_tax(
    incomes: tuple[Income, ...],
    expenses: tuple[Expense, ...],
    taxpayer_profile: TaxpayerProfile
) -> Decimal:
    total_income: Decimal = Decimal(0)
    for income in incomes:
        total_income += income.amount * CURRENCY_FACTORS[income.currency] / CURRENCY_FACTORS[taxpayer_profile.currency]

    total_expense: Decimal = Decimal(0)
    deductible_expense_types = DEDUCTIBLE_EXPENSES.get(taxpayer_profile.self_employment_taxation_type, set())

    for expense in expenses:
        is_expense_deductible = (
            expense.type in DEDUCTIBLE_EXPENSES
            and expense.type in DEDUCTIBLE_EXPENSES[expense.type]
        )

        total_expense -= expense.amount * CURRENCY_FACTORS[expense.currency] / CURRENCY_FACTORS[taxpayer_profile.currency]

    return max(total_income - total_expense, Decimal(0))

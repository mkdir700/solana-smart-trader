from typing import TypedDict


class TokenAmount(TypedDict):
    number: int
    decimals: int
    token_address: str


class TokenBalanceChange(TypedDict):
    address: str
    change_type: str
    decimals: int
    change_amount: str | float
    post_balance: str | float
    pre_balance: str | float
    token_address: str
    owner: str
    event_type: str
    post_owner: str
    pre_owner: str


class SolBalanceChange(TypedDict):
    address: str
    pre_balance: str | float
    post_balance: str | float
    change_amount: str | float

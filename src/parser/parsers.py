import json
import time
from typing import Any

from common.exception import APIError
from common.rpc_nodes import choice_rpc_node
from common.solscan import Solscan
from common.types import SolBalanceChange, TokenAmount, TokenBalanceChange
from loguru import logger
from solana.exceptions import SolanaRpcException
from solana.rpc.api import Client
from solders.signature import Signature


def to_ui_amount(amount: str | float, deciaml: int) -> float:
    # "34141019152748", 6
    # -> 34141019.152748
    if isinstance(amount, (float, int)):
        return amount / 10**deciaml
    return float(amount[:-deciaml] + "." + amount[-deciaml:])


def calculate_transaction_id(
    address: str,
    token_mint: str,
    token_amount: float,
    transaction_type: str,
) -> str:
    """计算交易 ID"""
    return f"{address}:{token_mint}:{token_amount}:{transaction_type}"


class TransactionParserWithSolscan:
    """通过 Solscan 服务的交易解析器"""

    def __init__(self, signature: str):
        self.signature = signature
        self.solscan_client = Solscan()
        self._transaction_details = None

    def get_transaction_details(self) -> dict:
        if self._transaction_details is None:
            try:
                self._transaction_details = self.solscan_client.get_transaction_details(
                    self.signature
                )
            except Exception as e:
                raise APIError(f"请求 Solscan 服务失败: {e}") from e
        return self._transaction_details

    def is_valid(self) -> bool:
        return self.get_transaction_details()["data"]["status"] == 1

    def get_signer(self) -> list[str]:
        return self.get_transaction_details()["data"]["signer"][::-1]

    def get_mint(self) -> str:
        return self.get_transaction_details()["data"]

    def get_token_info(self, token_address: str) -> dict:
        """
        {
            "token_address": "4uP8C8AWoXJQjU41RoVyjGneCwJtzzyHY1R4n7yPpump",
            "token_name": "Solana Music",
            "token_symbol": "SLMC",
            "token_icon": "https://cf-ipfs.com/ipfs/QmSPqJ8MZQDpxwQ5qFK6EhcNDkm4SCi6ceYhYWyGxzbL9v",
            "token_decimals": 6,
            "token_type": "token",
            "extensions": {
                "description": "Solana Music will serve music lovers by developing an application that includes music creation, original protection, copyright trading, music charts, talent voting, and more, creating a web3 music community. ",
                "twitter": "https://x.com/Solana_Music_X"
            },
            "onchain_extensions": ""
        }
        """
        metadata = self.get_transaction_details()["metadata"]
        tokens = metadata["tokens"]
        return tokens.get(token_address)

    def get_token_price(self, token_address: str):
        # https://price.jup.ag/v4/price?ids=DCWNeUNBQ5oCmrpQKdSpVsGVzHpiNF21qADgXVQzno2Q
        ...

    def get_sol_bal_change(self) -> list[SolBalanceChange]:
        return self.get_transaction_details()["data"]["sol_bal_change"]

    def get_token_bal_change(self) -> list[TokenBalanceChange]:
        return self.get_transaction_details()["data"]["token_bal_change"]

    def get_render_summary_main_actions(self) -> list[dict]:
        return self.get_transaction_details()["data"]["render_summary_main_actions"]

    def justify_transaction_type(self, pre_token_balance, post_token_balance) -> str:
        # 建仓，加仓，减仓，清仓
        if pre_token_balance == 0 and post_token_balance > 0:
            transaction_type = "open"
        elif pre_token_balance > 0 and post_token_balance == 0:
            transaction_type = "clear"
        elif pre_token_balance > 0 and post_token_balance > pre_token_balance:
            transaction_type = "add"
        elif pre_token_balance > 0 and post_token_balance < pre_token_balance:
            transaction_type = "reduce"
        elif pre_token_balance == post_token_balance == 0:
            transaction_type = "invalid"
        else:
            raise ValueError("未知交易类型")

        return transaction_type

    def parse_on_raydium(self):
        data = {}
        trader_address = self.get_signer()[0]
        summary_main_actions = self.get_render_summary_main_actions()

        action = None
        for _key in ("title", "body"):
            action = summary_main_actions[0][_key]
            for item in action[0]:
                if item.get("text") == "Swap":
                    break
        if action is None:
            raise ValueError("未找到 Swap 交易, 请检查")

        tokens_involved = self.get_tokens_involved()
        if len(tokens_involved) != 2:
            raise ValueError("交易涉及的 token 数量不正确")

        token1, token2 = tokens_involved
        if token1 == "So11111111111111111111111111111111111111112":
            wsol_token_address = token1
            swap_token_address = token2
        else:
            wsol_token_address = token2
            swap_token_address = token1

        sol_bal_changes = self.get_sol_bal_change()
        token_bal_changes = self.get_token_bal_change()

        if not sol_bal_changes and not token_bal_changes:
            raise ValueError("sol_bal_change 或 token_bal_change 为空")

        wsol_bal_change = None
        token_bal_change = None
        for bal_change in token_bal_changes:
            token_address = bal_change["token_address"]
            if bal_change["owner"] != trader_address:
                continue
            if token_address == wsol_token_address:
                wsol_bal_change = bal_change
            elif token_address == swap_token_address:
                token_bal_change = bal_change

        if token_bal_change is None:
            raise ValueError("未找到 token 余额变化")

        sol_bal_change = None
        if wsol_bal_change is None:
            for bal_change in sol_bal_changes:
                if bal_change["address"] != trader_address:
                    continue

                # 交易者 SOL 余额变化
                sol_bal_change = bal_change
                break
        else:
            sol_bal_change = wsol_bal_change

        if sol_bal_change is None:
            raise ValueError("未找到 SOL或wSOL 余额变化")

        deciaml = token_bal_change["decimals"]
        pre_token_balance = to_ui_amount(token_bal_change["pre_balance"], deciaml)
        post_token_balance = to_ui_amount(token_bal_change["post_balance"], deciaml)
        token_address = token_bal_change["token_address"]
        transaction_type = self.justify_transaction_type(
            pre_token_balance, post_token_balance
        )
        token_info = self.get_token_info(token_address)

        data["owner"] = trader_address
        data["signature"] = self.signature
        data["transaction_id"] = calculate_transaction_id(
            trader_address,
            token_address,
            post_token_balance,
            transaction_type,
        )
        data["transaction_type"] = transaction_type
        data["token"] = {
            "mint": token_address,
            "amount": post_token_balance,
            "pre_balance": pre_token_balance,
            "post_balance": post_token_balance,
            "change_amount": post_token_balance - pre_token_balance,
            "name": token_info.get("token_name", "SPL Token"),
            "symbol": token_info.get("token_symbol", "SPL"),
        }
        # wSOL 可以等价于 SOL
        data["sol"] = {
            "pre_balance": to_ui_amount(sol_bal_change["pre_balance"], 9),
            "post_balance": to_ui_amount(sol_bal_change["post_balance"], 9),
            "change_amount": to_ui_amount(sol_bal_change["change_amount"], 9),
        }
        return data

    def swap_sol_and_token(self):
        """使用 sol 去交换 token"""
        data = {}
        summary_main_actions = self.get_render_summary_main_actions()

        action = None
        for _key in ("title", "body"):
            for item in summary_main_actions[0][_key][0]:
                if item.get("text") == "Swap":
                    action = summary_main_actions[0][_key]
                    break
        if action is None:
            raise ValueError("未找到 Swap 交易, 请检查")

        token_to_swap_info: TokenAmount = action[0][2]["token_amount"]
        token_swapped_info: TokenAmount = action[0][4]["token_amount"]
        sol_bal_changes = self.get_sol_bal_change()
        token_bal_changes = self.get_token_bal_change()

        if not sol_bal_changes and not token_bal_changes:
            raise ValueError("sol_bal_change 或 token_bal_change 为空")

        trader_address = self.get_signer()[0]

        # 交易者的 token 余额变化
        token_bal_change = None
        for bal_change in token_bal_changes:
            token_address = bal_change["token_address"]
            if bal_change["owner"] != trader_address:
                continue
            if (
                token_address == token_swapped_info["token_address"]
                or token_address == token_to_swap_info["token_address"]
            ):
                token_bal_change = bal_change
                break

        sol_bal_change = None
        for bal_change in sol_bal_changes:
            if bal_change["address"] != trader_address:
                continue

            # 交易者 SOL 余额变化
            sol_bal_change = bal_change
            break

        if token_bal_change is None or sol_bal_change is None:
            raise ValueError("未找到 token 或 SOL 余额变化")

        data["owner"] = trader_address
        data["signature"] = self.signature
        deciaml = token_bal_change["decimals"]
        pre_token_balance = to_ui_amount(token_bal_change["pre_balance"], deciaml)
        post_token_balance = to_ui_amount(token_bal_change["post_balance"], deciaml)
        token_address = token_bal_change["token_address"]
        transaction_type = self.justify_transaction_type(
            pre_token_balance, post_token_balance
        )
        token_info = self.get_token_info(token_address)

        data["transaction_id"] = calculate_transaction_id(
            trader_address,
            token_address,
            post_token_balance,
            transaction_type,
        )
        data["transaction_type"] = transaction_type
        data["token"] = {
            "mint": token_address,
            "amount": post_token_balance,
            "pre_balance": pre_token_balance,
            "post_balance": post_token_balance,
            "change_amount": post_token_balance - pre_token_balance,
            "name": token_info.get("token_name", "SPL Token"),
            "symbol": token_info.get("token_symbol", "SPL"),
        }
        data["sol"] = {
            "pre_balance": to_ui_amount(sol_bal_change["pre_balance"], 9),
            "post_balance": to_ui_amount(sol_bal_change["post_balance"], 9),
            "change_amount": to_ui_amount(sol_bal_change["change_amount"], 9),
        }
        return data

    def get_accounts(self) -> dict:
        """获取参与该交易的账户"""
        metadata = self.get_transaction_details()["metadata"]
        accounts = metadata["accounts"]
        return accounts

    def get_tokens_involved(self) -> list[str]:
        """获取参与该交易的 token"""
        return self.get_transaction_details()["data"]["tokens_involved"]

    def get_result(self) -> dict:
        summary_main_actions = self.get_render_summary_main_actions()
        if not summary_main_actions:
            raise ValueError("不是 Swap 交易，跳过解析")

        action = None
        platform_account = None
        for _key in ("title", "body"):
            action = summary_main_actions[0][_key]
            for idx, item in enumerate(action[0]):
                if item.get("text") == "on":
                    platform_account = action[0][idx + 1]["account"]
                    break

        if platform_account is None or action is None:
            raise ValueError("未知平台的交易账户，暂不支持")

        accounts = self.get_accounts()
        account_label = accounts[platform_account]["account_label"]
        if account_label == "Pump.fun":
            data = self.swap_sol_and_token()
            data["platform"] = "Pump"
        elif "Raydium" in account_label:
            data = self.parse_on_raydium()
            data["platform"] = "Raydium"
        else:
            raise ValueError("未知平台")
        return data


class TransactionParserWithRPC:
    """通过 RPC 节点交易解析器"""

    def __init__(self, signature: str):
        self.signature = signature
        self.solscan_client = Solscan()
        self._transaction_details = None
        self.rpc_api = choice_rpc_node()

    def get_transaction_details(self) -> dict:
        if self._transaction_details is None:
            signature = Signature.from_string(self.signature)
            client = Client(f"https://{self.rpc_api}")
            response = client.get_transaction(
                signature,
                encoding="jsonParsed",
                max_supported_transaction_version=0,
            )
            js_data = response.to_json()
            return json.loads(js_data)["result"]
        return self._transaction_details

    def is_valid(self) -> bool:
        meta = self.get_transaction_details()["meta"]
        if not (meta["err"] is None and meta["status"]["Ok"] is None):
            return False

        return True

    def get_token_bal_change(self) -> dict:
        transaction_meta = self.get_transaction_details()["meta"]
        post_token_balances = transaction_meta["postTokenBalances"]
        pre_token_balances = transaction_meta["preTokenBalances"]

        pre_token_balances_map = {}
        for balance in pre_token_balances:
            mint = balance["mint"]
            owner = balance["owner"]
            pre_token_balances_map[f"{owner}:{mint}"] = balance["uiTokenAmount"][
                "uiAmount"
            ]

        post_token_balances_map = {}
        for balance in post_token_balances:
            mint = balance["mint"]
            owner = balance["owner"]
            post_token_balances_map[f"{owner}:{mint}"] = balance["uiTokenAmount"][
                "uiAmount"
            ]

        data = {}
        if len(pre_token_balances_map) > len(post_token_balances_map):
            for key, pre_balance in pre_token_balances_map.items():
                owner, mint = key.split(":")
                post_balance = post_token_balances_map.get(key, 0)
                data[owner] = {
                    "owner": owner,
                    "mint": mint,
                    "pre_balance": pre_balance,
                    "post_balance": post_balance,
                    "change_amount": post_balance - pre_balance,
                    "change_type": "inc" if post_balance > pre_balance else "dec",
                }
        else:
            for key, post_balance in post_token_balances_map.items():
                owner, mint = key.split(":")
                pre_balance = pre_token_balances_map.get(key, 0)
                data[owner] = {
                    "owner": owner,
                    "mint": mint,
                    "pre_balance": pre_balance,
                    "post_balance": post_balance,
                    "change_amount": post_balance - pre_balance,
                    "change_type": "inc" if post_balance > pre_balance else "dec",
                }
        return data

    def get_signer(self) -> list[str]:
        """获取交易的签名地址"""
        transaction = self.get_transaction_details()
        # 签名地址的数量
        signer_count = len(transaction["transaction"]["signatures"])
        if signer_count > 2:
            # 不处理多个签名地址的情况
            raise ValueError("多个签名地址")
        account_keys = transaction["transaction"]["message"]["accountKeys"]

        signer_pubkeys = []
        for key in account_keys:
            if key["signer"] is True:
                signer_pubkeys.append(key["pubkey"])
        return signer_pubkeys

    def parse_transaction(self, buyer_address):
        token_bal_change = self.get_token_bal_change()
        pre_token_balance = token_bal_change[buyer_address]["pre_balance"]
        post_token_balance = token_bal_change[buyer_address]["post_balance"]
        token_mint = token_bal_change[buyer_address]["mint"]
        change_amount = token_bal_change[buyer_address]["change_amount"]

        # 建仓，加仓，减仓，清仓
        if pre_token_balance == 0 and post_token_balance > 0:
            transaction_type = "open"
        elif pre_token_balance > 0 and post_token_balance == 0:
            transaction_type = "clear"
        elif pre_token_balance > 0 and post_token_balance > pre_token_balance:
            transaction_type = "add"
        elif pre_token_balance > 0 and post_token_balance < pre_token_balance:
            transaction_type = "reduce"
        elif pre_token_balance == post_token_balance == 0:
            transaction_type = "invalid"
        else:
            raise ValueError("未知交易类型")

        return {
            "address": buyer_address,
            "token_mint": token_mint,
            "token_amount": post_token_balance,
            "pre_token_balance": pre_token_balance,
            "post_token_balance": post_token_balance,
            "change_amount": change_amount,
            "transaction_type": transaction_type,
        }

    def handle_transaction(self) -> dict[str, Any] | None:
        transaction_details = self.get_transaction_details()
        if not transaction_details:
            return None

        data = None
        is_valid = False
        account_keys = self.get_signer()
        for key in account_keys[::-1]:
            if self.is_valid():
                is_valid = True
            data = self.parse_transaction(key)
            if data["token_mint"] is not None:
                break

        if is_valid:
            raise ValueError("交易失败")

        if data is None:
            raise ValueError(f"解析数据为空: {self.signature}")

        # transaction_id = self.calculate_transaction_id(data)
        # data["transaction_id"] = transaction_id
        data["signature"] = self.signature
        return data

    def get_result(self) -> dict:
        data = None
        # PERF: 优化请求交易详情
        # 目前使用的 API，并不能在交易的第一时间获取到交易详情
        # 所以只能在这里尝试多次重试，直到获取到交易详情
        for _ in range(60):
            try:
                data = self.handle_transaction()
            except SolanaRpcException:
                logger.warning(f"请求交易详情失败: {self.signature}")
                continue
            if data:
                break
            logger.warning(f"未找到交易结果: {self.signature}, 可能是未完成的交易")
            time.sleep(1)
        else:
            raise ValueError("未找到交易结果")

        return data

from typing import Literal

import httpx

#TODO: Set this up in the config
# api.jup.ag in not free anymore
JUPITER_API_URL = "https://lite-api.jup.ag"


class JupiterAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=JUPITER_API_URL)

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int,
    ) -> dict:
        """Get quote from Jupiter API.

        Args:
            input_mint (str): Input mint
            output_mint (str): Output mint
            amount (int): Amount. The number of input tokens before the decimal is applied,
                also known as the “raw amount” or “integer amount” in lamports for SOL or atomic units for all other tokens.
            slippage_bps (int): Slippage bps. The number of basis points
                you can tolerate to lose during time of execution. e.g. 1% = 100bps

        Returns:
            dict: Quote
        """
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps,
        }
        resp = await self.client.get("/swap/v1/quote", params=params)
        return resp.json()

    async def get_swap_transaction(
        self,
        input_mint: str,
        output_mint: str,
        user_publickey: str,
        amount: int,
        slippage_bps: int,
        priority_level: Literal["medium", "high", "veryHigh"] = "medium",
        max_priority_fee_lamports: int = 10**8,
        use_jito: bool = False,
        jito_tip_lamports: int | None = None,
    ) -> dict:
        """Get swap transaction from Jupiter API.

        {
            swapTransaction: 'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAGDkS+3LuGTbs......+/oD9qb31dH6i0QZ2IHELXUX3Y1YeW79p9Stkqk12z4yvZFJiQ4GCQwLBwYQBgUEDggNTQ==',
            lastValidBlockHeight: 279632475,
            prioritizationFeeLamports: 9999,
            computeUnitLimit: 388876,
            prioritizationType: {
                computeBudget: {
                    microLamports: 25715,
                    estimatedMicroLamports: 785154
                }
            },
            dynamicSlippageReport: {
                slippageBps: 50,
                otherAmount: 20612318,
                simulatedIncurredSlippageBps: -18,
                amplificationRatio: '1.5',
                categoryName: 'lst',
                heuristicMaxSlippageBps: 100
            },
            simulationError: null
        }

        Args:
            input_mint (str): 输入币种的 mint
            output_mint (str): 输出币种的 mint
            user_publickey (str): 用户公钥
            amount (int): 交易数量
            slippage_bps (int): 限价差
            priority_level (Literal["medium", "high", "veryHigh"], optional): 优先级, defaults to "medium"
            max_priority_fee_lamports (int, optional): 最大优先费用, defaults to 10**8
            use_jito (bool, optional): 是否使用 jito, defaults to False, 设置 Jito 时, priority_level 和 max_priority_fee_lamports 会忽略
            jito_tip_lamports (int, optional): jito tip lamports, defaults to None

        Returns:
            dict: 交易信息
        """
        quote_response = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
        if use_jito and not jito_tip_lamports:
            raise ValueError("jito_tip_lamports is required if use_jito is True")
        elif use_jito:
            prioritizationFeeLamports = {"jitoTipLamports": jito_tip_lamports}
        else:
            prioritizationFeeLamports = {
                "priorityLevelWithMaxLamports": {
                    "maxLamports": max_priority_fee_lamports,
                    "priorityLevel": priority_level,
                }
            }

        data = {
            "quoteResponse": quote_response,
            "userPublicKey": user_publickey,
            "dynamicComputeUnitLimit": True,
            "dynamicSlippage": True,
            "prioritizationFeeLamports": prioritizationFeeLamports,
        }
        resp = await self.client.post("/swap/v1/swap", json=data)
        resp.raise_for_status()
        return resp.json()

    async def get_swap_instructions(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int,
        user_publickey: str,
    ) -> dict:
        quote_response = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
        data = {
            "quoteResponse": quote_response,
            "userPublicKey": user_publickey,
        }

        resp = await self.client.post("/swap/v1/swap-instructions", json=data)
        resp.raise_for_status()
        return resp.json()

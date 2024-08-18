import httpx
import string
import random
import asyncio


def ensure_inited(func):

    if asyncio.iscoroutinefunction(func):

        async def wrapper1(self, *args, **kwargs):
            if not self._is_init:
                await self.init()
            return await func(self, *args, **kwargs)

        return wrapper1
    else:

        def wrapper2(self, *args, **kwargs):
            if not self._is_init:
                self.init()
            return func(self, *args, **kwargs)

        return wrapper2


class Solscan:

    def __init__(self):
        self.headers = {
            "authority": "api.solscan.io",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "origin": "https://solscan.io",
            "referer": "https://solscan.io/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        self.session = httpx.Client()
        self.session.headers.update(self.headers)
        self._is_init = False

    def __del__(self):
        self.session.close()

    def init(self):
        self.session.get("https://solscan.io/")
        newheader = {"sol-aut": self.generate_random_string()}
        self.session.headers.update(newheader)
        self.session.options("https://api.solscan.io/v2/publicize/all")
        resp = self.session.get("https://api.solscan.io/v2/publicize/all")
        etag = resp.headers.get("Etag")
        self.session.headers.update({"if-none-match": etag})
        self._is_init = True

    def generate_random_string(self):
        e = string.ascii_letters + string.digits + "==--"
        t = "".join(random.choice(e) for _ in range(16))
        r = "".join(random.choice(e) for _ in range(16))
        n = random.randint(0, 30)
        o = t + r
        i = o[:n] + "B9dls0fK" + o[n:]
        return i

    @ensure_inited
    def get_transaction_details(self, tx: str) -> dict:
        """获取交易详情.

        Args:
            tx: 签名

        Raises:
            ValueError: 接口响应错误时抛出

        Returns:
            dict: 接口数据
        """
        response = self.session.get(
            f"https://api-v2.solscan.io/v2/transaction/detail?tx={tx}"
        )
        if response.status_code != 200:
            raise ValueError(response.text)
        return response.json()


class AsyncSolcan:
    def __init__(self):
        self.headers = {
            "authority": "api.solscan.io",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "origin": "https://solscan.io",
            "referer": "https://solscan.io/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        self.session = httpx.AsyncClient()
        self.session.headers.update(self.headers)
        self._is_init = False

    async def init(self):
        await self.session.get("https://solscan.io/")
        newheader = {"sol-aut": self.generate_random_string()}
        self.session.headers.update(newheader)
        await self.session.options("https://api.solscan.io/v2/publicize/all")
        resp = await self.session.get("https://api.solscan.io/v2/publicize/all")
        etag = resp.headers.get("Etag")
        self.session.headers.update({"if-none-match": etag})
        self._is_init = True

    def generate_random_string(self):
        e = string.ascii_letters + string.digits + "==--"
        t = "".join(random.choice(e) for _ in range(16))
        r = "".join(random.choice(e) for _ in range(16))
        n = random.randint(0, 30)
        o = t + r
        i = o[:n] + "B9dls0fK" + o[n:]
        return i

    @ensure_inited
    async def get_transaction_details(self, tx: str) -> dict:
        """获取交易详情.

        Args:
            tx: 签名

        Raises:
            ValueError: 接口响应错误时抛出

        Returns:
            dict: 接口数据
        """
        response = await self.session.get(
            f"https://api-v2.solscan.io/v2/transaction/detail?tx={tx}"
        )
        if response.status_code != 200:
            raise ValueError(response.text)
        return response.json()

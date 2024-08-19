from parsers import TransactionParserWithSolscan


def recursive_compare(expected, data):
    # 首先检查两个对象是否都是字典
    if not isinstance(expected, dict) or not isinstance(data, dict):
        return False

    # 检查字典的键是否相同
    if expected.keys() != data.keys():
        print(f"keys not match: expected: {expected.keys()}, data: {data.keys()}")
        return False

    # 递归比较每个键的值
    for key in expected:
        value1 = expected[key]
        value2 = data[key]

        # 如果值是字典，则递归比较
        if isinstance(value1, dict) and isinstance(value2, dict):
            if not recursive_compare(value1, value2):
                return False
        elif isinstance(value1, float) and isinstance(value2, float):
            if str(value1) != str(value2):
                print(f"value1: {value1}, value2: {value2}")
                return False
        # 否则直接比较值
        elif value1 != value2:
            print(f"value1: {value1}, value2: {value2}")
            return False

    return True


class TestHandleTransaction:

    def test_sell_token_on_pump(self):
        """测试卖出代币时"""
        sig = "4WZR6kQU8iDbxwFpDntbfN13f2eHpVrxKVUkvLxq33m7KNuxWN36tjEQdJS4ooEhsuBW73XHFoVwDNm7oqCQ8SAC"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        assert recursive_compare(
            {
                "owner": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj",
                "signature": "4WZR6kQU8iDbxwFpDntbfN13f2eHpVrxKVUkvLxq33m7KNuxWN36tjEQdJS4ooEhsuBW73XHFoVwDNm7oqCQ8SAC",
                "transaction_id": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj:HEqhzg7NQMBiD7os4EEvXTaL4qJCoYSXMrtnY1twpump:0.0:clear",
                "transaction_type": "clear",
                "token": {
                    "mint": "HEqhzg7NQMBiD7os4EEvXTaL4qJCoYSXMrtnY1twpump",
                    "amount": 0.0,
                    "pre_balance": 34141019.152748,
                    "post_balance": 0.0,
                    "change_amount": -34141019.152748,
                    "name": "ALL IN",
                    "symbol": "ALL IN",
                },
                "sol": {
                    "pre_balance": 16.248613404,
                    "post_balance": 17.268662841,
                    "change_amount": 1.020049437,
                },
            },
            data,
        )

    def test_open_token_on_pump(self):
        """测试开仓交易，来自pump"""
        sig = "5uWAsNnrLaUudAqYDDm4qLBsLCgPy9pBYEStntdfaqSTVfnDirQFE3QzQXhUr63gaypK66BX694pwkub6Zfv68HM"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        print(data)
        assert recursive_compare(
            {
                "owner": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr",
                "signature": "5uWAsNnrLaUudAqYDDm4qLBsLCgPy9pBYEStntdfaqSTVfnDirQFE3QzQXhUr63gaypK66BX694pwkub6Zfv68HM",
                "transaction_id": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr:Fti665JXgJiQVS4fZfqL75ercvquS3mUkcAsvoqnpump:49036161.0:open",
                "transaction_type": "open",
                "token": {
                    "mint": "Fti665JXgJiQVS4fZfqL75ercvquS3mUkcAsvoqnpump",
                    "amount": 49036161.0,
                    "pre_balance": 0.0,
                    "post_balance": 49036161.0,
                    "change_amount": 49036161.0,
                    "name": "Yap Coin",
                    "symbol": "YAP",
                },
                "sol": {
                    "pre_balance": 11.663274066,
                    "post_balance": 8.811877559,
                    "change_amount": -2.851396507,
                },
            },
            data,
        )

    def test_03(self):
        sig = "kEXjseANbqzLKXpxNezK1pEkhgTq7zTBpF14aBWEWwyhbfNDfzjxwvZA4CgsofGXRhqiLZ5mKtUXaTNdDzj6CoF"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        print(data)
        assert recursive_compare(
            {
                "owner": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj",
                "signature": "kEXjseANbqzLKXpxNezK1pEkhgTq7zTBpF14aBWEWwyhbfNDfzjxwvZA4CgsofGXRhqiLZ5mKtUXaTNdDzj6CoF",
                "transaction_id": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj:BCm77iDU3VmL5qGQJcfKMeoXZwWNGUdq8G8hWywFpump:34141019.152748:open",
                "transaction_type": "open",
                "token": {
                    "mint": "BCm77iDU3VmL5qGQJcfKMeoXZwWNGUdq8G8hWywFpump",
                    "amount": 34141019.152748,
                    "pre_balance": 0.0,
                    "post_balance": 34141019.152748,
                    "change_amount": 34141019.152748,
                    "name": "BodhiBucks",
                    "symbol": "BOBU",
                },
                "sol": {
                    "pre_balance": 31.911599867,
                    "post_balance": 30.906192936,
                    "change_amount": -1.005406931,
                },
            },
            data,
        )

    def test_reduce_token_using_wsol_on_raydium(self):
        """测试减仓交易，来自Raydium交易所

        {
            "owner": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr",
            "signature": "2PToeWwAeyeFZk3KKdqmSRwtuTGkZfQq8jLDtt6WhndtL6BdFgZtAxsVeab3RofkhrNxpyY1kL6abx8vVBbNeCCe",
            "transaction_id": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr:98CdcBjcf83PUvRr5vPpvhy596TDdT74ksjccueMpump:0.740304:reduce",
            "transaction_type": "reduce",
            "token": {
                "mint": "98CdcBjcf83PUvRr5vPpvhy596TDdT74ksjccueMpump",
                "amount": 0.740304,
                "pre_balance": 1395184.740304,
                "post_balance": 0.740304,
                "change_amount": -1395184.0,
                "name": "Joey",
                "symbol": "JOEY"
            },
            "sol": {
                "pre_balance": 2.651727686,
                "post_balance": 4.775330168,
                "change_amount": 2.123602482
            }
        }
        """
        sig = "2PToeWwAeyeFZk3KKdqmSRwtuTGkZfQq8jLDtt6WhndtL6BdFgZtAxsVeab3RofkhrNxpyY1kL6abx8vVBbNeCCe"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        assert recursive_compare(
            {
                "owner": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr",
                "signature": "2PToeWwAeyeFZk3KKdqmSRwtuTGkZfQq8jLDtt6WhndtL6BdFgZtAxsVeab3RofkhrNxpyY1kL6abx8vVBbNeCCe",
                "transaction_id": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr:98CdcBjcf83PUvRr5vPpvhy596TDdT74ksjccueMpump:0.740304:reduce",
                "transaction_type": "reduce",
                "token": {
                    "mint": "98CdcBjcf83PUvRr5vPpvhy596TDdT74ksjccueMpump",
                    "amount": 0.740304,
                    "pre_balance": 1395184.740304,
                    "post_balance": 0.740304,
                    "change_amount": -1395184.0,
                    "name": "Joey",
                    "symbol": "JOEY",
                },
                "sol": {
                    "pre_balance": 2.651727686,
                    "post_balance": 4.775330168,
                    "change_amount": 2.123602482,
                },
            },
            data,
        )

    def test_swap_token_from_raydium_pool(self):
        # 从交易者钱包扣除 sol 到 Raydium Pool 中
        # 然后从 Pool 中提取代币
        sig = "2p9ea57oD8mHJg6pAJH38GjHZsjeXp9JyGNCq3QxqSCuAgSnqJPRvGhmvuPyo91GhpKhEy3HG8VBwpSkwMDXZpPP"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        print(data)
        assert recursive_compare(
            {
                "owner": "BoaaUDC1i3GnAN26M8d2sBKfk28LAn56LLAyctVoCrh2",
                "signature": "2p9ea57oD8mHJg6pAJH38GjHZsjeXp9JyGNCq3QxqSCuAgSnqJPRvGhmvuPyo91GhpKhEy3HG8VBwpSkwMDXZpPP",
                "transaction_id": "BoaaUDC1i3GnAN26M8d2sBKfk28LAn56LLAyctVoCrh2:Eyt3iDq7aWebvoTZGRiUEi53Ycbv6Kqws93GZE6ypump:7278641.175354:open",
                "transaction_type": "open",
                "token": {
                    "mint": "Eyt3iDq7aWebvoTZGRiUEi53Ycbv6Kqws93GZE6ypump",
                    "amount": 7278641.175354,
                    "pre_balance": 0.0,
                    "post_balance": 7278641.175354,
                    "change_amount": 7278641.175354,
                    "name": "Square Up Cat",
                    "symbol": "²up",
                },
                "sol": {
                    "pre_balance": 3.605925508,
                    "post_balance": 2.092415507,
                    "change_amount": -1.513510001,
                },
                "platform": "Raydium",
            },
            data,
        )

    def test_swap_token_to_raydium_pool(self):
        sig = "5fQeZCBpV76AGxqhPWE7KmwZwvK8rLwt5eQTqEGRdGeqmkicKAN6ULusTRLj6L8D63SqAx24dwKyccEuvr8Wmh87"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        print(data)
        assert recursive_compare(
            {
                "owner": "BoaaUDC1i3GnAN26M8d2sBKfk28LAn56LLAyctVoCrh2",
                "signature": "5fQeZCBpV76AGxqhPWE7KmwZwvK8rLwt5eQTqEGRdGeqmkicKAN6ULusTRLj6L8D63SqAx24dwKyccEuvr8Wmh87",
                "transaction_id": "BoaaUDC1i3GnAN26M8d2sBKfk28LAn56LLAyctVoCrh2:Eyt3iDq7aWebvoTZGRiUEi53Ycbv6Kqws93GZE6ypump:0.0:clear",
                "transaction_type": "clear",
                "token": {
                    "mint": "Eyt3iDq7aWebvoTZGRiUEi53Ycbv6Kqws93GZE6ypump",
                    "amount": 0.0,
                    "pre_balance": 7278641.175354,
                    "post_balance": 0.0,
                    "change_amount": -7278641.175354,
                    "name": "Square Up Cat",
                    "symbol": "²up",
                },
                "sol": {
                    "pre_balance": 1.350856909,
                    "post_balance": 2.781873861,
                    "change_amount": 1.431016952,
                },
                "platform": "Raydium",
            },
            data,
        )

    # TODO: 代测试
    # WSOL
    # 4DbJun1zGarSZhocdL3YjFysVfQX5oaahCi9iVhAsaVZUh7VTvzLP9qK9Y1w77YGnY2qLpwq4RUhvJWR6z24fKEH

    # def test_03(self):
    #     sig = "5EHuEwtZDuSGwZhiySHqEZrchwvmw9Vomsp3cWcZDTycrMyL96Gn541fpo791WJMNmrmvTBhW9T3ATEyoSPMxGJu"
    #     data = handle_transaction(sig)
    #     assert_dict(
    #         data,
    #         {},
    #     )

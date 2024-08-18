from parsers import TransactionParserWithSolscan


def assert_dict(data, expected):
    keys = (
        "address",
        "token_mint",
        "token_amount",
        "change_amount",
        "pre_token_balance",
        "post_token_balance",
        "transaction_type",
        "transaction_id",
        "signature",
    )
    for key in keys:
        if expected[key] != data.get(key):
            print(f"Expect: {expected[key]}, But {data.get(key)}")
            assert False


class TestHandleTransaction:

    def test_01(self):
        sig = "4WZR6kQU8iDbxwFpDntbfN13f2eHpVrxKVUkvLxq33m7KNuxWN36tjEQdJS4ooEhsuBW73XHFoVwDNm7oqCQ8SAC"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()

        assert_dict(
            data,
            {
                "address": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj",
                "token_mint": "HEqhzg7NQMBiD7os4EEvXTaL4qJCoYSXMrtnY1twpump",
                "token_amount": 0,
                "change_amount": -34141019.152748,
                "pre_token_balance": 34141019.152748,
                "post_token_balance": 0,
                "transaction_type": "clear",
                "transaction_id": "CANTSsRNWR2ykW4YejwMPgLBJ1GbR1FYoX47yJconumj:HEqhzg7NQMBiD7os4EEvXTaL4qJCoYSXMrtnY1twpump:0:clear",
                "signature": sig,
            },
        )

    def test_02(self):
        sig = "5uWAsNnrLaUudAqYDDm4qLBsLCgPy9pBYEStntdfaqSTVfnDirQFE3QzQXhUr63gaypK66BX694pwkub6Zfv68HM"
        tp = TransactionParserWithSolscan(sig)
        data = tp.get_result()
        assert_dict(
            data,
            {
                "address": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr",
                "token_mint": "Fti665JXgJiQVS4fZfqL75ercvquS3mUkcAsvoqnpump",
                "token_amount": 49036161.0,
                "pre_token_balance": 0,
                "post_token_balance": 49036161.0,
                "change_amount": 49036161.0,
                "transaction_type": "open",
                "transaction_id": "GxaeXcakf96MGvenQZssRNjHaNDGLSu2REq2xpKoTYr:Fti665JXgJiQVS4fZfqL75ercvquS3mUkcAsvoqnpump:49036161.0:open",
                "signature": "5uWAsNnrLaUudAqYDDm4qLBsLCgPy9pBYEStntdfaqSTVfnDirQFE3QzQXhUr63gaypK66BX694pwkub6Zfv68HM",
            },
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

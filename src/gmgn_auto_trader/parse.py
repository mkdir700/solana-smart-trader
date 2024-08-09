import re


class ExtractTop10Percent:
    """Extract the top 10 percent from a message."""

    rule = re.compile(r"(?<=✅TOP 10: )\d+\.\d+")

    @classmethod
    def get_value(cls, raw_message: str) -> float:
        match = cls.rule.search(raw_message)
        if match is None:
            raise ValueError("No match found")
        return float(match.group())


class MatchTop10Percent:
    """Match the top 10 percent message."""

    rule = re.compile(r"✅TOP 10:")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class MatchNoMintParser:
    """Extract the no mint message."""

    rule = re.compile(r"✅ NoMint")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class MatchBlacklistParser:

    rule = re.compile(r"✅Blacklist")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class MatchBurntParser:

    rule = re.compile(r"✅Burnt")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class MatchDevRichParser:

    rule = re.compile(r"🟢 Rich Dev")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class ExtractContractAddress:
    """Extract the contract address from a message."""

    rule = re.compile(r"\n([A-Za-z0-9]+)")

    @classmethod
    def get_value(cls, raw_message: str) -> str:
        match = cls.rule.search(raw_message)
        if match is None:
            raise ValueError("No match found")
        return match.group()


class MatchQuicklyCompletedOnPump:

    rule = re.compile(r"秒满 💊💊💊")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


class MatchCompletedOnPump:

    rule = re.compile(r"满 💊💊💊")

    @classmethod
    def get_value(cls, raw_message: str) -> bool:
        match = cls.rule.search(raw_message)
        return match is not None


def extract_top_10_percent(raw_message: str) -> float:
    """提取前10个钱包占比"""
    return ExtractTop10Percent.get_value(raw_message) / 100


def is_safe(raw_message: str) -> bool:
    """是否是安全的"""
    return (
        MatchTop10Percent.get_value(raw_message)
        and MatchNoMintParser.get_value(raw_message)
        and MatchBlacklistParser.get_value(raw_message)
        and MatchBurntParser.get_value(raw_message)
    )


def extract_contract_address(raw_message: str) -> str:
    """提取合约地址"""
    return ExtractContractAddress.get_value(raw_message).strip()


def is_dev_rich(raw_message: str) -> bool:
    return MatchDevRichParser.get_value(raw_message)


def is_completed_on_pump(raw_message: str) -> bool:
    return MatchCompletedOnPump.get_value(raw_message)

"""假数据生成工具，用于接口入参随机化，避免硬编码脏数据"""
import random
import string
import uuid
from datetime import datetime, timedelta


class FakerUtil:
    """随机测试数据生成"""
    @staticmethod
    def random_str(length: int = 8) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def random_name() -> str:
        surnames = ["张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴"]
        given = ["伟", "芳", "娜", "敏", "静", "磊", "军", "洋", "勇", "艳", "杰", "涛"]
        return random.choice(surnames) + random.choice(given)

    @staticmethod
    def random_phone() -> str:
        prefix = random.choice(["130", "131", "135", "136", "137", "138", "150", "158", "186", "189"])
        suffix = "".join(random.choices(string.digits, k=8))
        return prefix + suffix

    @staticmethod
    def random_email() -> str:
        return f"{FakerUtil.random_str(6)}@example.com"

    @staticmethod
    def random_uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def random_int(start: int = 1, end: int = 100) -> int:
        return random.randint(start, end)

    @staticmethod
    def future_date(days: int = 30) -> str:
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

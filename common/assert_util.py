"""统一断言组件（业务层）。支持状态码、jsonpath、正则、JSON Schema、响应时间 SLA。"""
import json
import re
import time

import jsonpath
from jsonschema import validate, ValidationError

from .config_util import read_ini_config


class AssertUtil:
    """统一断言工具"""

    @staticmethod
    def status_code(resp, expect_code=200, msg="状态码"):
        """状态码断言"""
        actual = resp.status_code
        assert actual == expect_code, f"{msg}断言失败: 预期{expect_code}, 实际{actual}"

    @staticmethod
    def jsonpath_equal(resp, expr: str, expect, msg="jsonpath字段"):
        """jsonpath提取字段并等于期望值"""
        data = resp.json()
        result = jsonpath.search(expr, data)
        assert result, f"{msg}断言失败: jsonpath {expr} 提取不到数据, 实际响应: {data}"
        actual = result[0]
        # 宽松比较：期望值可能是${变量}解析出的字符串，与int值比较时转成同一类型
        if isinstance(expect, str) and isinstance(actual, (int, float)) and expect.lstrip("-").isdigit():
            expect = int(expect) if isinstance(actual, int) else float(expect)
        assert actual == expect, f"{msg}断言失败: 预期{expect}, 实际{actual}"

    @staticmethod
    def regex_contains(text: str, pattern: str, msg="正则"):
        """文本包含指定正则"""
        assert re.search(pattern, text), f"{msg}断言失败: 在文本中未匹配到正则 {pattern}"
        print(f"[ASSERT] 正则 {pattern} 匹配成功")

    @staticmethod
    def json_schema(resp, schema: dict, msg="JSON Schema"):
        try:
            validate(instance=resp.json(), schema=schema)
            print(f"[ASSERT] {msg} 校验通过")
        except ValidationError as e:
            raise AssertionError(f"{msg}校验失败: {e.message}")

    @staticmethod
    def response_sla(resp, sla_ms: int = None, msg="响应时间SLA"):
        """响应时间SLA断言：响应耗时需在阈值内"""
        cfg = read_ini_config()
        sla_ms = sla_ms or cfg["requests"]["timeout"]
        elapsed_ms = resp.elapsed.total_seconds() * 1000
        assert elapsed_ms <= sla_ms, f"{msg}断言失败: 耗时{elapsed_ms:.0f}ms, 超出阈值{sla_ms}ms"
        print(f"[ASSERT] {msg}通过: 耗时{elapsed_ms:.0f}ms <= {sla_ms}ms")

    @staticmethod
    def elapsed_ms(resp) -> float:
        """返回响应时间"""
        return resp.elapsed.total_seconds() * 1000

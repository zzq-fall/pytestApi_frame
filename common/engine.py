"""
YAML 用例驱动引擎（业务层核心）
支持：
1. 数据驱动：读取 data/*.yaml 中用例，循环执行，0 代码新增用例
2. 参数关联：响应字段 jsonpath 提取存入变量，请求中用 ${变量} 引用
3. 统一断言：状态码 / jsonpath / 正则 / JSON Schema / 响应时间 SLA
4. 假数据：${__random_name} 等内置函数生成随机数据
"""
import json
import os
import re

import jsonpath
import yaml

from common.request_util import RequestUtil
from common.assert_util import AssertUtil
from common.faker_util import FakerUtil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXTRACT_FILE = os.path.join(DATA_DIR, "extract.yaml")

# 全局变量池：存储接口间关联数据
VARIABLES = {}

# 变量/假数据/内置函数 引用正则，例如${token}或${__random_name}
VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _load_extract():
    """启动时加载extract.yaml中历史关联数据"""
    global VARIABLES
    if os.path.exists(EXTRACT_FILE):
        data = yaml.safe_load(open(EXTRACT_FILE, encoding="utf-8")) or {}
        VARIABLES = data.get("extract", {})


def _save_extract():
    """把变量池写回 extract.yaml，便于排错查看关联数据"""
    with open(EXTRACT_FILE, "w", encoding="utf-8") as f:
        yaml.dump({"extract": VARIABLES}, f, allow_unicode=True)


def resolve(value):
    """把字符串/字典/列表中的 ${变量}或${__函数}替换为实际值"""
    if isinstance(value, dict):
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    if isinstance(value, str):
        def _replace(match):
            key = match.group(1).strip()
            if key.startswith("__"):
                func = getattr(FakerUtil, key[2:], None)
                if func:
                    return str(func())
                return ""
            return str(VARIABLES.get(key, ""))  # 未关联到则替换为空

        return VAR_PATTERN.sub(_replace, value)
    return value


def _do_assert(resp, expected: dict):
    """执行统一断言，expected结构参考data用例
    期望值也支持${变量}引用（resolve 后再比较）"""
    AssertUtil.status_code(resp, expected.get("status_code", 200))
    for expr, expect_val in (expected.get("jsonpath", {}) or {}).items():
        # 期望值允许引用关联变量，如 "$.data.id": "${new_user_id}"
        AssertUtil.jsonpath_equal(resp, expr, resolve(expect_val))
    for text in (expected.get("regex", []) or []):
        AssertUtil.regex_contains(resp.text, text)
    if "schema" in expected:
        schema = expected["schema"]
        if isinstance(schema, str):
            schema = json.loads(schema)
        AssertUtil.json_schema(resp, schema)
    if expected.get("sla"):
        AssertUtil.response_sla(resp, expected.get("sla_ms"))


def run_case(case: dict):
    """
    执行单条 yaml 用例
    """
    request_util = RequestUtil()
    req = case.get("request", {})
    method = req.get("method", "GET")
    url = resolve(req.get("url", ""))
    headers = resolve(req.get("headers", {}) or {})
    json_body = resolve(req.get("json"))
    data = resolve(req.get("data"))
    params = resolve(req.get("params"))

    resp = request_util.send(
        method, url,
        headers=headers, params=params,
        json_body=json_body, data=data,
    )

    # 响应字段提取，存入变量池，供后续用例关联
    for key, expr in (case.get("extract", {}) or {}).items():
        result = jsonpath.search(expr, resp.json())
        if result:
            VARIABLES[key] = result[0]
    _save_extract()

    # 统一断言
    _do_assert(resp, case.get("expected", {}) or {})

    print(f"[CASE-PASS] {case.get('name')}")
    return resp

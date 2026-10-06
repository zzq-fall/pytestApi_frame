# -*- coding: utf-8 -*-
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import pytest
import yaml
from common.engine import run_case

# 读取yaml用例文件
yaml_path = os.path.join(BASE_DIR, "data", "api_cases.yaml")

# 加载所有用例
with open(yaml_path, encoding="utf-8") as f:
    yaml_data = yaml.safe_load(f)
case_list = list(yaml_data.get("cases", {}).values())


# parametrize数据驱动：把yaml里每一条用例变成一条pytest测试
@pytest.mark.parametrize("case", case_list)
def test_api_flow(case):
    run_case(case)

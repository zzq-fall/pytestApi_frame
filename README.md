# pytest-api-automation

个人接口自动化测试练习项目（业务层封装）——对应简历"接口自动化测试框架（pytestapi-frame）"项目。

基于 `pytest + requests + PyYAML + jsonpath + allure` 开源技术栈，实现
**yaml 数据驱动**、**接口参数关联**、**统一断言组件**（jsonpath/正则/数据库）、**假数据生成**、
**Allure 报告集成**等业务层能力。本项目封装的是业务执行层代码，底层依赖成熟开源库，不重复造框架轮子。

> 说明：本项目为个人学习与求职展示项目，定位是"基于开源框架做业务层封装与扩展"，
> 底层 pytest / requests 等均为开源库；本人独立完成请求封装、断言组件、数据驱动、
> 参数关联、假数据、报告等业务代码。

---

## 功能特性

| 模块 | 说明 |
| --- | --- |
| YAML 数据驱动 | 在 `data/api_cases.yaml` 中写用例即可 0 代码新增用例 |
| 接口参数关联 | 响应字段 jsonpath 提取存入变量池，请求中用 `${变量}` 引用 |
| 统一断言组件 | 状态码 / jsonpath / 正则 / 数据库断言 |
| 假数据生成 | `${__random_name}` 等内置函数生成随机姓名、手机号、邮箱、UUID |
| Allure 报告 | 执行后生成原始结果，`allure serve` 查看可视化报告 |
| 可扩展 CI | 对接 Docker + Jenkins 实现持续集成（见下文） |

## 技术栈

- pytest（用例执行 / fixture）
- requests（HTTP 请求）
- PyYAML（用例数据驱动）
- jsonpath（响应字段提取 / 字段断言）
- allure-pytest（可视化测试报告）

## 目录结构

```
pytest-api-automation/
├── common/                  # 业务层公共封装（本项目核心代码）
│   ├── request_util.py      # 请求封装（复用 Session、统一超时）
│   ├── assert_util.py       # 统一断言（状态码/jsonpath/正则/数据库）
│   ├── engine.py            # yaml 驱动引擎（数据驱动+参数关联+断言执行）
│   ├── faker_util.py        # 假数据生成
│   └── config_util.py       # 配置读取
├── data/                    # 测试用例数据（yaml 驱动）
│   ├── api_cases.yaml       # 接口用例
│   └── extract.yaml         # 关联变量存储
│   └── test_api.py          # 测试业务
├── conf.ini                 # 环境 / 超时 / 数据库 / 报告配置
├── scripts/
│   └── mock_server.py       # 本地 mock 服务器（纯标准库，便于离线演示）
├── report/                  # allure 结果输出
├── run.py                   # 执行入口
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖（建议 Python 3.8+）
pip install -r requirements.txt

# 2. 启动 mock 服务器（新开一个终端）
python scripts/mock_server.py

# 3. 运行接口自动化用例（另开一个终端）
python run.py
# 或直接：pytest case -s --alluredir=report/allure-result

# 4. 查看 Allure 可视化报告
allure serve report/allure-result
```

执行成功会看到 4 个接口步骤全部通过：
`登录获取token → 创建用户(参数关联+假数据) → 查询用户列表 → 查询新用户(参数关联)`

## 用例编写示例

在 `data/api_cases.yaml` 中新增一个节点即可（0 代码新增用例）：

```yaml
my_new_case:
  name: "查询用户列表"
  request:
    method: GET
    url: /api/users
    params:
      page: 1
  expected:
    status_code: 200
    jsonpath:
      "$.code": 0
```

### 接口参数关联

```yaml
# 1. 在登录接口响应中提取 token
extract:
  token: "$.token"

# 2. 后续请求头引用
headers:
  Authorization: "Bearer ${token}"
```

### 假数据

```yaml
json:
  name: "${__random_name}"     # 随机中文名
  email: "${__random_email}"   # 随机邮箱
  phone: "${__random_phone}"   # 随机手机号
```

### 统一断言

```yaml
expected:
  status_code: 200
  jsonpath:        # jsonpath 字段断言
    "$.code": 0
  regex:           # 正则包含断言
    - "example.com"
  # db: [1, 1]    # 数据库断言：[查询到的行数, 期望行数]，接入真实 MySQL 后启用
```

## 持续集成（Docker + Jenkins）

接口自动化项目可直接接入 Docker + Jenkins 流水线：

1. 用 Dockerfile 构建含 pytest 依赖的 Python 镜像；
2. Jenkins 定时任务执行 `pytest case --alluredir=report/allure-result`；
3. 使用 allure 插件归档报告，失败时推送结果到邮箱。

## 接入真实项目

把 `conf.ini` 中的 `base_url` 改成真实被测环境地址即可，例如：

```ini
base_url = http://192.168.1.100:8090
```

## License

仅供学习与求职展示使用。

import pytest
from common.email_util import EmailSender
from .common.config_util import read_ini_config

# 会话级fixture，初始化邮件对象
@pytest.fixture(scope="session", autouse=True)
def email_send():
    cfg = read_ini_config()
    sender = EmailSender(
        smtp_server=cfg["smtp_server"],
        smtp_port=cfg["smtp_port"],
        email_user=cfg["email_user"],
        email_pwd=cfg["email_pwd"],
        receiver=cfg["receiver_email"]
    )
    yield sender

# pytest执行结束钩子，统计用例，发送邮件
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    cfg = read_ini_config()
    email = EmailSender(
        smtp_server=cfg["smtp_server"],
        smtp_port=cfg["smtp_port"],
        email_user=cfg["email_user"],
        email_pwd=cfg["email_pwd"],
        receiver=cfg["receiver_email"]
    )

    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    total = passed + failed + skipped

    email_content = f"""
【接口自动化测试执行报告】
总用例数：{total}
通过：{passed}
失败：{failed}
跳过：{skipped}
执行结果：{"全部用例执行通过" if failed == 0 else "存在失败用例，请及时排查！"}
"""
    email.send_email(subject="自动化测试任务通知", content=email_content)

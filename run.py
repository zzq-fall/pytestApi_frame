import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    if "--mock" in sys.argv:
        print(">> 启动 mock 服务器...")
        mock = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "scripts", "mock_server.py")])
        import time

        time.sleep(1)

    print("--执行接口自动化用例并生成 allure 结果...")
    code = subprocess.call([
        sys.executable, "-m", "pytest",
        os.path.join(BASE_DIR, "data"),
        "-s",
        "--alluredir", os.path.join(BASE_DIR, "report", "allure-result"),
    ])

    if "--mock" in sys.argv:
        mock.terminate()
    sys.exit(code)

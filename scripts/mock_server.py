"""
本地Mock服务器
默认监听 127.0.0.1:9000
"""
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST, PORT = "127.0.0.1", 9000

# 模拟数据库
DB = {
    "users": [
        {"id": 1, "name": "张伟", "email": "zhangwei@example.com"},
        {"id": 2, "name": "李娜", "email": "lina@example.com"},
    ]
}


class MockHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/login":
            body = self._read_body()
            if body.get("username") and body.get("password"):
                self._send_json({
                    "code": 0,
                    "token": "mock-token-abc123",
                    "expires_in": 7200,
                })
            else:
                self._send_json({"code": 40001, "message": "用户名或密码错误"}, 200)
        elif path == "/api/users":
            body = self._read_body()
            new_id = max(u["id"] for u in DB["users"]) + 1
            user = {"id": new_id, "name": body.get("name", ""), "email": body.get("email", "")}
            DB["users"].append(user)
            self._send_json({"code": 0, "data": user})
        else:
            self._send_json({"code": 40400, "message": "接口不存在"}, 404)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        time.sleep(0.05)  # 模拟网络耗时，用于演示SLA断言
        if path == "/api/users":
            page = int(dict(pair.split("=") for pair in parsed.query.split("&") if "=" in pair).get("page", 1))
            items = DB["users"]
            self._send_json({"code": 0, "data": {"page": page, "total": len(items), "items": items}})
        elif path.startswith("/api/users/"):
            uid = int(path.rsplit("/", 1)[-1])
            user = next((u for u in DB["users"] if u["id"] == uid), None)
            if user:
                self._send_json({"code": 0, "data": user})
            else:
                self._send_json({"code": 40400, "message": "用户不存在"}, 200)
        else:
            self._send_json({"code": 40400, "message": "接口不存在"}, 404)

    def log_message(self, *args):
        print(f"[MOCK] {self.command} {self.path}")


if __name__ == "__main__":
    print(f"Mock server 启动: http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), MockHandler).serve_forever()

# -*- coding: utf-8 -*-
"""HTTP 请求统一封装"""
import requests
from .config_util import  read_ini_config


class RequestUtil:
    """
    统一请求封装：复用 Session、统一超时、统一日志。
    """
    cfg=read_ini_config()

    def __init__(self):
        self.session = requests.Session()

    def send(self, method: str, url: str, *, headers=None, params=None,
             json_body=None, data=None, files=None) -> requests.Response:
        """
        发送任意方法请求。
        :param method:GET/POST/PUT/DELETE/PATCH
        :param url:相对路径
        :param headers:请求头
        :param params:query 参数
        :param json_body:JSON body
        :param data:form body
        :param files:文件上传
        """
        full_url = url if url.startswith("http") else self.cfg["environment"]["base_url"] + url
        method = method.upper()
        timeout = int(self.cfg["request"]["timeout"])

        resp = self.session.request(
            method=method,
            url=full_url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            files=files,
            timeout=timeout,
        )
        print(f"[HTTP] {method} {full_url} -> {resp.status_code}")
        return resp

    # 常用方法便捷封装
    def get(self, url, **kwargs):
        return self.send("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.send("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.send("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.send("DELETE", url, **kwargs)

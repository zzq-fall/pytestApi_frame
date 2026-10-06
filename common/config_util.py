import configparser
import os

def read_ini_config():
    """读取根目录conf.ini配置文件"""
    cfg = configparser.ConfigParser()
    # 获取项目根目录下conf.ini的路径
    ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conf.ini")
    cfg.read(ini_path, encoding="utf-8")
    return cfg

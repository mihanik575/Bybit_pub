import os
import requests
import time
import hashlib
import hmac
from pprint import pprint
import logging


# Настройка логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
py_logger.info(f"Testing the custom logger for module {__name__}...")


def print_log(text):
    #print(text)
    py_logger.info(text)


class BybitConnector:
    time_stamp: str

    def __init__(self, base_url, api_key, api_secret, recv_window):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.recv_window = recv_window
        self.http_client = requests.Session()

    def http_request(self, end_point, method, payload, info=None):
        self.time_stamp = str(int(time.time() * 10 ** 3))
        data = self.prepare_data(method, payload)
        signature = self.gen_signature(data)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': self.time_stamp,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        if method == "POST":
            response = self.http_client.request(method, self.base_url + end_point,
                                                headers=headers, data=data)
        else:
            response = self.http_client.request(method,
                                                self.base_url + end_point + "?" + data,
                                                headers=headers)
        if info:
            print_log(info + " Elapsed Time : " + str(response.elapsed))
        return response.json()

    def gen_signature(self, payload):
        param_str = str(self.time_stamp) + self.api_key + self.recv_window + payload
        hash = hmac.new(bytes(self.api_secret, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def prepare_data(self, method, data):
        if method == "POST":
            return '{' + ','.join([f'"{key}": "{value}"' for key, value in data.items()]) + '}'
        else:
            return '&'.join([f'{key}={value}' for key, value in data.items()])

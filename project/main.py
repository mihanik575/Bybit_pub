# imports block
import os
import time
from datetime import datetime
import logging

import yaml
from pprint import pprint
import matplotlib.pyplot as plt

from connection.methods import BybitConnector, py_logger, print_log


def print_time(number):
    print(datetime.fromtimestamp(int(number) / 1000))


# logic block
dir_path = os.path.dirname(os.path.realpath(__file__))

with open(f'{dir_path}/data/config.yaml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

with open(f'{dir_path}/data/requests.yaml', 'r') as file:
    params = yaml.load(file, Loader=yaml.FullLoader)

new_conn = BybitConnector(config['platform'],
                          config['api_key'],
                          config['api_secret'],
                          str(5000))


def get_btc_data():
    global params
    params['get_kline_btc']['start'] = '0'
    params['get_kline_btc']['end'] = str(int(time.time() * 10 ** 3))
    return new_conn.http_request("/v5/market/kline", "GET",
                                 params['get_kline_btc'])


def get_eth_data():
    global params
    params['get_kline_eth']['start'] = '0'
    params['get_kline_eth']['end'] = str(int(time.time() * 10 ** 3))
    return new_conn.http_request("/v5/market/kline", "GET",
                                 params['get_kline_eth'],
                                 "Get kline data ETH 'linear'")


def get_all_data(scale):
    btc_data = get_btc_data()
    eth_data = get_eth_data()

    # Общая временная шкала (настроен минутный интервал)
    global_time = [x[0] for x in btc_data['result']['list']]

    # Размер массива данных (установлен 60 в шаблонах requsts.yaml)
    len_data = len(btc_data['result']['list'])

    # Получаем разницу открытия и закрытия на каждом интервале (1мин)
    btc_start_price = [float(x[1]) for x in btc_data['result']['list']]
    btc_end_price = [float(x[4]) for x in btc_data['result']['list']]

    # Вычисление разниц на интервалах для BTCUSDT
    btc_margin = []
    for i in range(len_data):
        btc_margin.append(btc_end_price[i] - btc_start_price[i])

    eth_start_price = [float(x[1]) for x in eth_data['result']['list']]
    eth_end_price = [float(x[4]) for x in eth_data['result']['list']]
    print_log(f"last_end_price: {eth_end_price[0]}")
    show_tiker()

    # Цену, от которой считаем изменение собственной цены ETHUSDT
    # Начало 60 минутного интервала
    start_price = eth_end_price[-1]

    # Вычисление разниц на интервалах для ETHUSDT
    eth_margin = []
    for i in range(len_data):
        eth_margin.append(eth_end_price[i] - eth_start_price[i])

    # Получаем разницу между диапазонами изменения монет на каждом интервале
    # с учетом масштаба scale
    coins_margin = []
    for i in range(len_data):
        coins_margin.append(btc_margin[i] * scale - eth_margin[i])


    variations = []
    for i in range(len_data):
        variations.append(round(coins_margin[i]/start_price, 4))

    total_var = 0
    for i in variations:
        total_var += i
    print_log(f"total var: {total_var}")
    if abs(total_var):
        print(f"ИЗМЕНЕНИЕ ЦЕНЫ ЗА ПОСЛЕДНИЕ 60 МИНУТ СОСТАВИЛО {round(total_var*100, 2)}%")

    # Графики
    #plt.clf()
    #plt.plot(range(0, 60), variations)
    #plt.show()
    #plt.draw()
    #plt.gcf().canvas.flush_events()

def show_tiker():
    data = new_conn.http_request("/v5/market/tickers", "GET",
                                 params['get_tickers'])

    price = data['result']['list'][0]['lastPrice']
    print_log(f"get_ticker_price: {price}")


# Вычисляем глобальное отношение между активами (scale)
def get_scale():
    params = {'category': 'linear', 'symbol': 'ETHUSDT'}
    eth_data = new_conn.http_request("/v5/market/tickers", "GET", params)
    params = {'category': 'linear', 'symbol': 'BTCUSDT'}
    btc_data = new_conn.http_request("/v5/market/tickers", "GET", params)

    eth_price = float(eth_data['result']['list'][0]['lastPrice'])
    btc_price = float(btc_data['result']['list'][0]['lastPrice'])

    return eth_price/btc_price

def place_order():
    result = new_conn.http_request("/v5/order/create", "POST", params['place_order'])
    print(result)


def switch_mode():
    result = new_conn.http_request("/v5/position/switch-mode", "POST", params['switch_mode'])
    print(result)

def main():
   # switch_mode()
    place_order()


if __name__ == '__main__':
    main()

from binance.um_futures import UMFutures
#import finplot as fplt
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
import websocket
import websockets
import threading
import json
import telebot
import datetime
import statistics
import asyncio
import requests
import mplfinance as mpf
import csv
import joblib
import openpyxl
import xlsxwriter
import io
from matplotlib import pyplot as plt
from memory_profiler import profile
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error as mae # для подсчета ширины канала
import matplotlib 
matplotlib.use("agg")

key = '###'


stat_tg = '-###'  
screen_tg = '-###' # ver5
red_stop_tg = '-###'
screen_v20 = '-###'
max_8_take_40_tg = '-###'
clear_pnl_10_tg = '-###'
take_clear_pnl_80_tg = '-###'
error_tg = '-###'   
stat_tg = '-###'
TG_Bot_token = "###"  

client = UMFutures(key=key) # клиент для бинанса, КЛЮЧ обязателен для выгрузки трейдов
smooth_emoji = '🌊🌊🌊'
fast_emoji  = '💥💥💥'
btc_emoji = '‼️‼️‼️‼️‼️'
long_emoji = '🟢'
p_emoji = '❗️'
legendary_16 = '❗️❗️❗️❗️'
legendary_20 = '❗️❗️❗️❗️❗️'
legendary_30 = '🤯🤯🤯🤯🤯'
legendary_40 = '☠️☠️☠️☠️☠️'
legendary_60 = '🌋🗽🌋🗽'
legendary_100 = '🩻🤖🩻🤖🩻'
stats_emoji = '📈📈📈📈📈'

time_frame = '1m'

# TG_Bot_token=':'
bot = telebot.TeleBot(TG_Bot_token)

with open('/projects/data/price_acc.txt', 'r') as f:
    last = f.read()
    price_acc = json.loads(last)

with open('/projects/data/low_acc.txt', 'r') as f:
    last = f.read()
    low_acc = json.loads(last)

with open('/projects/data/high_acc.txt', 'r') as f:
    last = f.read()
    high_acc = json.loads(last)


symbols = []
for key in price_acc:
    symbols.append(key)

try:
    with open('/projects/Ver32/stats/alerts_stat.txt', 'r') as f:
        last = f.read()
        alerts_stat = json.loads(last)
except:
    alerts_stat = {
        'all_clear': float(0.0),
        'all_potential': float(0.0),
        'all_count_per_day': int(0),
        'wtp_potential': float(0.0),
        'wtp_clear': float(0.0),
        'wtp_count': int(0),
        'commission': float(0.0),
        'commission_wtp': float(0.0)
    }

try:
    with open('/projects/Ver32/stats/day_check.txt', 'r') as f:
        last = f.read()
        day_check = json.loads(last)
except:
    day_check = 0

try:
    with open('/projects/Ver32/stats_4h/alerts_stat_4h.txt', 'r') as f:
        last = f.read()
        alerts_stat_4h = json.loads(last)
except:
    alerts_stat_4h = {'clear': float(0.0), 'potential': float(0.0), 'wtp_clear': int(0), 'wtp_potential': float(0.0)}

try:
    with open('/projects/Ver32/stats_4h/alerts_stat_1h.txt', 'r') as f:
        last = f.read()
        alerts_stat_1h = json.loads(last)
except:
    alerts_stat_1h = {
        'plus_30': [0, 0, 0], 
        'plus_20': [0, 0, 0], 
        'plus_16': [0, 0, 0], 
        'plus_12': [0, 0, 0], 
        'plus_6': [0, 0, 0],
        'plus_3': [0, 0, 0], 
        'plus_1.5': [0, 0, 0], 
        'noise': [0, 0, 0], 
        'minus_1.5': [0, 0, 0], 
        'minus_3': [0, 0, 0], 
        'minus_6': [0, 0, 0], 
        'minus_12': [0, 0, 0], 
        'minus_16': [0, 0, 0], 
        'minus_20': [0, 0, 0], 
        'minus_30': [0, 0, 0]
    }


сap_name_1h = ['P!!!!!+', 'P!!!!!', 'P!!!!', 'P!!!', 'P!!', 'P!', 'P', 'N', 'D', 'D!', 'D!!', 'D!!!', 'D!!!!', 'D!!!!!', 'D!!!!!+'] 


try:
    with open('/projects/Ver32/stats_4h/hour_check_1h.txt', 'r') as f:
        last = f.read()
        hour_check_1h = json.loads(last)
except:
    hour_check_1h = 0


try:
    with open('/projects/Ver32/channel_price.txt', 'r') as f:
        last = f.read()
        channel_price = json.loads(last)

    with open('/projects/Ver32/channel_time.txt', 'r') as f:
        last = f.read()
        channel_time = json.loads(last)

    with open('/projects/Ver32/alerts_MT.txt', 'r') as f:
        last = f.read()
        alerts_MT = json.loads(last)

except:
    channel_price = {symbol: [[], []] for symbol in symbols}
    channel_time = {symbol: [[], []] for symbol in symbols}
    alerts_MT = {symbol: [1, 1] for symbol in symbols}

try:
    with open('/projects/Ver32/channel_cond.txt', 'r') as f:
        last = f.read()
        channel_cond = json.loads(last)
except:
    channel_cond = {symbol: [[], []] for symbol in symbols}

try:
    with open('/projects/Ver32/count_trades.txt', 'r') as f:
        last = f.read()
        count_trades = json.loads(last)
except:
    count_trades = 0

####################
try:
    high_ser = {}
    for i in high_acc:
        high_ser[i] = pd.Series(high_acc[i])

    low_ser = {}
    for i in low_acc:
        low_ser[i] = pd.Series(low_acc[i])

    close_ser = {}
    for i in price_acc:
        close_ser[i] = pd.Series(price_acc[i])

    with open('/projects/Ver32/lim_amp.txt', 'r') as f:
        last = f.read()
        lim_amp = json.loads(last)

    with open('/projects/Ver32/lim_atr.txt', 'r') as f:
        last = f.read()
        lim_atr = json.loads(last)

    # with open('/projects/Ver32/f1.txt', 'r') as f:
    #     last = f.read()
    #     f1 = json.loads(last)

    # with open('/projects/Ver32/f2.txt', 'r') as f:
    #     last = f.read()
    #     f2 = json.loads(last)

    with open('/projects/Ver32/current_minute_prices.txt', 'r') as f:
        last = f.read()
        current_minute_prices = json.loads(last)

    with open('/projects/Ver32/current_minute_start.txt', 'r') as f:
        last = f.read()
        current_minute_start = json.loads(last)

except:
    high_ser = {symb: pd.Series([None]) for symb in symbols}
    low_ser = {symb: pd.Series([None]) for symb in symbols}
    close_ser = {symb: pd.Series([None]) for symb in symbols}
    lim_amp = {symb: 0 for symb in symbols}
    lim_atr = {symb: 0 for symb in symbols}


    

    current_minute_prices = {symb: [] for symb in symbols}
    current_minute_start = {symb: 0 for symb in symbols}
############

try:
    with open('/projects/Ver32/max_average_bar_price.txt', 'r') as f:
        last = f.read()
        max_average_bar_price = json.loads(last)
except:
    max_average_bar_price = {symb: [0, 0] for symb in symbols}





def send_photo(chat_id, file, cap):
        url = f'https://api.telegram.org/bot{TG_Bot_token}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': chat_id, "caption": cap}
        response = requests.post(url, files=files, data=data)
        json_response = response.json()
        return json_response

##############-nk #############

# Гиперпараметры фильтра, объявляем как константу
try:
    with open('/projects/Ver32/time_last_kline.txt', 'r') as f:
        last = f.read()
        time_last_kline = json.loads(last)
except:
    time_last_kline = {symb: 0 for symb in symbols}


# хранят значения стопов и последний посчитанный ATR
try:
    with open('/projects/Ver32/red_stop.txt', 'r') as f:
        last = f.read()
        red_stop = json.loads(last)
except:
    red_stop = {symb: [None, None] for symb in symbols}

try:
    with open('/projects/Ver32/orange_stop.txt', 'r') as f:
        last = f.read()
        orange_stop = json.loads(last)
except:
    orange_stop = {symb: [None, None] for symb in symbols}

try:
    with open('/projects/Ver32/yellow_stop.txt', 'r') as f:
        last = f.read()
        yellow_stop = json.loads(last)
except:     
    yellow_stop = {symb: [None, None] for symb in symbols}

try:
    with open('/projects/Ver32/last_atr.txt', 'r') as f:
        last = f.read()
        last_atr = json.loads(last)
except:    
    last_atr = {symb: None for symb in symbols}

try:
    with open('/projects/Ver32/orange_ten_min_start.txt', 'r') as f:
        last = f.read()
        orange_ten_min_start = json.loads(last)
except:     
    orange_ten_min_start = {symb: [0, 0] for symb in symbols}

try:
    with open('/projects/Ver32/ten_min_start.txt', 'r') as f:
        last = f.read()
        ten_min_start = json.loads(last)
except:   
    ten_min_start = {symb: [0, 0] for symb in symbols}

try:
    with open('/projects/Ver32/sl_time.txt', 'r') as f:
        last = f.read()
        sl_time = json.loads(last)

except:    
    sl_time = {symb: [None, None] for symb in symbols}
    
try:
    with open('/projects/Ver32/green_mile.txt', 'r') as f:
        last = f.read()
        green_mile = json.loads(last)

    with open('/projects/Ver32/green_mile_time.txt', 'r') as f:
        last = f.read()
        green_mile_time = json.loads(last)

    with open('/projects/Ver32/green_mile_price.txt', 'r') as f:
        last = f.read()
        green_mile_price = json.loads(last)

    with open('/projects/Ver32/on_w4.txt', 'r') as f:
        last = f.read()
        on_w4 = json.loads(last)

    with open('/projects/Ver32/on_w4_price.txt', 'r') as f:
        last = f.read()
        on_w4_price = json.loads(last)

    with open('/projects/Ver32/on_w4_time.txt', 'r') as f:
        last = f.read()
        on_w4_time = json.loads(last)

except:    
    green_mile = {symb: [None, None] for symb in symbols}
    green_mile_time = {symb: [None, None] for symb in symbols}
    green_mile_price = {symb: [0, 0] for symb in symbols}
    on_w4 = {symb: [None, None] for symb in symbols}
    on_w4_price = {symb: [None, None] for symb in symbols}
    on_w4_time = {symb: [None, None] for symb in symbols}
    
###########Динамическая страховка#################
try:
    with open('/projects/Ver32/max_price.txt', 'r') as f:
        last = f.read()
        max_price = json.loads(last)

    with open('/projects/Ver32/stop.txt', 'r') as f:
        last = f.read()
        stop = json.loads(last)

except:
    max_price = {symbol: [0, 0] for symbol in symbols}
    stop = {symbol: [1, 1] for symbol in symbols}
#############################################

try:
    with open('/projects/Ver32/rsl_time.txt', 'r') as f:
        last = f.read()
        rsl_time = json.loads(last)
except:    
    rsl_time = {symb: [None, None] for symb in symbols}       


PARAMS = {"n": 3, "limit": 1.5, "long_base": 20, "alg": "3_SL",
          "atr_limit": 0.46, "length": 14, "block_min": 5, 
          "down_rsl": 1.0, "step_rsl": 0.5, "sl_time": 2,
          "down_osl": 1.6, "step_osl": 0.5, "down_ysl": 3}

# ТОЛЬКО v9
PARAMS9 = {"n": 3, "limit": 1.5, "long_base": 20, "alg": "3_SL",
          "atr_limit": 0.46, "length": 14, "block_min": 5, 
          "down_rsl": 1.0, "step_rsl": 0.5, "sl_time": 2,
          "down_osl": 1.6, "step_osl": 0.5, "down_ysl": 3}   ### ТОЛЬКО v9

f1, f2 = {symb: [] for symb in symbols}, {symb: [] for symb in symbols}




def calc_prev_min_chandles(channel_data_price: dict[list[float]], symb: str, 
                           i: int):
    """Собирает нужное число (49) предыдущих минутных свечей"""
    global PARAMS
    
    
    idxs = range(-(PARAMS["long_base"] + PARAMS["length"] + 15) * 60 -1, -1, 60)
    prices = channel_data_price[symb]
    
    try:
        high_ser_loc = pd.Series((max(prices[j: j + 60]) for j in idxs))
        low_ser_loc = pd.Series((min(prices[j: j + 60]) for j in idxs))
    except Exception as er:
        bot.send_message(error_tg, f"ver 32 fail calc_prev_min_chandles, min([]), i={i}, symb={symb}, er={er}")  ### отладка - поиск min([])   -nk-
        high_ser_loc = pd.Series(((prices[j]) for j in idxs))
        low_ser_loc = pd.Series(((prices[j]) for j in idxs))
    close_ser_loc = pd.Series((prices[j] for j in (*idxs, -1)))
    return high_ser_loc, low_ser_loc, close_ser_loc

# Считаем значения лимитов (1 раз, при получении алерта)

def calc_limits(high_ser: dict[list[pd.core.series.Series]],
                low_ser: dict[list[pd.core.series.Series]],
                close_ser: dict[list[pd.core.series.Series]], 
                symb: str, i: int):
    """Считает лимиты фильтров по 49 минутным свечам"""
    
    global PARAMS
    
    start = len(low_ser[symb]) - PARAMS["long_base"]
    # long_base - за сколько минут считаем средние для лимитов
    
    avg_candle = abs(close_ser[symb][start - 10:] -                 ### добавил -10
                     close_ser[symb][start - 10:].shift()).mean()   ### добавил -10

    # Средняя разница цен открытия и закрытия (высота тела свечи)
    lim_amp_loc = avg_candle * PARAMS["limit"]
    
    alert_candle = abs(close_ser[symb].iloc[-1] - close_ser[symb].iloc[-2])
    if alert_candle > avg_candle * 5:  # Поправка при высокой свече алерта
        lim_amp_loc = lim_amp_loc * 1.3
    
    # ATR на предыдыщих свечах (по длине long_base)
    atr_prev = ta.atr(high_ser[symb], low_ser[symb], 
                      close_ser[symb][-len(high_ser[symb]): ],
                      length=PARAMS["length"]).iloc[start - 2: -2]
    # Амплитуда предыдущих ATR * коэфициент
    if len(atr_prev) == 0:
        bot.send_message(error_tg, f"ver 32 len(atr_prev) == 0 in calc_limits, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
    
    lim_atr_loc = (atr_prev.max() - atr_prev.min()) * PARAMS["atr_limit"]
    return lim_amp_loc, lim_atr_loc

# def calc_filter_on_alert(high_ser,
#                          low_ser,
#                          close_ser,
#                          symb: str, i: int, lim_amp, lim_atr):
#     """
#     Считает первые точки фильтра при получении алерта.
    
#     Формирует списки значений фильтров за последние 5 минут до алерта
#     по 26 последним минутным свечам и 2-м лимитам.
#     """
#     global PARAMS
    
#     start = PARAMS["block_min"] + PARAMS["length"] + 15   ### добавил +10 к +5
#     atr = ta.atr(high_ser[symb][-start:], low_ser[symb][-start:], 
#                  close_ser[symb][-start:], length=PARAMS["length"])
#     f1_list = (atr.diff() > -lim_atr[symb]).tolist()[-PARAMS["block_min"]: ]
#     amp = (high_ser[symb].rolling(3).max() - 
#            low_ser[symb].rolling(3).min())
#     f2_list = (amp.diff() > -lim_amp[symb]).tolist()[-PARAMS["block_min"]: ]
#     return f1_list, f2_list

# def filter_calc(lim_amp, lim_atr, symb: str, i: int) -> None:
#     """
#     Считает новые 2 точки фильтра за последнюю минуту.
    
#     Обновляет списки значений фильтров за 6 и 10 минут 
#     по 16 последним минутным свечам и 2-м лимитам.
#     """
#     global high_ser, low_ser, close_ser, f1, f2, PARAMS
    
#     #if len(high_ser[symb]) != 17:
#     #     return
#     try:
#         d_atr = ta.atr(high_ser[symb], low_ser[symb], 
#                     close_ser[symb][-len(high_ser[symb]): ],
#                     length=PARAMS["length"]).diff().values[-1]
        
        
#         f1[symb]= f1[symb] + [d_atr > -lim_atr[symb]]
#         f1[symb] = f1[symb][-PARAMS["block_min"] - 2: ]  ### добавил 2 минуты (донастройка по результату анализа)
        
#         d_amp = (max(high_ser[symb][-PARAMS["n"]: ]) - 
#                 min(low_ser[symb][-PARAMS["n"]: ]) -
#                 max(high_ser[symb][-PARAMS["n"] - 1: -1]) + 
#                 min(low_ser[symb][-PARAMS["n"] - 1: -1]))
#         f2[symb] = f2[symb] + [d_amp > -lim_amp[symb]]
#         f2[symb] = f2[symb][-PARAMS["block_min"]: ]
#     except:
#         lim_atr[symb] = 0
#         f2[symb] = []
    
 
def cummul_chandle_calc(time_tick: int, price: float, symb: str, i: int, 
                        s_len = PARAMS["length"] + 12) -> None:  ### также удлинил серию (+12)
    """Накопительно считает минутные свечи"""
    
    global high_ser, low_ser, close_ser, current_minute_start, current_minute_prices
    
    current_minute_prices[symb] = current_minute_prices[symb] + [price]
    if time_tick >= current_minute_start[symb] + 60 * 1000:        
        
        high_ser[symb] = high_ser[symb][-s_len:].reset_index(drop=True)
        high_ser[symb].loc[s_len] = max(current_minute_prices[symb])
        
        low_ser[symb] = low_ser[symb][-s_len:].reset_index(drop=True)
        low_ser[symb].loc[s_len] = min(current_minute_prices[symb])
        
        close_ser[symb] = close_ser[symb][-s_len:].reset_index(drop=True)
        close_ser[symb].loc[s_len] = price
        
        current_minute_prices[symb] = []
        #current_minute_start[symb] = current_minute_start[symb] + 60 * 1000   # есть в ver_trade, где i=1

def filter_allows(f1: list[bool], f2: list[bool], symb: str, i: int) -> bool:
    """Определяет, разрешен ли фильтром вход в лонг"""
    return all(f1) and all(f2)




##############-nk #############
last_trade_ignore_bar_number = 6  # бар входа в сделку + 5 баров, которые мы не отслеживаем
last_trade_check_bar_number = 11  # бар входа в сделку + 10 баров, которые мы отслеживаем
last_trade_price_border_percent = 4  # процент, на который цена входа в сделку должна быть > цены алерта
last_trade_valid_pnl = 2  # минимальный процент pnl, который должен быть взять на предыдущей закрытой сделке
check_wtp = {symbol: [0,0] for symbol in symbols}

symbols_old = []
for key in alerts_MT:            
    symbols_old.append(key)

symbol_new=list(set(symbols)-set(symbols_old))
if len(symbol_new) != 0:
    for symbol in symbol_new:
        channel_price[symbol] = [[],[]]
        channel_time[symbol] = [[],[]] 
        alerts_MT[symbol] = [1,1] 
        channel_cond[symbol] = [[],[]]
        high_ser[symbol] = pd.Series([None])
        low_ser[symbol] = pd.Series([None])
        close_ser[symbol] = pd.Series([None])
        lim_amp[symbol] = 0
        lim_amp[symbol] = 0
        #f1[symbol] = []
        #f1[symbol] = []
        current_minute_prices[symbol] = []
        current_minute_start[symbol] = 0
        max_average_bar_price[symbol] = [0,0]
        red_stop[symbol] = [None, None]
        orange_stop[symbol] = [None, None]
        yellow_stop[symbol] = [None, None]
        last_atr[symbol] = None
        lim_atr[symbol] = 0
        orange_ten_min_start[symbol] = [0, 0]
        ten_min_start[symbol] = [0, 0]
        sl_time[symbol] = [None, None]
        rsl_time[symbol] = [None, None]
        green_mile[symbol] = [None,None]
        on_w4[symbol] = [None,None]
        green_mile_time[symbol] = [None,None]
        green_mile_price[symbol] = [0,0]
        check_wtp[symbol] = [0,0]
        on_w4_price[symbol] = [None,None]
        on_w4_time[symbol] = [None,None]
        max_price[symbol] = [0,0]
        stop[symbol] = [1,1]

        
def ver_trade(channel_data_price, symb, price_last_alert_algo_1, time_last_alert_algo_1, time_tick, price, alerts,
                channel_data_cline_10m,channel_data_cline_7m,channel_data_width_7m,channel_data_cline_4m,
                channel_data_width_3m, channel_data_cline_3m, channel_data_cline_2m, channel_data_cline_30s, koef, koef_base, last_psar_01,check_pump, last_psar_01_old,
                green_psar, k0, k1, price_acc, price_last_dinamic_sl, time_check_sl, check_volatility, q70, col_trades, number_of_trades, last_10_avg_vol, zatupok, antifrod): 
        
        def kline_MT_9(i,k):    
            if check_wtp[symb][i] == 0:
                if price_acc[symb] == []:
                    bot.send_message(error_tg, f'ver 32 price_acc[{symb}] == [] in kline_MT_9({i}, {k})')  ### отладка - поиск min([])   -nk-
                
                min3 = min(price_acc[symb][-3:])
                if (price - min3) / min3 * 100  >= 3: #and (price - price_last_alert_algo_1[symb][i] * 1.03) / price_last_alert_algo_1[symb][i] * 100  >= 3:
                    check_wtp[symb][i] = 1
                    

        

            ################################## Зеленые горы ################################################        
            
            if green_mile[symb][i] == None and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000:
                if ((alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                    price < price_last_dinamic_sl[symb][i]) or\
                ((alerts_MT[symb][i] == 2) and time_tick >= time_last_alert_algo_1[symb][i] + 42 * 60 * 1000 and time_tick <= time_last_alert_algo_1[symb][i] + 50 * 60 * 1000 and\
                    not(check_pump[symb][i]) and check_pump[symb][i] != '' and price >= price_last_alert_algo_1[symb][i] * 1.002) or\
                    (not(check_pump[symb][i]) and check_pump[symb][i] != ''):
                        green_mile[symb][i] = 1
                        green_mile_time[symb][i] = time_tick
                        green_mile_price[symb][i] = price
                        red_stop[symb][i] = (price_last_alert_algo_1[symb][i] * (1 - PARAMS["down_rsl"] * 0.01))             # =0.7  
                        ten_min_start[symb][i] = time_tick // 60000 * 60000
            ################################## Зеленые горы ################################################
                    
                

            # открытие сделки на резком взлете на первой минуте
            if alerts_MT[symb][i] == 1 and\
                time_tick < time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005: # вход
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['on']
                sl_time[symb][i] = None       ### сброс времени подтверждения SL
                rsl_time[symb][i] = None
                max_price[symb][i] = price

                try:
                    last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                            close_ser[symb][-len(high_ser[symb]):],    ### срез для выравнивания длины серий
                                            length=PARAMS["length"]).tolist()[-1]
#                         print(last_atr[symb])
                    if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb][-len(high_ser[symb]):],  ### срез для выравнивания длины серий
                                                length=PARAMS["length"] // 3).tolist()[-1]
                except: pass  

                orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки 
            
            # открытие первой сделки (не on)
            elif alerts_MT[symb][i] == 1 and len(channel_price[symb][i]) <= 1 and price >= price_last_alert_algo_1[symb][i] * 1.005 and\
            antifrod[symb][i]:
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['op05']
                sl_time[symb][i] = None
                rsl_time[symb][i] = None
                max_price[symb][i] = price
                green_mile_time[symb][i] = time_tick
                green_mile_price[symb][i] = price
                # 1 раз при каждом входе в лонг
                if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                    try:
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                            close_ser[symb], 
                                            length=PARAMS["length"]).tolist()[-1]
                        #print(last_atr[symb])
                    except:
                        if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                            last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                    close_ser[symb], 
                                                    length=PARAMS["length"] // 3).tolist()[-1]
                    #print(last_atr[symb])
    #                 print("last_atr[symb]=", last_atr[symb], "или", 
    #                       last_atr[symb] / price * 100, "%")               ### Для отладки -nk

                    orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                    yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                    orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000 and\
                  ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < k[0]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > k[1]) & (channel_data_cline_4m[symb][i][-1] > k[2]) & (channel_data_width_7m[symb][i][-1] < k[3]) & (channel_data_width_3m[symb][i][-1] > k[4]))) and\
                    price > channel_price[symb][i][-1] * 1.003: # 1 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c1']
                        orange_stop[symb][i] = None
                        max_price[symb][i] = 0
                        on_w4[symb][i] = None       ### сброс сигналов w4
                        on_w4_price[symb][i] = 0
                        on_w4_time[symb][i] = None
                        green_mile_price[symb][i] = 0
                        check_wtp[symb][i] = 0
                
            elif ((alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                    ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < 1.5 * k[9]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > 1.5 * k[10]) & (channel_data_cline_4m[symb][i][-1] > 1.5 * k[11]) & (channel_data_width_7m[symb][i][-1] < 0.5 * k[12]) & ((channel_data_cline_2m[symb][i][-1] - channel_data_cline_2m[symb][i][-1 - 10]) > 0.5 * k[13]) & (channel_data_cline_2m[symb][i][-1] < k[14]))) and\
                    price > channel_price[symb][i][-1] * 1.003: # 2 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c2']
                        orange_stop[symb][i] = None
                        max_price[symb][i] = 0
                        on_w4[symb][i] = None       ### сброс сигналов w4
                        on_w4_price[symb][i] = 0
                        on_w4_time[symb][i] = None 
                        green_mile_price[symb][i] = 0
                        check_wtp[symb][i] = 0
                        
            elif alerts_MT[symb][i] == 2 and time_tick >= time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and\
                time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000 and\
                (max_price[symb][i] - price > stop[symb][i]/100 * price_last_alert_algo_1[symb][i]) and\
                price > channel_price[symb][i][-1]*1.005: # страховка 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 1
                channel_cond[symb][i] = channel_cond[symb][i] + ['ins1']
                max_price[symb][i] = 0
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None 
                green_mile_price[symb][i] = 0
                check_wtp[symb][i] = 0
            
            # ver4 
            elif (((alerts_MT[symb][i] == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 2 * 60 * 1000) or (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000)) and\
                price >= price_last_alert_algo_1[symb][i] * 1.03 and\
                ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1])< 0.0005) and\
                (channel_data_cline_4m[symb][i][-1-10] - channel_data_cline_4m[symb][i][-1]> 0.0009) and\
                (channel_data_cline_4m[symb][i][-1] > 0.006) and\
                (channel_data_width_7m[symb][i][-1] < 0.85) and\
                (channel_data_width_3m[symb][i][-1] > 0.3))) and\
                price > channel_price[symb][i][-1] * 1.01: # 1 возможность перегиба
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['c4']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
              

            # закрытие по закруглениям DE
            elif (alerts_MT[symb][i] == 2) and len(channel_price[symb][i]) != 0 and max_average_bar_price[symb][i] != 0 and\
                time_tick >= channel_time[symb][i][-1] + 5 * 60 * 1000 and\
                ((average_bar_price / max_average_bar_price[symb][i]) - 1) * 100 <= -0.5 and\
                price > max(channel_price[symb][i]) * 1.015:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cCV']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                    
            # DE
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                ((max(price_acc[symb][-3:]) - price) / max(price_acc[symb][-3:]) * 100  >  1) and check_wtp[symb][i] and\
                price > max(channel_price[symb][i]) * 1.015:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cDE']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            # zatupok

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 10 * 60 * 1000 and time_tick >= channel_time[symb][i][-1] + 17 * 60 * 1000) and\
                last_10_avg_vol[symb] <= zatupok[symb][i] * 0.65 and price <= channel_price[symb][i][-1] * 1.007 and\
                len(channel_price[symb][i]) == 1 and\
                ((price_acc[symb][-1] < price_acc[symb][-2] and price_acc[symb][-2] < price_acc[symb][-3] and price_acc[symb][-1] > min(price_acc[symb][-10:]) * 1.003) or (price >= channel_price[symb][i][-1] * 1.004)):
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['ztpk']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            # stoploss 1%

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000) and\
                price <= price_last_alert_algo_1[symb][i] * 0.995:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['sl1%']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            

            # открытие сделки 
            
            elif (((channel_data_cline_3m[symb][i][-1] > 1.6 * k[15]) & (all(elem > 1.6 * k[16] for elem in channel_data_cline_3m[symb][i][-1 - 60:-1])) and len(channel_time[symb][i]) > 0) or (price > price_last_alert_algo_1[symb][i] * 1.005 and len(channel_time[symb][i]) == 0)) and\
                    (alerts_MT[symb][i] == 1 or (alerts_MT[symb][i] == 4 and time_tick >= channel_time[symb][i][-1] + 4 * 60 * 1000)) and\
                    ((len(channel_time[symb][i]) > 0 and time_tick >= channel_time[symb][i][-1] + 90 * 1000) or (len(channel_time[symb][i]) == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 90 * 1000)) and\
                    time_tick < time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005 and (red_stop[symb][i] != None and price >= red_stop[symb][i] * 1.005) and\
                    (number_of_trades[symb][-1] < q70[symb][-1] and col_trades < q70[symb][-1]) and\
                    (price < price_acc[symb][-1] * 1.03) and\
                    (len(channel_cond[symb][i]) == 0 or (len(channel_cond[symb][i]) != 0 and channel_cond[symb][i][-1] == 'ztpk' and price < price_last_alert_algo_1[symb][i] * 1.007) or (len(channel_price[symb][i]) != 0 and price > max(channel_price[symb][i]) * 1.005 and channel_cond[symb][i][-1] != 'ztpk'))and\
                    antifrod[symb][i]: # вход
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 2
                        channel_cond[symb][i] = channel_cond[symb][i] + ['ops']
                        sl_time[symb][i] = None
                        rsl_time[symb][i] = None
                        max_price[symb][i] = price
                        green_mile_time[symb][i] = time_tick
                        green_mile_price[symb][i] = price
                        
                        if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                            try:
                                last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                    close_ser[symb], 
                                                    length=PARAMS["length"]).tolist()[-1]
                                #print(last_atr[symb])
                            except:
                                if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                                    last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                            close_ser[symb], 
                                                            length=PARAMS["length"] // 3).tolist()[-1]
                            #print(last_atr[symb])
            #                 print("last_atr[symb]=", last_atr[symb], "или", 
            #                       last_atr[symb] / price * 100, "%")               ### Для отладки -nk

                            orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                            yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                            orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки

            ########################################################### Вставка 3 SL                    
            # red SL =-1.0% от алерта, затем через 30 мин +0.5% каждые 10 мин.  
            elif alerts_MT[symb][i] == 2 and red_stop[symb][i] != None and rsl_time[symb][i] == None and price < red_stop[symb][i]:
                rsl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (5 мин до выхода)

            # Проверка временем R-стопа (5 мин)
            elif alerts_MT[symb][i] == 2 and rsl_time[symb][i] != None and red_stop[symb][i] != None and price > red_stop[symb][i]:
                rsl_time[symb][i] = None        ### сброс времени при возврате цены выше красного стопа
                
            elif (alerts_MT[symb][i] == 2 and rsl_time[symb][i] != None and red_stop[symb][i] != None and\
                  time_tick > rsl_time[symb][i] + 5 * 60 * 1000):  ### 5 минут
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['R']
                    orange_stop[symb][i] = None 
                    rsl_time[symb][i] = None       ### сброс времени после срабатывания
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    max_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                    
                    
                                        
            # orange SL =-1.5*ATR от входа в лонг, затем через 20 мин +0.5% каждые 10 мин.  
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and orange_stop[symb][i] != None and price < orange_stop[symb][i] and not on_w4[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (1,5 мин до выхода)

            # yellow SL =-2.4*ATR от входа в лонг, затем =-2.4*ATR от максимума цены
            # (растёт с ростом цены каждую минуту)
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and yellow_stop[symb][i] != None and price < yellow_stop[symb][i] and not on_w4[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (3 мин до выхода)
            
            # Проверка временем стопов (4 мин. для O, 2 мин. для Y, 40 сек. для O+Y)
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and\
                  orange_stop[symb][i] != None and price > orange_stop[symb][i] and price > yellow_stop[symb][i]) and not on_w4[symb][i]:
                    sl_time[symb][i] = None        ### сброс времени при возврате цены выше стопов
                    
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and\
                  orange_stop[symb][i] != None and\
                  time_tick > sl_time[symb][i] + PARAMS["sl_time"] * 60 * 1000) and not on_w4[symb][i]:  ### 2 минуты
# =============================================================================
#                     channel_price[symb][i] = channel_price[symb][i] + [price]
#                     channel_time[symb][i] = channel_time[symb][i] + [time_tick]
#                     alerts_MT[symb][i] = 1
#                     # пометка на скрине заистит от сработавших стопов на момент выхода
#                     if price <= yellow_stop[symb][i] and price <= orange_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['YO']
#                     elif price <= yellow_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['Y']
#                     elif price <= orange_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['O']
#                     else:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['?']  ### не должны сюда попасть, но мало ли
# =============================================================================
                    sl_time[symb][i] = None       ### сброс времени после срабатывания
                    orange_stop[symb][i] = None
                    on_w4[symb][i] = 1
                    on_w4_price[symb][i] = price
                    on_w4_time[symb][i] = time_tick
            
            ################### Выходы 4w по стопам Y,O 22_3################################
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and all(pr < on_w4_price[symb][i] * 0.99 for pr in channel_data_price[symb][-20:]):
                
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw3']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and price > on_w4_price[symb][i] *1.02:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw1']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and time_tick > on_w4_time[symb][i] + 8*60*1000 and price > np.median(price_acc[symb][-30:-5])*1.0017:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw2']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                
                
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and time_tick > on_w4_time[symb][i] + 3*60*1000 and price > np.mean(price_acc[symb][-10:-3])*1.005:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw4']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            ################### Выходы 4w по стопам Y,O 22_3################################
            
            ################################## Зеленые горы 22_1############################################
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and all(pr < green_mile_price[symb][i] * 0.99 for pr in channel_data_price[symb][-20:]):
                
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow3']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and price > green_mile_price[symb][i] *1.02:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow1']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and time_tick > green_mile_time[symb][i] + 20*60*1000 and price > np.median(price_acc[symb][-30:-5])*1.0017 and time_tick>channel_time[symb][i][-1] + 20*60*1000:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow2']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and time_tick > green_mile_time[symb][i] + 15*60*1000 and price > np.mean(price_acc[symb][-10:-3])*1.005 and time_tick>channel_time[symb][i][-1] + 12*60*1000:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow4']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                
                    
            ################################## Зеленые горы 22_1############################################
                                        
            # Если оба стопа активны, за 1 сек. смещаем время проверки на 6 секунд (-5)
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and\
                  orange_stop[symb][i] != None and\
                  price < orange_stop[symb][i] and price < yellow_stop[symb][i]:
                    sl_time[symb][i] = sl_time[symb][i] - 5 * 1000
                    
            # Если только Y-стоп, за 1 сек. смещаем время проверки на 2 секунды (-1)
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and\
                  orange_stop[symb][i] != None and price < yellow_stop[symb][i]:
                    sl_time[symb][i] = sl_time[symb][i] - 1 * 1000    
##################################################### Конец вставки 3 SL
 
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000:
                    alerts_MT[symb][i] = 3
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    channel_cond[symb][i] = channel_cond[symb][i] + ['e']
                    orange_stop[symb][i] = None
                    red_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    green_mile[symb][i] = None
                    check_wtp[symb][i] = 0
        
        def kline_MT_20(i,k, average_bar_price):   
            
            if check_wtp[symb][i] == 0:
                min3 = min(price_acc[symb][-3:])
                if (price - min3) / min3 * 100  >= 3: #and (price - price_last_alert_algo_1[symb][i] * 1.03) / price_last_alert_algo_1[symb][i] * 100  >= 3:
                    check_wtp[symb][i] = 1
                    
            ################################## Зеленые горы ################################################        
            
            if green_mile[symb][i] == None and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000:
                if ((alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                    price < price_last_dinamic_sl[symb][i]) or\
                ((alerts_MT[symb][i] == 2) and time_tick >= time_last_alert_algo_1[symb][i] + 42 * 60 * 1000 and time_tick <= time_last_alert_algo_1[symb][i] + 50 * 60 * 1000 and\
                    not(check_pump[symb][i]) and check_pump[symb][i] != '' and price >= price_last_alert_algo_1[symb][i] * 1.002) or\
                    (not(check_pump[symb][i]) and check_pump[symb][i] != ''):
                        green_mile[symb][i] = 1
                        green_mile_time[symb][i] = time_tick
                        green_mile_price[symb][i] = price
                        red_stop[symb][i] = (price_last_alert_algo_1[symb][i] * (1 - PARAMS["down_rsl"] * 0.01))             # =0.7  
                        ten_min_start[symb][i] = time_tick // 60000 * 60000
            ################################## Зеленые горы ################################################   

            # открытие сделки на резком взлете на первой минуте
            if alerts_MT[symb][i] == 1 and\
                time_tick < time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005: # вход
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['on']
                sl_time[symb][i] = None
                rsl_time[symb][i] = None
                max_price[symb][i] = price

                try:
                    last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                            close_ser[symb][-len(high_ser[symb]):],    ### срез для выравнивания длины серий
                                            length=PARAMS["length"]).tolist()[-1]
#                         print(last_atr[symb])
                    if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb][-len(high_ser[symb]):],  ### срез для выравнивания длины серий
                                                length=PARAMS["length"] // 3).tolist()[-1]
                except: pass  

                orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки 

            # открытие первой сделки (не on)
            elif alerts_MT[symb][i] == 1 and len(channel_price[symb][i]) <= 1 and price >= price_last_alert_algo_1[symb][i] * 1.005 and\
            antifrod[symb][i]:
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['op05']
                sl_time[symb][i] = None
                rsl_time[symb][i] = None
                max_price[symb][i] = price
                green_mile_time[symb][i] = time_tick
                green_mile_price[symb][i] = price
                # 1 раз при каждом входе в лонг
                if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                    try:
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                            close_ser[symb], 
                                            length=PARAMS["length"]).tolist()[-1]
                        #print(last_atr[symb])
                    except:
                        if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                            last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                    close_ser[symb], 
                                                    length=PARAMS["length"] // 3).tolist()[-1]
                    #print(last_atr[symb])
    #                 print("last_atr[symb]=", last_atr[symb], "или", 
    #                       last_atr[symb] / price * 100, "%")               ### Для отладки -nk

                    orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                    yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                    orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки

            # открытие сделки 
            
            elif (((channel_data_cline_3m[symb][i][-1] > 1.6 * k[15]) & (all(elem > 1.6 * k[16] for elem in channel_data_cline_3m[symb][i][-1 - 60:-1])) and len(channel_time[symb][i]) > 0) or (price > price_last_alert_algo_1[symb][i] * 1.005 and len(channel_time[symb][i]) == 0)) and\
                    (alerts_MT[symb][i] == 1 or (alerts_MT[symb][i] == 4 and time_tick >= channel_time[symb][i][-1] + 4 * 60 * 1000) or (alerts_MT[symb][i] == 5 and time_tick >= channel_time[symb][i][-1] + 1.5 * 60 * 1000)) and\
                    ((len(channel_time[symb][i]) > 0 and time_tick >= channel_time[symb][i][-1] + 90 * 1000) or (len(channel_time[symb][i]) == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 90 * 1000)) and\
                    time_tick < time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005 and\
                    (red_stop[symb][i] != None and price >= red_stop[symb][i] * 1.005) and\
                    (number_of_trades[symb][-1] < q70[symb][-1] and col_trades < q70[symb][-1]) and\
                    (price < price_acc[symb][-1] * 1.03) and\
                    (len(channel_cond[symb][i]) == 0 or (len(channel_cond[symb][i]) != 0 and channel_cond[symb][i][-1] == 'ztpk' and price < price_last_alert_algo_1[symb][i] * 1.007 ) or (len(channel_price[symb][i]) != 0 and price > max(channel_price[symb][i]) * 1.005 and channel_cond[symb][i][-1] != 'ztpk')) and\
                    antifrod[symb][i]: # вход
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 2
                    channel_cond[symb][i] = channel_cond[symb][i] + ['ops']
                    sl_time[symb][i] = None
                    rsl_time[symb][i] = None
                    max_price[symb][i] = price
                    green_mile_time[symb][i] = time_tick
                    green_mile_price[symb][i] = price
                    # 1 раз при каждом входе в лонг
                    if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                        try:
                            last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb], 
                                                length=PARAMS["length"]).tolist()[-1]
                            #print(last_atr[symb])
                        except:
                            if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                                last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                        close_ser[symb], 
                                                        length=PARAMS["length"] // 3).tolist()[-1]
                        #print(last_atr[symb])
        #                 print("last_atr[symb]=", last_atr[symb], "или", 
        #                       last_atr[symb] / price * 100, "%")               ### Для отладки -nk

                        orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                        yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                        orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки
            

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000 and\
                    ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < k[0]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > k[1]) & (channel_data_cline_4m[symb][i][-1] > k[2]) & (channel_data_width_7m[symb][i][-1] < k[3]) & (channel_data_width_3m[symb][i][-1] > k[4]))) and\
                    price > channel_price[symb][i][-1] * 1.002: # 1 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c1']
                        orange_stop[symb][i] = None
                        max_price[symb][i] = 0
                        on_w4[symb][i] = None       ### сброс сигналов w4
                        on_w4_price[symb][i] = 0
                        on_w4_time[symb][i] = None
                        green_mile_price[symb][i] = 0
                        check_wtp[symb][i] = 0
                
            elif ((alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                    ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < 1.5 * k[9]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > 1.5 * k[10]) & (channel_data_cline_4m[symb][i][-1] > 1.5 * k[11]) & (channel_data_width_7m[symb][i][-1] < 0.5 * k[12]) & ((channel_data_cline_2m[symb][i][-1] - channel_data_cline_2m[symb][i][-1 - 10]) > 0.5 * k[13]) & (channel_data_cline_2m[symb][i][-1] < k[14]))) and\
                    price > channel_price[symb][i][-1] * 1.002: # 2 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c2']
                        orange_stop[symb][i] = None
                        max_price[symb][i] = 0
                        on_w4[symb][i] = None       ### сброс сигналов w4
                        on_w4_price[symb][i] = 0
                        on_w4_time[symb][i] = None
                        green_mile_price[symb][i] = 0
                        check_wtp[symb][i] = 0
            
            # ver4 
            elif (((alerts_MT[symb][i] == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 2 * 60 * 1000) or (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000)) and\
                price >= price_last_alert_algo_1[symb][i] * 1.03 and\
                ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1])< 0.0005) and\
                (channel_data_cline_4m[symb][i][-1-10] - channel_data_cline_4m[symb][i][-1]> 0.0009) and\
                (channel_data_cline_4m[symb][i][-1] > 0.006) and\
                (channel_data_width_7m[symb][i][-1] < 0.85) and\
                (channel_data_width_3m[symb][i][-1] > 0.3))) and\
                price > channel_price[symb][i][-1] * 1.002: # 1 возможность перегиба
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['c4']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            # DE
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                ((max(price_acc[symb][-3:]) - price) / max(price_acc[symb][-3:]) * 100  >  1) and check_wtp[symb][i]:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cDE']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            # zatupok

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 10 * 60 * 1000 and time_tick >= channel_time[symb][i][-1] + 17 * 60 * 1000) and\
                last_10_avg_vol[symb] <= zatupok[symb][i] * 0.65 and price <= channel_price[symb][i][-1] * 1.007 and\
                len(channel_price[symb][i]) == 1 and\
                ((price_acc[symb][-1] < price_acc[symb][-2] and price_acc[symb][-2] < price_acc[symb][-3] and price_acc[symb][-1] > min(price_acc[symb][-10:]) * 1.003) or (price >= channel_price[symb][i][-1] * 1.004)):
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['ztpk']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                    
            # stoploss 1%

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000) and\
                price <= price_last_alert_algo_1[symb][i] * 0.995:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['sl1%']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            #green_psar_1
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                (time_tick < time_last_alert_algo_1[symb][i] + 50 * 60 * 1000) and green_psar[symb][1] <= 5 and\
                price >= price_last_alert_algo_1[symb][i] * 1.015 and last_psar_01[symb][0] > price:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cps1']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            #green_psar_2
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                (time_tick >= time_last_alert_algo_1[symb][i] + 50 * 60 * 1000) and green_psar[symb][0] >= 49 and\
                price >= price_last_alert_algo_1[symb][i] * 1.025 and last_psar_01[symb][0] > price and\
                green_psar[symb][1] <= 5:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 3
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cps2']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                    
            elif alerts_MT[symb][i] == 2 and time_tick >= time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and\
                time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000 and\
                (max_price[symb][i] - price > stop[symb][i]/100 * price_last_alert_algo_1[symb][i]) and\
                price > channel_price[symb][i][-1]*1.005: # страховка 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 1
                channel_cond[symb][i] = channel_cond[symb][i] + ['ins1']
                max_price[symb][i] = 0
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None 
                green_mile_price[symb][i] = 0
                check_wtp[symb][i] = 0

            

            # экстренное закрытие сделки после резкого взлета на первой минуте
            elif alerts_MT[symb][i] == 2 and len(channel_price[symb][i]) == 1 and\
                time_tick < time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and price <= channel_price[symb][i][-1] * 0.995: # вход
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 5
                channel_cond[symb][i] = channel_cond[symb][i] + ['off'] 
                orange_stop[symb][i] = None
                max_price[symb][i] = 0
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                check_wtp[symb][i] = 0

########################################################### Вставка 3 SL                    
            # red SL =-1.0% от алерта, затем через 30 мин +0.5% каждые 10 мин.  
            elif alerts_MT[symb][i] == 2 and red_stop[symb][i] != None and rsl_time[symb][i] == None and price < red_stop[symb][i]:
                rsl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (5 мин до выхода)

            # Проверка временем R-стопа (5 мин)
            elif alerts_MT[symb][i] == 2 and rsl_time[symb][i] != None and red_stop[symb][i] != None and price > red_stop[symb][i]:
                rsl_time[symb][i] = None        ### сброс времени при возврате цены выше красного стопа
                
            elif alerts_MT[symb][i] == 2 and rsl_time[symb][i] != None and red_stop[symb][i] != None and\
                  time_tick > rsl_time[symb][i] + 5 * 60 * 1000:  ### 5 минут
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['R']
                    orange_stop[symb][i] = None 
                    rsl_time[symb][i] = None       ### сброс времени после срабатывания
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                                        
            # orange SL =-1.5*ATR от входа в лонг, затем через 20 мин +0.5% каждые 10 мин.  
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and orange_stop[symb][i] != None and price < orange_stop[symb][i] and not on_w4[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (1,5 мин до выхода)

            # yellow SL =-2.4*ATR от входа в лонг, затем =-2.4*ATR от максимума цены
            # (растёт с ростом цены каждую минуту)
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and yellow_stop[symb][i] != None and price < yellow_stop[symb][i] and not on_w4[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (3 мин до выхода)
            
            # Проверка временем стопов (4 мин. для O, 2 мин. для Y, 40 сек. для O+Y)
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and
                  orange_stop[symb][i] != None and price > orange_stop[symb][i] and price > yellow_stop[symb][i]) and not on_w4[symb][i]:
                    sl_time[symb][i] = None        ### сброс времени при возврате цены выше стопов
                    
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and
                  orange_stop[symb][i] != None and 
                  time_tick > sl_time[symb][i] + PARAMS["sl_time"] * 60 * 1000) and not on_w4[symb][i]:  ### 2 минуты
# =============================================================================
#                     channel_price[symb][i] = channel_price[symb][i] + [price]
#                     channel_time[symb][i] = channel_time[symb][i] + [time_tick]
#                     alerts_MT[symb][i] = 1
#                     # пометка на скрине заистит от сработавших стопов на момент выхода
#                     if price <= yellow_stop[symb][i] and price <= orange_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['YO']
#                     elif price <= yellow_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['Y']
#                     elif price <= orange_stop[symb][i]:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['O']
#                     else:
#                         channel_cond[symb][i] = channel_cond[symb][i] + ['?']  ### не должны сюда попасть, но мало ли
# =============================================================================
                    sl_time[symb][i] = None       ### сброс времени после срабатывания
                    orange_stop[symb][i] = None
                    on_w4[symb][i] = 1
                    on_w4_price[symb][i] = price
                    on_w4_time[symb][i] = time_tick
                                        
            # Если оба стопа активны, за 1 сек. смещаем время проверки на 6 секунд (-5)
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and
                  orange_stop[symb][i] != None and 
                  price < orange_stop[symb][i] and price < yellow_stop[symb][i]):
                    sl_time[symb][i] = sl_time[symb][i] - 5 * 1000
                    
            # Если только Y-стоп, за 1 сек. смещаем время проверки на 2 секунды (-1)
            elif (alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and
                  orange_stop[symb][i] != None and price < yellow_stop[symb][i]):
                    sl_time[symb][i] = sl_time[symb][i] - 1 * 1000 
##################################################### Конец вставки 3 SL
            ################### Выходы 4w по стопам Y,O 22_3################################
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and all(pr < on_w4_price[symb][i] * 0.99 for pr in channel_data_price[symb][-20:]):
                
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw3']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and price > on_w4_price[symb][i] *1.02:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw1']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and time_tick > on_w4_time[symb][i] + 8*60*1000 and price > np.median(price_acc[symb][-30:-5])*1.0017:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw2']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                
                
            elif alerts_MT[symb][i] == 2 and on_w4[symb][i] and time_tick > on_w4_time[symb][i] + 3*60*1000 and price > np.mean(price_acc[symb][-10:-3])*1.005:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['sw4']
                max_price[symb][i] = 0
                sl_time[symb][i] = None       ### сброс времени после срабатывания
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            ################### Выходы 4w по стопам Y,O 22_3################################
            
            ################################## Зеленые горы 22_1############################################
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and all(pr < green_mile_price[symb][i] * 0.99 for pr in channel_data_price[symb][-20:]):
                
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow3']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and price > green_mile_price[symb][i] *1.02:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow1']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and time_tick > green_mile_time[symb][i] + 20*60*1000 and price > np.median(price_acc[symb][-30:-5])*1.0017 and time_tick>channel_time[symb][i][-1] + 20*60*1000:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow2']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                    
            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 30 * 60 * 1000 and green_mile[symb][i] and time_tick > green_mile_time[symb][i] + 15*60*1000 and price > np.mean(price_acc[symb][-10:-3])*1.005 and time_tick>channel_time[symb][i][-1] + 12*60*1000:
                alerts_MT[symb][i] = 1
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['ow4']
                max_price[symb][i] = 0
                orange_stop[symb][i] = None
                on_w4[symb][i] = None       ### сброс сигналов w4
                on_w4_price[symb][i] = 0
                on_w4_time[symb][i] = None
                green_mile_price[symb][i] = 0
                    
                
                    
            ################################## Зеленые горы 22_1############################################

        
            # закрытие по last trade
            elif (alerts_MT[symb][i] == 2) and len(channel_price[symb][i]) >=2 and\
                channel_price[symb][i][-1] > channel_price[symb][i][-2] and time_tick >= channel_time[symb][i][-1] + last_trade_ignore_bar_number * 60 * 1000 and time_tick < channel_time[symb][i][-1] + last_trade_check_bar_number * 60 * 1000 and\
                (channel_price[symb][i][-1] - channel_price[symb][i][-2] > last_trade_valid_pnl or price > price_last_alert_algo_1[symb][i] * 1.04) and\
                price < channel_price[symb][i][-1]:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['LT']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0
                    


            # закрытие по закруглениям DE
            elif (alerts_MT[symb][i] == 2) and len(channel_price[symb][i]) != 0 and max_average_bar_price[symb][i] != 0 and\
                time_tick >= channel_time[symb][i][-1] + 5 * 60 * 1000 and\
                ((average_bar_price / max_average_bar_price[symb][i]) - 1) * 100 <= -0.5 and\
                    price > max(channel_price[symb][i]) * 1.015:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cCV']
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    check_wtp[symb][i] = 0

            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000:
                    alerts_MT[symb][i] = 3
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    channel_cond[symb][i] = channel_cond[symb][i] + ['e']
                    red_stop[symb][i] = None
                    orange_stop[symb][i] = None
                    max_price[symb][i] = 0
                    on_w4[symb][i] = None       ### сброс сигналов w4
                    on_w4_price[symb][i] = 0
                    on_w4_time[symb][i] = None
                    green_mile_price[symb][i] = 0
                    green_mile[symb][i] = None
                    check_wtp[symb][i] = 0

        if alerts[symb][0] >= 1 and time_tick < time_last_alert_algo_1[symb][0] + 2.1 * 60 * 60 * 1000:
            try:
                try:
                    ####################################################
                    if alerts_MT[symb][0] == 2:
                        if price > max_price[symb][0]:
                            max_price[symb][0] = price
                            pr_k = (price-price_last_alert_algo_1[symb][0])/price_last_alert_algo_1[symb][0]*100
                            if pr_k < 1:
                                stop[symb][0] = 1
                            elif pr_k > 21:
                                stop[symb][0] = 4
                            else:
                                stop[symb][0] = 0.2*pr_k + 0.8
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-1 {symb}\n\n{e}')
                try:
                    ###########################################################
                    average_bar_price = (price_acc[symb][-1] + price_acc[symb][-2]) / 2
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-2 {symb}\n\n{e}')
                try:
                    if time_tick >= current_minute_start[symb] + 60 * 1000:  ### фильтр входа на хаях
                        # Движение красного стопа:
                        if time_tick >= ten_min_start[symb][0] + 10 * 60 * 1000:
                            if (time_tick >= time_last_alert_algo_1[symb][0] + 29 * 60 * 1000 and red_stop[symb][0] != None and not(green_mile[symb][0])) or\
                                (green_mile_time[symb][0] != None and time_tick >= green_mile_time[symb][0] + 39 * 60 * 1000 and red_stop[symb][0] != None and (green_mile[symb][0])):
                                red_stop[symb][0] = red_stop[symb][0] + price_last_alert_algo_1[symb][0] * PARAMS["step_rsl"] * 0.01           # =0.5
                            ten_min_start[symb][0] = ten_min_start[symb][0] + 10 * 60 * 1000
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-3 {symb}\n\n{e}')
                try:                   
                        # Движение оранжевого стопа:
                        if time_tick >= orange_ten_min_start[symb][0] + 10 * 60 * 1000:  ### Потом можно убрать, когда сделаем:
                            orange_ten_min_start[symb][0] = orange_ten_min_start[symb][0] + 10 * 60 * 1000              ### (ten_min_start = orange_ten_min_start)
                            if (orange_stop[symb][0] != None and len(channel_time[symb][0]) != 0 and time_tick >= channel_time[symb][0][-1] + 14 * 60 * 1000):
                                orange_stop[symb][0] = orange_stop[symb][0] + price * 0.01 * PARAMS["step_osl"]  #* atr[i_n]  ### можно привязать к ATR
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-4 {symb}\n\n{e}')
                try:         
                        # Движение жёлтого стопа:
                        if (orange_stop[symb][0] != None and
                            time_tick >= current_minute_start[symb] + 59 * 1000 and
                            (price > high_ser[symb].iloc[-1] or high_ser[symb].iloc[-1] > high_ser[symb].iloc[-2])):
                                yellow_stop[symb][0] =  0.998 * max(price, high_ser[symb].iloc[-1]) - PARAMS["down_ysl"] * last_atr[symb]
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-5 {symb}\n\n{e}')
                try:         
                        

                        ##### закругления ДЕ #####
                        

                        # условия для начала отслеживания средних значений тела бара
                        if len(channel_price[symb][0]) != 0:
                            general_conditions = [
                                time_tick - channel_time[symb][0][-1] > 5 * 60 * 1000,
                                average_bar_price > channel_price[symb][0][-1],
                            ]

                            if max_average_bar_price[symb][0] == 0 and all(general_conditions):
                                max_average_bar_price[symb][0] = average_bar_price
                            
                            elif max_average_bar_price[symb][0] != 0 and average_bar_price >= max_average_bar_price[symb][0]:
                                max_average_bar_price[symb][0] = average_bar_price

                        else:
                            max_average_bar_price[symb][0] = 0
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-6 {symb}\n\n{e}')
                try:         
                    if check_volatility == 0:
                        kline_MT_9(0,k0)
                    else:
                        kline_MT_20(0,k0, average_bar_price)
                except Exception as e:
                    bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail-7 {symb}\n\n{e}')
            except Exception as e:
                # pass
                bot.send_message(error_tg, f'ver 32 kline_MT(0,k) fail {symb}\n\n{e}')

        if alerts[symb][1] >= 1 and time_tick < time_last_alert_algo_1[symb][1] + 2.1 * 60 * 60 * 1000:
            try:
                ####################################################
                if alerts_MT[symb][1] == 2:
                    if price > max_price[symb][1]:
                        max_price[symb][1] = price
                        pr_k = (price-price_last_alert_algo_1[symb][1])/price_last_alert_algo_1[symb][1]*100
                        if pr_k <= 1:
                            stop[symb][1] = 1
                        elif pr_k > 21:
                            stop[symb][1] = 4
                        else:
                            stop[symb][1] = 0.2*pr_k + 0.8
                   
                        
                ###########################################################
                
                    
                average_bar_price = (price_acc[symb][-1] + price_acc[symb][-2]) / 2
                if time_tick >= current_minute_start[symb] + 60 * 1000:  ### фильтр входа на хаях
                    #filter_calc(lim_amp, lim_atr, symb, 1)                  ### фильтр входа на хаях 
                    # Движение красного стопа:
                    if time_tick >= ten_min_start[symb][1] + 10 * 60 * 1000:
                        if red_stop[symb][1] == None:
                            red_stop[symb][1] = (price_last_alert_algo_1[symb][1] * (1 - PARAMS["down_rsl"] * 0.01))             # =0.7  
                            ten_min_start[symb][1] = time_tick // 60000 * 60000
                        if (time_tick >= time_last_alert_algo_1[symb][1] + 39 * 60 * 1000 and red_stop[symb][1] != None and not(green_mile[symb][1])) or\
                            (green_mile_time[symb][1] != None and time_tick >= green_mile_time[symb][1] + 29 * 60 * 1000 and red_stop[symb][1] != None and (green_mile[symb][1])):
                            red_stop[symb][1] = red_stop[symb][1] + price_last_alert_algo_1[symb][1] * PARAMS["step_rsl"] * 0.01           # =0.5
                        ten_min_start[symb][1] += 10 * 60 * 1000
                        

                    # Движение оранжевого стопа:
                    if time_tick >= orange_ten_min_start[symb][1] + 10 * 60 * 1000:  ### Потом можно убрать, когда сделаем:
                        orange_ten_min_start[symb][1] += 10 * 60 * 1000              ### (ten_min_start = orange_ten_min_start)
                        if (orange_stop[symb][1] != None and len(channel_time[symb][0]) != 0 and time_tick >= channel_time[symb][1][-1] + 14 * 60 * 1000):
                            orange_stop[symb][1] += price * 0.01 * PARAMS["step_osl"]  #* atr[i_n]  ### можно привязать к ATR

                    # Движение жёлтого стопа:
                    if (orange_stop[symb][1] != None and
                        time_tick >= current_minute_start[symb] + 59 * 1000 and
                        (price > high_ser[symb].iloc[-1] or high_ser[symb].iloc[-1] > high_ser[symb].iloc[-2])):
                            yellow_stop[symb][1] =  0.998 * max(price, high_ser[symb].iloc[-1]) - PARAMS["down_ysl"] * last_atr[symb]


                    ##### закругления ДЕ #####
                    

                    # условия для начала отслеживания средних значений тела бара
                    if len(channel_price[symb][1]) != 0:
                        general_conditions = [
                            time_tick - channel_time[symb][1][-1] > 5 * 60 * 1000,
                            average_bar_price > channel_price[symb][1][-1],
                        ]

                        if max_average_bar_price[symb][1] == 0 and all(general_conditions):
                            max_average_bar_price[symb][1] = average_bar_price
                        
                        elif max_average_bar_price[symb][1] != 0 and average_bar_price >= max_average_bar_price[symb][1]:
                            max_average_bar_price[symb][1] = average_bar_price

                    else:
                        max_average_bar_price[symb][1] = 0

                    cummul_chandle_calc(time_tick=time_tick, price=price, symb=symb, i=i,
                                        s_len = PARAMS["length"] + 12)  ### здесь +12 прописал, можно в функции не править

                    ##### закругления ДЕ #####

                    current_minute_start[symb] = current_minute_start[symb] + 60 * 1000
                if check_volatility == 0:
                    kline_MT_9(1,k1)
                else:
                    kline_MT_20(1,k1, average_bar_price)
            except Exception as e:
                # pass
                bot.send_message(error_tg, f'ver 32 kline_MT(1,k) fail {symb}\n\n{e}')


def rewrite(symb, price, time, channel_data_price, price_acc, high_acc, low_acc):
    
    try:

        if symb not in channel_price:
            channel_price[symb] = [[],[]]
        if symb not in channel_time:
            channel_time[symb] = [[],[]] 
        if symb not in alerts_MT:
            alerts_MT[symb] = [1,1] 
        if symb not in channel_cond:   
            channel_cond[symb] = [[],[]]
        if symb not in high_ser:   
            high_ser[symb] = pd.Series([None])
        if symb not in low_ser:  
            low_ser[symb] = pd.Series([None])
        if symb not in close_ser:
            close_ser[symb] = pd.Series([None])
        if symb not in lim_atr:
            lim_atr[symb] = 0
        if symb not in lim_amp:
            lim_amp[symb] = 0
        if symb not in current_minute_prices:
            current_minute_prices[symb] = []
        if symb not in current_minute_start:
            current_minute_start[symb] = 0
        if symb not in max_average_bar_price:
            max_average_bar_price[symb] = [0,0]
        if symb not in red_stop:
            red_stop[symb] = [None, None]
        if symb not in orange_stop:
            orange_stop[symb] = [None, None]
        if symb not in yellow_stop:
            yellow_stop[symb] = [None, None]
        if symb not in last_atr:
            last_atr[symb] = None
        if symb not in orange_ten_min_start:
            orange_ten_min_start[symb] = [0, 0]
        if symb not in ten_min_start:
            ten_min_start[symb] = [0, 0]
        if symb not in sl_time:
            sl_time[symb] = [None, None]
        if symb not in rsl_time:
            rsl_time[symb] = [None, None] 
        if symb not in check_wtp:
            check_wtp[symb] = [0, 0]
        if symb not in green_mile:
            green_mile[symb] = [None, None] 
        if symb not in green_mile_price:
            green_mile_price[symb] = [0, 0]
        if symb not in green_mile_time:
            green_mile_time[symb] = [None, None]
        if symb not in on_w4:
            on_w4[symb] = [None, None] 
        if symb not in on_w4_price:
            on_w4_price[symb] = [None, None]
        if symb not in on_w4_time:
            on_w4_time[symb] = [None, None]
        if symb not in max_price:
            max_price[symb] = [0, 0]
        if symb not in stop:
            stop[symb] = [1,1]
        

        channel_price[symb][0] = channel_price[symb][1]
        channel_time[symb][0] = channel_time[symb][1]

        sl_time[symb][0] = sl_time[symb][1]
        sl_time[symb][1] = None
        rsl_time[symb][0] = rsl_time[symb][1]
        rsl_time[symb][1] = None

        channel_price[symb][1] = []
        channel_time[symb][1] = []
        alerts_MT[symb][0] = alerts_MT[symb][1]
        alerts_MT[symb][1] = 1 

        channel_cond[symb][0] = channel_cond[symb][1]
        channel_cond[symb][1] = []

        check_wtp[symb][0] = check_wtp[symb][1]
        check_wtp[symb][1] = 0

        max_average_bar_price[symb][0] = max_average_bar_price[symb][1]
        max_average_bar_price[symb][1] = 0

        
        #high_ser[symb], low_ser[symb], close_ser[symb] = calc_prev_min_chandles(channel_data_price, symb, 1)
        high_ser[symb], low_ser[symb], close_ser[symb] = pd.Series(high_acc[symb][-49:]), pd.Series(low_acc[symb][-49:]), pd.Series(price_acc[symb][-49:])
        
        #lim_amp[symb], lim_atr[symb] = calc_limits(high_ser, low_ser, close_ser, 
        #                                                symb, 1)
        
        #f1[symb], f2[symb] = calc_filter_on_alert(high_ser, low_ser, close_ser,
        #                                                symb, 1, lim_amp, lim_atr)
        
        current_minute_start[symb] = time // 60000 * 60000
        current_minute_prices[symb] = []

        ########### Green mile ###############
        green_mile[symb][0] = green_mile[symb][1]
        green_mile_time[symb][0] = green_mile_time[symb][1]
        green_mile_price[symb][0] = green_mile_price[symb][1]
        max_price[symb][0] = max_price[symb][1]
        on_w4[symb][0] = on_w4[symb][1]
        on_w4_price[symb][0] = on_w4_price[symb][1]
        on_w4_time[symb][0] = on_w4_time[symb][1]
        stop[symb][0] = stop[symb][1]
        

        green_mile[symb][1] = None
        green_mile_time[symb][1] = None
        green_mile_price[symb][1] = 0
        max_price[symb][1] = 0
        on_w4[symb][1] = None
        on_w4_price[symb][1] = None
        on_w4_time[symb][1] = None
        stop[symb][1] = 1
        
        #############################

        red_stop[symb][0] = red_stop[symb][1]
        ten_min_start[symb][0] = ten_min_start[symb][1]
        orange_stop[symb][0] = orange_stop[symb][1]
        yellow_stop[symb][0] = yellow_stop[symb][1]
        orange_ten_min_start[symb][0] = orange_ten_min_start[symb][1]
        orange_stop[symb][1] = None
        yellow_stop[symb][1] = None
        red_stop[symb][1] = None
        orange_ten_min_start[symb][1] = 0
        if red_stop[symb][1] is None:  ### условие выполняется только 1 раз при получении алерта
            red_stop[symb][1] = (price * (1 - PARAMS["down_rsl"] * 0.01))             # =0.7  
            ten_min_start[symb][1] = time // 60000 * 60000
            time_red = get_formatted_time(ten_min_start[symb][1])
            pcnt_red = round((red_stop[symb][1] - price)/ price * 100, 2)
            
    
    except Exception as e:
        bot.send_message(error_tg, f'rewrite 32\n\n{e}')
    


def save():
    try:
        with open('/projects/Ver32/channel_price.txt', 'w') as file:
            file.write(json.dumps(channel_price))
                
        with open('/projects/Ver32/channel_time.txt', 'w') as file:
            file.write(json.dumps(channel_time))

        with open('/projects/Ver32/alerts_MT.txt', 'w') as file:
            file.write(json.dumps(alerts_MT)) 

        with open('/projects/Ver32/channel_cond.txt', 'w') as file:
            file.write(json.dumps(channel_cond))   

        with open(f'/projects/Ver32/stats/{str(day_check)}_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))

        with open('/projects/Ver32/stats/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))
            
        with open('/projects/Ver32/stats/day_check.txt', 'w') as file:
            file.write(json.dumps(day_check))

        with open('/projects/Ver32/stats_4h/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_4h))

        with open('/projects/Ver32/stats_4h/alerts_stat_1h.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_1h))
            
        with open('/projects/Ver32/stats_4h/hour_check_1h.txt', 'w') as file:
            file.write(json.dumps(hour_check_1h))
        
        with open('/projects/Ver32/sl_time.txt', 'w') as file:
            file.write(json.dumps(sl_time))

        with open('/projects/Ver32/rsl_time.txt', 'w') as file:
            file.write(json.dumps(rsl_time))            

        high_ser_dict = {}
        for i in high_ser:
            high_ser_dict[i] = high_ser[i].to_list()

        with open('/projects/Ver32/high_ser.txt', 'w') as file:
            file.write(json.dumps(high_ser_dict)) 
        del high_ser_dict

        low_ser_dict = {}
        for i in low_ser:
            low_ser_dict[i] = low_ser[i].to_list()
        with open('/projects/Ver32/low_ser.txt', 'w') as file:
            file.write(json.dumps(low_ser_dict)) 
        del low_ser_dict
        
        close_ser_dict = {}
        for i in close_ser:
            close_ser_dict[i] = close_ser[i].to_list()
        with open('/projects/Ver32/close_ser.txt', 'w') as file:
            file.write(json.dumps(close_ser_dict))
        del close_ser_dict 

        with open('/projects/Ver32/lim_amp.txt', 'w') as file:
            file.write(json.dumps(lim_amp))

        with open('/projects/Ver32/lim_atr.txt', 'w') as file:
            file.write(json.dumps(lim_atr))
        '''
        with open('/projects/Ver32/f1.txt', 'w') as file:
            file.write(json.dumps(f1))

        with open('/projects/Ver32/f2.txt', 'w') as file:
            file.write(json.dumps(f2))
        '''
        with open('/projects/Ver32/current_minute_start.txt', 'w') as file:
            file.write(json.dumps(current_minute_start))

        with open('/projects/Ver32/current_minute_prices.txt', 'w') as file:
            file.write(json.dumps(current_minute_prices))

        with open('/projects/Ver32/count_trades.txt', 'w') as file:
            file.write(json.dumps(count_trades))

        with open('/projects/Ver32/time_last_kline.txt', 'w') as file:
            file.write(json.dumps(time_last_kline))

        with open('/projects/Ver32/red_stop.txt', 'w') as file:
            file.write(json.dumps(red_stop))

        with open('/projects/Ver32/orange_stop.txt', 'w') as file:
            file.write(json.dumps(orange_stop))
        
        with open('/projects/Ver32/yellow_stop.txt', 'w') as file:
            file.write(json.dumps(yellow_stop))

        with open('/projects/Ver32/last_atr.txt', 'w') as file:
            file.write(json.dumps(last_atr))

        with open('/projects/Ver32/orange_ten_min_start.txt', 'w') as file:
            file.write(json.dumps(orange_ten_min_start))

        with open('/projects/Ver32/ten_min_start.txt', 'w') as file:
            file.write(json.dumps(ten_min_start))

        with open('/projects/Ver32/max_average_bar_price.txt', 'w') as file:
            file.write(json.dumps(max_average_bar_price))
        
        with open('/projects/Ver32/green_mile.txt', 'w') as file:
            file.write(json.dumps(green_mile))
        with open('/projects/Ver32/green_mile_price.txt', 'w') as file:
            file.write(json.dumps(green_mile_price))
        with open('/projects/Ver32/green_mile_time.txt', 'w') as file:
            file.write(json.dumps(green_mile_time))
        with open('/projects/Ver32/on_w4.txt', 'w') as file:
            file.write(json.dumps(on_w4))
        with open('/projects/Ver32/on_w4_price.txt', 'w') as file:
            file.write(json.dumps(on_w4_price))
        with open('/projects/Ver32/on_w4_time.txt', 'w') as file:
            file.write(json.dumps(on_w4_time))
        with open('/projects/Ver32/max_price.txt', 'w') as file:
            file.write(json.dumps(max_price))
        with open('/projects/Ver32/stop.txt', 'w') as file:
            file.write(json.dumps(stop))
        


    except:
        pass


def screen(symb, i, df, time_last_alert_algo_1, price_last_alert_algo_1, df_vol, df_btc):
        global day_check, hour_check_1h, count_trades
        try:
            print('start send screen' , symb)
            #time.sleep(0.01)
           
            df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
            time_alert = int(time_last_alert_algo_1[i] - (time_last_alert_algo_1[i] % 60000))
            ########
            df_chanels = df.copy()
            df_chanels['Close'] = df_chanels['Close'].astype(float)
            df_chanels['High'] = df_chanels['High'].astype(float)
            df_chanels['Low'] = df_chanels['Low'].astype(float)
            df_chanels['Open'] = df_chanels['Open'].astype(float)
            ########
            df['Time_alert'] = time_alert
            df['Price_alert'] = price_last_alert_algo_1[i]
            
            ###############
            df['Close'] = df['Close'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Open'] = df['Open'].astype(float)
            df['Number of trades'] = df['Number of trades'].astype(int)
            df['Volume'] = df['Volume'].astype(float)


            ### parabolic ###
            df['psar_high'] = None
            df['psar_low'] = None
            psar = ta.psar(high=pd.Series(df['High'], copy=False), low=pd.Series(df['Low'], copy=False), close=pd.Series(df['Close'], copy=False), af0=0.01, af=0.01, max_af=0.05)
            df['psar_high'] = pd.DataFrame(psar)['PSARs_0.01_0.05']
            df['psar_low'] = pd.DataFrame(psar)['PSARl_0.01_0.05']
            df['psar_high'] = round((df['psar_high'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['psar_low'] = round((df['psar_low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            
            df['signal'] = None
            df['line_alert'] = 0
            df['price_open'] = None
            df['price_close'] = None
            df['open_cond'] = None
            df['close_cond'] = None 
            df['pnl_description'] = None
            ######################################### Для отрисовки стоп-лоссов -nk
            df["atr"] = ta.atr(df.High, df.Low, df.Close, length=PARAMS["length"], offset = 1, 
                            drift=1) / price_last_alert_algo_1[i] * 100
        ######################### Конец вставки "Для отрисовки стоп-лоссов" -nk 

            ind = df[df['Time'] >= time_alert].index.values.astype(int)[:1]

            ###### avg vol ######
            df_avg_vol = df[['Volume', 'Taker buy base asset volume']][:ind[0]].copy()
            df_avg_vol['Volume'] = df_avg_vol['Volume'].astype(float)
            df_avg_vol['Taker buy base asset volume'] = df_avg_vol['Taker buy base asset volume'].astype(float)
            def max_vol(x, max_v):
                if x >= max_v:
                    return x/2
                else:
                    return x
            max_volume = max(df_avg_vol['Volume'])
            df_avg_vol['Volume'] = df_avg_vol['Volume'].apply(lambda x: max_vol(x,max_volume))
            max_volume = max(df_avg_vol['Volume'])
            df_avg_vol['Volume'] = df_avg_vol['Volume'].apply(lambda x: max_vol(x,max_volume))
            avg_vol = statistics.mean(df_avg_vol['Volume'])
            avg1 = round(float(df.iloc[ind[0]]['Taker buy base asset volume']) / avg_vol, 2)
            avg2 = round(float(df.iloc[ind[0]+1]['Taker buy base asset volume']) / avg_vol, 2)
            avg3 = round(float(df.iloc[ind[0]+2]['Taker buy base asset volume']) / avg_vol, 2)
            max_avg_10min = 0
            for v in range(ind[0]-10,10, -10):
                if statistics.mean(df_avg_vol['Volume'][v-10:v]) > max_avg_10min:
                    max_avg_10min = statistics.mean(df_avg_vol['Volume'][v-10:v])
            classification = [
                avg1 >= 6,
                avg2 >= 4,
                avg3 >= 3,
                float(df.iloc[ind[0]+1]['Taker buy base asset volume']) >= float(df.iloc[ind[0]]['Taker buy base asset volume']) / 4,
                max_avg_10min < avg_vol * 3
            ]

            if all(classification):
                predict_vol = 1
            else:
                predict_vol = 0

            ###### avg vol ######

            ind_1_line = ind[0] - 15
            ind_2_line = ind[0] + 120 + 1
            
            line_1 = time_alert - 15 * 60 * 1000 + 3 * 60 * 60 * 1000
            line_2 = time_alert + 120 * 60 * 1000 + 3 * 60 * 60 * 1000
            df_line = pd.DataFrame({'Data': [line_1, line_2]})
            df_line['Data_line'] = pd.to_datetime(df_line['Data'], unit = 'ms')
            
            #try:
            
            if len(channel_time[symb][i]) % 2 == 1:
                channel_time[symb][i] = channel_time[symb][i] + [int(time_alert + 120 * 60 * 1000)]
                channel_price[symb][i] = channel_price[symb][i] + [float(df.iloc[ind[0]+120]['Close'])]
                channel_cond[symb][i] = channel_cond[symb][i] + ['e']

            # ver
            MT_pnl = []
            for k in range(len(channel_time[symb][i])):
                if k % 2 == 0:
                    time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                    ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                    df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                    try:
                        df.loc[ind_time_open[0], 'open_cond'] = channel_cond[symb][i][k]
                    except: pass

                if k % 2 == 1:
                    time_close = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                    ind_time_close = df[df['Time'] == time_close].index.values.astype(int)
                    df.loc[ind_time_close[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                    try:
                        df.loc[ind_time_close[0], 'close_cond'] = channel_cond[symb][i][k]
                    except: pass
                    MT_pnl = MT_pnl + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]

            MT_pnl_total = round(sum(MT_pnl),2)
            MT_pnl_clear = round(MT_pnl_total - len(MT_pnl)*0.16, 2)
            count_trades = count_trades + len(MT_pnl)
            df.loc[ind_2_line+2, 'pnl_description'] = MT_pnl_clear/2
            df['avg_vol'] = df['Volume']/df['Number of trades']
            index_vol = round(float(df.iloc[ind[0]]['Volume'] / statistics.mean(df['Volume'][ind[0]-5:ind[0]])), 2)
            

            df.loc[ind[0], 'signal'] = 0 
            df['Time'] = df['Time'] + 3 * 60 * 60 * 1000
            df = df.merge(df_vol, on='Time', how='left')
            df = df.merge(df_btc, on='Time', how='left')
            df = df.where(pd.notnull(df), None)

            df['Close_btc'] = df['Close_btc'].astype(float)
            corr = float(df['Close'].corr(df['Close_btc']))
            corr_before = float(df['Close'][:ind[0]].corr(df['Close_btc'][:ind[0]])) 
            corr_before_15 = float(df['Close'][:ind_1_line].corr(df['Close_btc'][:ind_1_line]))

            df.loc[0, 'volatility'] = 0
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            if len(df['Low']) == 0:
                bot.send_message(error_tg, f'ver 32 len(df["Low"]) == 0 in screen({symb}, {i})')  ### отладка - поиск min([])   -nk-
            if (max(df['High']) - min(df['Low'])) / min(df['Low']) * 100 < 5:
                df.loc[0, 'High'] = statistics.mean([max(df['High']), min(df['Low'])]) * 1.025
                df.loc[0, 'Low'] = statistics.mean([max(df['High']), min(df['Low'])]) * 0.975
                df.loc[0, 'Close'] = statistics.mean([max(df['High']), min(df['Low'])])
                df.loc[0, 'Open'] = statistics.mean([max(df['High']), min(df['Low'])])

            df['Time_for_sl'] = df['Time']
            df = df.set_index('Time')
            df.index = pd.to_datetime(df.index, unit = 'ms')
            cols = df.columns.to_list()
            cols.remove('open_cond')
            cols.remove('close_cond')
            df[cols] = df[cols].astype(float) 
            
            if len(df['Low'][(ind[0]+1):ind_2_line]) == 0:
                bot.send_message(error_tg, f'ver 32 len(df["Low"][(ind[0]+1):ind_2_line]) == 0 in screen({symb}, {i})')  ### отладка - поиск min([])   -nk-    
            percent_high = round(((float(max(df['High'][ind[0]:ind_2_line])) - float(price_last_alert_algo_1[i]))/float(price_last_alert_algo_1[i])*100),2)
            
            percent_low = round(((float(min(df['Low'][(ind[0]+1):ind_2_line])) - float(price_last_alert_algo_1[i]))/float(price_last_alert_algo_1[i])*100),2)
            
            if percent_low >= 0:
                percent_low = 0
            if percent_high == 0:
                percent_high = 1
            df['count'] = df['Close'] 
            df['count'] = df['count'].apply(lambda x: 1 if x >= float(price_last_alert_algo_1[i]) else 0)
            
            count_plus_pnl = int(sum(df['count'][ind[0]:ind_2_line]) / len(df[ind[0]:ind_2_line]) * 100)
            count_minus_pnl = 100 - count_plus_pnl
            
            time_pump = get_formatted_time(int(time_last_alert_algo_1[i] + 3 * 60 * 60 * 1000))
            
            if percent_high >= 30:
                description = сap_name_1h[0]
            elif percent_high >= 20:
                description = сap_name_1h[1]
            elif percent_high >= 16:
                description = сap_name_1h[2]
            elif percent_high >= 12:
                description = сap_name_1h[3]
            elif percent_high >= 6:
                description = сap_name_1h[4]
            elif percent_high >= 3:
                description = сap_name_1h[5]
            elif percent_high >= 1.5:
                description = сap_name_1h[6]
            elif percent_high < 1.5 and percent_low > -1.5:
                description = сap_name_1h[7]
            elif percent_low <= -30:
                description = сap_name_1h[-1]
            elif percent_low <= -20:
                description = сap_name_1h[-2]
            elif percent_low <= -16:
                description = сap_name_1h[-3]
            elif percent_low <= -12:
                description = сap_name_1h[-4]
            elif percent_low <= -6:
                description = сap_name_1h[-5]
            elif percent_low <= -3:
                description = сap_name_1h[-6]
            elif percent_low <= -1.5:
                description = сap_name_1h[-7]
 
            if percent_high >= 100 or percent_low <= -100:
                power_emoji = f'{legendary_100}'
            elif percent_high >= 60 or percent_low <= -60:
                power_emoji = f'{legendary_60}'
            elif percent_high >= 40 or percent_low <= -40:
                power_emoji = f'{legendary_40}'
            elif percent_high >= 30 or percent_low <= -30:
                power_emoji = f'{legendary_30}'
            elif percent_high >= 20 or percent_low <= -20:
                power_emoji = f'{legendary_20}'
            elif percent_high >= 16 or percent_low <= -16:
                power_emoji = f'{legendary_16}'
            elif percent_high >= 12 or percent_low <= -12:
                power_emoji = f'{p_emoji}{p_emoji}{p_emoji}'
            elif percent_high >= 6 or percent_low <= -6:
                power_emoji = f'{p_emoji}{p_emoji}'
            elif percent_high >= 3 or percent_low <= -3:
                power_emoji = f'{p_emoji}'
            else:
                power_emoji = ''

            df['Close'] = round((df['Close'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['Open'] = round((df['Open'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['High'] = round((df['High'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['Low'] = round((df['Low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            btc_zero_price = df.iloc[ind[0]]['Close_btc']
            delta = df.iloc[0]['Close']
            df['Close_btc'] = round((df['Close_btc'] - float(btc_zero_price)) / float(btc_zero_price) * 100, 2) + delta
            if len(df['Close'][:ind[0]]) == 0:
                bot.send_message(error_tg, f"ver 32 len(df['Close'][:ind[0]]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
            min_pcnt_befor = min(df['Close'][:ind[0]])
            
            ################################ Ценовые каналы ##############################
            ##############################################################################
            df_chanels['Close'] = round((df_chanels['Close'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['Open'] = round((df_chanels['Open'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['High'] = round((df_chanels['High'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['Low'] = round((df_chanels['Low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            
            def create_dist(df):
                distr = np.linspace(df.Low, df.High, 10)
                return distr
        
            def calculate_chanel(data, candles_num):

                data = data[-candles_num-3:-3]
                chanel_time_end = data[-1:].Time.values[0]
                chanel_time_start = data[:1].Time.values[0]
                data = data.reset_index(drop=True)
                
                data['candle_dist']= data.apply(create_dist, axis = 1)
                data['dateIndex'] = data.index + 1
                
                data_exp = data.explode('candle_dist')
                X = np.asarray(data_exp.dateIndex)
                y = np.asarray(data_exp.candle_dist)
                
                conc = np.concatenate((X.reshape(-1,1),y.reshape(-1,1)), axis = 1)
                pca = PCA(1)
                pca_tr = pca.fit_transform(conc)
                pca_inv = pca.inverse_transform(pca_tr)
                y_0 = pca_inv[0,1]
                y_1 = pca_inv[-1,1]
                
                y_new = y - pca_inv[:,1]
                chanel_width = y_new.std()*2*2
                return (chanel_width, (chanel_time_start, chanel_time_end), (y_0, y_1))
            
            def chanel_widths(ser: pd.Series, df: pd.DataFrame):
                data = df.loc[ser.index]
                data = data.reset_index(drop=True)
                
                data['candle_dist']= data.apply(create_dist, axis = 1)
                data['dateIndex'] = data.index + 1
            
                data_exp = data.explode('candle_dist')
                X = np.asarray(data_exp.dateIndex)
                Y = np.asarray(data_exp.candle_dist)
                X = X.reshape(-1,1)
                Y = Y.reshape(-1,1)
                reg = LinearRegression().fit(X, Y)
                y_fit = reg.predict(X)
            
                chanel_width = 2*2*mae(Y, y_fit) #*1.2
                return chanel_width
            

            time_alert_msk = time_alert + 3 * 60 * 60 * 1000
            time_alert_msk = time_alert_msk - time_alert_msk%60000
            df_chanels['Time'] = df_chanels['Time'] + 3 * 60 * 60 * 1000 ####
            df_chanels.reset_index(inplace=True)

            ################### Подсчет метрик ширин каналов ##############################################
            chanel_width_params = {'w30_med': 0.65, 'w5_med':0.33}
            median_30 = df_chanels[df_chanels['Time'] <= time_alert_msk -2*60*1000].High.rolling(window = 30).apply(chanel_widths, args=(df_chanels,)).median()
            median_5 = df_chanels[(df_chanels['Time'] >= time_alert_msk - 60*60*1000)&(df_chanels['Time'] <= time_alert_msk -2*60*1000)].High.rolling(window = 5).apply(chanel_widths, args=(df_chanels,)).median()
            
            narrow_30_chanel = int(median_30 <=chanel_width_params['w30_med'])
            narrow_5_chanel = int(median_5 <=chanel_width_params['w5_med'])
            ##################################################################################################

            window = df_chanels['Time'] < time_alert_msk
            
            data_alert = df_chanels[window]
            data_after = df_chanels[~window]
            data_after = data_after.reset_index(drop = True)
            start_anomaly = data_alert[-2:-1].Low.values[0]
            start_anomaly_time = data_alert[-2:-1].Time.values[0]
            time_before_alert = [5, 10, 20]
            
            chanels_info = [calculate_chanel(data_alert, candles) for candles in time_before_alert]
            points = []
            widths = np.asarray([i[0] for i in chanels_info])
            widths_rounded = np.around(widths,2) # Ширины каналов
            
            s0 = np.around(-start_anomaly/widths,2) # -> array - индикаторы в момент алерта  
            mins_indi = [] # индикаторы в моменты 1, 5, 10, 30, 60 минутных свечей после алерта
            times = [1, 5, 10, 30, 60]
        
            for time in times:
                indic = np.around((data_after.loc[time,'High'] - start_anomaly)/widths,2)
                mins_indi.append(indic)
            
            max_indi = np.around((percent_high - start_anomaly)/widths, 2) # индикаторы максимума
            min_indi = np.around((percent_low - start_anomaly)/widths, 2) # индикаторы минимума
            
            colors_ = np.concatenate([([i]*2) for i in ['r','b','g','y']], axis=0).tolist()

            # Точки для отрисовки каналов
            
            for info in chanels_info:
                xx = [get_formatted_time(int(x)) for x in info[1]]
                yy = info[2]
                points_1 = [(i, j - info[0]/2) for (i, j) in zip(xx,yy)]
                points_2 = [(i, j + info[0]/2) for (i, j) in zip(xx,yy)]
                points.append(points_1)
                points.append(points_2)

            text = f'\nalert:{s0}; 1 min:{mins_indi[0]}; 5 min:{mins_indi[1]}\n10 min:{mins_indi[2]}; 30 min:{mins_indi[3]}; 60 min:{mins_indi[4]}\nmax:{max_indi}; min:{min_indi}'
            #######################
            #######################
            if len(channel_price[symb][i]) == 0:
                df['pnl_line'] = 0
            else:
                df['pnl_line'] = MT_pnl_clear

            
            apds = [mpf.make_addplot(df['signal'],type='scatter', color='#2d5ff5',markersize=50, secondary_y=False),
                    mpf.make_addplot(df['psar_high'],type='scatter', color='r',markersize=0.5, secondary_y=False),
                    mpf.make_addplot(df['psar_low'],type='scatter', color='g',markersize=0.5, secondary_y=False),
                    mpf.make_addplot(df['pnl_line'],type='scatter', color='purple', alpha = 0.6, markersize=0.1, secondary_y=False),
                    mpf.make_addplot(df['line_alert'],type='scatter', color='g',markersize=0.1, secondary_y=False),
                    mpf.make_addplot(df['price_close'], type='scatter', color='r',markersize=20, marker='v', secondary_y=False),
                    mpf.make_addplot(df['price_open'], type='scatter', color='g',markersize=20, marker='^', secondary_y=False),
                    mpf.make_addplot(df['volatility'], color='lime', alpha=0.2),
                    mpf.make_addplot(df['Close_btc'], color='y', alpha = 0.3, secondary_y=False)]
            
            cap = f'ver32 {description} {symb}\n{power_emoji}\nclear_pnl: {MT_pnl_clear}%\ntake_clear_potential: {round(MT_pnl_clear/percent_high*100,2)}%'
            
            title_mess = f'\n\n\nver32 {symb}, price: {price_last_alert_algo_1[i]}, time: {time_pump}\nmax={percent_high}%, min={percent_low}%, coef={count_plus_pnl}/{count_minus_pnl}, Ind_Vol= {index_vol}\ntotal_pnl: {MT_pnl_total}%, clear_pnl: {MT_pnl_clear}%, count_trades: {len(MT_pnl)}, comm+sq: {round(len(MT_pnl)*0.16, 2)}%, take_potential: {round(MT_pnl_total/percent_high*100,2)}%,take_clear_potential: {round(MT_pnl_clear/percent_high*100,2)}%,\npnl_trades: {MT_pnl}\n corr: {round(corr,2)}, corr_before: {round(corr_before,2)}, corr_before_15: {round(corr_before_15,2)}, min_pcnt_before: {round(min_pcnt_befor, 2)}, predict_volume: {predict_vol}, chanel_30: {narrow_30_chanel}, chanel_5: {narrow_5_chanel}' #, PnL% = {percent_order}
            ### сохраняем последний трейд для отправки в wtp all
            trade_str = f'ver32: {MT_pnl_clear}% / {round(MT_pnl_clear/percent_high*100,2)}%'

############################# Конец вставки "Oтрисовка стоп-лоссов" -nk 
            osl_ser = pd.Series(None, index=df.index, dtype=float)
            ysl_ser = pd.Series(None, index=df.index, dtype=float)
            # строю фрагмент линии для каждого трейда
            for _, (t, p, cur_atr) in df[df.price_open > -100][["Time_for_sl", "price_open", "atr"]].iterrows():
                t2 = df[(df.Time_for_sl >= t) & (df.price_close > -100)].Time_for_sl.values[0]  # время закрытия трейда

                # добавляю вылет за пределы трейда на 3 свечи для удобства восприятия
                mask = (df.Time_for_sl >= t - 1 * 60000) & (df.Time_for_sl < t2 + 1 * 60000)
                osl_ser[mask] = p  - 0.2 - PARAMS["down_osl"] * cur_atr
                mask = (df.Time_for_sl >= t + 20 * 60000) & (df.Time_for_sl < t2 + 1 * 60000)  # лесенка с 20-й минуты
                osl_ser[mask] = p  - 0.2 - PARAMS["down_osl"] * cur_atr + PARAMS["step_osl"] * ((df.Time_for_sl - t) // (10 * 60 * 1000) - 1)
                osl_ser[osl_ser > df.High.max()] = None


                tmp_ser = df.High.copy()    # Чтобы не затереть
                tmp_ser[df.Time_for_sl <= t] = p   # Чтобы убрать максимуиы цены до входа в лонг
                mask = (df.Time_for_sl >= t - 1 * 60000) & (df.Time_for_sl <= t2 + 1 * 60000)  # +1 минута за пределами трейда
                ysl_ser[mask] = (tmp_ser - 0.2 - PARAMS["down_ysl"] * cur_atr).rolling(int((t2 - t) / 60000) + 2).max()
                ysl_ser[ysl_ser > df.High.max()] = None
                # = максимум цены от начала трейда минус 3*ATR

            # формирую доп.линии для графика mpf
#             rsl_apd = mpf.make_addplot(rsl_ser, secondary_y=False, color="darkred", linestyle="--", alpha=.5)
            osl_apd = mpf.make_addplot(osl_ser, secondary_y=False, color="darkorange", linestyle="--", alpha=.5)
            ysl_apd = mpf.make_addplot(ysl_ser.shift(), secondary_y=False, color="y", alpha=.5)
#             apds.extend([rsl_apd])
            apds.extend([osl_apd, ysl_apd])

############################# Конец вставки "Oтрисовка стоп-лоссов" -nk 

            al = dict(alines=points, colors=colors_, linewidths=2, alpha=0.6)
            vl = dict(vlines=[df_line.iloc[0,1],df_line.iloc[1,1]],linewidths=(1,1))
            buf6 = io.BytesIO()
            df['where'] = (df['Close'] == df['Close'].iloc[ind_2_line + 2]) & (df['Open'] == df['Open'].iloc[ind_2_line + 2]).values
            if percent_high >= 12 or percent_low <= -12:
                title_mess = '\n\n\n' + title_mess + text
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, fill_between=dict(y1=0,y2=MT_pnl_clear,where=df['where'],alpha=0.6,color='purple'), alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6,returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')

                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    t = t * 2
                    axlist[0].text(x,y,t,fontstyle='italic')

                fig.savefig(fname=buf6,dpi=100,pad_inches=0.25) 
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            else:
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, fill_between=dict(y1=0,y2=MT_pnl_clear,where=df['where'],alpha=0.6,color='purple'), addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14),returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')

                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    t = t * 2
                    axlist[0].text(x,y,t,fontstyle='italic',fontsize='x-large')

                fig.savefig(fname=buf6,dpi=100,pad_inches=0.25)

            try:
                for ax in axlist:
                        del ax
                plt.cla()
                plt.clf()

                #plt.close(fig)
                plt.close('all')
                del fig, axlist
            except: pass
            '''
            if percent_high >= 12 or percent_low <= -12:
                title_mess = '\n\n\n' + title_mess + text
                
                mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, savefig=dict(fname=buf6,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            else:
                mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, savefig=dict(fname=buf6,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            
            '''
            buf6.seek(0)
            id_photo = send_photo(chat_id=screen_tg, file=buf6, cap=cap)
        
            f_id = str(id_photo['result']['photo'][-1]['file_id'])
            #id_photo = bot.send_photo(screen_tg, buf6, caption=cap)            
            #f_id = id_photo.photo[-1].file_id
            buf6.close()
            
            #bot.send_message(a1_v31,cap)
            #if percent_high >= 3:
                #bot.send_photo(wtp_screen_tg, open(f'/projects/Ver32/mt_screen/screen{symb}.jpeg','rb'), caption=cap)
                #bot.send_message(wtp_v31,cap)
            '''if len(MT_pnl) > 0:
                bot.send_photo(screen_v20, f_id, caption=cap)
            if MT_pnl_clear >= 8 and round(MT_pnl_clear/percent_high*100,2) <= 40:
                bot.send_photo(max_8_take_40_tg, f_id, caption=cap)
            
            if MT_pnl_clear >= 10:
                bot.send_photo(clear_pnl_10_tg, f_id, caption=cap)

            if round(MT_pnl_clear/percent_high*100,2) >= 80:
                bot.send_photo(take_clear_pnl_80_tg, f_id, caption=cap)'''

            
            
            print('end send screen')

            
            alerts_MT[symb][i] = 0

            


            channel_price[symb][i] = []
            channel_time[symb][i] = []
            return f_id, trade_str
            

        except Exception as e:
                #bot.send_message(screen_tg, f'fail screen {symb}')
                bot.send_message(error_tg, f'a1_v32 fail screen {symb} i={i}\n\n{e}')
                
                channel_price[symb][i] = []
                channel_time[symb][i] = []
                alerts_MT[symb][i] = 0
                return '', ''
                
            




def get_formatted_time(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return time_str
    
def get_formatted_day(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    time_str = dt_object.strftime("%Y-%m-%d")
    return time_str
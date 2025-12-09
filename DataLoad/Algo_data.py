
#import finplot as fplt
import pandas as pd
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
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error as mae # для подсчета ширины канала
from binance.um_futures import UMFutures



key = ''

screen_tg = '-' 
wtp_screen_tg = '-' # 
stat_tg = '-'


client = UMFutures() # пробую против дисконнекта                                           -eg-
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
check_send = 1




symbols = []
tickers = client.mark_price() # Подгружаем данные по всем фьючам
    

for i in tickers: 
        if i['symbol'] == 'BTCUSDT':
            continue
        if i['symbol'] == 'ETHUSDT':
            continue
        if i['symbol'] == 'USDCUSDT':
            continue
        if i['symbol'] == 'BTCUSDT_230929':
            continue
        if i['symbol'] == 'ETHUSDT_230929':
            continue
        #if i['symbol'] == 'CVXUSDT':
        #    continue
        ticker = i['symbol']
        if 'BTC' in ticker and i['symbol'] != 'BTCUSDT':
            continue
        if 'ETH' in ticker and ticker!= 'ETHFIUSDT':
            continue
        if 'USDT' in ticker:
            symbols.append(ticker)
                






time_frame = '1m'
last_klines = 1440
last_klines_check_algo = 15
price_acc = {}
high_acc = {}
low_acc = {}
volume_accumulator = {}
atr_accumulator = {}
time_last_kline = {}
number_of_trades = {}
quote_asset_volume = {}
taker_buy_base_asset_volume = {}

def get_last_klines(symbol, interval, tf):
            global price_acc
            #print(symbol)
            last_klines = client.klines(symbol=symbol, interval=tf, limit=(interval+1))
            check_bag = 0
            for klines_null in range(len(last_klines)-10,len(last_klines)+1):
                if last_klines[-klines_null][1] == last_klines[-klines_null][2] == last_klines[-klines_null][3] == last_klines[-klines_null][4] and float(last_klines[-klines_null][5]) == 0:
                    check_bag = check_bag + 1
            if check_bag == 11:
                update_symbols.remove(symbol)
                print(f'{symbol} delisting')
                return

            last_close = [float(last_klines[i][4]) for i in range(len(last_klines)-1)]
            price_acc[symbol] = last_close

            last_high = [float(last_klines[i][2]) for i in range(len(last_klines)-1)]
            high_acc[symbol] = last_high
            
            last_low = [float(last_klines[i][3]) for i in range(len(last_klines)-1)]
            low_acc[symbol] = last_low
            
            last_vol = [float(last_klines[i][5]) for i in range(len(last_klines)-1)]
            volume_accumulator[symbol] = last_vol

            last_qav = [float(last_klines[i][7]) for i in range(len(last_klines)-1)]
            quote_asset_volume[symbol] = last_qav

            last_tbbav = [float(last_klines[i][9]) for i in range(len(last_klines)-1)]
            taker_buy_base_asset_volume[symbol] = last_tbbav

            last_atr = [float(last_klines[i][2]) - float(last_klines[i][3]) for i in range(len(last_klines)-1)]
            atr_accumulator[symbol] = last_atr

            col_trades = [int(last_klines[i][8]) for i in range(len(last_klines)-1)]
            number_of_trades[symbol] = col_trades

            last_time = last_klines[-2][0] 
            time_last_kline[symbol] = int(last_time)

            if len(last_klines)>2:
                last_time = last_klines[-2][0]
                time_last_kline[symbol] = int(last_time)

update_symbols = symbols.copy()
for symbol in symbols:
        try:
            get_last_klines(symbol, last_klines, time_frame)
            time.sleep(0.05)
        except Exception as e:
            update_symbols.remove(symbol)
            print(f'{symbol} listing soon/bag {e}')
            
symbols = update_symbols

symbols_ws = []
for symbol in symbols:
        symbols_ws.append(str(symbol).lower())



volume_acc_last_kline = {symbol: 0.0 for symbol in symbols}
atr_accumulator_last_kline = {symbol: 0.0 for symbol in symbols}
number_of_trades_last_kline = {symbol: 0 for symbol in symbols}
high_last_kline = {symbol: 0.0 for symbol in symbols}
low_last_kline = {symbol: 0.0 for symbol in symbols}
bav_last_kline = {symbol: 0.0 for symbol in symbols}
tbbav_last_kline = {symbol: 0.0 for symbol in symbols}

l = [0.0 for i in range(2400)]
channel_data_price = {symbol: l for symbol in symbols}
for i in tickers:
        symbol = i['symbol']
        pr = float(i['markPrice'])
        try:
            channel_data_price[symbol] = [pr for _ in range(2400)]
        except: pass



TG_Bot_token=':'
bot = telebot.TeleBot(TG_Bot_token)

def send_to_telegram(message):
        apiURL = f'https://api.telegram.org/bot{TG_Bot_token}/sendMessage'
        try:    
            response = requests.post(apiURL, json={'chat_id': screen_tg, 'text': message})
        except Exception as e:
            print(e)
    



    #send_to_telegram('restarted')
print('restart')

symbols_bag = symbols.copy()

class BinanceFuturesWebSocket:
    def __init__(self):
        self.base_url = "wss://fstream.binance.com/ws/"
        self.symbols = symbols_ws
        self.threads = []
        


    async def on_message(self, ws, message):
        global volume_acc_last_kline, volume_accumulator, price_acc, time_last_kline, atr_accumulator, atr_accumulator_last_kline
        data_json = json.loads(message)
        
        
        
        symb = str(data_json['k']['s'])
        price = float(data_json['k']['c'])
        high = float(data_json['k']['h'])
        low = float(data_json['k']['l'])
        atr = float(data_json['k']['h']) - float(data_json['k']['l'])
        qty = float(data_json['k']['v'])
        time = int(data_json['k']['t'])
        col_trades = int(data_json['k']['n'])
        qav = float(data_json['k']['q'])
        tbbav = float(data_json['k']['V'])
        
        
            

        
        #time_5s = int(time - (time % 60000)) # 5000 - 5 секунд, 60000 - 1 минута
        if time > int(time_last_kline[symb]) and volume_acc_last_kline[symb] !=0:
            volume_accumulator[symb] = volume_accumulator[symb][1:] + [float(volume_acc_last_kline[symb])]
            atr_accumulator[symb] = atr_accumulator[symb][1:] + [float(atr_accumulator_last_kline[symb])]
            price_acc[symb] = price_acc[symb][1:] + [float(price)]
            high_acc[symb] = high_acc[symb][1:] + [float(high_last_kline[symb])]
            low_acc[symb] = low_acc[symb][1:] + [float(low_last_kline[symb])]
            number_of_trades[symb] = number_of_trades[symb][1:] + [int(number_of_trades_last_kline[symb])]
            quote_asset_volume[symb] = quote_asset_volume[symb][1:] + [float(bav_last_kline[symb])]
            taker_buy_base_asset_volume[symb] = taker_buy_base_asset_volume[symb][1:] + [float(tbbav_last_kline[symb])]
            time_last_kline[symb] = time
            
            if symb == 'XRPUSDT':
                print('XRPUSDT')
        else:
            volume_acc_last_kline[symb] = qty
            atr_accumulator_last_kline[symb] = atr
            number_of_trades_last_kline[symb] = col_trades
            high_last_kline[symb] = high
            low_last_kline[symb] = low
            bav_last_kline[symb] = qav
            tbbav_last_kline[symb] = tbbav
        
    async def save_data(self):
        while True:
            await asyncio.sleep(10)
            try:
                with open('/projects/data/volume_accumulator.txt', 'w') as file:
                    file.write(json.dumps(volume_accumulator))

                with open('/projects/data/atr_accumulator.txt', 'w') as file:
                    file.write(json.dumps(atr_accumulator))
                with open('/projects/data/price_acc.txt', 'w') as file:
                    file.write(json.dumps(price_acc))
                with open('/projects/data/high_acc.txt', 'w') as file:
                    file.write(json.dumps(high_acc))
                with open('/projects/data/low_acc.txt', 'w') as file:
                    file.write(json.dumps(low_acc))
                with open('/projects/data/number_of_trades.txt', 'w') as file:
                    file.write(json.dumps(number_of_trades))
                with open('/projects/data/time_last_kline.txt', 'w') as file:
                    file.write(json.dumps(time_last_kline))
                with open('/projects/data/channel_data_price.txt', 'w') as file:
                    file.write(json.dumps(channel_data_price))
                with open('/projects/data/quote_asset_volume.txt', 'w') as file:
                    file.write(json.dumps(quote_asset_volume))
                with open('/projects/data/taker_buy_base_asset_volume.txt', 'w') as file:
                    file.write(json.dumps(taker_buy_base_asset_volume))


            except: pass
            print('save')
            
    

    def get_formatted_time(self, timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
        return time_str
    
    def get_formatted_day(self, timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d")
        return time_str
    
    def on_open(self, ws):
        print("Websocket was opened")
    '''
    def on_error(self, ws,  error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")
    '''        

    async def connect(self, symbol):
        url = self.base_url + f"{symbol}@kline_1m"
        try:
            async with websockets.connect(uri=url,open_timeout = 90, ping_interval=None, ping_timeout=None) as ws: #kline_1m
                
                while True:
                    try:
                        message = await ws.recv()
                        await self.on_message(ws, message)
                    except (asyncio.TimeoutError, asyncio.exceptions.CancelledError,asyncio.exceptions.TimeoutError) as e:
                        continue
        except Exception as e:
            print(f'{symbol} kline_1m not connect {e}')
            async with websockets.connect(uri=url,open_timeout = 90, ping_interval=None, ping_timeout=None) as ws: #kline_1m
                while True:
                    try:
                        message = await ws.recv()
                        await self.on_message(ws, message)
                    except (asyncio.TimeoutError, asyncio.exceptions.CancelledError,asyncio.exceptions.TimeoutError) as e:
                        continue
        finally: print(f'{symbol} kline_1m not connect again')
    '''
    async def start(self):
        #await self.initialize()
        connections = [self.connect(symbol) for symbol in self.symbols]
        connections.append(self.save_data())
        # Print and reset volume is run concurrently with the connections
        #connections.append(self.print_and_reset_volume())
        await asyncio.gather(*connections)

    async def run(self):
        #loop = asyncio.get_event_loop()
        #if loop.is_running():
        task = asyncio.create_task(self.start())
        #else:
            #loop.run_until_complete(self.start())
    '''
    async def main(self):
        connections = [self.connect(symbol) for symbol in self.symbols]
        connections.append(self.save_data())
        return connections
        #await asyncio.gather(*connections)


 
 


 
 
class BinanceFuturesWebSocketMT:
    def __init__(self):
       self.base_url = "wss://fstream.binance.com/ws/"
       self.symbols = symbols_ws
       self.threads = []
       
 
 
    async def on_message(self, ws, message):
        data_json = json.loads(message)
 
        symb = data_json['s']
        price = float(data_json['p'])
        
        
        channel_data_price[symb] = channel_data_price[symb][1:] + [price]
       
    

    def get_formatted_time(self, timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
        return time_str
    
    def get_formatted_day(self, timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d")
        return time_str
    
    def on_open(self, ws):
        print("Websocket was opened")
    '''
    def on_error(self, ws,  error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")
    '''        

    async def connect(self, symbol):
        url = self.base_url + f"{symbol}@markPrice@1s"
        try:
            async with websockets.connect(uri=url,open_timeout = 90, ping_interval=None, ping_timeout=None) as ws: #markPrice@1s
                while True:
                    try:
                        message = await ws.recv()
                        await self.on_message(ws, message)
                    except (asyncio.TimeoutError, asyncio.exceptions.CancelledError,asyncio.exceptions.TimeoutError) as e:
                        continue
        except Exception as e:
            print(f'{symbol} markPrice not connect {e}')
            async with websockets.connect(uri=url,open_timeout = 90, ping_interval=None, ping_timeout=None) as ws: #markPrice@1s
                while True:
                    try:
                        message = await ws.recv()
                        await self.on_message(ws, message)
                    except (asyncio.TimeoutError, asyncio.exceptions.CancelledError,asyncio.exceptions.TimeoutError) as e:
                        continue
        finally: print(f'{symbol} markPrice not connect again')

    '''
    async def start(self):
        #await self.initialize()
        connections = [self.connect(symbol) for symbol in self.symbols]
        connections.append(self.save_data())
        # Print and reset volume is run concurrently with the connections
        #connections.append(self.print_and_reset_volume())
        await asyncio.gather(*connections)

    async def run(self):
        #loop = asyncio.get_event_loop()
        #if loop.is_running():
        task = asyncio.create_task(self.start())
        #else:
            #loop.run_until_complete(self.start())
    '''
    async def main(self):
        connections = [self.connect(symbol) for symbol in self.symbols]
        
        return connections
        #await asyncio.gather(*connections)

async def main():
    conn_MT = await BinanceFuturesWebSocketMT().main()
    conn_algo = await BinanceFuturesWebSocket().main()
    connections = conn_MT + conn_algo
    
    await asyncio.gather(*connections)
    


if __name__ == "__main__":
    
    
    import nest_asyncio
    nest_asyncio.apply()

        
    #bws = BinanceFuturesWebSocket()
    #bws_MT = BinanceFuturesWebSocketMT()
    #asyncio.get_event_loop().run_until_complete(bws.main())
    asyncio.run(main())
    

    

    try:
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nWebSocket connection terminated.")
from binance.um_futures import UMFutures
import json

key = '#' #402
secret = '#'

client = UMFutures(key, secret) 
# client = UMFutures() 


symbols = []
tickers = client.mark_price() # Подгружаем данные по всем фьючам
for i in tickers: 
    if i['symbol'] == 'ETHUSDT':
        continue
    if i['symbol'] == 'USDCUSDT':
        continue
    if i['symbol'] == 'BTCUSDT_230929':
        continue
    if i['symbol'] == 'ETHUSDT_230929':
        continue
    ticker = i['symbol']
    if 'USDT' in ticker:
        symbols.append(ticker)


lot_info = {}
TickSize = {symbol: 0.0 for symbol in symbols}
leverage = 5
max_lot = {}

exchange = client.exchange_info()
for i in exchange['symbols']:
    if i['symbol'] in symbols:
        symbb = i['symbol']
        TickSize[symbb] = float(i['filters'][0]['tickSize'])
        stepSize = float(i['filters'][1]['stepSize'])
        minQty = float(i['filters'][1]['minQty'])
        lot_info[symbb] = [stepSize, minQty]
        max_lot[symbb] = int(i['filters'][2]['maxQty'])
        try:
            client.change_leverage(symbol=symbb, leverage=leverage, recvWindow=50000)
            # if symbb == 'XRPUSDT':
            print(symbb, "\tlot_info=", lot_info[symbb], "\tmax_lot=", max_lot[symbb], "\tTickSize=", TickSize[symbb])
        except:
            print(symbb, 'not 5 leverage')

with open('/projects/short_VJ/TickSize.txt', 'w') as file:
            file.write(json.dumps(TickSize))
                
with open('/projects/short_VJ/lot_info.txt', 'w') as file:
    file.write(json.dumps(lot_info))

with open('/projects/short_VJ/max_lot.txt', 'w') as file:
    file.write(json.dumps(max_lot))

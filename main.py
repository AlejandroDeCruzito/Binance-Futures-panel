import ccxt
# import time, datetime
from indicators import *
import PySimpleGUI as sg
from threading import Timer
import pandas as pd

# enter your keys here
apiKey = ''
secretKey = ''

symbol = 'TRXUSDT'

# API CONNECT
exchange = ccxt.binance({ 'apiKey': apiKey, 'secret': secretKey, 'options': { 'defaultType': 'future'}, 'enableRateLimit': True})

candleBody = []
candleLowLevel = []
candleSmoothedHeikinAshiTrend = [] 

timeRange = "15m"
initSmoothedHeikenAshiEma1 = 10
initSmoothedHeikenAshiEma2 = 10
price = 0
minPrice = 0
maxPrice = 0
lowPriceCandle = 0
highPriceCandle = 0
lineEma1 = []
lineEma2 = []
lineEma3 = []
initLineEma1 = 10
initLineEma2 = 20
initLineEma3 = 50

newInfo_flag = False

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def THREAD1():
    global newInfo_flag
    global price
    global minPrice
    global maxPrice
    global lowPriceCandle
    global highPriceCandle
    global candleBody
    global candleLowLevel
    global candleSmoothedHeikinAshiTrend
    global timeStamp
    global prevTimeStamp
    global noOfTotalDisplayCandles    
    global choosedTimeFrame
    global choosedSmoothedHeikenAshiEma1
    global choosedSmoothedHeikenAshiEma2    
    global lineEma1
    global lineEma2
    global lineEma3
    global choosedLineEma1
    global choosedLineEma2
    global choosedLineEma3

    try:
        # balance = exchange.fetch_balance()
        # free_balance = exchange.fetch_free_balance()
        # positions = balance['info']['positions']
        # current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == symbol]
        # position_info = pd.DataFrame(current_positions, columns=['symbol', 'entryPrice', 'unrealizedProfit',\
        #                                                          'isolatedWallet', 'positionAmt', 'positionSide', 'leverage'])
        # Load basic candlesticks
        
        candlesSticks = exchange.fetch_ohlcv(symbol, timeframe=choosedTimeFrame, since = None, limit = noOfTotalDisplayCandles+60)
        frame = pd.DataFrame(candlesSticks)
        frame = frame.iloc[:,:6]
        frame.columns = ['Time','Open','High','Low','Close','Volume']
        timeStamp = frame['Time'].iloc[-2]
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index, unit='ms' ) + pd.offsets.Hour(+2)
        frame = frame.astype(float)
        # frame = HEIKIN_ASHI( frame )
        frame = SMOOTHED_HEIKIN_ASHI( frame, choosedSmoothedHeikenAshiEma1, choosedSmoothedHeikenAshiEma2 )
        # EMA1, EMA2, EMA3
        frame['EMA1'] = frame['Close'].ewm( span = choosedLineEma1, adjust=False).mean()          
        frame['EMA2'] = frame['Close'].ewm( span = choosedLineEma2, adjust=False).mean()          
        frame['EMA3'] = frame['Close'].ewm( span = choosedLineEma3, adjust=False).mean()          
        frame.dropna(inplace=True)    
        
        if ( timeStamp >= prevTimeStamp and newInfo_flag == False):
            prevTimeStamp = timeStamp
            price = frame['Close'].iloc[-1]            

            lowPriceCandle = price*1000.0
            highPriceCandle = 0.0
                            
            for i in range( 0, noOfTotalDisplayCandles, 1):
                lineEma1[i] = frame['EMA1'].iloc[60+i]
                lineEma2[i] = frame['EMA2'].iloc[60+i] 
                lineEma3[i] = frame['EMA3'].iloc[60+i] 
                candleLowLevel[i] = frame['Low'].iloc[60+i]
                candleBody[i] = frame['High'].iloc[60+i]-frame['Low'].iloc[60+i];
                if ( frame['Low'].iloc[60+i] < lowPriceCandle ):
                    lowPriceCandle = frame['Low'].iloc[60+i]
                if ( frame['High'].iloc[60+i] > highPriceCandle ):
                    highPriceCandle = frame['High'].iloc[60+i]
                if ( frame['smHA_Close'].iloc[60+i] >= frame['smHA_Open'].iloc[60+i] ):
                    candleSmoothedHeikinAshiTrend[i] = 1
                else:
                    candleSmoothedHeikinAshiTrend[i] = -1
            newInfo_flag = True

    except ccxt.BaseError as Error:
        print ("[ERROR] ", Error )
        
def main():
    global newInfo_flag
    global noOfTotalDisplayCandles
    global candleBody
    global candleLowLevel
    global candleSmoothedHeikinAshiTrend
    global lowPriceCandle
    global highPriceCandle
    global choosedTimeFrame
    global prevTimeStamp
    global timeStamp
    global price
    global choosedSmoothedHeikenAshiEma1
    global choosedSmoothedHeikenAshiEma2
    global lineEma1
    global lineEma2
    global lineEma3
    global choosedLineEma1
    global choosedLineEma2
    global choosedLineEma3
    global symbolPrecision
    
    timeStamp = 0
    prevTimeStamp = timeStamp
    
    choosedTimeFrame = timeRange
    prevChoosedTimeFrame = choosedTimeFrame
    choosedSmoothedHeikenAshiEma1 = initSmoothedHeikenAshiEma1
    choosedSmoothedHeikenAshiEma2 = initSmoothedHeikenAshiEma2
    
    sg.theme('DarkGray6')
    noOfTotalDisplayCandles = 200 
    candleBody = [0.0]*noOfTotalDisplayCandles
    candleLowLevel = [0.0]*noOfTotalDisplayCandles     
    candleSmoothedHeikinAshiTrend = [0]*noOfTotalDisplayCandles
    lineEma1 = [0.0]*noOfTotalDisplayCandles
    lineEma2 = [0.0]*noOfTotalDisplayCandles
    lineEma3 = [0.0]*noOfTotalDisplayCandles
    choosedLineEma1 = initLineEma1
    choosedLineEma2 = initLineEma2
    choosedLineEma3 = initLineEma3
        
    layout =[
             [ sg.Graph(canvas_size=(noOfTotalDisplayCandles*6+60,500), key='mini_graph', graph_bottom_left=(0, 0),\
                graph_top_right=(noOfTotalDisplayCandles*6+60,500), background_color='#1C202A', pad=(0,4), enable_events=True ) ],
             [ 
                sg.Text ('Time frame'),
                sg.Combo(['1m','3m','5m','15m','30m','1h'], default_value = timeRange, key='-timeFrame-'),
                sg.Text (f'candles:{noOfTotalDisplayCandles} symbol:{symbol}'),
             ],
             [
                sg.Text ('Smoothed Heiken Ashi parameters'),
                sg.Text ('EMA#1'),
                sg.Spin([x+1 for x in range(60)], choosedSmoothedHeikenAshiEma1, size=(4,1), key='-shal1-' ),
                sg.Text ('EMA#2'),
                sg.Spin([x+1 for x in range(60)], choosedSmoothedHeikenAshiEma2, size=(4,1), key='-shal2-' ),
             ],
             [
                sg.Text ('Lines'),
                sg.Checkbox('EMA#1', default=True, key='-chkema1-'),
                sg.Spin([x+1 for x in range(60)], choosedLineEma1 , size=(4,1), key='-ema1-' ),
                sg.Checkbox('EMA#2', default=True, key='-chkema2-'),
                sg.Spin([x+1 for x in range(60)], choosedLineEma2, size=(4,1), key='-ema2-' ),
                sg.Checkbox('EMA#3', default=True, key='-chkema3-'),
                sg.Spin([x+1 for x in range(60)], choosedLineEma3, size=(4,1), key='-ema3-' ),
             ],             
            ]
    window = sg.Window('Binance Futures PANEL',
                       layout,
                       location=(0,0),                       
                       size = (noOfTotalDisplayCandles*6+68, 680),
                       element_padding=(2,2),
                       no_titlebar=False,
                       keep_on_top=True,
                       grab_anywhere=False,
                       font=('Consolas',10),
                       finalize=True
                       )
    graph = window['mini_graph']
  
    balance = exchange.fetch_balance()
    infos = exchange.market(symbol)
    symbolPrecision = infos['precision']['price']    
    
    timer = RepeatTimer(1, THREAD1)
    timer.start()
    
    while True:
        event, values = window.read(timeout=50)
        if event == sg.WIN_CLOSED:
            break
        
        if ( newInfo_flag == True ):
            graph.erase()
            if ( lowPriceCandle == highPriceCandle ):
                graphStretchFactor = 1.0
            else:    
                graphStretchFactor = 480.0/(highPriceCandle - lowPriceCandle)
                        
            for i in range(0, noOfTotalDisplayCandles , 1):
                if ( candleSmoothedHeikinAshiTrend[i] == 1 ):
                    graph.DrawRectangle((6*i,1), (6*i+5, 20), fill_color='#00FF00', line_color='#000000', line_width=1 )
                    graph.DrawRectangle((6*i,21), (6*i+5, 499), fill_color='#003300', line_color='#000000', line_width=1 )
                else:
                    graph.DrawRectangle((6*i,1), (6*i+5, 20), fill_color='#FF0000', line_color='#000000', line_width=1 )             
                    graph.DrawRectangle((6*i,21), (6*i+5, 499), fill_color='#330000', line_color='#000000', line_width=1 ) 
                yCoordinate = (candleLowLevel[i]-lowPriceCandle)*graphStretchFactor + 21
                bar = candleBody[i]*graphStretchFactor + yCoordinate
                graph.DrawRectangle((6*i+1, yCoordinate), (6*i+4, bar), fill_color='#4C879F', line_color='#000000', line_width=0 )

            for i in range(1, noOfTotalDisplayCandles , 1):
                if ( values['-chkema1-']== True ):
                    graph.DrawLine( (6*(i-1)+6, (lineEma1[i-1]-lowPriceCandle)*graphStretchFactor+21), (6*i+6, (lineEma1[i]-lowPriceCandle)*graphStretchFactor+21), color='#BB4B00' )
                if ( values['-chkema2-']== True ):
                    graph.DrawLine( (6*(i-1)+6, (lineEma2[i-1]-lowPriceCandle)*graphStretchFactor+21), (6*i+6, (lineEma2[i]-lowPriceCandle)*graphStretchFactor+21), color='#FF8737' )
                if ( values['-chkema3-']== True ):
                    graph.DrawLine( (6*(i-1)+6, (lineEma3[i-1]-lowPriceCandle)*graphStretchFactor+21), (6*i+6, (lineEma3[i]-lowPriceCandle)*graphStretchFactor+21), color='#FFB888' )

            graph.DrawLine( (0,(price-lowPriceCandle)*graphStretchFactor+21),(noOfTotalDisplayCandles*6,(price-lowPriceCandle)*graphStretchFactor+21), color='#6C97BF')
            graph.DrawText( f'{lowPriceCandle:.{symbolPrecision}f}',(noOfTotalDisplayCandles*6+23,22), color='#6C97BF')
            graph.DrawText( f'{highPriceCandle:.{symbolPrecision}f}',(noOfTotalDisplayCandles*6+23,494), color='#6C97BF')            
            graph.DrawText( f'{price:.{symbolPrecision}f}',(noOfTotalDisplayCandles*6+23,(price-lowPriceCandle)*graphStretchFactor+21  ), color='#ACE7FF')

            deltaPercent = ((highPriceCandle - lowPriceCandle)/lowPriceCandle)*100
            symbolMessage = f'{symbol} {price:.{symbolPrecision}f}, d: {deltaPercent:.2f}% '
            graph.DrawText( symbolMessage ,(len(symbolMessage)*8,500-16), font=('Dotrice Condensed',24,'bold'), color='#000000')
            graph.DrawText( symbolMessage ,(len(symbolMessage)*8,500-16), font=('Dotrice Condensed',24), color='#ACE7FF')
            choosedSmoothedHeikenAshiEma1 = values['-shal1-']
            choosedSmoothedHeikenAshiEma2 = values['-shal2-']
            choosedLineEma1 = values['-ema1-']
            choosedLineEma2 = values['-ema2-']
            choosedLineEma3 = values['-ema3-']
            newInfo_flag = False

        choosedTimeFrame = values['-timeFrame-']
        if (prevChoosedTimeFrame!=choosedTimeFrame):
            prevChoosedTimeFrame = choosedTimeFrame
            prevTimeStamp = 0           
        
    timer.cancel()
    window.close()

if __name__ == '__main__':
    main()    

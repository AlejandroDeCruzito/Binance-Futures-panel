
def SMOOTHED_HEIKIN_ASHI(_df, _len1=10, _len2=10):
    _df['O1'] = _df['Open'].ewm( com = _len1-1, adjust=False).mean()    
    _df['H1'] = _df['High'].ewm( com = _len1-1, adjust=False).mean()    
    _df['L1'] = _df['Low'].ewm( com = _len1-1, adjust=False).mean()    
    _df['C1'] = _df['Close'].ewm( com = _len1-1, adjust=False).mean()  
    
    _df['HAClose'] = (_df['O1']+ _df['H1']+ _df['L1']+_df['C1'])/4
    
    idx = _df.index.name
    _df.reset_index(inplace=True)
    for i in range(0, len(_df)):
        if i == 0:
            _df._set_value(i, 'HAOpen', ((_df._get_value(i, 'O1') + _df._get_value(i, 'C1')) / 2))
        else:
            _df._set_value(i, 'HAOpen', ((_df._get_value(i - 1, 'HAOpen') + _df._get_value(i - 1, 'HAClose')) / 2))
    if idx:
        _df.set_index(idx, inplace=True)
    _df['HAHigh']= _df[['HAOpen','HAClose','H1']].max(axis=1)
    _df['HALow']= _df[['HAOpen','HAClose','L1']].min(axis=1)

    _df['smHA_Open'] = _df['HAOpen'].ewm( com = _len2-1, adjust=False).mean()    
    _df['smHA_High'] = _df['HAHigh'].ewm( com = _len2-1, adjust=False).mean()    
    _df['smHA_Low'] = _df['HALow'].ewm( com = _len2-1, adjust=False).mean()    
    _df['smHA_Close'] = _df['HAClose'].ewm( com = _len2-1, adjust=False).mean()
  
    # Delete temporarily used columns
    columns = ['O1','H1','L1','C1','HAOpen','HAHigh','HALow','HAClose' ]
    _df.drop(columns, inplace=True, axis=1)
            
    return _df

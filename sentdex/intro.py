import datetime as dt
import matplotlib.pyplot as plt
from numpy import DataSource
import pandas as pd
import pandas_datareader.data as web
import matplotlib as style
import yfinance as yf


style.use('MacOSX')

start = dt.datetime(2000,1,1)
end = dt.datetime(2016,12,31)


# df = web.DataReader('TSLA', data_source='yahoo', start=start, end=end)
# print(df.head())

df = yf.download('TSLA', start, end)
print(df.head())
# ValueError: 'ggplot' is not a valid value for backend; 
# supported values are 
# ['GTK3Agg', 'GTK3Cairo', 'GTK4Agg', 'GTK4Cairo', 
#  'MacOSX', 'nbAgg', 'QtAgg', 'QtCairo', 'Qt5Agg', 'Qt5Cairo', 
#  'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 
#  'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']








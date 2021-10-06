import streamlit as st
import pandas as pd 
from PIL import Image
import base64
import matplotlib.pyplot as plt 
import seaborn as sns
from bs4 import BeautifulSoup
import requests
import json
import time

st.set_page_config(layout="wide")

image=Image.open("/home/diksha/Desktop/GraphsandDP/logo.jpg")

st.image(image,width=500)

st.title('Crypto Price App')

st.markdown("""
This app retrives cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!""")

expander_bar=st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf).
""")


col1=st.sidebar
col2,col3=st.columns((2,1))  

col1.header('Input Options') #header for the sidebar

currency_price_unit=col1.selectbox('Select Currency for Price',('USD','BTC','ETH'))

#Web scrapting the CoinMarketCap data

@st.cache
def loadata():
    cmc=requests.get('https://coinmarketcap.com/')
    soup=BeautifulSoup(cmc.content,'html.parser')
    # using soup.prettify to find the webpage's format 
    # print(soup.prettify())

    data=soup.find('script',id='__NEXT_DATA__',type='application/json')
    coins={}
    coin_data=json.loads(data.contents[0])
    listings=coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings[1:]:
        coins[str(i[8])]=i[125]

    coin_name=[]
    coin_symbol=[]
    market_cap=[]
    percent_change_1h=[]
    percent_change_24h=[]
    percent_change_7d=[]
    price=[]
    volume_24h=[]

    for i in listings[1:]:
        coin_name.append(i[125])
        coin_symbol.append(i[126])
        price.append(i[28])
        percent_change_1h.append(i[22])
        percent_change_24h.append(i[23])
        percent_change_7d.append(i[26])
        market_cap.append(i[17])
        volume_24h.append(i[30])

    for i in listings[1:]:
        coin_name.append(i[125])
        coin_symbol.append(i[126])
        if currency_price_unit == 'BTC':
                price.append(i[28])
                percent_change_1h.append(i[22])
                percent_change_24h.append(i[23])
                percent_change_7d.append(i[26])
                market_cap.append(i[19])
                volume_24h.append(i[30])
        if currency_price_unit == 'USD':
                price.append(i[64])
                percent_change_1h.append(i[58])
                percent_change_24h.append(i[59])
                percent_change_7d.append(i[62])
                market_cap.append(i[55])
                volume_24h.append(i[66])
        if currency_price_unit == 'ETH':
                price.append(i[46])
                percent_change_1h.append(i[40])
                percent_change_24h.append(i[41])
                percent_change_7d.append(i[44])
                market_cap.append(i[37])
                volume_24h.append(i[48]) 
    

    df=pd.DataFrame(columns=['coin_name','coin_symbol','market_cap','percent_change_1h','percent_change_24h','percent_change_7d','price','volume_24h'])
    df['coin_name']=coin_name
    df['coin_symbol']=coin_symbol
    df['price']=price
    df['percent_change_1h']=percent_change_1h
    df['percent_change_24h']=percent_change_24h
    df['percent_change_7d']=percent_change_7d
    df['market_cap']=market_cap
    df['volume_24h']=volume_24h
    return df

df=loadata()
loadata()

#coin selection from sidebar
sorted_coin=sorted(df['coin_symbol'])
selected_coin=col1.multiselect('Cryptocurrency',sorted_coin,sorted_coin)

df_selected_coin=df[df['coin_symbol'].isin(selected_coin)] #getting data of selected coin

# slider for selecting no of coins
num_coin=col1.slider('Display Top N Coins',1,100,100)
df_coins=df_selected_coin[:num_coin]

# select box for selecting the timeframe(1h,24h,7D)
percent_timeframe=col1.selectbox('Percent change time frame',['7d','24h','1h'])
percent_dict={"7d":'percent_change_7d','24h':'percent_change_24h','1h':'percent_change_1h'}
selected_percent_timeframe=percent_dict[percent_timeframe]

#select box for sorting values
sort_values=col1.selectbox('Sort values?',['Yes','No'])

col2.subheader('Price Data for Selected Cryptocurrency')

col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

col2.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader('Bar plot of % Price Change')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    col3.write('*7 days period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_24h'])
    col3.write('*24 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_1h'])
    col3.write('*1 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
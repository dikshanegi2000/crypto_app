import streamlit as st
import pandas as pd 
from PIL import Image
import base64
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup
import requests
import json
import time
import _json
import csv
import warnings
warnings.filterwarnings('ignore')



#Page expands to full width
st.set_page_config(layout = "wide")
#Logo for the app
image = Image.open('logo.jpg')

st.container()
# st.columns(spec)
col1, col2 = st.columns(2)
col1.image(image,width=500)


# title----------------------------------------
col2.title('IDK crypto App')
col2.markdown(""" 
IDK crypto app retrives the latest info about the top 100 cryptocurrencies so now u know what's treanding in cryptocurrencies 
""")

#about------------------------------------------
# expander_bar  = col1.expander("About")

col2.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf).
* **Contributed by:** Vaishnavi Kalgutkar, Diksha Negi 
""")


#-------------------------------------
#col1 is sidebar and col2 and col3 page contents
col1  = st.sidebar
# col2 is twice in width as col1
col2,col3 = st.columns((2,1))

#header for col1 
col1.header('Input options')
#sidebar - currency price unit
currency_price_unit = col1.selectbox('Select currency for price',('USD','BTC','ETH'))


@st.cache(hash_funcs={json.load: None})
def load_data():
    cmc=requests.get('https://coinmarketcap.com')
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






    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'price', 'volume_24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percent_change_1h'] = percent_change_1h
    df['percent_change_24h'] = percent_change_24h
    df['percent_change_7d'] = percent_change_7d
    df['market_cap'] = market_cap
    df['volume_24h'] = volume_24h
    return df


df = load_data()



sorted_coin = sorted(df['coin_symbol'])
selected_coin = col1.multiselect('Cryptocurrency',sorted_coin,sorted_coin)

df_selected_coin = df[df['coin_symbol'].isin(selected_coin)]

num_coin = col1.slider('Display Top N coins',1,100,100)
df_coins = df_selected_coin[:num_coin]

percent_timeframe = col1.selectbox('Percent change time frame',['7d','24h','1h'])
percent_dict={"7d":'percent_change_7d','24h':'percent_change_24h','1h':'percent_change_1h'}
selected_percent_timeframe=percent_dict[percent_timeframe]


sort_values = col1.selectbox('Sort values?',['Yes','No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)


def filedownload(df) :
    csvfile = df.to_csv(index=False)
    b64 = base64.b64encode(csvfile.encode()).decode()
    href = f'<a href="data:file/csv;base64{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin),unsafe_allow_html=True)

col2.subheader('Table of % Price Change')
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] >0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] >0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] >0
col2.dataframe(df_change)


col3.subheader('Bar plot of % Price Change')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    col3.write('*7 days period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1,bottom =0)
    df_change['percent_change_7d'].plot(kind  = 'barh',color=df_change.positive_percent_change_7d.map({True:'g',False:'r'}))
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

col2.subheader('Cryptocurrency Dashboard')
# tickers = [
# "AAVE","ADA","ALGO","AMP","AR","ATOM","AVAX","AXS","BAT","BCH","BNB","BSV","BTC","BTCB","BTG","BTT","BUSD","CAKE","CEL","CELO","CHZ","COMP","CRO","CRV","DAI","DASH","DCR","DOGE","DOT","DYDX","EGLD","ENJ","EOS","ETC","ETH","FIL","FLOW",
# "FTM"
# ,"FTT"
# ,"GRT"
# ,"HBAR"
# ,"HNT"
# ,"HOT"
# ,"HT"
# ,"ICP"
# ,"ICX"
# ,"IOST"
# ,"KLAY"
# ,"KSM"
# ,"LEO"
# ,"LINK"
# ,"LTC"
# ,"LUNA"
# ,"MANA"
# ,"MATIC"
# ,"MINA"
# ,"MIOTA"
# ,"MKR"
# ,"NEAR"
# ,"NEO"
# ,"NEXO"
# ,"OKB"
# ,"OMG"
# ,"ONE"
# ,"QNT"
# ,"QTUM"
# ,"REN"
# ,"RENBTC"
# ,"REV"
# ,"RUNE"
# ,"RVN"
# ,"SHIB"
# ,"SNX"
# ,"SOL"
# ,"SRM"
# ,"STX"
# ,"SUSHI"
# ,"TEL"
# ,"TFUEL"
# ,"THETA"
# ,"TRX"
# ,"TUSD"
# ,"UNI"
# ,"USDC"
# ,"USDP"
# ,"USDT"
# ,"UST"
# ,"VET"
# ,"WAVES"
# ,"WBTC"
# ,"XDC"
# ,"XEC"
# ,"XEM"
# ,"XLM"
# ,"XMR"
# ,"XRP"
# ,"XTZ"
# ,"YFI"
# ,"ZEC"
# ,"ZIL"]


# dropdown = col2.selectbox('Select Your Cryptocurrency', tickers)




# from cryptocmd import CmcScraper

# # initialise scraper without time interval
# scraper = CmcScraper(dropdown)

# # get raw data as list of list
# headers, data = scraper.get_data()

# # get data in a json format
# xrp_json_data = scraper.get_data("json")

# # export the data as csv file, you can also pass optional `name` parameter
# scraper.export("csv")

# # Pandas dataFrame for the same data
# df = scraper.get_dataframe()

# import plotly.graph_objects as go

# fig = go.Figure()

# fig.add_trace(go.Scatter(x = df.Date, y = df.Volume,
#                                  mode = 'lines',
#                                  name = 'yooyo'))

# col2.plotly_chart(fig, use_container_width=False)

# # if len(dropdown) >0:
#     # df  = yf.download(dropdown,start,end)['Adj Close']
 
    
#     # col2.line_chart(df['Volume'])


dropdown = col2.multiselect('Select Your Cryptocurrency', sorted_coin)

start = col2.date_input('Start',value = pd.to_datetime('2021-01-01')).strftime("%d-%m-%Y")
end = col2.date_input('End',value = pd.to_datetime('today')).strftime("%d-%m-%Y")

from cryptocmd import CmcScraper

f_df = pd.DataFrame(columns=dropdown)
for options in dropdown:


    # initialise scraper with time interval
    scraper = CmcScraper(options, start, end)

    # get raw data as list of list
    headers, data = scraper.get_data()

    # get data in a json format
    json_data = scraper.get_data("json")

    # export the data to csv
    scraper.export("csv")

    # get dataframe for the data
    df = scraper.get_dataframe()

    f_df[options] = df['Market Cap']

if(f_df.empty):
      col2.write('Invalid Date')

elif len(dropdown) > 0:
    f_df = f_df.set_index(df['Date'])
    #print(df) 
    #f_df = f_df.pct_change()
    col2.line_chart(f_df)


import bs4 as bs
import pickle
from numpy import append
import requests

def save_osbex_tickers():
    resp = requests.get('https://no.wikipedia.org/wiki/OSEBX-indeksen')
    soup = bs.BeautifulSoup(resp.text)
    table = soup.find('table', {'class': 'sortable wikitable jquery-tablesorter'})
    tickers = []
    for row in table.findAll('body'):
        print(row)
        ticker = row.findAll('td')[1].text
        tickers.append(ticker)

    with open('osebxtickers.pickle', 'wb') as f:
        pickle.dump(tickers, f)

    print(tickers)
    return tickers

save_osbex_tickers()


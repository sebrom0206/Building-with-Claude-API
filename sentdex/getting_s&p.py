import bs4 as bs
import pickle
import requests

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text)
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find('td').text
        tickers.append(ticker)

    with open('sp500tickers.pickle', 'w') as f:
        pickle.dump(tickers, f)
        
    print(tickers)
    return tickers

save_sp500_tickers

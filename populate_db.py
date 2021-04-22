import sqlite3
import alpaca_trade_api as tradeapi


connection = sqlite3.connect('app.db')

cursor = connection.cursor()

api = tradeapi.REST('PK75VUTF353H81KOOZB7', 'yAkrPrBsaGDcvqvDilkU4ukY7qAEDjCMoHiC2YFj', base_url='https://paper-api.alpaca.markets') # or use ENV Vars shown below
assets = api.list_assets()
for asset in assets:
    if asset.status == 'active' and asset.tradable:
            cursor.execute("INSERT INTO stock (symbol, company) VALUES (?, ?)", (asset.symbol, asset.name))


connection.commit()




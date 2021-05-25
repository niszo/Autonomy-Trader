import sqlite3
import config
import alpaca_trade_api as tradeapi
import smtplib, ssl
from datetime import date
import pandas as pd

context = ssl.create_default_context()

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    select id from strategy where name = 'opening_range_breakout'
""")

strategy_id = cursor.fetchone()['id']  

cursor.execute("""
    select symbol, name
    from stock
    join stock_strategy on stock_strategy.stock_id = stock.id
    where stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks] 

current_date = date.today().isoformat() 
NY = "America/New_York"

start_minute_bar = pd.Timestamp(f"{current_date} 09:30:00-04:00", tz=NY).isoformat()
end_minute_bar = pd.Timestamp(f"{current_date} 09:45:00-04:00", tz=NY).isoformat()

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

orders = api.list_orders(status='all', limit=500, after=f"{current_date}T13:30:00Z")

existing_order_symbols = [order.symbol for order in orders]



start=pd.Timestamp(f"{current_date} 09:30:00-04:00", tz=NY).isoformat()
end=pd.Timestamp(f"{current_date} 11:00:00-04:00", tz=NY).isoformat()

messages = []
for symbol in symbols:
    minute_bars = api.get_barset(symbol, 'minute', start=start, end=end).df 


    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar) 
    opening_range_bars = minute_bars.loc[opening_range_mask]
    
    opening_range_low = opening_range_bars[symbol, 'low'].min()
    opening_range_high = opening_range_bars[symbol, 'high'].max()
    opening_range = opening_range_high - opening_range_low
    
    

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]


    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars[symbol, 'close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakout.iloc[0][symbol, 'close']
            
            messages.append(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")
            print(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

            api.submit_order(
            side= "buy",
                symbol= symbol,
                type= "limit",
                qty= "100",
                time_in_force= "day",
                order_class= "bracket",
                limit_price= limit_price,
                take_profit= dict(
                    limit_price= limit_price + opening_range + 0.01, #inserted the + 0.01 due to error
                ),
                stop_loss=dict(
                    stop_price= limit_price - opening_range - 0.011, #inserted the - 0.011 due to error 

                ) 
            )
        else:
            print(f"Already an order for {symbol}, skipping")

print(messages)


with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
    email_message += "\n\n".join(messages)

    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_SMS, email_message)

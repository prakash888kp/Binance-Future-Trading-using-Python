import ccxt
import pandas as pd
import time

# Set up the Binance API
api_key = "n1kytIim3quQOzxH0g2eSBDzaLRwD0GuHdVovsxeK6r7w7iZxyW05RN5gQhev82s"
secret_key = "CGbRVxr6HcVt6X6helZrrxRhSmW9x3iITKyr8NyRwrnyvFTAjBHN5oLlEUGppJ5f"
symbol = 'DOT/USDT'  # Replace with your desired trading pair
timeframe = '30m'    # Replace with your desired timeframe
stop_loss_percent = 1   # Adjust as per your risk tolerance
allocation_percentage = 0.25   # Percentage of balance to allocate for trades
excel_file = 'trades.xlsx'  # Replace with the desired file name

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {
        'defaultType': 'future',  # Set the default market type to Futures
    }
})

# Create an empty DataFrame to store trade data
trade_data = pd.DataFrame(columns=['Timestamp', 'Action', 'Quantity', 'Price', 'Profit(%)'])

# Define your trading strategy
def execute_strategy():
    # Get historical OHLCV data
    # Get historical OHLCV data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)

    # Perform your technical analysis or use indicators
    # to determine buy or sell signals

    # Implement your trading logic
    # Example: Buy when the price crosses above the moving average
    if ohlcv[-1][4] > ohlcv[-2][4] and ohlcv[-2][4] < ohlcv[-3][4]:
        print("Buy signal")
        # Calculate the stop loss price
        stop_loss_price = ohlcv[-1][4] * (1 - stop_loss_percent / 100)

        # Check account balance
        balance = exchange.fetch_balance()
        usdt_balance = balance['total']['USDT']
        quantity = usdt_balance * allocation_percentage / ohlcv[-1][4]

       # Calculate the adjusted quantity to meet the minimum notional value
        min_notional = exchange.markets[symbol]['limits']['cost']['min']
        min_notional_qty = min_notional / ohlcv[-1][4]
        adjusted_quantity = max(min_notional_qty, quantity)

        print("Min Notional:", min_notional)
        print("Min Notional Quantity:", min_notional_qty)
        print("Adjusted Quantity:", adjusted_quantity)

        if usdt_balance >= adjusted_quantity:
            # Place a market buy order
            response = exchange.create_market_order(symbol, 'buy', adjusted_quantity)
            print(response)

            # Store trade data
            trade_data.loc[len(trade_data)] = [pd.Timestamp.now(), 'Buy', quantity, ohlcv[-1][4], '-']
        else:
            print("Insufficient USDT balance to place the order")
    # Example: Sell when the price crosses below the moving average
    elif ohlcv[-1][4] < ohlcv[-2][4] and ohlcv[-2][4] > ohlcv[-3][4]:
        print("Sell signal")
        # Check account balance
        balance = exchange.fetch_balance()
        btc_balance = balance['total']['BTC']
        quantity = btc_balance * allocation_percentage

        if btc_balance >= quantity:
            # Place a market sell order
            #response = exchange.create_market_sell_order(symbol, quantity=quantity)
            response = exchange.create_market_order(symbol, 'sell', quantity)
            print(response)

            # Calculate and store trade profit percentage
            buy_price = trade_data.loc[trade_data['Action'] == 'Buy', 'Price'].values[-1]
            profit_percent = (ohlcv[-1][4] - buy_price) / buy_price * 100
            trade_data.loc[len(trade_data)] = [pd.Timestamp.now(), 'Sell', quantity, ohlcv[-1][4], profit_percent]
        else:
            print("Insufficient BTC balance to place the order")

    # Save trade data to Excel file
    trade_data.to_excel(excel_file, index=False)
# Run the trading strategy continuously
while True:
    execute_strategy()
    time.sleep(60) # Adjust the sleep interval as needed (in seconds)
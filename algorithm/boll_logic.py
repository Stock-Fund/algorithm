# boll逻辑 todo
import pandas as pd


def calculate_bollinger_bands(data, window_size, num_std):
    df = pd.DataFrame(data, columns=["Close"])
    df["MA"] = df["Close"].rolling(window=window_size).mean()
    df["std"] = df["Close"].rolling(window=window_size).std()
    df["UpperBand"] = df["MA"] + num_std * df["std"]
    df["LowerBand"] = df["MA"] - num_std * df["std"]
    return df[["Close", "MA", "UpperBand", "LowerBand"]]


# 股票价格数据示例
stock_prices = [10, 12, 14, 15, 14, 16, 18, 17, 20, 19, 18, 20, 22, 21, 19, 18]

# Bollinger Bands参数
window_size = 5
num_std = 2

# 计算Bollinger Bands
bollinger_bands = calculate_bollinger_bands(stock_prices, window_size, num_std)

# 打印每个时间点的收盘价、移动平均线、上轨和下轨
for i, row in bollinger_bands.iterrows():
    print(
        f"Time {i+1}: Close = {row['Close']}, MA = {row['MA']}, Upper Band = {row['UpperBand']}, Lower Band = {row['LowerBand']}"
    )

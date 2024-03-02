import numpy as np
import algorithm.fitting as fitting
import talib as ta

# 长线逻辑(趋势逻辑)


# 检查收盘价是否靠近某条均线
# 短期看5，10，20
# 长期看30，40，60等
def check_close_near_ma(stock, day, threshold=1.0):
    if not stock.CloseValues.any():
        prices_array = np.array(stock.CloseValues, dtype=np.double)
    ma = sum(prices_array[-day:]) / day
    if abs(stock.CloseValues[-1] - ma) <= threshold:
        return True
    return False


# 主升浪逻辑
def MainSL(stock):
    mainBoo = False
    # 1-N作为x轴的数值
    closeDays = len(stock.CloseValues) + 1
    days = np.arange(1, closeDays).reshape(-1, 1)
    # 收盘价 趋势连续上涨。价格形成一系列超过坚振位的高点和低点,形成上扬趋势。
    slope = fitting.simple_fit(days, stock.CloseValues)
    # 简单判断，当60日收盘价拟合斜率为正，表示60日收盘价处于上涨趋势，可以简单的算作主升浪情况
    # 日K线斜率在0.001~0.005之间。这个范围内表示股价走势呈现出小幅上涨趋势。
    # 日K线斜率在0.005~0.01之间。此时股价走势属于中等上涨趋势。
    # 日K线斜率在0.01以上。这种斜率代表股价处于明显的强劲上涨趋势中。
    mainBoo = True if slope > 0 else False
    # 均线上行。成交量均线、动量指标等有力指标呈现上升趋势MA(C,5)>MA(C,10) AND MA(C,10)>MA(C,20) AND MA(C,20)>MA(C,N) AND MA(C,N)>MA(C,120) AND MA(C,120)>REF(MA(C,120),1) AND MA(C,5)>REF(MA(C,5),1);
    MA5Len = len(stock.MA5s) + 1
    slopeMA5 = fitting.simple_fit(MA5Len, stock.MA5s)
    MA10Len = len(stock.MA10s) + 1
    slopeMA10 = fitting.simple_fit(MA10Len, stock.MA10s)
    MA20Len = len(stock.MA20s) + 1
    slopeMA20 = fitting.simple_fit(MA20Len, stock.MA20s)
    MA30Len = len(stock.MA30s) + 1
    slopeMA30 = fitting.simple_fit(MA30Len, stock.MA30s)
    MA60Len = len(stock.MA60s) + 1
    slopeMA60 = fitting.simple_fit(MA60Len, stock.MA60s)
    MA120Len = len(stock.MA120s) + 1
    slopeMA120 = fitting.simple_fit(MA120Len, stock.MA120s)
    mainBoo = (
        True
        if slopeMA5 > slopeMA10
        and slopeMA10 > slopeMA20
        and slopeMA20 > slopeMA30
        and slopeMA30 > slopeMA60
        and slopeMA60 > slopeMA120
        else False
    )
    # 如果在5日、10日、30日和60日的斜率中，大部分都处于0.03到-0.03之间，这可以是一个指示该股票在这段时间内处于横盘状态的迹象。斜率接近于零表示价格变化相对平稳，没有明显的上升或下降趋势。
    # 然而，为了更准确地判断股票是否处于横盘状态，建议综合考虑其他因素，包括但不限于以下几点：
    # 考虑价格走势图：观察价格走势图中是否存在明显的价格区间，价格在这个区间内波动，并且没有持续的上升或下降趋势。
    # 考虑成交量变化：观察成交量是否在这段时间内保持相对稳定，没有明显的大幅增加或减少。
    # 考虑支撑和阻力位：观察价格是否在特定的支撑位和阻力位之间来回波动，没有突破这些关键价格水平。
    # 考虑市场整体趋势：了解市场整体的走势，如果整个市场也处于横盘状态，那么该股票处于横盘的可能性较高。
    # todo 横盘判断
    # todo 判断低位集中收购

    # todo 判断新高突破
    # todo 指标穿线支持。如动量指标金叉死叉等技术信号表明趋势有望继续

    return mainBoo


# 获取给定日期长度的收盘价均值
def get_MA(stock, day):
    return np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=day), nan=0)


# 计算收盘的均值
def calculateCloseMA(stock):
    stock.close_prices_array = np.array(stock.CloseValues, dtype=np.double)
    # 计算MACD
    stock.macd = ta.MACD(
        stock.close_prices_array, fastperiod=12, slowperiod=26, signalperiod=9
    )

    # 将数据中NAN替换为0，原因是不让数据的数量失真
    stock.MA5 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=5), nan=0)
    stock.MA10 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=10), nan=0)
    stock.MA20 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=20), nan=0)
    stock.MA30 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=30), nan=0)
    stock.MA40 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=40), nan=0)
    stock.MA60 = np.nan_to_num(ta.SMA(stock.close_prices_array, timeperiod=60), nan=0)
    stock.close_price_max = np.nanmax(stock.close_prices_array)
    stock.close_price_min = np.nanmin(stock.close_prices_array)


def calculateWeekMA(stock):
    stock.MA_5W = stock.Week_series.rolling(window=5).mean()
    stock.MA_10W = stock.Week_series.rolling(window=10).mean()
    stock.MA_20W = stock.Week_series.rolling(window=20).mean()
    stock.MA_30W = stock.Week_series.rolling(window=30).mean()


def calculateMouthMA(stock):
    stock.MA_5M = stock.Mouth_series.rolling(window=5).mean()
    stock.MA_10M = stock.Mouth_series.rolling(window=10).mean()
    stock.MA_20M = stock.Mouth_series.rolling(window=20).mean()
    stock.MA_30M = stock.Mouth_series.rolling(window=30).mean()


# 计算成交量的均值
def calculateVolumesMA(stock):
    stock.volumes_array = np.array(stock.Volumes, dtype=np.double)
    stock.volumeMA5 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=5), nan=0)
    stock.volumeMA10 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=10), nan=0)
    stock.volumeMA20 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=20), nan=0)
    stock.volumeMA30 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=30), nan=0)
    stock.volumeMA40 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=40), nan=0)
    stock.volumeMA60 = np.nan_to_num(ta.SMA(stock.volumes_array, timeperiod=60), nan=0)
    stock.volume_max = np.nanmax(stock.volumes_array)
    stock.volume_min = np.nanmin(stock.volumes_array)


# 判断趋势的逻辑
def detect_trend(stock):
    ma5 = stock.MA5[-1]
    ma10 = stock.MA10[-1]
    ma20 = stock.MA20[-1]
    ma30 = stock.MA30[-1]
    ma40 = stock.MA40[-1]
    ma60 = stock.MA60[-1]
    trend = []
    if ma5 > ma10 and ma10 > ma20 and ma20 > ma30 and ma30 > ma40 and ma40 > ma60:
        trend.append("长期多头排列")
    elif ma5 < ma10 and ma10 < ma20 and ma20 < ma30 and ma30 < ma40 and ma40 < ma60:
        trend.append("长期空头排列")
    else:
        if ma5 > ma10 and ma10 > ma20 and ma20 > ma30:
            trend.append("短期多头排列")
        elif ma5 < ma10 and ma10 < ma20 and ma20 < ma30:
            trend.append("短期空头排列")
        else:
            trend.append("震荡")
    return trend


# 判断对应均线一定日期内的趋势
def check_moving_average_trend(stock, type, time, range=10):
    if type == "Day":
        MAS = stock.MA5
        if time == 5:
            MAS = stock.MA5
        elif time == 10:
            MAS = stock.MA10
        elif time == 20:
            MAS = stock.MA20
        elif time == 30:
            MAS = stock.MA30
        elif time == 60:
            MAS = stock.MA60
    elif type == "Week":
        MAS = stock.MA_5W
        if time == 5:
            MAS = stock.MA_5W
        elif time == 10:
            MAS = stock.MA_10W
        elif time == 20:
            MAS = stock.MA_20W
        elif time == 30:
            MAS = stock.MA_30W
        elif time == 60:
            MAS = stock.MA_60W
    elif type == "Month":
        MAS = stock.MA_5M
        if time == 5:
            MAS = stock.MA_5M
        elif time == 10:
            MAS = stock.MA_10M
        elif time == 20:
            MAS = stock.MA_20M
        elif time == 30:
            MAS = stock.MA_30M
        elif time == 60:
            MAS = stock.MA_60M
    MAS = MAS[-range:]
    # 计算均线
    window_size = 30  # 指定日期范围
    # 找到最低点
    lowest_index = np.argmin(MAS)
    lowest_date = lowest_index + window_size  # 对应的日期是窗口期加上最低点的索引
    lowest_price = MAS[lowest_date]
    current_price = MAS[-1]
    # 当前价位与最低价位的比较，如果当前价位大于等于最低价位返回True，反之返回False
    return current_price >= lowest_price
    # print("最低点日期：", lowest_date, "最低点收盘价：", lowest_price)


# 判断均线是否粘合
def check_moving_average_convergence(stock, type, range=10):
    if type == "Day":
        MA10 = stock.MA10
        MA20 = stock.MA20
        MA30 = stock.MA30
        MA60 = stock.MA60
    elif type == "Week":
        MA10 = stock.MA_10W
        MA20 = stock.MA_20W
        MA30 = stock.MA_30W
        MA60 = stock.MA_60W
    elif type == "Month":
        MA10 = stock.MA_10M
        MA20 = stock.MA_20M
        MA30 = stock.MA_30M
        MA60 = stock.MA_60M

    tolerance = 0.05  # 定义容差范围

    diff_avg = (
        abs(MA10[-range:] - MA20[-range:])
        + abs(MA20[-range:] - MA30[-range:])
        + abs(MA30[-range:] - MA60[-range:])
    ) / 3

    if diff_avg <= tolerance:
        print("均线粘合")
        return True
    else:
        print("均线不粘合")
        return False


# 周线级别金叉,股价进入上升通道
def check_ma_crossing(stock):
    MA10 = stock.MA_10W
    MA30 = stock.MA_30W

    if MA10[-1] > MA30[-1] and MA10[-2] <= MA30[-2]:
        print("10周均线上穿30周均线")
        return True
    else:
        print("10周均线未上穿30周均线")
        return False


# 破位逻辑
def checkBroken(stock):
    closeValue = stock.CloseValues[-1]
    if closeValue < stock.MA5:
        print("破5日线")
    if closeValue < stock.MA10:
        print("破10日线")
    if closeValue < stock.MA20:
        print("破20日线")
    if closeValue < stock.MA30:
        print("破30日线")
    if closeValue < stock.MA60:
        print("破60日线")


# 5日短线逻辑
def checkMA5(stock):
    closeValue = stock.CloseValues[-1]
    maValue = stock.MA5[-1]
    if closeValue > maValue:
        # print("5日线上穿")
        return True
    else:
        # print("5日线下穿")
        return False


# 20日生命线逻辑
def checkMA20(stock):
    closeValue = stock.CloseValues[-1]
    maValue = stock.MA20[-1]
    if closeValue > maValue:
        # print("20日线上穿")
        return True
    else:
        # print("20日线下穿")
        return False


# 检测收盘价是否上穿/下穿某均线
def checkMA(stock, day):
    closeValue = stock.CloseValues[-1]
    ma = stock.MA5[-1]
    if day == 5:
        ma = stock.MA5[-1]
    elif day == 10:
        ma = stock.MA10[-1]
    elif day == 20:
        ma = stock.MA20[-1]
    elif day == 30:
        ma = stock.MA30[-1]
    elif day == 40:
        ma = stock.MA40[-1]
    elif day == 60:
        ma = stock.MA60[-1]
    return closeValue > ma


# 检测月线是否为红通道
def CheckMouth(stock):
    # todo 月线收盘价
    return False


# 检测周线是否为红通道
def CheckWeek(stock):
    return False


# 上一个交易日是否是跌势
def IsFallYesterday(stock):
    value = stock.CloseValues[-2]
    open = stock.OpenValues[-2]
    return value < open


# 当前交易日是否是跌势
def IsFallToday(stock):
    value = stock.CloseValues[-1]
    open = stock.OpenValues[-1]
    return value < open


# 计算价格和均线值之间的距离
def calculate_distance_from_sma(price, sma):
    distance = abs(price - sma)
    return distance


# N日乖离率计算
# 在弱势市场环境下，当乖离率达到5以上表示超买，反之达到-5以上表示超卖
# 在强势市场环境下，当乖离率达到10以上表示超买，反之达到-10以上表示超卖
# 一般以20日均线为基准，较为准确
def calculate_bias(stock, day=20):
    close = stock.CloseValues[-1]
    if day == 5:
        sma = stock.MA5[-1]
    elif day == 10:
        sma = stock.MA10[-1]
    elif day == 20:
        sma = stock.MA20[-1]
    elif day == 30:
        sma = stock.MA30[-1]
    elif day == 40:
        sma = stock.MA40[-1]
    elif day == 60:
        sma = stock.MA60[-1]
    bias = (close - sma) / sma * 100
    name = stock.Name
    print(f"{name}的{day}日乖离率为:{bias}")
    return bias


def CheckWeekTrend(stock):
    return stock.MA_5W > stock.MA_30W


def CheckMonthTrend(stock):
    return stock.MA_5M > stock.MA_30M

import numpy as np
import algorithm.fitting as fitting
import talib as ta
import statistics


class Stock:
    # 计算移动平均函数
    def moving_average(data, window):
        weights = np.repeat(1.0, window) / window
        ma = np.convolve(data, weights, "valid")
        return ma

    def CalculateAverage(self, num):
        # nums = self.CloseValues
        return self.moving_average(self.CloseValues, num)

    # 上一个交易日是否是跌势
    def IsFallYesterday(self):
        value = self.CloseValues[1]
        open = self.OpenValues[1]
        return value < open

    # 当前交易日是否是跌势
    def IsFallToday(self):
        value = self.CloseValues[0]
        open = self.OpenValues[0]
        return value < open

    # 预测明天5日线价格,可能是阶段低点
    def Calculate5_predict(self, s=1.099):
        self.predictValue = (
            self.CloseValues[0] * s
            + self.CloseValues[0]
            + self.CloseValues[1]
            + self.CloseValues[2]
            + self.CloseValues[3]
        ) / 5
        return self.predictValue

    # =========== 短线逻辑
    # 龙头低吸算法1（预测5日线买入算法）
    def CheckBuyByPredict(self):
        return self.CurrentValue < self.predictValue

    # 龙头低吸算法2（5日线-10日线检测买入算法）
    def CheckBuy(self):
        currentValue = self.CurrentValue
        # 只有连续5板以上
        # 只有在昨天下跌的情况下
        if self.IsFallYesterday():
            MA5 = self.MA5
            MA10 = self.MA10
            if currentValue > MA5:
                return False
            # 触摸5日线
            elif currentValue == MA5:
                return True
            # 击穿5日线，就以10日线为准
            elif currentValue < MA5:
                # 在5-10日线之间，没有支撑位，破位！
                if currentValue > MA10:
                    return False
                # 触摸到10日线，找到10日线
                elif currentValue == MA10:
                    return True
                # 10日线以下，放弃
                else:
                    return False

    # 卖出逻辑
    def CheckSell(self, value):
        # value 传入当前成本价
        return (
            self.CurrentValue >= value * self.TakeProfit
            or self.CurrentValue <= value * self.StopLoss
        )

    # 长线逻辑(趋势逻辑)
    # 判断趋势的逻辑
    def detect_trend(ma5, ma10, ma20):
        trend = []
        if ma5 > ma10 and ma5 > ma20:
            trend.append("上涨")
        elif ma5 < ma10 and ma5 < ma20:
            trend.append("下跌")
        else:
            trend.append("震荡")
        return trend

    # 箱体逻辑
    def checkBox(self, max, min):
        if self.CurrentValue >= max:
            return True
        elif self.CurrentValue <= min:
            return False
        else:
            return False

    # 判断市场热度
    def CheckMarketPopularity(self):
        if self.turnoverRates >= 10:
            return 1
        elif self.turnoverRates >= 1 and self.turnoverRates <= 5:
            return 0
        elif self.turnoverRates >= 0.1 and self.turnoverRates <= 1:
            return -1

    # 破位逻辑
    def checkBroken(self):
        closeValue = self.CloseValues[-1]
        if closeValue < self.MA5:
            print("破5日线")
        if closeValue < self.MA10:
            print("破10日线")
        if closeValue < self.MA20:
            print("破20日线")
        if closeValue < self.MA30:
            print("破30日线")
        if closeValue < self.MA60:
            print("破60日线")

    # 判断成交量是否超过平均量
    # 以该股票最近一个月或者三个月的日均交易量为基准平均值。
    # 如果该日交易量高于基准平均值的一定倍数(如150%或者200%),则认为该日交易量较大,是放量。
    # 如果该日交易量低于基准平均值的一定比例(如50%或者70%),则认为该日交易量较小,是缩量。
    # 如果在基准平均值和放量标准之间,则认为交易量一般,既不是明显放量也不是缩量。
    def checkVolumeIncreaseOrShrink(self):
        totalVolume = sum(self.Volumes)
        count = len(self.volumes)
        average = totalVolume / count
        # 放量
        if self.Volumes[-1] >= average * 1.5:
            return 1
        # 缩量
        elif self.Volumes[-1] <= average * 0.5:
            return -1
        # 正常量
        else:
            return 0

    # 判断某天收盘是否为红盘(收盘价高于开盘价)
    def checkRise(self, index):
        return self.CloseValues[index] > self.OpenValues[index]

    # 检测当天量能是否放量，反转 ，返回 True 放量反转 False 未放量反转
    def checkVolums_Climax_Reversal(self):
        currentVolum = self.Volumes[-1]
        preVolums = self.Volumes[:-1]
        averageVolum = sum(preVolums) / len(preVolums)
        if currentVolum > averageVolum:
            return True
        else:
            return False

    # 计算价格波动幅度
    def calculate_price_std(self, prices):
        price_std = statistics.stdev(prices)
        return price_std

    def calculate_distance_from_sma(self, price, sma):
        distance = abs(price - sma)
        return distance

    def check_closeness_to_sma(self, prices, sma_list, threshold=1.0):
        price_std = self.calculate_price_std(prices)
        close_to_sma = []

        for sma in sma_list:
            distance = self.calculate_distance_from_sma(prices[-1], sma)
            adjusted_distance = distance / price_std

        if adjusted_distance < threshold:
            close_to_sma.append(sma)

        return close_to_sma

    # 检查收盘价是否靠近均线
    def check_close_near_ma(self, threshold=1.0):
        ma_periods = [5, 10, 20, 30, 40, 60]
        days = []
        if not self.close_prices_array.any():
            self.close_prices_array = np.array(self.CloseValues, dtype=np.double)
        for periods in ma_periods:
            ma = sum(self.close_prices_array[-periods:]) / periods
            if abs(self.CloseValues[-1] - ma) <= threshold:
                days.append(periods)
        return days

    # 主升浪逻辑
    def MainSL(self):
        mainBoo = False
        # 1-N作为x轴的数值
        closeDays = len(self.CloseValues) + 1
        days = np.arange(1, closeDays).reshape(-1, 1)
        # 收盘价 趋势连续上涨。价格形成一系列超过坚振位的高点和低点,形成上扬趋势。
        slope = fitting.simple_fit(days, self.CloseValues)
        # 简单判断，当60日收盘价拟合斜率为正，表示60日收盘价处于上涨趋势，可以简单的算作主升浪情况
        # 日K线斜率在0.001~0.005之间。这个范围内表示股价走势呈现出小幅上涨趋势。
        # 日K线斜率在0.005~0.01之间。此时股价走势属于中等上涨趋势。
        # 日K线斜率在0.01以上。这种斜率代表股价处于明显的强劲上涨趋势中。
        mainBoo = True if slope > 0 else False

        # 均线上行。成交量均线、动量指标等有力指标呈现上升趋势MA(C,5)>MA(C,10) AND MA(C,10)>MA(C,20) AND MA(C,20)>MA(C,N) AND MA(C,N)>MA(C,120) AND MA(C,120)>REF(MA(C,120),1) AND MA(C,5)>REF(MA(C,5),1);
        MA5Len = len(self.MA5s) + 1
        slopeMA5 = fitting.simple_fit(MA5Len, self.MA5s)
        MA10Len = len(self.MA10s) + 1
        slopeMA10 = fitting.simple_fit(MA10Len, self.MA10s)
        MA20Len = len(self.MA20s) + 1
        slopeMA20 = fitting.simple_fit(MA20Len, self.MA20s)
        MA30Len = len(self.MA30s) + 1
        slopeMA30 = fitting.simple_fit(MA30Len, self.MA30s)
        MA60Len = len(self.MA60s) + 1
        slopeMA60 = fitting.simple_fit(MA60Len, self.MA60s)
        MA120Len = len(self.MA120s) + 1
        slopeMA120 = fitting.simple_fit(MA120Len, self.MA120s)
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

    # boll逻辑 todo

    def Update(self, value):
        self.CurrentValue = value
        return self.CheckBuyByPredict()

    #  return self.CheckBuyValue(self)

    # 计算收盘的均值
    def calculateCloseMA(self):
        self.close_prices_array = np.array(self.CloseValues, dtype=np.double)
        # 计算MACD
        self.macd = ta.MACD(
            self.close_prices_array, fastperiod=12, slowperiod=26, signalperiod=9
        )

        # 将数据中NAN替换为0，原因是不让数据的数量失真
        self.MA5 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=5), nan=0)
        self.MA10 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=10), nan=0)
        self.MA20 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=20), nan=0)
        self.MA30 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=30), nan=0)
        self.MA40 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=40), nan=0)
        self.MA60 = np.nan_to_num(ta.SMA(self.close_prices_array, timeperiod=60), nan=0)
        self.close_price_max = np.nanmax(self.close_prices_array)
        self.close_price_min = np.nanmin(self.close_prices_array)

    # 计算成交量的均值
    def calculateVolumesMA(self):
        self.volumes_array = np.array(self.Volumes, dtype=np.double)
        self.volumeMA5 = np.nan_to_num(ta.SMA(self.volumes_array, timeperiod=5), nan=0)
        self.volumeMA10 = np.nan_to_num(
            ta.SMA(self.volumes_array, timeperiod=10), nan=0
        )
        self.volumeMA20 = np.nan_to_num(
            ta.SMA(self.volumes_array, timeperiod=20), nan=0
        )
        self.volumeMA30 = np.nan_to_num(
            ta.SMA(self.volumes_array, timeperiod=30), nan=0
        )
        self.volumeMA40 = np.nan_to_num(
            ta.SMA(self.volumes_array, timeperiod=40), nan=0
        )
        self.volumeMA60 = np.nan_to_num(
            ta.SMA(self.volumes_array, timeperiod=60), nan=0
        )
        self.volume_max = np.nanmax(self.volumes_array)
        self.volume_min = np.nanmin(self.volumes_array)

    def __init__(self, data, datas):
        # N日内的收盘价格列表
        self.CloseValues = data["Close"].tolist()
        # N日内的开盘价格列表
        self.OpenValues = data["Open"].tolist()
        self.MaxValues = data["High"].tolist()
        self.MinValues = data["Low"].tolist()
        # N日内成交量
        self.Volumes = data["Volume"].tolist()

        # self.MA5 = data["Close"].rolling(window=5).mean()
        # self.MA10 = data["Close"].rolling(window=10).mean()
        # self.MA20 = data["Close"].rolling(window=20).mean()
        # self.MA30 = data["Close"].rolling(window=30).mean()
        # self.MA40 = data["Close"].rolling(window=40).mean()
        # self.MA60 = data["Close"].rolling(window=60).mean()

        self.Time = datas[0]  # 10点之前打到预测ma5直接买，下午就缓缓
        # 当前价格
        self.CurrentValue = datas[1]

        # N日内换手率
        self.turnoverRates = datas[2]

        # N日量比
        self.QuantityRatios = datas[3]

        # N日分时均价  均价=成交总额/成交量 由于分时均价频率较高，则使用   均价 = 每日收盘时的成交总额/每日收盘时的成交量
        self.AveragePrices = datas[4]

        # N内筹码集中度
        # 筹码集中度=成本区间的（高值-低值）/（高值+低值）
        self.Chipsconcentrations = datas[5]

        # 止盈卖出系数
        self.TakeProfit = 1.1
        # 止损卖出系数
        self.StopLoss = 0.97

        self.Calculate5_predict(1.099)
        self.calculateCloseMA()
        self.calculateVolumesMA()

    # 获取某个时间段内的均线值
    def get_MA(self, time):
        return ta.SMA(self.close_prices_array, timeperiod=time)

    def get_MACD(self):
        return ta.MACD(self.close_prices_array)

    def get_slope(self, time):
        if time == 5:
            MANS = self.MA5
        elif time == 10:
            MANS = self.MA10
        elif time == 20:
            MANS = self.MA20
        elif time == 30:
            MANS = self.MA30
        elif time == 40:
            MANS = self.MA40
        elif time == 60:
            MANS = self.MA60
        daylen = len(MANS) + 1
        days = np.arange(1, daylen).reshape(-1, 1)
        return fitting.simple_fit(days, MANS)

    @property
    def get_CurrentValue(self):
        return self.CurrentValue

    @get_CurrentValue.setter
    def get_CurrentValue(self, value):
        self.CurrentValue = value

    @property
    def get_turnoverRates(self):
        return self.turnoverRates

    @get_turnoverRates.setter
    def get_turnoverRates(self, value):
        self.turnoverRates = value

    @property
    def get_QuantityRatios(self):
        return self.QuantityRatios

    @get_QuantityRatios.setter
    def get_QuantityRatios(self, value):
        self.QuantityRatios = value

    @property
    def get_AveragePrices(self):
        return self.AveragePrices

    @get_AveragePrices.setter
    def get_AveragePrices(self, value):
        self.AveragePrices = value

    @property
    def get_Chipsconcentrations(self):
        return self.Chipsconcentrations

    @get_Chipsconcentrations.setter
    def get_QuantityRatios(self, value):
        self.Chipsconcentrations = value

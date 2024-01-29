import numpy as np
import algorithm.fitting as fitting
import algorithm.ma_logic as ma
import algorithm.predict_logic as predict
import algorithm.box_logic as box
import algorithm.volum_logic as volum
import talib as ta


class Stock:
    # 判断某天收盘是否为红盘(收盘价高于开盘价)
    def checkRise(self, index):
        return self.CloseValues[index] > self.OpenValues[index]

    # def Update(self, value):
    #     self.CurrentValue = value
    #     return self.CheckBuyByPredict()

    def __init__(self, data, datas):
        # N日内的收盘价格列表
        self.CloseValues = data["Close"].tolist()
        # N日内的开盘价格列表
        self.OpenValues = data["Open"].tolist()
        self.MaxValues = data["High"].tolist()
        self.MinValues = data["Low"].tolist()
        # N日内成交量
        self.Volumes = data["Volume"].tolist()

        # 股票数据记录时间范围
        self.Date = data["Date"].tolist

        self.close_prices_array = np.array(self.CloseValues, dtype=np.double)

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
        # 股票代码
        self.StockNum = datas[6]
        # 股票名字
        self.Name = datas[7]

        # 止盈卖出系数
        self.TakeProfit = 1.1
        # 止损卖出系数
        self.StopLoss = 0.97

        predict.Calculate5_predict(self, 1.099)
        ma.calculateCloseMA(self)
        ma.calculateVolumesMA(self)

    def checkMA(self, day):
        return ma.checkMA(self, day)

    def checkMA5(self, day):
        return ma.checkMA5(self, day)

    def checkMA20(self):
        return ma.checkMA20(self)

    # 是否超过平均量 ===> 放量
    def checkReversalVolums(self):
        return volum.checkAverageVolums_Climax_Reversal(self)

    # 是否超过前一天的量能 ===> 反包
    def checkVolumClimaxReversal(self):
        return volum.checkVolum_Climax_Reversal(self)

    def checkbias(self, day):
        return ma.calculate_bias(self, day)

    # 获取指定股票的某段时间内的成交量净值,主力是否在该股票中持有
    def checkNetVolumes(self, days):
        return volum.check_net_volume(self, days)

    # 获取某个时间段内的均线值
    def get_MA(self, time):
        return ta.SMA(self.close_prices_array, timeperiod=time)

    # 获取某个时间段内的macd数据
    """
        talib官方默认参数 fastperiod=12, slowperiod=26,signalperiod=9
        参数:
           fastperiod:快线【短周期均线】
           slowperiod:慢线【长周期均线】
           signalperiod:计算signalperiod天的macd的EMA均线【默认是9,无需更改】
        返回参数：
           macd【DIF】 = 12【fastperiod】天EMA - 26【slowperiod】天EMA
           macdsignal【DEA或DEM】 = 计算macd的signalperiod天的EMA
           macdhist【MACD柱状线】 = macd - macdsignal
        对照表：
              TA-lib的macd函数计算macd值，函数输出3个值，
              macd（对应diff）
              macdsignal（对应dea）
              macdhist（对应macd）
              然后按照下面的原则判断买入还是卖出。
              1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。
              2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
              3.DEA线与K线发生背离，行情反转信号。
              4.分析MACD柱状线，由正变负，卖出信号；由负变正，买入信号。
    """

    def get_MACD(self, fastTime=12, slowTime=26, signalperiod=9):
        return np.nan_to_num(
            ta.MACD(
                self.close_prices_array,
                fastperiod=fastTime,
                slowperiod=slowTime,
                signalperiod=signalperiod,
            ),
            nan=0,
        )

    # 获取某个时间段内的macd的上涨区间
    def get_MACD_Rise_Fall_Range(self, fastTime=12, slowTime=26, signalperiod=9):
        macd_hist = np.nan_to_num(
            ta.MACD(
                self.close_prices_array,
                fastperiod=fastTime,
                slowperiod=slowTime,
                signalperiod=signalperiod,
            ),
            nan=0,
        )
        # 找到日MACD的上涨区间和下降区间
        daily_ranges = []
        current_range_start = None

        for i in range(len(macd_hist)):
            if macd_hist[i] > 0:
                if current_range_start is None:
                    current_range_start = i
            else:
                if current_range_start is not None:
                    daily_ranges.append((current_range_start, i - 1))
                    current_range_start = None

        if current_range_start is not None:
            daily_ranges.append((current_range_start, len(macd_hist) - 1))
        return daily_ranges

    def get_slope(self):
        daylen = len(self.close_prices_array) + 1
        days = np.arange(1, daylen).reshape(-1, 1)
        return fitting.simple_fit(days, self.close_prices_array)

    def get_MA_slope(self, time):
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

    # 判断股票是否存在反转信号
    def get_whether_reverse(self, time):
        if self.checkReversalVolums():
            # 检测当前日是否反包
            return self.checkReversalVolums()
        else:
            return False

    # 成交量复合判断逻辑
    def get_final_result(self, time):
        # 斜率为正表示MA趋势向上
        if self.get_MA_slope(time) > 0:
            # 斜率为正表示收盘价趋势向上
            if self.get_slope() > 0:
                # 检测当前日是否放量
                if self.checkReversalVolums():
                    # 检测当前日是否反包
                    if self.checkReversalVolums():
                        # 检查股票检查时间段内成交量是否为正，主力是否还在潜伏
                        return self.checkNetVolumes(0) > 0
        else:
            return False

    def checkbiasoffset(self, day):
        bias_offset = 0.03
        if day == 5:
            bias_offset = 0.02
        elif day == 10:
            bias_offset = 0.02
        elif day == 20:
            bias_offset = 0.03
        elif day == 30:
            bias_offset = 0.03
        elif day == 40:
            bias_offset = 0.05
        elif day == 60:
            bias_offset = 0.05
        elif day == 120:
            bias_offset = 0.05
        return bias_offset

    # 乖离率距离均线逻辑，一般以20日生命线为中期基准
    # 5日，10日乖离率远离5日均线±2%范围内表示短期偏离正常，反之就有较大偏离需要注意离场
    # 20日，30日乖离率远离5日均线±3%范围内表示短期偏离正常，反之就有较大偏离需要注意离场
    # 40日，60日，120日乖离率远离5日均线±5%范围内表示短期偏离正常，反之就有较大偏离需要注意离场
    def get_bias_result(self, day=20):
        bias_offset = self.checkbiasoffset(day)
        bias = ma.calculate_bias(self, day)
        if abs(bias) > bias_offset:
            return False
        else:
            return True

    # 获取某个时间点超买，超卖状态
    # -1 表示超买 ； 1 表示超卖 ； 0 表示在震荡区间内
    def get_over_trade(self, day=20):
        bias_offset = self.checkbias(day)
        bias = ma.calculate_bias(self, day)
        if abs(bias) > bias_offset:
            if bias > 0:
                return -1
            else:
                return 1
        else:
            return 0

    def getMA(self, day):
        if day == 5:
            return self.MA5
        elif day == 10:
            return self.MA10
        elif day == 20:
            return self.MA20
        elif day == 30:
            return self.MA30
        elif day == 60:
            return self.MA60
        elif day == 120:
            return self.MA120

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
    def get_Chipsconcentrations(self, value):
        self.Chipsconcentrations = value

    @property
    def get_Name(self):
        return self.Name

    @get_Name.setter
    def get_Name(self, value):
        self.Name = value

    @property
    def get_Close_Values(self):
        return self.close_prices_array

    @get_Close_Values.setter
    def get_Close_Values(self, value):
        self.close_prices_array = value

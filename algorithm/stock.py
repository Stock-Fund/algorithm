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

    # 获取指定股票的某段时间内的成交量净值
    def checkNetVolumes(self, days):
        return volum.check_net_volume(self, days)

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

    def get_final_result(self, time):
        # 斜率为正表示趋势向上
        if self.get_slope(self, time) > 0:
            # 检测当前日是否放量
            if self.checkReversalVolums():
                # 检测当前日是否反包
                return self.checkReversalVolums()
        else:
            return False

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

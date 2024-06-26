import numpy as np
import algorithm.fitting as fitting
import algorithm.ma_logic as ma
import algorithm.predict_logic as predict
import algorithm.box_logic as box
import algorithm.volum_logic as volum
import algorithm.chips_logic as chips
import algorithm.line_regression as line_regression
import talib as ta
import pandas as pd


class Stock:
    # 判断某天收盘是否为红盘(收盘价高于开盘价)
    def checkRise(self, index):
        return self.CloseValues[index] > self.OpenValues[index]

    # def Update(self, value):
    #     self.CurrentValue = value
    #     return self.CheckBuyByPredict()

    def __init__(self, data, datas):
        self.dataFrame = data
        # N日内的收盘价格列表
        self.CloseValues = data.loc[0:, "Close"].tolist()
        # N日内的开盘价格列表
        self.OpenValues = data.loc[0:, "Open"].tolist()
        self.MaxValues = data.loc[0:, "High"].tolist()
        self.MinValues = data.loc[0:, "Low"].tolist()
        # N日内成交量
        self.Volumes = data.loc[0:, "Volume"].tolist()
        print(f"{self.Volumes}")
        # N日内不复权收盘价
        self.adjCloses = data.loc[0:, "Adj Close"].tolist()
        # 股票数据记录时间范围
        self.Date = data.loc[0, "Date"]

        # 收盘价变化量
        self.ClosePrices_change = data.loc[0:, "Close"].diff()
        # 成交量变化量
        self.Volumes_change = data.loc[0:"Volume"].diff()
        # 将Date列转换为日期时间类型
        data["Date"] = pd.to_datetime(data["Date"])
        # 将Date列设置为索引
        data.set_index("Date", inplace=True)
        # 对数据进行周重采样，并选择每周的最后一个值作为聚合方式
        self.WeekData = data.resample("W").agg(
            {
                "Open": "last",
                "High": "last",
                "Low": "last",
                "Close": "last",
                "Adj Close": "last",
                "Volume": "last",
            }
        )

        self.WeekClose = self.WeekData["Close"].values
        self.week_close_prices_array = np.array(self.WeekClose, dtype=np.double)

        # 月级别数据
        self.MouthData = data.resample("M").agg(
            {
                "Open": "last",
                "High": "last",
                "Low": "last",
                "Close": "last",
                "Adj Close": "last",
                "Volume": "last",
            }
        )
        self.MouthClose = self.MouthData["Close"].values
        self.mouth_close_prices_array = np.array(self.MouthClose, dtype=np.double)

        self.close_prices_array = np.array(self.CloseValues, dtype=np.double)
        self.open_prices_array = np.array(self.OpenValues, dtype=np.double)
        self.high_prices_array = np.array(self.MaxValues, dtype=np.double)
        self.low_prices_array = np.array(self.MinValues, dtype=np.double)
        self.volumes_array = np.array(self.Volumes, dtype=np.double)
        self.Time = datas[0]  # 10点之前打到预测ma5直接买，下午就缓缓

        self.stockTimeData = datas[1]
        # 当前价格
        self.CurrentValue = self.stockTimeData[0]

        # 当日分时均价  均价=成交总额/成交量 由于分时均价频率较高，则使用   均价 = 每日收盘时的成交总额/每日收盘时的成交量
        self.AveragePrices = self.stockTimeData[1]

        # 当日内换手率
        self.turnoverRates = self.stockTimeData[6]

        # 当日日量比
        self.QuantityRatios = self.stockTimeData[7]

        # 当日开盘价
        self.OpenValue = self.stockTimeData[10]
        # 当日外盘
        plat_value = 10000
        self.outer_plat = self.stockTimeData[14]
        if self.outer_plat.endswith("万"):
            self.outer_plat = round(
                float(self.outer_plat.replace("万", "")) * plat_value, 2
            )
        else:
            self.outer_plat = round(float(self.outer_plat), 2)
        # 当日内盘
        self.inner_plat = self.stockTimeData[15]
        if self.inner_plat.endswith("万"):
            self.inner_plat = round(
                float(self.inner_plat.replace("万", "")) * plat_value, 2
            )
        else:
            self.inner_plat = round(float(self.inner_plat), 2)

        # 历史资金流入流出情况
        self.in_out_flow = datas[2]

        # N内筹码集中度
        # 90筹码集中度
        self.Chips90concentrations = datas[3]
        # 90筹码成本 eg:“10_20”
        self.Chips90Prices = datas[4]
        # 筹码获利比例
        self.Profitratios = datas[5]
        # 筹码均价
        self.ChipAveragePrices = datas[6]
        # 股票代码
        self.StockNum = datas[7]
        # 股票名字
        self.Name = datas[8]

        # 止盈卖出系数
        self.TakeProfit = 1.1
        # 止损卖出系数
        self.StopLoss = 0.97

        predict.Calculate5_predict(self, 1.099)
        ma.calculateCloseMA(self)
        ma.calculateWeekMA(self)
        ma.calculateMouthMA(self)
        ma.calculateVolumesMA(self)

    # ==================== 上下影线逻辑
    # 判断N日内股价在一定幅度内震动，且出现多个上影线，主力可能存在试盘操作
    def multiple_upper_shadows_when_daily_fluctuation_stable(
        self,
        n_days=5,  # 一般默认为5天，短期侧罗
        percent_threshold=5,  # 默认5%的幅度
        upper_Offset=0.1,  # 判断上影线为默认10%的幅度的差距
        shadows_needed=3,
    ):
        # 首先判断N日内每日收盘价与前一天收盘价的浮动幅度是否小于5%
        # 反转数据
        reverse_close_prices_array = self.close_prices_array[::-1]
        reverse_high_prices_array = self.high_prices_array[::-1]
        reverse_open_prices_array = self.open_prices_array[::-1]
        for i in range(1, n_days):
            if (
                abs(
                    (reverse_close_prices_array[i] - reverse_close_prices_array[i - 1])
                    / reverse_close_prices_array[i - 1]
                )
                > percent_threshold / 100
            ):
                return False  # 如果某日收盘价与前一天收盘价的浮动幅度超过阈值则直接返回False

        # 然后计算在价格稳定的情况下，n日内的上影线数量
        upper_shadows = 0
        for i in range(n_days):
            upper_shadow = reverse_high_prices_array[i] - max(
                reverse_open_prices_array[i], reverse_close_prices_array[i]
            )
            if upper_shadow > upper_Offset:
                upper_shadows += 1

        # 如果上影线的数量达到要求,则返回True，否则返回False
        if upper_shadows >= shadows_needed:
            return True
        else:
            return False

    # 判断是否有下影线
    def has_lower_shadow(self):
        # 如果收盘价大于等于开盘价（阳线），则下影线为开盘价减最低价
        # 如果收盘价小于开盘价（阴线），则下影线为收盘价减最低价
        lower_shadow = (
            min(self.open_prices_array[-1], self.close_prices_array[-1])
            - self.low_prices_array[-1]
        )

        # 确定是否有下影线，这里我们可以定一个阈值，如0.01，防止价格差过小误判为有影线
        if lower_shadow > 0.01:
            return True  # 如果有下影线，返回True
        else:
            return False  # 如果没有下影线，返回False

    # ===================== 均线逻辑
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

    # 获取某个时间段内的均线值
    def get_MA(self, time):
        return ta.SMA(self.close_prices_array, timeperiod=time)

    def checkMA(self, day):
        return ma.checkMA(self, day)

    def checkMA5(self, day):
        return ma.checkMA5(self, day)

    def checkMA20(self):
        return ma.checkMA20(self)

    # 检测超买超卖
    def CheckDayOverBuy(self, maxPrice, minPrice, day=0):
        return ma.CheckDayOverBuy(self, maxPrice, minPrice, day)

    def CheckWeekOverBuy(self, maxPrice, minPrice, day=0):
        return ma.CheckWeekOverBuy(self, maxPrice, minPrice, day)

    def CheckMouthOverBuy(self, maxPrice, minPrice, day=0):
        return ma.CheckMouthOverBuy(self, maxPrice, minPrice, day)

    # 计算对应均线在一定时间跨度内的趋势
    def checkMovingAverageTrend(self, type, day, range=10):
        return ma.check_moving_average_trend(self, type, day, range)

    # 计算对应均线是否存在均线粘合
    def checkMovingAverageConvergence(self, type, range=10):
        return ma.check_moving_average_convergence(self, type, range)

    def checkbias(self, day):
        return ma.calculate_bias(self, day)

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

    # 短期5日线情绪 上穿则短期情绪高涨
    def get_short_result(self):
        return self.checkMA5(self)

    # 股票周线级别买入逻辑
    def StockBuy(self):
        # 股价进入上升通道
        if ma.check_ma_crossing(self):
            # 股票的周线是否存在粘合状态
            return self.checkMovingAverageConvergence(self, "Week", 20)
        return False

    # 股票日线级别买入逻辑
    def StockBuy_short(self):
        return ma.calculateDayMABuy(self)

    # 股票日线级别卖出逻辑
    def StockSell_short(self):
        return ma.calculateDayMASell(self)

    # ===================== 成交量逻辑
    # 是否超过平均量 ===> 放量
    def checkReversalVolums(self):
        return volum.checkVolumeIncreaseOrShrink(self)
    
    # 判断是否存在主力进场逻辑
    def checkDetermineEntryExit(self):
        return volum.determine_entry_exit(self.dataFrame)

    # 是否超过前一天的量能 ===> 反包
    def checkVolumClimaxReversal(self):
        return volum.checkVolum_Climax_Reversal(self)

    # 检查成就量和股价变化对于后市的股价走势的判断
    def checkVolumLogic(self):
        return volum.check_volum_logic(self)

    # 获取指定股票的某段时间内的成交量净值,主力是否在该股票中持有
    def checkNetVolumes(self, days):
        return volum.check_net_volume(self, days)

    # 检测指定股票某段时间内的资金流入流出情况 默认1天
    def checkFlow(self, day=1):
        return volum.check_Large_order_net_amount(self, day)

    # 检测一个月(22日)内资金流入流出情况
    def checkMouthFlow(self):
        return volum.check_Large_order_net_amount(self, 22)

    # 检测一周(5日)内资金流入流出情况
    def checkWeekFlow(self):
        return volum.check_Large_order_net_amount(self, 5)

    # 判断股票是否存在反转信号
    def get_whether_reverse(self, time):
        if self.checkReversalVolums():
            # 检测当前日是否反包
            return self.checkReversalVolums()
        else:
            return False

    # =============== 筹码判断逻辑
    # 判断股票的90%筹码聚散程度
    def check90ChipGatheringsituation(self):
        return chips.check90Chip(self)

    # 判断股票的90%筹码价格的高低
    def check90ChipPriceHighOrLow(self):
        return chips.check90ChipPriceHighOrLow(self)

    # =============== 获取某个时间段内的macd数据
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

    # 获取macd顶，底背离
    def get_MACD_divergenc(self, fastperiod=12, slowperiod=26, signalperiod=9):
        # ===== 找到MACD峰值
        df = self.dataFrame
        macd, signal, hist = np.nan_to_num(
            ta.MACD(
                self.close_prices_array,
                fastperiod,
                slowperiod,
                signalperiod,
            ),
            nan=0,
        )
        # 计算需要补充的长度差
        diff_len = len(self.dataFrame) - len(hist)
        if diff_len > 0:
            # 添加`diff_len`个零到`hist`的前面
            hist = np.pad(hist, (diff_len, 0), "constant", constant_values=0)
        # 现在可以将hist添加到self.dataFrame中
        df["MACD_Hist"] = hist
        max_tab = np.zeros(hist.shape[0])
        min_tab = np.zeros(hist.shape[0])
        peaks_max = np.greater_equal(hist, np.roll(hist, 1)) & np.greater_equal(
            hist, np.roll(hist, -1)
        )
        valleys_min = np.less_equal(hist, np.roll(hist, 1)) & np.less_equal(
            hist, np.roll(hist, -1)
        )
        max_tab[peaks_max] = hist[peaks_max]
        min_tab[valleys_min] = hist[valleys_min]
        df_max = pd.DataFrame(max_tab, index=df.index, columns=["MACD_Peaks"])
        df_min = pd.DataFrame(min_tab, index=df.index, columns=["MACD_Valleys"])
        df["MACD_Peaks"] = df_max
        df["MACD_Valleys"] = df_min
        # ===== 找到MACD的顶部与底部背离
        divergence = np.where(
            (
                (df["MACD_Peaks"].shift() > df["MACD_Peaks"])
                & (df["Close"].shift() < df["Close"])
            )
            | (
                (df["MACD_Valleys"].shift() < df["MACD_Valleys"])
                & (df["Close"].shift() > df["Close"])
            ),
            "True",
            "False",
        )

        df["MACD_Divergence"] = divergence
        # 找出MACD背离的日期
        divergence_days = df.loc[df["MACD_Divergence"] == "True"].index
        print("MACD背离的日期有：")
        for day in divergence_days:
            closeValue = df["Close"][day]
            volumeValue = df["Volume"][day]
            print(f"日期：{day}，收盘价：{closeValue}, 成交量：{volumeValue}")

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
                else:
                    return False
            else:
                return False
        else:
            return False

    # ============== 乖离率逻辑
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
        bias_offset = self.checkbiasoffset(day)
        bias = ma.calculate_bias(self, day)
        if abs(bias) > bias_offset:
            if bias > 0:
                return -1
            else:
                return 1
        else:
            return 0

    # ================ 蒙特卡罗模拟逻辑
    # 蒙特卡罗模拟基于生成多个随机场景来模拟系统的可变性。在金融环境中，我们可以使用这种技术来模拟股票的未来表现、风险评估、期权定价和预测未来资产价格
    def monte_carlo_simulation(self, num_simulations):
        # Get historical data
        prices = self.dataFrame["Close"]

        # Calculate daily returns
        daily_returns = prices.pct_change().dropna()

        # Calculate mean and standard deviation of daily returns
        mean_return = daily_returns.mean()
        std_dev = daily_returns.std()

        # Generate random numbers based on normal distribution
        simulations = np.random.normal(
            loc=mean_return, scale=std_dev, size=(num_simulations, len(prices))
        )

        # Calculate simulated prices
        self.simulated_prices = prices.iloc[-1] * (1 + simulations).cumprod(axis=1)
        return self.simulated_prices

    def get_highest_probability_simulated_price(self, threshold=120):
        occurrences = (self.simulated_prices > threshold).sum(
            axis=1
        )  # 统计每个路径中超过阈值的次数
        probabilities = occurrences / len(self.simulated_prices)  # 计算概率值
        # 按照概率值从高到低排序
        sorted_indices = probabilities.argsort()[::-1]  # 按照概率值从高到低排序的索引
        top_results = sorted_indices[:5]  # 取概率最高的前5个结果

        # 输出概率最高的几个结果
        for result_index in top_results:
            probability = probabilities[result_index]
            print(f"Result: {result_index}, Probability: {probability}")

    # ================== kdj指标
    # 返回kdj指标
    def calculate_kdj(self, n=9, m1=3, m2=3):
        df = pd.DataFrame(
            {
                "close": self.CloseValues,
                "open": self.OpenValues,
                "high": self.MaxValues,
                "low": self.MinValues,
            }
        )
        df["lowest_low"] = df["low"].rolling(window=n).min()
        df["highest_high"] = df["high"].rolling(window=n).max()
        df["rsv"] = (
            (df["close"] - df["lowest_low"])
            / (df["highest_high"] - df["lowest_low"])
            * 100
        )
        df["k"] = df["rsv"].ewm(com=m1 - 1).mean()
        df["d"] = df["k"].ewm(com=m2 - 1).mean()
        df["j"] = 3 * df["k"] - 2 * df["d"]
        return df

    # ================ 量价背离判断
    def checkValueVolumeReversal(self):
        # 收盘价变化量
        self.dataFrame["ClosePrices_change"] = self.dataFrame["Close"].diff()

        # 成交量变化量
        self.dataFrame["Volumes_change"] = self.dataFrame["Volume"].diff()

        # 找到价格创新低但交易量没有放大的点 价跌量缩
        self.dataFrame["Divergence1"] = np.where(
            (self.dataFrame["ClosePrices_change"] < 0)
            & (self.dataFrame["Volumes_change"] < 0),
            "True",
            "False",
        )

        # 找到成交量创新低而价格没有跟着下跌的点 价涨量缩
        self.dataFrame["Divergence2"] = np.where(
            (self.dataFrame["ClosePrices_change"] > 0)
            & (self.dataFrame["Volumes_change"] < 0),
            "True",
            "False",
        )

        # 将两种底背离的情况合并
        self.dataFrame["Divergence"] = np.where(
            (self.dataFrame["Divergence1"] == "True")
            | (self.dataFrame["Divergence2"] == "True"),
            "True",
            "False",
        )

        # 找出底部缩量下跌的日期
        divergence_days = self.dataFrame.loc[
            self.dataFrame["Divergence"] == "True"
        ].index
        print("底部缩量下跌和高位缩量上涨的日期有：")
        for day in divergence_days:
            closeValue = self.dataFrame["Close"][day]
            volumeValue = self.dataFrame["Volume"][day]
            print(
                f"日期：{day}，价格：{closeValue},成交量：{volumeValue}"
                # f"日期：{self.dataFrame.index[day].strftime('%Y-%m-%d')},价格：{self.dataFrame['Close'][day]},成交量：{self.dataFrame['Volume'][day]}"
            )
    # ================ 预测值
    def Get_Prediction_Value(self):
        # 获取预测值
        return line_regression.Get_LinePrediction(self.dataFrame)


    # ================ stock属性
    @property
    def get_Date(self):
        return self.Date

    @property
    def get_weekClose(self):
        return self.WeekClose

    @property
    def get_mouthClose(self):
        return self.MouthClose

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
    def get_Chips90concentrations(self):
        return self.Chips90concentrations

    @get_Chips90concentrations.setter
    def get_Chips90concentrations(self, value):
        self.Chips90concentrations = value

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

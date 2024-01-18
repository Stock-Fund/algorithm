# 价格预测逻辑
# 短线逻辑
# 预测明天5日线价格,可能是阶段低点
def Calculate5_predict(stock, s=1.099):
    if len(stock.CloseValues) < 5:
        # 如果 CloseValues 的长度小于 5，无法进行预测，可以抛出异常或返回默认值
        # raise ValueError("Insufficient data to make prediction.")
        print("stock.CloseValues的长度不满足计算条件")
        # 或者返回默认值
        predictValue = -1
    else:
        predictValue = (
            stock.CloseValues[-1] * s
            + stock.CloseValues[-3]
            + stock.CloseValues[-2]
            + stock.CloseValues[-4]
            + stock.CloseValues[-5]
        ) / 5
    stock.predictValue = predictValue


# 龙头低吸算法1（预测5日线买入算法）
def CheckBuyByPredict(stock):
    return stock.CurrentValue < stock.predictValue


# 龙头低吸算法2（5日线-10日线检测买入算法）
def CheckBuy(stock):
    currentValue = stock.CurrentValue
    # 只有连续5板以上
    # 只有在昨天下跌的情况下
    if stock.IsFallYesterday():
        MA5 = stock.MA5
        MA10 = stock.MA10
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
def CheckSell(stock, value):
    # value 传入当前成本价
    return (
        stock.CurrentValue >= value * stock.TakeProfit
        or stock.CurrentValue <= value * stock.StopLoss
    )

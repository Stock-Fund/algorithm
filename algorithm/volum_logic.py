# 判断成交量是否超过平均量
# 以该股票最近一个月或者三个月的日均交易量为基准平均值。
# 如果该日交易量高于基准平均值的一定倍数(如150%或者200%),则认为该日交易量较大,是放量。
# 如果该日交易量低于基准平均值的一定比例(如50%或者70%),则认为该日交易量较小,是缩量。
# 如果在基准平均值和放量标准之间,则认为交易量一般,既不是明显放量也不是缩量。
def checkVolumeIncreaseOrShrink(stock):
    totalVolume = sum(stock.Volumes)
    count = len(stock.Volumes)
    average = totalVolume / count
    # 放量
    if stock.Volumes[-1] >= average * 1.5:
        return 1
    # 缩量
    elif stock.Volumes[-1] <= average * 0.5:
        return -1
    # 正常量
    else:
        return 0


# 检测当天量能是否放量超过平均量
def checkAverageVolums_Climax_Reversal(stock):
    currentVolum = stock.Volumes[-1]
    preVolums = stock.Volumes[:-1]
    averageVolum = sum(preVolums) / len(preVolums)
    if currentVolum > averageVolum:
        return True
    else:
        return False


# 检测当天量能是否放量，反转 ，返回 True 放量反转 False 未放量反转
def checkVolum_Climax_Reversal(stock):
    currentVolum = stock.Volumes[-1]
    preVolum = stock.Volumes[-2]
    if currentVolum > preVolum:
        return True
    else:
        return False


# 检测净成交量，得出的结果为正，表示该股内仍有主力，看多；反之则表示主力已出场，看空
def check_net_volume(stock, days):
    CloseValues = stock.CloseValues[-days:]
    OpenValues = stock.OpenValues[-days:]
    Volumes = stock.Volumes[-days:]
    volumeNet = []
    for i in range(len(CloseValues)):
        closeValue = CloseValues[i]
        openValue = OpenValues[i]
        volumes = Volumes[i]
        if closeValue > openValue:
            volumeNet.append(volumes)  # 上涨，成交量为正
        elif closeValue < openValue:
            volumeNet.append(-volumes)  # 下跌，成交量为负
        else:
            volumeNet.append(0)  # 持平，成交量为0

    # 计算成交量净值
    volumeNetValue = sum(volumeNet)
    return volumeNetValue
    # print(f'成交量净值：{volumeNetValue}')
    # if volumeNetValue >= 0:
    #     return True
    # else:
    #     return False


# 计算N日内股票资金流入流出情况
def check_Large_order_net_amount(stock, day):
    in_out_flow_count = len(stock.in_out_flow)
    closeValues_cout = len(stock.CloseValues)
    tmpCount = 0
    if day < in_out_flow_count:
        in_out_flow_count = day
    if in_out_flow_count < closeValues_cout:
        tmpCount = in_out_flow_count
    else:
        tmpCount = closeValues_cout
    curFlow = 0
    for i in range(tmpCount):
        curFlow += stock.in_out_flow[i]
    return curFlow

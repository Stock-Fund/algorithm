import statistics


# 箱体逻辑
# 1 突破上边界
# -1 突破下边界
# 0 横盘震荡中
def checkBox(curValue, max, min):
    if curValue >= max:
        return 1
    elif curValue <= min:
        return -1
    else:
        return 0


# 检查价格偏离多个均线时是否处于相对稳定状态。该函数遍历提供的均线列表，
# 对于每个均线，根据偏离因子计算上下边界，即均线加减偏离因子乘以价格标准差。
# 然后判断最后一个价格是否在上下边界之间，如果是，则认为价格处于相对稳定状态
# 收盘价  均线数组  价格浮动幅度参数
def check_price_status(stock, time_range, deviation_factor=0.5):
    upper_bound = float("-inf")  # 初始值负无穷大
    lower_bound = float("inf")  # 初始值正无穷大
    _minValues = stock.MaxValues[-time_range:]
    _maxValues = stock.MinValues[-time_range:]

    current_upper_bound = max(_maxValues)
    current_lower_bound = min(_minValues)

    if current_upper_bound > upper_bound:
        upper_bound = current_upper_bound

    if current_lower_bound < lower_bound:
        lower_bound = current_lower_bound

    return checkBox(upper_bound, lower_bound)


# 计算价格波动幅度
def calculate_price_std(stock, prices):
    price_std = statistics.stdev(prices)
    return price_std

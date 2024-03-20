# 检查筹码分布情况
# -2，-1 为筹码开始分散；
# 0，1 为筹码无规律情况；
# 2，3 为筹码开始聚集
# 数字越小越要离场，数字越大需要关注
def check90ChipGatheringsituation(stock):
    checkValue = 15  # 筹码判断基准
    curValue = float(stock.Chips90concentrations[-1].replace("%", ""))
    preValue0 = float(stock.Chips90concentrations[-2].replace("%", ""))
    preValue1 = float(stock.Chips90concentrations[-3].replace("%", ""))
    # 筹码集中度变大，筹码开始分散
    if curValue > preValue0 or curValue > preValue1:
        if curValue > checkValue:
            return -2
        else:
            return -1
    # 筹码集中度变小，筹码开始聚集
    elif curValue < preValue0 and preValue0 < preValue1:
        if curValue > checkValue:
            return 2
        else:
            return 3
    else:  # 筹码集中度无规律改变
        if curValue > checkValue:
            return 0
        else:
            return 1


def check90ChipPriceHighOrLow(stock):
    chips90price_range = stock.Chips90Prices[-1]
    chips90prices = chips90price_range.split("_")
    minPrice = float(chips90prices[0])
    maxPrice = float(chips90prices[1])
    curPrice = float(stock.CurrentValue)
    if curPrice >= minPrice and curPrice <= maxPrice:
        return 0
    elif curPrice < minPrice:
        print("处于价格低位")
        return -1
    elif curPrice > maxPrice:
        print("处于价格高位")
        return 1
    
# def checkChip(stock):
#     curProfitRatio = float(stock.ProfitRatios[-1])
#     curPrice = float(stock.CurrentValue)
#     curChipAveragePrice = float(stock.ChipAveragePrices[-1])
#         # 当前价格大于筹码平均价格，股价处于平均点之上
#     if curPrice > curChipAveragePrice:
#         return True


# # import pandas as pd
# # import copy


# # def __init__(stock):
# #     stock.Chip = {}  # 当前获利盘
# #     stock.ChipList = {}  # 所有的获利盘的


# # def get_data(stock):
# #     stock.data = pd.read_csv("test.csv")


# def calcuJUN(stock, dateT, highT, lowT, volT, TurnoverRateT, A, minD):

#     x = []
#     l = (highT - lowT) / minD
#     for i in range(int(l)):
#         x.append(round(lowT + i * minD, 2))
#     length = len(x)
#     eachV = volT / length
#     for i in stock.Chip:
#         stock.Chip[i] = stock.Chip[i] * (1 - TurnoverRateT * A)
#     for i in x:
#         if i in stock.Chip:
#             stock.Chip[i] += eachV * (TurnoverRateT * A)
#         else:
#             stock.Chip[i] = eachV * (TurnoverRateT * A)
#     import copy

#     stock.ChipList[dateT] = copy.deepcopy(stock.Chip)


# def calcuSin(stock, dateT, highT, lowT, avgT, volT, TurnoverRateT, minD, A):
#     x = []

#     l = (highT - lowT) / minD
#     for i in range(int(l)):
#         x.append(round(lowT + i * minD, 2))

#     length = len(x)

#     # 计算仅仅今日的筹码分布
#     tmpChip = {}
#     eachV = volT / length

#     # 极限法分割去逼近
#     for i in x:
#         x1 = i
#         x2 = i + minD
#         h = 2 / (highT - lowT)
#         s = 0
#         if i < avgT:
#             y1 = h / (avgT - lowT) * (x1 - lowT)
#             y2 = h / (avgT - lowT) * (x2 - lowT)
#             s = minD * (y1 + y2) / 2
#             s = s * volT
#         else:
#             y1 = h / (highT - avgT) * (highT - x1)
#             y2 = h / (highT - avgT) * (highT - x2)

#             s = minD * (y1 + y2) / 2
#             s = s * volT
#         tmpChip[i] = s

#     for i in stock.Chip:
#         stock.Chip[i] = stock.Chip[i] * (1 - TurnoverRateT * A)

#     for i in tmpChip:
#         if i in stock.Chip:
#             stock.Chip[i] += tmpChip[i] * (TurnoverRateT * A)
#         else:
#             stock.Chip[i] = tmpChip[i] * (TurnoverRateT * A)
#     import copy

#     stock.ChipList[dateT] = copy.deepcopy(stock.Chip)


# def calcu(stock, dateT, highT, lowT, avgT, volT, TurnoverRateT, minD=0.01, flag=1, AC=1):
#     if flag == 1:
#         stock.calcuSin(dateT, highT, lowT, avgT, volT, TurnoverRateT, A=AC, minD=minD)
#     elif flag == 2:
#         stock.calcuJUN(dateT, highT, lowT, volT, TurnoverRateT, A=AC, minD=minD)


# def calcuChip(stock, flag=1, AC=1):  # flag 使用哪个计算方式,    AC 衰减系数
#     low = stock.MinValues
#     high = stock.MaxValues
#     vol = stock.Volumes
#     TurnoverRate = stock["TurnoverRate"]
#     avg = stock["avg"]
#     date = stock["date"]

#     for i in range(len(date)):
#         #     if i < 90:
#         #         continue

#         highT = high[i]
#         lowT = low[i]
#         volT = vol[i]
#         TurnoverRateT = TurnoverRate[i]
#         avgT = avg[i]
#         # print(date[i])
#         dateT = date[i]
#         stock.calcu(
#             dateT, highT, lowT, avgT, volT, TurnoverRateT / 100, flag=flag, AC=AC
#         )  # 东方财富的小数位要注意，兄弟萌。我不除100懵逼了

#     # 计算winner


# def winner(stock, p=None):
#     Profit = []
#     date = stock.data["date"]

#     if p == None:  # 不输入默认close
#         p = stock.data["close"]
#         count = 0
#         for i in stock.ChipList:
#             # 计算目前的比例

#             Chip = stock.ChipList[i]
#             total = 0
#             be = 0
#             for i in Chip:
#                 total += Chip[i]
#                 if i < p[count]:
#                     be += Chip[i]
#             if total != 0:
#                 bili = be / total
#             else:
#                 bili = 0
#             count += 1
#             Profit.append(bili)
#     else:
#         for i in stock.ChipList:
#             # 计算目前的比例

#             Chip = stock.ChipList[i]
#             total = 0
#             be = 0
#             for i in Chip:
#                 total += Chip[i]
#                 if i < p:
#                     be += Chip[i]
#             if total != 0:
#                 bili = be / total
#             else:
#                 bili = 0
#             Profit.append(bili)

#     # import matplotlib.pyplot as plt
#     # plt.plot(date[len(date) - 200:-1], Profit[len(date) - 200:-1])
#     # plt.show()

#     return Profit


# def lwinner(stock, N=5, p=None):

#     data = copy.deepcopy(stock.data)
#     date = data["date"]
#     ans = []
#     for i in range(len(date)):
#         print(date[i])
#         if i < N:
#             ans.append(None)
#             continue
#         stock.data = data[i - N : i]
#         stock.data.index = range(0, N)
#         stock.__init__()
#         stock.calcuChip()  # 使用默认计算方式
#         a = stock.winner(p)
#         ans.append(a[-1])
#     import matplotlib.pyplot as plt

#     plt.plot(date[len(date) - 60 : -1], ans[len(date) - 60 : -1])
#     plt.show()

#     stock.data = data
#     return ans


# def cost(stock, N):
#     date = stock.data["date"]

#     N = N / 100  # 转换成百分比
#     ans = []
#     for i in stock.ChipList:  # 我的ChipList本身就是有顺序的
#         Chip = stock.ChipList[i]
#         ChipKey = sorted(Chip.keys())  # 排序
#         total = 0  # 当前比例
#         sumOf = 0  # 所有筹码的总和
#         for j in Chip:
#             sumOf += Chip[j]

#         for j in ChipKey:
#             tmp = Chip[j]
#             tmp = tmp / sumOf
#             total += tmp
#             if total > N:
#                 ans.append(j)
#                 break
#     import matplotlib.pyplot as plt

#     plt.plot(date[len(date) - 1000 : -1], ans[len(date) - 1000 : -1])
#     plt.show()
#     return ans


# # if __name__ == "__main__":
# #     a = ChipDistribution()
# #     a.get_data()  # 获取数据
# #     a.calcuChip(flag=1, AC=1)  # 计算
# #     a.winner()  # 获利盘
# #     a.cost(90)  # 成本分布

# #     a.lwinner()

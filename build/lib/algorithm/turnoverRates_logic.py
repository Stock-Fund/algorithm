# 换手率逻辑
# 判断市场热度
def CheckMarketPopularity(self):
    if self.turnoverRates >= 10:
        return 1
    elif self.turnoverRates >= 1 and self.turnoverRates <= 5:
        return 0
    elif self.turnoverRates >= 0.1 and self.turnoverRates <= 1:
        return -1

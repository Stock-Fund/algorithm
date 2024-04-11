# 线性逻辑

import pandas as pd
from sklearn.linear_model import LinearRegression

# 加载数据
df = pd.read_csv('your_stock_data.csv')
X = df['time'].values.reshape(-1, 1)
y = df['close_price'].values.reshape(-1, 1)

# 线性回归模型
model = LinearRegression()
model.fit(X, y)

# 输出回归系数与截距
print("回归系数：", model.coef_)
print("截距:", model.intercept_)

# todo
# 预测
# future_time = [[2024, 11]] # 示例时间：2024年11月
# predicted_price = model.predict(future_time)

# print("预测价格为：", predicted_price)
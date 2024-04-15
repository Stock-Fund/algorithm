# 线性回归逻辑

# 导入所需库
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pandas as pd
import numpy as np


# 获取线性回归模型,得到后续N天的预测值
def Get_LinePrediction(df,day = 30):
   # 使用 'Close' 列作为预测的目标值
   df['Prediction'] = df[['Close']].shift(-day)
   # 创建独立变量数据集（X）
   X = np.array(df.drop(['Prediction'],1))
   # 除去最后day行数据
   X = X[:-day]
   # 创建目标数据集 (y)
   y = np.array(df['Prediction'])
   # 除去最后day行数据
   y = y[:-day]
   # 分割数据为80%训练集和20%测试集
   x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

   # 创建并训练模型
   lr = LinearRegression()
   lr.fit(x_train, y_train)

   # 测试模型：计算和打印误差
   y_train_pred = lr.predict(x_train)
   y_test_pred = lr.predict(x_test)

   print(f'Train error: {metrics.mean_squared_error(y_train, y_train_pred)}')
   print(f'Test error: {metrics.mean_squared_error(y_test, y_test_pred)}')
   
   return y_train_pred, y_test_pred
   

def linear_regression(feature, target):
   # 划分训练集和测试集
   X_train, X_test, y_train, y_test = train_test_split(feature, target, test_size=0.2, random_state=0)
   # 训练线性回归模型
   model = LinearRegression()  
   model.fit(X_train, y_train)

   # 预测测试集结果
   y_pred = model.predict(X_test)
      # 评估模型
   print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))  
   print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))  
   print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
   return model, y_pred, X_test, y_test

def polyfit(feature,target):
    # 使用numpy的polyfit函数进行线性回归
    coefficients = np.polyfit(feature.flatten(), target.flatten(), 1)
    # 生成线性回归模型
    model = np.poly1d(coefficients)
    # 在X上进行预测 
    y_pred = model(feature)
    
    return model,y_pred

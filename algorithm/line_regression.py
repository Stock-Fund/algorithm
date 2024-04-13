# 线性回归逻辑

# 导入所需库
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pandas as pd
import numpy as np

# 假设我们有一个数据集 df，包含特征X和目标值y
# df = pd.read_csv('your_dataset.csv')
# X = df['feature_column'].values.reshape(-1,1)
# y = df['target_column'].values.reshape(-1,1)
# 以下用随机生成数据进行演示
# X = np.random.rand(100, 1)
# y = 2 + 3 * X + np.random.rand(100, 1)

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

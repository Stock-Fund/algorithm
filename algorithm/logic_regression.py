# 逻辑回归逻辑
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
from sklearn.metrics import confusion_matrix, accuracy_score


def Get_Logistic(x):
    # 加载数据集
    iris = datasets.load_iris()
    X = iris.data  # 特征数据
    y = iris.target  # 目标类别

    # 划分数据集为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

    # 创建逻辑回归模型
    logistic_model = LogisticRegression(max_iter=200)

    # 训练模型
    logistic_model.fit(X_train, y_train)

    # 进行预测
    y_pred = logistic_model.predict(X_test)

    # 计算准确率
    accuracy = accuracy_score(y_test, y_pred)
    print(f'准确率: {accuracy:.2f}')

    # 打印混淆矩阵
    conf_matrix = confusion_matrix(y_test, y_pred)
    print('混淆矩阵:')
    print(conf_matrix)



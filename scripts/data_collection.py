import pandas as pd
import numpy as np
import requests
import zipfile
import os
from io import BytesIO
import logging

def download_data():
    """
    从UCI机器学习仓库下载鸢尾花数据集
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # UCI鸢尾花数据集URL
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        
        logger.info("开始下载数据集...")
        response = requests.get(url)
        
        if response.status_code == 200:
            # 定义列名
            column_names = ['sepal_length', 'sepal_width', 
                           'petal_length', 'petal_width', 'species']
            
            # 读取数据
            data = pd.read_csv(BytesIO(response.content), 
                              names=column_names, 
                              header=None)
            
            logger.info(f"数据集下载成功，共 {len(data)} 条记录")
            
            # 保存原始数据
            raw_data_path = 'data/raw/iris_raw.csv'
            os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)
            data.to_csv(raw_data_path, index=False)
            
            logger.info(f"原始数据已保存至: {raw_data_path}")
            
            return data
            
        else:
            logger.error(f"下载失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"数据下载过程中发生错误: {str(e)}")
        return None

def load_local_data(filepath='data/raw/iris_raw.csv'):
    """
    加载本地数据（备用方案）
    """
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        # 如果文件不存在，创建示例数据
        from sklearn.datasets import load_iris
        iris = load_iris()
        data = pd.DataFrame(iris.data, columns=iris.feature_names)
        data['species'] = iris.target
        data['species'] = data['species'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data.to_csv(filepath, index=False)
        
        print(f"创建示例数据集并保存至: {filepath}")
        return data

if __name__ == "__main__":
    data = download_data()
    if data is None:
        print("使用备用数据源...")
        data = load_local_data()
    print(data.head())
    print(f"数据集形状: {data.shape}")
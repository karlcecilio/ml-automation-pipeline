import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import os
import logging

class DataPreprocessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
    def load_data(self, filepath='data/raw/iris_raw.csv'):
        """加载数据"""
        return pd.read_csv(filepath)
    
    def explore_data(self, data):
        """数据探索"""
        print("="*50)
        print("数据基本信息:")
        print(data.info())
        print("\n数据统计描述:")
        print(data.describe())
        print("\n类别分布:")
        print(data['species'].value_counts())
        print("\n缺失值检查:")
        print(data.isnull().sum())
        
        # 保存探索结果
        with open('data/processed/data_exploration.txt', 'w') as f:
            f.write(f"数据集形状: {data.shape}\n")
            f.write(f"特征数量: {len(data.columns)-1}\n")
            f.write(f"类别分布:\n{data['species'].value_counts().to_string()}\n")
        
        return data
    
    def preprocess(self, data, test_size=0.2, random_state=42):
        """数据预处理"""
        logging.info("开始数据预处理...")
        
        # 分离特征和标签
        X = data.drop('species', axis=1)
        y = data['species']
        
        # 编码标签
        y_encoded = self.label_encoder.fit_transform(y)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
        
        # 特征标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 保存预处理后的数据
        self.save_processed_data(X_train_scaled, X_test_scaled, y_train, y_test)
        
        # 保存预处理对象
        self.save_preprocessor()
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def save_processed_data(self, X_train, X_test, y_train, y_test):
        """保存处理后的数据"""
        os.makedirs('data/processed', exist_ok=True)
        
        np.save('data/processed/X_train.npy', X_train)
        np.save('data/processed/X_test.npy', X_test)
        np.save('data/processed/y_train.npy', y_train)
        np.save('data/processed/y_test.npy', y_test)
        
        logging.info("处理后的数据已保存")
    
    def save_preprocessor(self):
        """保存预处理模型"""
        os.makedirs('models', exist_ok=True)
        
        with open('models/preprocessor.pkl', 'wb') as f:
            pickle.dump({
                'label_encoder': self.label_encoder,
                'scaler': self.scaler
            }, f)
        
        logging.info("预处理模型已保存")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    preprocessor = DataPreprocessor()
    data = preprocessor.load_data()
    data = preprocessor.explore_data(data)
    X_train, X_test, y_train, y_test = preprocessor.preprocess(data)
    
    print(f"训练集形状: {X_train.shape}")
    print(f"测试集形状: {X_test.shape}")
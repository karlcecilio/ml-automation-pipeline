import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import pickle
import joblib
import json
import os
import logging

class ModelTrainer:
    def __init__(self):
        self.best_model = None
        self.best_params = None
        
    def load_data(self):
        """加载预处理后的数据"""
        X_train = np.load('data/processed/X_train.npy')
        X_test = np.load('data/processed/X_test.npy')
        y_train = np.load('data/processed/y_train.npy')
        y_test = np.load('data/processed/y_test.npy')
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, X_train, y_train):
        """训练随机森林模型"""
        logging.info("开始训练随机森林模型...")
        
        # 定义模型
        rf = RandomForestClassifier(random_state=42)
        
        # 定义超参数网格
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # 网格搜索
        grid_search = GridSearchCV(
            rf, 
            param_grid, 
            cv=5, 
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        self.best_model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        logging.info(f"最佳参数: {self.best_params}")
        logging.info(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")
        
        return self.best_model
    
    def evaluate_model(self, model, X_test, y_test):
        """评估模型性能"""
        # 预测
        y_pred = model.predict(X_test)
        
        # 计算准确率
        accuracy = accuracy_score(y_test, y_pred)
        
        # 分类报告
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # 保存评估结果
        evaluation_results = {
            'accuracy': accuracy,
            'classification_report': report,
            'best_params': self.best_params
        }
        
        with open('models/evaluation_results.json', 'w') as f:
            json.dump(evaluation_results, f, indent=4)
        
        # 打印结果
        print("="*50)
        print("模型评估结果:")
        print(f"准确率: {accuracy:.4f}")
        print("\n分类报告:")
        print(pd.DataFrame(report).transpose())
        
        return evaluation_results
    
    def save_model(self, model, model_name='random_forest_model'):
        """保存训练好的模型"""
        os.makedirs('models', exist_ok=True)
        
        # 保存为pickle格式
        with open(f'models/{model_name}.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        # 保存为joblib格式（推荐用于sklearn模型）
        joblib.dump(model, f'models/{model_name}.joblib')
        
        logging.info(f"模型已保存为 models/{model_name}.pkl 和 models/{model_name}.joblib")
    
    def train_pipeline(self):
        """完整的训练流程"""
        logging.basicConfig(level=logging.INFO)
        
        # 1. 加载数据
        X_train, X_test, y_train, y_test = self.load_data()
        
        # 2. 训练模型
        model = self.train_random_forest(X_train, y_train)
        
        # 3. 评估模型
        results = self.evaluate_model(model, X_test, y_test)
        
        # 4. 保存模型
        self.save_model(model)
        
        return model, results

if __name__ == "__main__":
    trainer = ModelTrainer()
    model, results = trainer.train_pipeline()
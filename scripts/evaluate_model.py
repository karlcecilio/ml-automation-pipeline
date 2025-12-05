import pickle
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

class ModelEvaluator:
    def __init__(self):
        self.model = None
        self.results = None
        
    def load_model(self, model_path='models/random_forest_model.joblib'):
        """加载模型"""
        try:
            self.model = joblib.load(model_path)
            logging.info(f"模型已从 {model_path} 加载")
            return True
        except Exception as e:
            logging.error(f"加载模型失败: {str(e)}")
            return False
    
    def load_test_data(self):
        """加载测试数据"""
        X_test = np.load('data/processed/X_test.npy')
        y_test = np.load('data/processed/y_test.npy')
        return X_test, y_test
    
    def make_predictions(self, X_test):
        """进行预测"""
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        return y_pred, y_pred_proba
    
    def generate_confusion_matrix(self, y_test, y_pred, save_path='reports/confusion_matrix.png'):
        """生成混淆矩阵"""
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, 
                                      display_labels=['setosa', 'versicolor', 'virginica'])
        disp.plot(cmap='Blues', values_format='d')
        plt.title('混淆矩阵')
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"混淆矩阵已保存至 {save_path}")
        
        return cm
    
    def generate_feature_importance(self, feature_names=None, save_path='reports/feature_importance.png'):
        """生成特征重要性图"""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            if feature_names is None:
                feature_names = ['sepal_length', 'sepal_width', 
                                'petal_length', 'petal_width']
            
            # 创建DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            # 绘制条形图
            plt.figure(figsize=(10, 6))
            sns.barplot(x='importance', y='feature', data=importance_df)
            plt.title('特征重要性')
            plt.xlabel('重要性')
            plt.ylabel('特征')
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 保存为CSV
            importance_df.to_csv('reports/feature_importance.csv', index=False)
            
            logging.info(f"特征重要性图已保存至 {save_path}")
            
            return importance_df
        
        else:
            logging.warning("模型没有feature_importances_属性")
            return None
    
    def generate_evaluation_report(self, y_test, y_pred, y_pred_proba=None):
        """生成评估报告"""
        from sklearn.metrics import (accuracy_score, precision_score, 
                                   recall_score, f1_score)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision_macro': precision_score(y_test, y_pred, average='macro'),
            'recall_macro': recall_score(y_test, y_pred, average='macro'),
            'f1_macro': f1_score(y_test, y_pred, average='macro')
        }
        
        # 保存指标
        report = {
            'metrics': metrics,
            'model_type': type(self.model).__name__,
            'model_params': self.model.get_params()
        }
        
        with open('reports/evaluation_report.json', 'w') as f:
            json.dump(report, f, indent=4)
        
        # 创建HTML报告
        self.generate_html_report(metrics, report)
        
        return report
    
    def generate_html_report(self, metrics, report):
        """生成HTML格式的报告"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>模型评估报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 1000px; margin: auto; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .images {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .image-container {{ flex: 1; margin: 10px; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>机器学习模型评估报告</h1>
                    <p>生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <h3>准确率</h3>
                        <div class="metric-value">{metrics['accuracy']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>精确率 (Macro)</h3>
                        <div class="metric-value">{metrics['precision_macro']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>召回率 (Macro)</h3>
                        <div class="metric-value">{metrics['recall_macro']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>F1分数 (Macro)</h3>
                        <div class="metric-value">{metrics['f1_macro']:.4f}</div>
                    </div>
                </div>
                
                <div class="images">
                    <div class="image-container">
                        <h3>混淆矩阵</h3>
                        <img src="confusion_matrix.png" alt="混淆矩阵">
                    </div>
                    <div class="image-container">
                        <h3>特征重要性</h3>
                        <img src="feature_importance.png" alt="特征重要性">
                    </div>
                </div>
                
                <div>
                    <h3>模型参数</h3>
                    <pre>{json.dumps(report['model_params'], indent=2)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        os.makedirs('reports', exist_ok=True)
        with open('reports/evaluation_report.html', 'w') as f:
            f.write(html_content)
        
        logging.info("HTML报告已生成")
    
    def evaluate_pipeline(self):
        """完整的评估流程"""
        logging.basicConfig(level=logging.INFO)
        
        # 1. 加载模型
        if not self.load_model():
            return None
        
        # 2. 加载测试数据
        X_test, y_test = self.load_test_data()
        
        # 3. 进行预测
        y_pred, y_pred_proba = self.make_predictions(X_test)
        
        # 4. 生成混淆矩阵
        self.generate_confusion_matrix(y_test, y_pred)
        
        # 5. 生成特征重要性图
        self.generate_feature_importance()
        
        # 6. 生成评估报告
        report = self.generate_evaluation_report(y_test, y_pred, y_pred_proba)
        
        logging.info("评估流程完成")
        
        return report

if __name__ == "__main__":
    evaluator = ModelEvaluator()
    report = evaluator.evaluate_pipeline()
    if report:
        print("\n评估完成！报告已保存至 reports/ 目录")
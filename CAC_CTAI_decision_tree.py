import numpy as np
import pandas as pd
import pickle
import os
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import GridSearchCV


class MedicalDecisionTree:
    def __init__(self):
        # 创建两个决策树模型：一个用于Risk预测，一个用于FollowUp_advice预测
        self.risk_tree = DecisionTreeClassifier(
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        self.followup_tree = DecisionTreeClassifier(
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )

        # 存储训练数据的特征范围
        self.feature_ranges = {}

    def _preprocess_cac(self, value):
        if value < 3:
            return 0  # 低
        elif value <= 8:
            return 1  # 中
        else:
            return 2  # 高

    def _preprocess_ctai(self, value):
        if value < 65:
            return 0  # 低
        elif value < 85:
            return 1  # 中
        else:
            return 2  # 高

    def _preprocess_nodule_size(self, value):
        if value < 5:
            return 0  # 小
        elif value <= 10:
            return 1  # 中
        else:
            return 2  # 大

    def preprocess_data(self, data):
        # 创建数据副本
        processed_data = data.copy()

        # 对各个特征进行预处理，直接转换为数值类别
        processed_data['CAC'] = processed_data['CAC'].apply(self._preprocess_cac)
        processed_data['CTAI'] = processed_data['CTAI'].apply(self._preprocess_ctai)
        processed_data['Nodule_Size'] = processed_data['Nodule_Size'].apply(self._preprocess_nodule_size)
        # FollowUp已经是0-3的值，不需要处理

        return processed_data

    def fit(self, X, y_risk, y_followup):
        # 存储特征范围
        self.feature_ranges = {
            'CAC': [X['CAC'].min(), X['CAC'].max()],
            'CTAI': [X['CTAI'].min(), X['CTAI'].max()],
            'Nodule_Size': [X['Nodule_Size'].min(), X['Nodule_Size'].max()],
            'FollowUp': [X['FollowUp'].min(), X['FollowUp'].max()]
        }

        # 预处理输入数据
        X_processed = self.preprocess_data(X)

        # 设置特征权重
        feature_weights = np.ones(len(X_processed))
        # 增加CAC和CTAI的权重
        cac_mask = X_processed['CAC'].notnull()
        ctai_mask = X_processed['CTAI'].notnull()
        feature_weights[cac_mask] *= 2
        feature_weights[ctai_mask] *= 1.5

        # 训练模型
        self.risk_tree.fit(X_processed, y_risk, sample_weight=feature_weights)
        self.followup_tree.fit(X_processed, y_followup, sample_weight=feature_weights)

    def tune_parameters(self, X, y_risk, y_followup):
        param_grid = {
            'max_depth': [3, 5, 7, 10],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        # 预处理输入数据
        X_processed = self.preprocess_data(X)

        # 设置特征权重
        feature_weights = np.ones(len(X_processed))
        cac_mask = X_processed['CAC'].notnull()
        ctai_mask = X_processed['CTAI'].notnull()
        feature_weights[cac_mask] *= 2
        feature_weights[ctai_mask] *= 1.5

        # 使用GridSearchCV进行参数调优
        grid_search_risk = GridSearchCV(self.risk_tree, param_grid, cv=5, scoring='accuracy')
        grid_search_risk.fit(X_processed, y_risk, sample_weight=feature_weights)
        self.risk_tree = grid_search_risk.best_estimator_

        grid_search_followup = GridSearchCV(self.followup_tree, param_grid, cv=5, scoring='accuracy')
        grid_search_followup.fit(X_processed, y_followup, sample_weight=feature_weights)
        self.followup_tree = grid_search_followup.best_estimator_

        print("Best parameters for risk prediction tree:", grid_search_risk.best_params_)
        print("Best parameters for follow-up advice tree:", grid_search_followup.best_params_)

    def predict(self, X):
        # 预处理输入数据
        X_processed = self.preprocess_data(X)

        # 预测
        risk_pred = self.risk_tree.predict(X_processed)
        followup_pred = self.followup_tree.predict(X_processed)

        return pd.DataFrame({
            'Risk': risk_pred,
            'FollowUp_advice': followup_pred
        })

    def print_trees(self):
        feature_names = ['CAC', 'CTAI', 'Nodule_Size', 'FollowUp']

        print("Risk Prediction Tree:")
        print(export_text(self.risk_tree,
                          feature_names=feature_names,
                          show_weights=True))

        print("\nFollow-up Advice Tree:")
        print(export_text(self.followup_tree,
                          feature_names=feature_names,
                          show_weights=True))

    def save_model(self, filepath):
        """
        保存模型到指定路径
        """
        model_data = {
            'risk_tree': self.risk_tree,
            'followup_tree': self.followup_tree,
            'feature_ranges': self.feature_ranges
        }

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 保存模型
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"模型已保存到: {filepath}")

    @classmethod
    def load_model(cls, filepath):
        """
        从指定路径加载模型
        """
        # 加载模型数据
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        # 创建新的模型实例
        model = cls()

        # 恢复模型状态
        model.risk_tree = model_data['risk_tree']
        model.followup_tree = model_data['followup_tree']
        model.feature_ranges = model_data['feature_ranges']

        return model


# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    df = pd.read_csv('/data/zhenyu/Program/Explain_LLM/data/data_mix.csv', encoding='gbk')
    data = df[['CAC', 'CTAI', 'NoduleSize', 'FollowUpCompare']]
    data.columns = ['CAC', 'CTAI', 'Nodule_Size', 'FollowUp']
    risk = df['risk_label_guo']
    followup_advice = df['followup_advice_guo']

    # 初始化和训练模型
    model = MedicalDecisionTree()
    model.fit(data, risk, followup_advice)
    model.tune_parameters(data, risk, followup_advice)
    #保存模型
    # model.save_model('/data/zhenyu/Program/Explain_LLM/data/explain_pred_model.pkl')

    # # 加载模型
    # model = None
    # model = MedicalDecisionTree.load_model('/data/zhenyu/Program/Explain_LLM/data/explain_pred_model.pkl')

    # 预测
    predictions = model.predict(data)

    #计算准确率
    risk_accuracy = (predictions['Risk'] == risk).mean()
    followup_accuracy = (predictions['FollowUp_advice'] == followup_advice).mean()
    print(f"Risk Prediction Accuracy: {risk_accuracy:.2f}")
    print(f"Follow-up Advice Prediction Accuracy: {followup_accuracy:.2f}")
    # print(predictions)
    # #fix the predictions to the original data
    df['risk_pred'] = predictions['Risk']
    df['followup_advice_pred'] = predictions['FollowUp_advice']
    df.to_csv('/data/zhenyu/Program/Explain_LLM/data/data_mix_dicision_tree_pred.csv', index=False, encoding='gbk')

    # 打印决策树结构
    # model.print_trees()
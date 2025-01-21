import os
from idlelib.iomenu import encoding
from operator import index

import pandas as pd
import json
import numpy as np

data_guo_path = 'CAC-CTAI患者随访建议--郭英鹏.csv'
data_cheng_path = 'CAC-CTAI患者随访建议-程主任.csv'

followup_compare = {
    '首次':0,
    '增大':1,
    '变小':2,
    '无明显变化':3
}

risk_label_map = {
    '低':0,
    '较低':1,
    '中':2,
    '较高':3,
    '高':4
}

followup_advice_map = {
    '3个月':0,
    '6个月':1,
    '12个月':2
}

clinical_advice_map = {
    '':0,
    '积极治疗（手术切除）':1,
    '抗炎治疗后复查CT':2,
    '年度体检':3
}


def data_mix():
    df_guo = pd.read_csv(data_guo_path, encoding='gbk')
    df_cheng = pd.read_csv(data_cheng_path, encoding='gbk')

    print(df_cheng.columns)
    #create a new table to store the mixed data
    new_df = pd.DataFrame()

    new_df['ID'] = df_guo['编号']
    new_df['CAC'] = df_guo["CAC个数"]
    new_df['CTAI'] = df_guo["CTAI风险值(0-99)"]
    new_df['NoduleSize'] = df_guo["结节大小/mm"]
    new_df['FollowUpCompare'] = df_guo["随访对比"].map(followup_compare)

    new_df['risk_label_guo'] = df_guo['综合风险评估'].map(risk_label_map)
    new_df['followup_advice_guo'] = df_guo['随访建议'].map(followup_advice_map)
    new_df['clinical_advice_guo'] = df_guo['临床建议'].map(clinical_advice_map)

    new_df['risk_label_cheng'] = df_cheng['综合风险评估'].map(risk_label_map)
    new_df['followup_advice_cheng'] = df_cheng['随访建议'].map(followup_advice_map)
    new_df['clinical_advice_cheng'] = df_cheng['临床建议'].map(clinical_advice_map)

    #save the mixed data to a new csv file
    new_df.to_csv('data_mix.csv', index=False, encoding='gbk')
    pass

def data_analysis():
    df = pd.read_csv('data_mix.csv', encoding='gbk')
    #get risk label and convert to integer
    risk_label_guo = df['risk_label_guo'].astype(int).tolist()
    risk_label_cheng = df['risk_label_cheng'].astype(int).tolist()
    followup_advice_guo = df['followup_advice_guo'].astype(int).tolist()
    followup_advice_cheng = df['followup_advice_cheng'].astype(int).tolist()

    #draw the confusion matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    # confusion_matrix = [[0 for i in range(5)] for j in range(5)]
    # for i in range(len(risk_label_guo)):
    #     confusion_matrix[risk_label_guo[i]][risk_label_cheng[i]] += 1
    #
    # plt.figure(figsize=(10, 7))
    # sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=[1, 2, 3, 4, 5],
    #             yticklabels=[1, 2, 3, 4, 5])
    # plt.xlabel('CHENG Risk Label')
    # plt.ylabel('GUO Risk Label')
    # plt.title('Confusion Matrix')
    # plt.show()

    confusion_matrix = [[0 for i in range(3)] for j in range(3)]
    for i in range(len(followup_advice_guo)):
        confusion_matrix[followup_advice_guo[i]][followup_advice_cheng[i]] += 1

    plt.figure(figsize=(10, 7))
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['3 months', "6 months", '12 months'],
                yticklabels=['3 months', "6 months", '12 months'])
    plt.xlabel('CHENG Followup Advice')
    plt.ylabel('GUO Followup Advice')
    plt.title('Confusion Matrix')
    plt.show()


    pass
def data_process():
    new_df = pd.read_csv('data_mix.csv', encoding='gbk')
    df_ai = pd.read_csv('/data/zhenyu/Program/Explain_LLM/data/data_mix_mulChain.csv', encoding='gbk')

    new_df['risk_label_AI_mulChain'] = df_ai['risk_label_ai'].map(risk_label_map)
    new_df['followup_advice_AI_mulChain'] = df_ai['followup_advice_ai'].map(followup_advice_map)

    new_df.to_csv('data_mix.csv', index=False, encoding='gbk')
    pass

def data_analysis_ai():
    df = pd.read_csv('data_mix_dicision_tree_pred.csv', encoding='gbk')
    risk_label_guo = df['risk_label_guo'].astype(int).tolist()
    risk_label_cheng = df['risk_label_cheng'].astype(int).tolist()
    risk_label_ai = df['risk_label_AI_mulChain'].astype(int).tolist()

    # followup_label_guo = df['followup_advice_guo'].astype(int).tolist()
    # followup_label_cheng = df['followup_advice_cheng'].astype(int).tolist()
    # followup_label_ai = df['followup_advice_AI_mulChain'].astype(int).tolist()

    import matplotlib.pyplot as plt
    import seaborn as sns

    # confusion_matrix = [[0 for i in range(5)] for j in range(5)]
    # for i in range(len(risk_label_guo)):
    #     confusion_matrix[risk_label_guo[i]][risk_label_ai[i]] += 1
    # plt.figure(figsize=(10, 7))
    # sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=[1, 2, 3, 4, 5],
    #             yticklabels=[1, 2, 3, 4, 5])
    # plt.xlabel('AI Risk Label')
    # plt.ylabel('GUO Risk Label')
    # plt.title('Confusion Matrix')
    # plt.show()

    # confusion_matrix = [[0 for i in range(5)] for j in range(5)]
    # for i in range(len(risk_label_cheng)):
    #     confusion_matrix[risk_label_cheng[i]][risk_label_ai[i]] += 1
    #
    # plt.figure(figsize=(10, 7))
    # sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=[1, 2, 3, 4, 5],
    #             yticklabels=[1, 2, 3, 4, 5])
    # plt.xlabel('AI Risk Label')
    # plt.ylabel('Cheng Risk Label')
    # plt.title('Confusion Matrix')
    # plt.show()

    # confusion_matrix = [[0 for i in range(3)] for j in range(3)]
    # for i in range(len(followup_label_guo)):
    #     confusion_matrix[followup_label_guo[i]][followup_label_ai[i]] += 1
    # plt.figure(figsize=(10, 7))
    # sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['3 months', "6 months", '12 months'],
    #             yticklabels=['3 months', "6 months", '12 months'])
    #
    # plt.xlabel('AI Followup Advice')
    # plt.ylabel('GUO Followup Advice')
    # plt.title('Confusion Matrix')
    #
    # plt.show()

    # confusion_matrix = [[0 for i in range(3)] for j in range(3)]
    # for i in range(len(followup_label_cheng)):
    #     confusion_matrix[followup_label_cheng[i]][followup_label_ai[i]] += 1
    # plt.figure(figsize=(10, 7))
    # sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['3 months', "6 months", '12 months'],
    #             yticklabels=['3 months', "6 months", '12 months'])
    # plt.xlabel('AI Followup Advice')
    # plt.ylabel('Cheng Followup Advice')
    # plt.title('Confusion Matrix')
    # plt.show()



    pass


if __name__ == '__main__':
    # data_mix()
    # data_analysis()
    # data_process()
    data_analysis_ai()
    pass



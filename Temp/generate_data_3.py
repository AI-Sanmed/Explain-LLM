import os
import pandas as pd
import numpy as np
import random

CTAI_CATEGORIES = {
    (0, 0.65),  # 0%到65%
    (0.65, 0.85),  # 65%到85%
    (0.85, 0.99)  # 85%到99%
}

NODULE_SIZE_CATEGORIES = {
    (0, 5),  # 0到5 mm
    (5, 10),  # 5到8 mm
    (11, 100)  # 9到30 mm
}

ctai_data_path = '/data/zhenyu/DataSets/LLM_FollowUp/Qingdao/SecondData/tuma_maxScoreNodule_results.csv'

df = pd.read_csv(ctai_data_path, encoding='gbk')


CAC_CATEGORIES = {
    (0, 3),  # 0到2.99
    (3, 8),  # 3到8
    (9, 20)  # 9到20
}

FOLLOW_UP_CATEGORIES = [
    '首次',  # 首次
    '增大',  # 增大
    '变小',  # 变小
    '无明显变化'  # 无明显变化
]

final_df = pd.DataFrame(columns=['CTAI_Score', 'Nodule_Size', 'CAC_Score', 'Follow_Up'])


for ctai_category in CTAI_CATEGORIES:
    for nodule_size in NODULE_SIZE_CATEGORIES:
        filtered_df = df[(df['NoduleSize'] <= nodule_size[1]) & (df['NoduleSize'] >= nodule_size[0])
                         & (df['NoduleScore'] <= ctai_category[1]) & (df['NoduleScore'] >= ctai_category[0])]
        #如果大于12个，随机挑选12个
        if len(filtered_df) >= 12:
            sampled_df = filtered_df.sample(n=12)
            i = 0
            for cac_category in CAC_CATEGORIES:
                for followup_category in FOLLOW_UP_CATEGORIES:
                    cac_value = random.randint(cac_category[0], cac_category[1])
                    sample_data = sampled_df.iloc[i]
                    final_df = final_df._append({
                        'CAC':cac_value,
                        'CTAI': sample_data['NoduleScore'],
                        'NoduleSize':sample_data['NoduleSize'],
                        'FollowUp':followup_category
                    }, ignore_index=True)
                    i+=1
        else:
            print(f'CTAI_Score:{ctai_category}, nodule_size{nodule_size}')

final_df.to_csv('explain_data.csv')


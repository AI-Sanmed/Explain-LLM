import os
from idlelib.iomenu import encoding

import pandas as pd
import json
import requests
from tqdm import tqdm

followup_compare = {
    0:'首次发现',
    1:'较前增大',
    2:'较前减小',
    3:'较前无明显变化'
}

def mulchain_test():
    data_path = 'data_mix.csv'
    df = pd.read_csv(data_path, encoding='gbk')
    df['JsonFormat_Success'] = None
    df['Result'] = None
    num = 1
    pbar = tqdm(total=len(df))
    for index, row in df.iterrows():
        ID = row['ID']
        CAC = row['CAC']
        CTAI = row['CTAI']
        NoduleSize = row['NoduleSize']
        FollowUpCompare = followup_compare[row['FollowUpCompare']]
        data = {
            'ID': ID,
            "cac_value": str(CAC),
            "ctai_value": str(CTAI)+'%',
            "nodule_size": str(NoduleSize)+'mm',
            "other_info":'随访对比：'+FollowUpCompare
        }
        data_json = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url='http://172.16.43.57:8005/explain_chat', data=data_json,headers=headers, timeout=600)
        if response.status_code == 200:
            JsonFormat_Success = response.json().get('JsonFormat_Success')
            result = response.json().get('Result')
            #save result and jsonFormat in the df
            df.at[index, 'JsonFormat_Success'] = JsonFormat_Success
            df.at[index, 'Result'] = result
        pbar.update(1)
    #save
    df.to_csv('data_mix_mulChain.csv', index=False, encoding='gbk')
    pass

if __name__ == '__main__':
    mulchain_test()
    pass
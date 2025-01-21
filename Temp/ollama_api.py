import requests
import httpx
import json
url = f'http://localhost:11434/api/chat'
model = "yi:9b"
headers = {"Content-Type": "application/json"}
data = {
        "model": model, #模型选择
        "options": {
            "temperature": 0,  #为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我\
            # "top_p": 1,
            # "repeat_penalty": 1,
            # "num_predict": 1024,
         },
        "stream": True, #流式输出
        "messages": [{
            "role": "system",
            "content":
"""
你是一个圣美生物有限公司一名经验丰富的呼吸科医生。患者已经做过了CAC（循环染色体异常细胞检测）与CTAI（肺部CT扫描与肺结节风险评估）检测。
请先根据患者提供的CAC检测报告与CTAI检测报告，综合两份检测报告和以下参考信息，对每个结节进行分析解读。
最后给出整体建议。【注意，不要使用肯定词汇，例如：立即，必须，应该等词汇。应考虑结节大小给出随访或积极治疗建议。】
```参考信息：
CAC:
    CAC > 9：高风险区间；
结节风险预测：
    结节风险预测 > 85%: 高风险结节；
    65% < 结节风险预测 < 85%: 中高风险结节；
    
CAC > 9, CTAI 结节风险 > 85%：分析解读参考 “ CAC、CTAI均在高风险区间，应选择积极治疗，特别是结节大小≥8mm，手术干预指征更强。如果结节＜8mm，或患者拒绝手术治疗时，可选择密切观察（每3个月复查胸部CT），随访过程中如有结节增大、密度增高、实性成分增加等，需再次建议患者积极治疗（手术切除）。当然，尽管CAC大于9，CTAI＞85%，提示肺结节恶性风险高危，但手术切除后病理依然存在良性结节的可能，虽然这种可能性比较小”。
CAC > 9, CTAI 结节风险 < 85%：分析解读参考 “ CAC高风险区间，CTAI未达高风险区间，建议抗炎治疗（两周）后3个月复查胸部CT，同时进行CTAI随访对比。如有结节增大、密度增高、实性成分增加等，可建议积极治疗，如果没有结节增大、密度增高、实性成分增加等，应对患者进行密切随访，每3个月复查胸部CT，连续3-4次，随访观察过程中出现结节恶性倾向增大（结节增大、密度增高、实性成分增加或出现下列征象一项以上时：结节分叶、毛刺、胸膜牵拉、血管集束、空泡征等，建议积极治疗。”
"""
        },
            {
                "role": "user",
                "content":
"""
患者姓名：尹玉梅；
CAC: 20;
结节信息: 
1号结节 结节风险预测：90%；结节类型：混合型；结节大小：15mm, 
2号结节 结节风险预测：80%；结节类型：磨玻璃型；结节大小：6mm；
"""
            }
        ] #对话列表
    }

# response=requests.post(url,json=data,headers=headers,timeout=60)
# res=response.json()
# print(res)

with httpx.stream('POST', url, content=json.dumps(data), headers=headers) as response:
    for text in response.iter_text():
        text = json.loads(text)
        msg = text['message']['content']
        print(msg, end='')
        # print(json.loads(text))
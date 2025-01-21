import streamlit as st
import time

def generate_analysis(cac_score, nodules):
    analysis = f"基于您提供的CAC评分 {cac_score} 和 {len(nodules)} 个CTAI结节信息，分析如下：\n\n"
    for i, nodule in enumerate(nodules, 1):
        analysis += f"结节 {i}: 位于{nodule['location']}，大小 {nodule['size']}mm，类型为{nodule['type']}，"
        analysis += f"密度 {nodule['density']}HU，风险程度 {nodule['risk']}%\n"
    analysis += "\n综合分析：[这里是基于数据的详细分析]\n\n"
    analysis += "建议：[这里是基于分析的医疗建议]"
    return analysis

st.set_page_config(page_title="CAC和CTAI报告分析器", layout="wide")

st.title("CAC和CTAI报告分析器")

with st.form("cac_ctai_form"):
    st.header("CAC评分")
    cac_score = st.number_input("输入CAC评分", min_value=0, step=1)

    st.header("CTAI结节信息")
    nodules = []

    cols = st.columns(5)
    with cols[0]:
        st.subheader("位置")
    with cols[1]:
        st.subheader("大小 (mm)")
    with cols[2]:
        st.subheader("类型")
    with cols[3]:
        st.subheader("密度 (HU)")
    with cols[4]:
        st.subheader("风险 (%)")

    nodule_count = st.number_input("输入结节数量", min_value=1, max_value=10, step=1)
    generate_button = st.form_submit_button("确认")

    if generate_button:
        for i in range(nodule_count):  # 根据用户输入的结节数量生成输入框
            cols = st.columns(5)
            with cols[0]:
                location = st.selectbox(f"结节{i + 1}位置", ["", "左上叶", "左下叶", "右上叶", "右中叶", "右下叶"],
                                        key=f"location_{i}")
            with cols[1]:
                size = st.number_input(f"结节{i + 1}大小", min_value=0.0, step=0.1, key=f"size_{i}")
            with cols[2]:
                nodule_type = st.selectbox(f"结节{i + 1}类型", ["", "实性", "部分实性", "磨玻璃"], key=f"type_{i}")
            with cols[3]:
                density = st.number_input(f"结节{i + 1}密度", step=0.1, key=f"density_{i}")
            with cols[4]:
                risk = st.number_input(f"结节{i + 1}风险", min_value=0.0, max_value=100.0, step=0.1, key=f"risk_{i}")

            if location and size and nodule_type and density and risk:
                nodules.append({
                    "location": location,
                    "size": size,
                    "type": nodule_type,
                    "density": density,
                    "risk": risk
                })

    submitted = st.form_submit_button("提交分析")

if submitted:
    if not nodules:
        st.error("请至少添加一个结节信息")
    else:
        with st.spinner("正在分析..."):
            # 模拟分析过程
            time.sleep(2)
            analysis = generate_analysis(cac_score, nodules)

        st.success("分析完成")
        st.subheader("报告解读")

        # 模拟打字机效果
        report = st.empty()
        for i in range(len(analysis) + 1):
            report.markdown(analysis[:i])
            time.sleep(0.01)
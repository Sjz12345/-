import streamlit as st
from agent.react_agent import ReactAgent  # 导入你的 Agent 类


# 初始化 Agent（使用缓存，避免重复加载）
@st.cache_resource
def get_agent():
    return ReactAgent()


agent = get_agent()

# 页面标题
st.set_page_config(page_title="扫地机器人智障客服", page_icon="🤖")
st.title("🤖 扫地机器人智障客服")
st.markdown("我是你的扫地/扫拖机器人专家，请问有什么可以帮你的？")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入你的问题..."):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用 Agent 获取回答（流式）
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        # 使用 Agent 的 execute_stream 方法
        for chunk in agent.execute_stream(prompt):
            full_response += chunk
            response_container.markdown(full_response + "▌")
        response_container.markdown(full_response)

    # 添加助手回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
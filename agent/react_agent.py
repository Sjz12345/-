from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from model.factory import chat_model
from agent.tools.agent_tools import *  # 确保这里导入了所有需要的工具
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self):
        # 1. 加载自定义系统提示词（此时文件内容应为简化的 ReAct 模板）
        system_prompt_str = load_system_prompts()

        # 2. 确保所有必要占位符存在（如果文件中缺失则自动追加，但文件已包含则不需要）
        required = ["{tools}", "{tool_names}", "{agent_scratchpad}"]
        for ph in required:
            if ph not in system_prompt_str:
                if ph == "{tools}":
                    system_prompt_str += "\n\n工具列表：\n{tools}"
                elif ph == "{tool_names}":
                    system_prompt_str += "\n\n可用工具名称：{tool_names}"
                elif ph == "{agent_scratchpad}":
                    system_prompt_str += "\n\n{agent_scratchpad}"

        # 3. 构建提示模板
        prompt = PromptTemplate.from_template(system_prompt_str)

        # 4. 定义工具列表（必须与提示词中描述的工具完全一致）
        self.tools = [
            rag_summarize,
            get_weather,
            get_user_location,
            fetch_external_data
        ]

        # 5. 打印最终模板（调试用）
        print("=== 最终提示词模板 ===\n", prompt.template)

        # 6. 创建 ReAct Agent
        agent = create_react_agent(
            llm=chat_model,
            tools=self.tools,
            prompt=prompt
        )

        # 7. 包装为 AgentExecutor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # 开启详细输出，观察 Agent 思考过程
            max_iterations=10,
            early_stopping_method="generate",
            handle_parsing_errors=True,
        )

    def execute_stream(self, query: str):
        for chunk in self.agent_executor.stream({"input": query}):
            if "output" in chunk:
                yield chunk["output"] + "\n"


if __name__ == "__main__":
    agent = ReactAgent()
    user_input = "该机器人运到我的城市包邮吗，会下雨淋坏吗"
    for output in agent.execute_stream(user_input):
        print(output, end="")

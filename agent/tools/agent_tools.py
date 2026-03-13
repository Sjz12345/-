import os

from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import requests
from utils.config_handler import agent_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

rag = RagSummarizeService()
external_data = {}


@tool(description="从向量中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="查询对应城市的天气,以消息字符串的形式返回")
def get_weather(city):
    url = "https://uapis.cn/api/v1/misc/weather"

    try:
        r = requests.get(url, params={"city": city}, timeout=10)

        r.raise_for_status()

        if r.status_code == 200:
            return r.json()
        else:
            return "API返回错误"

    except Exception as e:
        return f"请求失败: {e}"


@tool(description="获取用户自己的ip地址,位置等信息")
def get_user_location() -> str:
    url = "https://uapis.cn/api/v1/network/myip"
    try:
        r = requests.get(url, timeout=10)

        r.raise_for_status()

        if r.status_code == 200:
            return r.json()
        else:
            return "API返回错误"

    except Exception as e:
        return f"请求失败: {e}"


def get_generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"File {external_data_path} not found.")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")
                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "feature": feature,
                    "efficiency": efficiency,
                    "comparison": comparison,
                    "consumables": consumables
                }


@tool(description="从外部系统中获取用户指定月份的使用记录,以纯字符串形式返回,如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    get_generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError as e:
        logger.warning(f"No Found for id: {user_id}, month: {month}")
        return ""


if __name__ == "__main__":
    print(get_weather.invoke("上海"))
    print(get_user_location.invoke({}))
    print(fetch_external_data.invoke({
        "user_id": "1001",
        "month": "2025-01"
    }))

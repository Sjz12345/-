import os
from abc import ABC, abstractmethod
from typing import Union

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from utils.config_handler import rag_config

load_dotenv()

class BaseModelFactory(ABC):

    @abstractmethod
    def generator(self) -> Union[Embeddings, BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):

    def generator(self) -> BaseChatModel:
        api_key = os.getenv("TONGYI_API_KEY")

        return ChatTongyi(
            model=rag_config["chat_model_name"],
            api_key=api_key
        )


class EmbeddingsFactory(BaseModelFactory):

    def generator(self) -> Embeddings:
        api_key = os.getenv("DASHSCOPE_API_KEY")

        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not found")

        return DashScopeEmbeddings(
            model=rag_config["embedding_model_name"],
            dashscope_api_key=api_key
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()

if __name__ == "__main__":
    print(chat_model)
    print(embed_model)

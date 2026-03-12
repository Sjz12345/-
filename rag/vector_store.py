import os

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from model.factory import embed_model
from utils.config_handler import chroma_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from utils.file_handler import (
    pdf_loader,
    txt_loader,
    listdir_with_allowed_types,
    get_file_md5_hex,
)



class VectorStoreService:

    def __init__(self):

        # 初始化向量库
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_config["persist_directory"],
        )

        # 文档切分器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separator"],
            length_function=len,
        )

        # MD5记录文件
        self.md5_store_path = get_abs_path(chroma_config["md5_hex_store"])

        if not os.path.exists(self.md5_store_path):
            open(self.md5_store_path, "w", encoding="utf-8").close()

    def get_retriever(self):

        return self.vector_store.as_retriever(
            search_kwargs={"k": chroma_config["k"]}
        )

    def check_md5(self, md5_hex: str):

        with open(self.md5_store_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == md5_hex:
                    return True

        return False

    def save_md5(self, md5_hex: str):

        with open(self.md5_store_path, "a", encoding="utf-8") as f:
            f.write(md5_hex + "\n")

    def load_file_document(self, file_path: str):

        if file_path.endswith(".txt"):
            return txt_loader(file_path)

        if file_path.endswith(".pdf"):
            return pdf_loader(file_path)

        return []

    def load_document(self):

        logger.info("Start loading documents...")

        allowed_files = listdir_with_allowed_types(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_knowledge_file_type"]),
        )

        for path in allowed_files:

            try:

                md5_hex = get_file_md5_hex(path)

                if self.check_md5(md5_hex):
                    logger.info(f"MD5 exists, skip: {path}")
                    continue

                documents = self.load_file_document(path)

                if not documents:
                    logger.warning(f"No document loaded: {path}")
                    continue

                split_docs = self.splitter.split_documents(documents)

                if not split_docs:
                    logger.warning(f"Split empty: {path}")
                    continue

                # 批量写入向量库
                self.vector_store.add_documents(split_docs)

                self.save_md5(md5_hex)

                logger.info(f"Saved to vector DB: {path}")

            except Exception as e:

                logger.error(f"Error loading {path}")
                logger.exception(e)

        logger.info("Document loading finished.")


if __name__ == "__main__":

    vs = VectorStoreService()

    # 加载知识库
    vs.load_document()

    # 获取检索器
    retriever = vs.get_retriever()

    # 测试查询
    query = "迷路"

    res = retriever.invoke(query)

    print("\n=== Query Result ===\n")

    for doc in res:
        print(doc.page_content[:200])
        print("-" * 50)

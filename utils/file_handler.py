import hashlib
import os
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# 获取文件的md5十六进制字符串
def get_file_md5_hex(filepath: str) -> str:
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return "File not found"

    if not os.path.isfile(filepath):
        logger.error(f"Not a file: {filepath}")
        return "Not a file"

    hash_md5 = hashlib.md5()
    # 分片大小
    chunk_size = 4096

    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_md5.update(chunk)

            md5_hex = hash_md5.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"Error while getting file md5: {filepath}")
        return "Error getting file md5"


# 返回文件列表内指定的后缀的文件
def listdir_with_allowed_types(dir_path: str, allowed_types: tuple[str]):
    files = []
    if not os.path.isdir(dir_path):
        logger.error(f"Not a directory: {dir_path}")
        return allowed_types
    for file in os.listdir(dir_path):
        if file.endswith(allowed_types):
            files.append(os.path.join(dir_path, file))

    return tuple(files)


def pdf_loader(filepath: str, password: str = None) -> list[Document]:
    return PyPDFLoader(filepath, password).load()

def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()

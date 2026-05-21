"""向量存储管理器 - 封装 ChromaDB VectorStore 操作

使用 ChromaDB 的 PersistentClient，本地文件存储，无需 Docker。
"""

import time
import uuid
from typing import List, Optional

from loguru import logger

from app.config import config
from app.core.chroma_client import chroma_manager
from app.services.vector_embedding_service import vector_embedding_service


# 统一使用 biz collection
COLLECTION_NAME = "biz"


class VectorStoreManager:
    """向量存储管理器（ChromaDB 版本）"""

    def __init__(self):
        """初始化向量存储管理器"""
        self.collection_name = COLLECTION_NAME
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """初始化 ChromaDB VectorStore"""
        try:
            # 连接 ChromaDB
            _ = chroma_manager.connect()
            logger.info(f"VectorStore 初始化成功, collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"VectorStore 初始化失败: {e}")
            raise

    def add_documents(self, documents: List) -> List[str]:
        """
        批量添加文档到向量存储（自动批量向量化）

        Args:
            documents: 文档列表

        Returns:
            List[str]: 文档 ID 列表
        """
        try:
            start_time = time.time()

            # 生成 ID
            ids = [str(uuid.uuid4()) for _ in documents]

            # 生成向量
            texts = [doc.page_content for doc in documents]
            embeddings = vector_embedding_service.embed_documents(texts)

            # 准备元数据
            metadatas = [doc.metadata for doc in documents]

            # 插入到 ChromaDB
            collection = chroma_manager.get_collection()
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            elapsed = time.time() - start_time
            logger.info(
                f"批量添加 {len(documents)} 个文档到 VectorStore 完成, "
                f"耗时: {elapsed:.2f}秒"
            )
            return ids

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise

    def delete_by_source(self, file_path: str) -> int:
        """
        删除指定文件的所有文档

        Args:
            file_path: 文件路径

        Returns:
            int: 删除的文档数量
        """
        try:
            collection = chroma_manager.get_collection()

            # 查找该文件的所有文档
            results = collection.get(where={"_source": file_path})

            if results and results.get("ids"):
                ids_to_delete = results["ids"]
                collection.delete(ids=ids_to_delete)
                deleted_count = len(ids_to_delete)
                logger.info(f"删除文件旧数据: {file_path}, 删除数量: {deleted_count}")
                return deleted_count

            logger.debug(f"文件 {file_path} 无旧数据需要删除")
            return 0

        except Exception as e:
            logger.warning(f"删除旧数据失败 (可能是首次索引): {e}")
            return 0

    def get_vector_store(self):
        """
        获取 VectorStore 实例（collection）

        Returns:
            Collection: ChromaDB collection 实例
        """
        return chroma_manager.get_collection()

    def similarity_search(self, query: str, k: int = 3) -> List:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            List[Document]: 相关文档列表
        """
        try:
            # 生成查询向量
            query_vector = vector_embedding_service.embed_query(query)

            # 搜索
            collection = chroma_manager.get_collection()
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=k,
                include=["documents", "metadatas"],
            )

            # 转换为 Document 对象
            from langchain_core.documents import Document
            docs = []

            if results and results.get("documents"):
                documents = results["documents"][0]
                metadatas = results.get("metadatas", [[]])[0]

                for doc, meta in zip(documents, metadatas):
                    docs.append(Document(
                        page_content=doc,
                        metadata=meta or {},
                    ))

            logger.debug(f"相似度搜索完成: query='{query}', 结果数={len(docs)}")
            return docs

        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            return []


# 全局单例 - 延迟初始化
_vector_store_manager_instance: Optional[VectorStoreManager] = None


def _get_instance() -> VectorStoreManager:
    """获取单例实例（延迟初始化）"""
    global _vector_store_manager_instance
    if _vector_store_manager_instance is None:
        _vector_store_manager_instance = VectorStoreManager()
    return _vector_store_manager_instance


class _VectorStoreManagerProxy:
    """代理类，用于延迟初始化"""

    def __getattr__(self, name):
        return getattr(_get_instance(), name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(_get_instance(), name, value)


# 使用代理，延迟初始化 VectorStoreManager
vector_store_manager: VectorStoreManager = _VectorStoreManagerProxy()  # type: ignore

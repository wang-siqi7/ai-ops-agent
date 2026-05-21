"""ChromaDB 客户端工厂模块

使用 ChromaDB 的 PersistentClient，支持本地文件存储，无需 Docker。
"""

import os
from loguru import logger

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import config


class ChromaClientManager:
    """ChromaDB 客户端管理器

    使用 ChromaDB PersistentClient，本地文件存储，无需 Docker。
    """

    # 常量定义
    COLLECTION_NAME: str = "biz"
    VECTOR_DIM: int = 1024  # 统一使用 1024 维

    def __init__(self) -> None:
        """初始化 ChromaDB 客户端管理器"""
        self._client: chromadb.PersistentClient | None = None

    def connect(self) -> chromadb.PersistentClient:
        """
        连接到 ChromaDB 并初始化 collection

        Returns:
            chromadb.PersistentClient: ChromaDB 客户端实例

        Raises:
            RuntimeError: 连接或初始化失败时抛出
        """
        # 幂等：避免重复初始化
        if self._client is not None:
            logger.debug("ChromaDB 已连接，跳过重复 connect")
            return self._client

        try:
            # 获取数据存储路径
            data_path = config.chroma_data_path or "./chroma_data"

            logger.info(f"正在启动 ChromaDB，存储路径: {data_path}")

            # 创建 PersistentClient
            self._client = chromadb.PersistentClient(
                path=data_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            logger.info("ChromaDB 连接成功")

            # 检查并创建 collection
            if not self._collection_exists():
                logger.info(f"collection '{self.COLLECTION_NAME}' 不存在，正在创建...")
                self._create_collection()
                logger.info(f"成功创建 collection '{self.COLLECTION_NAME}'")
            else:
                logger.info(f"collection '{self.COLLECTION_NAME}' 已存在")

            return self._client

        except Exception as e:
            logger.error(f"ChromaDB 操作失败: {e}")
            self.close()
            raise RuntimeError(f"ChromaDB 操作失败: {e}") from e

    def _collection_exists(self) -> bool:
        """检查 collection 是否存在"""
        if self._client is None:
            return False
        try:
            return self.COLLECTION_NAME in [c.name for c in self._client.list_collections()]
        except Exception:
            return False

    def _create_collection(self) -> None:
        """创建 biz collection"""
        if self._client is None:
            raise RuntimeError("ChromaDB 客户端未初始化")

        # ChromaDB 会自动管理 schema，创建 collection 时不需要手动定义字段
        self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Business knowledge collection"},
        )
        logger.info(f"成功创建 collection '{self.COLLECTION_NAME}'")

    def get_client(self) -> chromadb.PersistentClient:
        """
        获取 ChromaDB 客户端实例

        Returns:
            chromadb.PersistentClient: ChromaDB 客户端实例

        Raises:
            RuntimeError: 客户端未初始化时抛出
        """
        if self._client is None:
            raise RuntimeError("ChromaDB 客户端未初始化，请先调用 connect()")
        return self._client

    def get_collection(self):
        """获取 collection 实例"""
        if self._client is None:
            raise RuntimeError("ChromaDB 客户端未初始化，请先调用 connect()")
        return self._client.get_collection(name=self.COLLECTION_NAME)

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: True 表示健康，False 表示异常
        """
        try:
            if self._client is None:
                return False
            # 尝试获取 collection 列表
            _ = self._client.list_collections()
            return True
        except Exception as e:
            logger.error(f"ChromaDB 健康检查失败: {e}")
            return False

    def close(self) -> None:
        """关闭连接"""
        try:
            if self._client is not None:
                self._client = None
                logger.info("已关闭 ChromaDB 连接")
        except Exception as e:
            logger.warning(f"关闭 ChromaDB 连接时出现警告: {e}")
        finally:
            self._client = None

    def __enter__(self) -> "ChromaClientManager":
        """上下文管理器入口"""
        _ = self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object
    ) -> None:
        """上下文管理器退出"""
        self.close()


# 全局单例
chroma_manager = ChromaClientManager()

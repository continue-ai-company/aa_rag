import json
from typing import Dict, Any, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from aa_rag import utils, setting
from aa_rag.db.base import BaseNoSQLDataBase
from aa_rag.gtypes.enums import NoSQLDBType
from aa_rag.gtypes.models.knowlege_base.solution import CompatibleEnv, Project, Guide
from aa_rag.knowledge_base.base import BaseKnowledge


class SolutionKnowledge(BaseKnowledge):
    _knowledge_name = "Solution"

    def __init__(self, nosql_db: NoSQLDBType = setting.db.nosql, **kwargs):
        """
        Solution Knowledge Base. Built-in Knowledge Base.
        Args:
            nosql_db: 指定使用的 NoSQL 数据库类型（此处默认使用 TinyDB）
            **kwargs: 其他关键字参数
        """
        super().__init__(**kwargs)
        self.nosql_db: BaseNoSQLDataBase = utils.get_db(nosql_db)
        self.table_name = self.knowledge_name.lower()
        # # 初始化 TinyDB 表（如果表不存在，则自动创建）
        # self.nosql_db.using(self.table_name)

    def _is_compatible_env(
        self, source_env_info: CompatibleEnv, target_env_info: CompatibleEnv
    ) -> bool:
        """
        判断 source_env_info 与 target_env_info 是否兼容。
        """
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert in computer hardware device information. 
                    I will provide you with two jsons. Each json is the detailed data of a computer hardware device information.
                    --Requirements--
                    1. Please determine whether the two devices are compatible. If compatible, please return "True". Otherwise, return "False".
                    2. Do not return other information. Just return "True" or "False".
                    
                    --Data--
                    source_env_info: {source_env_info}
                    target_env_info: {target_env_info}
                    
                    --Result--
                    result:
                    """,
                )
            ]
        )

        chain = prompt_template | self.llm | StrOutputParser()
        result = chain.invoke(
            {
                "source_env_info": json.dumps(source_env_info.model_dump()),
                "target_env_info": json.dumps(target_env_info.model_dump()),
            }
        )
        try:
            result = bool(result)
        except Exception:
            result = False
        return result

    def _get_project_in_db(self, project_meta: Dict[str, Any]) -> Project | None:
        """
        从 TinyDB 中查询项目记录（通过项目名称进行匹配），并返回 Project 对象。
        """
        # 为方便查询，将项目名称在顶层存储，因此这里直接查询 "name" 字段
        query = {"name": project_meta["name"]}
        with self.nosql_db.using(self.table_name) as table:
            records = table.select(query)
        if records:
            record = records[0]
            # 从记录中还原 guides 列表
            guides_data: List[Dict[str, Any]] = record.get("guides", [])
            guides: List[Guide] = [
                Guide(
                    procedure=item["procedure"],
                    compatible_env=CompatibleEnv(**item["compatible_env"]),
                )
                for item in guides_data
            ]
            # 获取记录中存储的 project_id
            project_id = record.get("project_id", None)
            return Project(
                **record.get("project_meta", {}), guides=guides, id=project_id
            )
        else:
            return None

    def _project_to_db(self, project: Project) -> int:
        """
        将项目保存到 TinyDB 中：
          - 若 project.id 为 None，则执行插入操作，并利用返回的 doc_id 作为项目 id；
          - 否则执行更新操作。
        Returns:
            1（表示操作成功）
        """
        # 准备待保存的数据：
        # 这里除了存储 guides 和 project_meta 外，还将 project_meta 中的 "name" 字段在顶层存储，便于查询。
        record = {
            "guides": [guide.model_dump() for guide in project.guides],
            "project_meta": project.model_dump(exclude={"guides", "id"}),
            "name": project.model_dump(exclude={"guides", "id"}).get("name"),
        }
        with self.nosql_db.using(self.table_name) as table:
            if project.id is None:
                # generate project id
                project_id = utils.get_uuid()
                record["project_id"] = project_id
                table.insert(record)
            else:
                # 更新指定 doc_id 的记录
                table.update(record, query={"project_id": project.id})
        return 1  # 此处返回 1 表示成功

    def _merge_procedure(self, source_procedure: str, target_procedure: str) -> str:
        """
        合并 source_procedure 与 target_procedure，返回合并后的 MarkDown 格式流程。
        """
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Merge the source procedure with the target procedure.
                    --Requirements--
                    1. The merged procedure should be in a MarkDown format.
                    2. Just return the merged procedure. Do not return other information.
                    --Data--
                    source_procedure: {source_procedure}
                    target_procedure: {target_procedure}
                    --Result--
                    merged_procedure:
                    """,
                )
            ]
        )

        chain = prompt_template | self.llm | StrOutputParser()
        result: str = chain.invoke(
            {"source_procedure": source_procedure, "target_procedure": target_procedure}
        )

        return result

    def index(
        self, env_info: Dict[str, Any], procedure: str, project_meta: Dict[str, Any]
    ) -> int:
        """
        将解决方案写入知识库：
          - 若已有相同项目，则判断环境兼容性，兼容则合并流程，不兼容则新增 guide；
          - 若没有相同项目，则新建项目记录。
        Returns:
            1（表示操作成功）
        """
        env_info_obj = CompatibleEnv(**env_info)

        project = self._get_project_in_db(project_meta)
        if project:
            for guide in project.guides:
                is_compatible: bool = self._is_compatible_env(
                    env_info_obj, guide.compatible_env
                )
                if is_compatible:
                    # 合并流程
                    merged_procedure = self._merge_procedure(guide.procedure, procedure)
                    guide.procedure = merged_procedure
                    break
            else:  # 如果没有环境兼容的 guide，则新增一个 guide
                guide = Guide(procedure=procedure, compatible_env=env_info_obj)
                project.guides.append(guide)
        else:  # 新建项目
            guide = Guide(procedure=procedure, compatible_env=env_info_obj)
            project = Project(guides=[guide], **project_meta)

        # 将项目数据保存到 TinyDB
        return self._project_to_db(project)

    def retrieve(
        self, env_info: Dict[str, Any], project_meta: Dict[str, Any]
    ) -> Guide | None:
        """
        从知识库中检索与给定环境兼容的 guide。
        """
        env_info_obj = CompatibleEnv(**env_info)
        project = self._get_project_in_db(project_meta)
        if project:
            for guide in project.guides:
                is_compatible: bool = self._is_compatible_env(
                    env_info_obj, guide.compatible_env
                )
                if is_compatible:
                    return guide
        return None

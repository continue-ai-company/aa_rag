import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Dict, Any, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from aa_rag import setting
from aa_rag.gtypes.models.knowlege_base.solution import CompatibleEnv, Project, Guide
from aa_rag.knowledge_base.base import BaseKnowledge


class SolutionKnowledge(BaseKnowledge):
    _knowledge_name = "Solution"

    def __init__(self, relation_db_path: str = setting.db.relation.uri, **kwargs):
        """
        Solution Knowledge Base. Built-in Knowledge Base.
        Args:
            relation_db_path: The path of the relation database.
            **kwargs: The keyword arguments.
        """
        super().__init__(**kwargs)

        # create the directory and file if not exist
        relation_db_path_obj = Path(relation_db_path)
        if not relation_db_path_obj.exists():
            relation_db_path_obj.touch()
        # create the connection and create the table if not exist
        self.relation_db_conn = sqlite3.connect(relation_db_path)
        self.relation_table_name = self.knowledge_name.lower()
        self.relation_db_conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.relation_table_name} (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guides TEXT NOT NULL,
                project_meta TEXT NOT NULL)""")
        self.relation_db_conn.commit()

    def _is_compatible_env(
        self, source_env_info: CompatibleEnv, target_env_info: CompatibleEnv
    ) -> bool:
        """
        Check if the source environment is compatible with the target environment.
        Args:
            source_env_info: to be checked
            target_env_info: to be checked

        Returns:
            bool: True if compatible, False otherwise.
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
        except:
            result = False
        return result

    def _get_project_in_db(self, project_meta: Dict[str, Any]) -> Project | None:
        """
        Retrieve the project from the database and return the project object.
        Args:
            project_meta: The project meta information.

        Returns:
            Project: The project object if found, None otherwise.

        """
        with closing(self.relation_db_conn.cursor()) as cursor:
            cursor.execute(f"""
                SELECT project_id,guides,project_meta
                 FROM {self.relation_table_name}
                WHERE json_extract(project_meta, '$.name') = '{project_meta["name"]}'
            """)
            result = cursor.fetchone()
            if result:
                project_id, guide_s_str, project_meta_str = result
            else:
                return None
            if guide_s_str:
                guide_s: List[Guide] = [
                    Guide(
                        procedure=json.loads(_)["procedure"],
                        compatible_env=CompatibleEnv(**json.loads(_)["compatible_env"]),
                    )
                    for _ in json.loads(guide_s_str)
                ]
                return Project(
                    **{"guides": guide_s, **json.loads(project_meta_str)}, id=project_id
                )

            else:
                return None

    def _merge_procedure(self, source_procedure: str, target_procedure: str) -> str:
        """
        Merge the source procedure with the target procedure.
        Args:
            source_procedure: The source procedure to be merged.
            target_procedure: The target procedure to be merged.

        Returns:
            str: The merged procedure.

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

    def _project_to_db(self, project: Project):
        """
        Save the project to the database.
        Args:
            project: The project to be saved.

        Returns:
            affected_rows: The number of affected rows.
        """

        # if project.id is None, insert the project, otherwise update the project

        with closing(self.relation_db_conn.cursor()) as cursor:
            guides_json = json.dumps([_.model_dump_json() for _ in project.guides])
            project_meta_json = project.model_dump_json(
                exclude={"guides", "id"}, exclude_none=True
            )
            if project.id is None:
                cursor.execute(
                    f"""
                    INSERT INTO {self.relation_table_name} (guides, project_meta)
                    VALUES (?, ?)""",
                    (guides_json, project_meta_json),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE {self.relation_table_name}
                    SET guides = ?, project_meta = ?
                    WHERE project_id = ?
                """,
                    (guides_json, project_meta_json, project.id),
                )

            self.relation_db_conn.commit()

            affected_rows = cursor.rowcount
        return affected_rows

    def index(
        self, env_info: Dict[str, Any], procedure: str, project_meta: Dict[str, Any]
    ) -> int:
        """
        Index the solution to the knowledge base.
        Args:
            env_info: Environment information.
            procedure: The deployment procedure of the solution.
            project_meta: The project meta information.

        Returns:
            affected_rows: The number of affected rows.

        """
        env_info = CompatibleEnv(**env_info)

        project = self._get_project_in_db(project_meta)
        if project:
            for guide in project.guides:
                is_compatible: bool = self._is_compatible_env(
                    env_info, guide.compatible_env
                )
                if is_compatible:
                    # merge the procedure
                    merged_procedure = self._merge_procedure(guide.procedure, procedure)
                    # update the guide
                    guide.procedure = merged_procedure
                    break
            else:  # if not compatible, create a new guide
                guide = Guide(procedure=procedure, compatible_env=env_info)
                project.guides.append(guide)

        else:  # create a new project
            guide = Guide(procedure=procedure, compatible_env=env_info)
            project = Project(guides=[guide], **project_meta)

        # push the project to the database
        return self._project_to_db(project)

    def retrieve(
        self, env_info: Dict[str, Any], project_meta: Dict[str, Any]
    ) -> Guide | None:
        env_info: CompatibleEnv = CompatibleEnv(**env_info)
        # check if there is the same project name in db
        project: Project = self._get_project_in_db(project_meta)
        if project:
            for guide in project.guides:
                is_compatible: bool = self._is_compatible_env(
                    env_info, guide.compatible_env
                )
                if is_compatible:
                    return guide
        else:
            return None

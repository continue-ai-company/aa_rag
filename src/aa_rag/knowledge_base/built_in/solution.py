import ast
from typing import Dict, Any, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from aa_rag import utils, setting
from aa_rag.db.base import BaseNoSQLDataBase
from aa_rag.gtypes.enums import NoSQLDBType
from aa_rag.gtypes.models.knowlege_base.solution import CompatibleEnv, Project, Guide
from aa_rag.knowledge_base.base import BaseKnowledge


class SolutionKnowledge(BaseKnowledge):
    @property
    def knowledge_name(self):
        return "Solution"

    def __init__(self, nosql_db: NoSQLDBType = setting.storage.nosql, **kwargs):
        """
        Initialize the SolutionKnowledge class.

        Args:
            nosql_db (NoSQLDBType): The type of NoSQL database to use (default is TinyDB).
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.nosql_db: BaseNoSQLDataBase = utils.get_db(nosql_db)
        self.table_name = self.knowledge_name.lower()

    def _is_compatible_env(
        self, source_env_info: CompatibleEnv, target_env_info: CompatibleEnv
    ) -> bool:
        """
        Determine if source_env_info is compatible with target_env_info.

        Args:
            source_env_info (CompatibleEnv): The source environment information.
            target_env_info (CompatibleEnv): The target environment information.

        Returns:
            bool: True if compatible, False otherwise.
        """
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert in computer hardware device information. I will provide you with two jsons. Each json is the detailed data of a computer hardware device information. Please determine whether the two devices are compatible.
                    --Requirements--
                    1. Please determine whether the two device environments are compatible when i install a software in each devices. If compatible, please return "True". Otherwise, return "False".
                    2. Different operating system platform are not compatible.
                    3. Different CPU architecture are not compatible.
                    4. Please compare the platform and architecture of the two devices and strictly judge according to my requirements.
                    5. Do not return other information. Just return "True" or "False" according to the requirements.
                    
                    
                    --Example 1--
                    -Input-
                    source_env_info: {{"platform": "windows","arch": "x64"}}
                    target_env_info: {{"platform": "darwin","arch": "arm64"}}
                    
                    -Output- 
                    False
                    
                    --Example 2--
                    -Input-
                    source_env_info: {{"platform": "darwin","arch": "m2"}}
                    target_env_info: {{"platform": "darwin","arch": "m3"}}
                    
                    -Output-
                    True
                    
                    
                    --Real Data--
                    -Input-
                    source_env_info: {source_env_info}
                    target_env_info: {target_env_info}
                    
                    -Output-
                    """,
                )
            ]
        )

        chain = prompt_template | self.llm | StrOutputParser()
        result = chain.invoke(
            {
                "source_env_info": source_env_info.model_dump(),
                "target_env_info": target_env_info.model_dump(),
            }
        )
        try:
            # result=bool(result)
            result = ast.literal_eval(result)
        except Exception:
            result = False
        return result

    def _get_project_in_db(self, project_meta: Dict[str, Any]) -> Project | None:
        """
        Retrieve a project record from TinyDB by project name and return a Project object.

        Args:
            project_meta (Dict[str, Any]): The project metadata.

        Returns:
            Project | None: The Project object if found, None otherwise.
        """
        query = {"name": project_meta["name"]}
        with self.nosql_db.using(self.table_name) as table:
            records = table.select(query)
        if records:
            record = records[0]
            guides_data: List[Dict[str, Any]] = record.get("guides", [])
            guides: List[Guide] = [
                Guide(
                    procedure=item["procedure"],
                    compatible_env=CompatibleEnv(**item["compatible_env"]),
                )
                for item in guides_data
            ]
            project_id = record.get("project_id", None)
            return Project(
                **record.get("project_meta", {}), guides=guides, id=project_id
            )
        else:
            return None

    def _project_to_db(self, project: Project) -> int:
        """
        Save a project to TinyDB. Insert if project.id is None, otherwise update.

        Args:
            project (Project): The project to save.

        Returns:
            int: 1 indicating success.
        """
        record = {
            "guides": [guide.model_dump() for guide in project.guides],
            "project_meta": project.model_dump(exclude={"guides", "id"}),
            "name": project.model_dump(exclude={"guides", "id"}).get("name"),
        }
        with self.nosql_db.using(self.table_name) as table:
            if project.id is None:
                project_id = utils.get_uuid()
                record["project_id"] = project_id
                table.insert(record)
            else:
                table.update(record, query={"project_id": project.id})
        return 1

    def _merge_procedure(self, source_procedure: str, target_procedure: str) -> str:
        """
        Merge source_procedure with target_procedure and return the merged procedure in MarkDown format.

        Args:
            source_procedure (str): The source procedure.
            target_procedure (str): The target procedure.

        Returns:
            str: The merged procedure in MarkDown format.
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
        Write a solution to the knowledge base. Merge procedures if compatible, otherwise add a new guide.

        Args:
            env_info (Dict[str, Any]): The environment information.
            procedure (str): The procedure to index.
            project_meta (Dict[str, Any]): The project metadata.

        Returns:
            int: 1 indicating success.
        """
        env_info_obj = CompatibleEnv(**env_info)

        project = self._get_project_in_db(project_meta)
        if project:
            for guide in project.guides:
                is_compatible: bool = self._is_compatible_env(
                    env_info_obj, guide.compatible_env
                )
                if is_compatible:
                    merged_procedure = self._merge_procedure(guide.procedure, procedure)
                    guide.procedure = merged_procedure
                    break
            else:
                guide = Guide(procedure=procedure, compatible_env=env_info_obj)
                project.guides.append(guide)
        else:
            guide = Guide(procedure=procedure, compatible_env=env_info_obj)
            project = Project(guides=[guide], **project_meta)

        return self._project_to_db(project)

    def retrieve(
        self, env_info: Dict[str, Any], project_meta: Dict[str, Any]
    ) -> Guide | None:
        """
        Retrieve a guide from the knowledge base that is compatible with the given environment.

        Args:
            env_info (Dict[str, Any]): The environment information.
            project_meta (Dict[str, Any]): The project metadata.

        Returns:
            Guide | None: The compatible guide if found, None otherwise.
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

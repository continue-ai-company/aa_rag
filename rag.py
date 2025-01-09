import json
import dotenv

from retrieve import RetrieveKnowledge

dotenv.load_dotenv(dotenv.find_dotenv())


async def retriever(vo):
    result = ""
    assert "input" in vo, "input is required"
    input: str = vo["input"]
    knowlegde_name: str = vo.get("knowledge_name", "default")
    retrieve_type: str = vo.get("retrieve_type", "hybrid")

    retriever = RetrieveKnowledge(knowlegde_name, retrieve_type=retrieve_type)

    result = retriever.retrieve(input,only_page_content=False)

    return json.dumps({"result": result})


def regAPI(vo):
    vo["retriever"] = retriever


default = regAPI
__all__ = ["default", "regAPI"]

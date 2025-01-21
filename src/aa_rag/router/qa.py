from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter(
    prefix="/qa", tags=["qa"], responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "问题/解决方案库",
    }


class TmpItem(BaseModel):
    model_config = ConfigDict(extra="allow")


@router.post("/index")
async def index(item: TmpItem):
    return item


@router.post("/retrieve")
async def retrieve(item: TmpItem):
    return item

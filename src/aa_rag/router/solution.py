from fastapi import APIRouter

router = APIRouter(
    prefix="/solution", tags=["solution"], responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "项目部署方案库",
    }

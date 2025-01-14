from fastapi import APIRouter

router = APIRouter(
    prefix="/qa", tags=["qa"], responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "问题/解决方案库",
    }

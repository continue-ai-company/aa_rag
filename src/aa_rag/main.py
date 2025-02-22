from fastapi import FastAPI
from pydantic import SecretStr, BaseModel

from aa_rag import setting
from aa_rag.exceptions import handle_exception_error
from aa_rag.router import qa, solution, index, retrieve

app = FastAPI()
app.include_router(qa.router)
app.include_router(solution.router)
app.include_router(index.router)
app.include_router(retrieve.router)
app.add_exception_handler(Exception, handle_exception_error)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/default")
async def default():
    def mask_secrets(model: BaseModel) -> dict:
        """
        Mask secrets in the model.
        # !! It should be implemented by pydantic-settings, but it's not working now.
        """

        def recursive_mask(obj):
            if isinstance(obj, BaseModel):
                masked = {}
                for name, field in obj.__fields__.items():  # 使用__fields__获取字段定义
                    value = getattr(obj, name)

                    # 检查字段类型是否是SecretStr
                    if field.annotation is SecretStr:
                        masked[name] = value[:2] + len(value[2:-4]) * "*" + value[-4:]
                    # 处理嵌套模型
                    elif isinstance(value, BaseModel):
                        masked[name] = recursive_mask(value)
                    # 处理列表中的模型（可选）
                    elif isinstance(value, list):
                        masked[name] = [
                            recursive_mask(i) if isinstance(i, BaseModel) else i
                            for i in value
                        ]
                    else:
                        masked[name] = value
                return masked
            return obj

        return recursive_mask(model)

    return mask_secrets(setting)


def startup():
    import uvicorn

    uvicorn.run(app, host=setting.server.host, port=setting.server.port)


if __name__ == "__main__":
    startup()

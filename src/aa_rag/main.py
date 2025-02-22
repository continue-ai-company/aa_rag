from fastapi import FastAPI

from aa_rag import setting
from aa_rag.exceptions import handle_exception_error
from aa_rag.router import qa, solution, index, retrieve
from aa_rag.settings import mask_secrets

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
    return mask_secrets(setting)


def startup():
    import uvicorn

    uvicorn.run(app, host=setting.server.host, port=setting.server.port)


if __name__ == "__main__":
    startup()

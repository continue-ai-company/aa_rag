from fastapi import FastAPI

from aa_rag import setting
from aa_rag.exceptions import handle_exception_error, handel_FileNotFoundError
from aa_rag.router import qa, solution, index, retrieve

app = FastAPI()
app.include_router(qa.router)
app.include_router(solution.router)
app.include_router(index.router)
app.include_router(retrieve.router)
app.add_exception_handler(Exception, handle_exception_error)
app.add_exception_handler(FileNotFoundError, handel_FileNotFoundError)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/default")
async def default():
    return setting.model_dump()


def startup():
    import uvicorn

    uvicorn.run(app, host=setting.server.host, port=setting.server.port)


if __name__ == "__main__":
    startup()

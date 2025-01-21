from fastapi import FastAPI
from pydantic import ValidationError

from aa_rag import setting
from aa_rag.exceptions import *
from aa_rag.router import qa, solution, index, retrieve

app = FastAPI()
app.include_router(qa.router)
app.include_router(solution.router)
app.include_router(index.router)
app.include_router(retrieve.router)
app.add_exception_handler(ValidationError, handle_validation_error)
app.add_exception_handler(AssertionError, handle_assertion_error)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/default")
async def default():
    return setting.model_dump()


def startup():
    import uvicorn

    uvicorn.run(app, host=setting.server.host, port=setting.server.port)

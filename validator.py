from fastapi import FastAPI, Request
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import asyncio

app = FastAPI()


class ValidateRequest(BaseModel):
    checker: str
    candidate: str
    entrypoint: str
    timeout: int


executor = ThreadPoolExecutor(max_workers=8)


def f(checker, candidate, entrypoint):
    try:
        namespace = {}
        exec(candidate + "\n" + checker, namespace)
        f = namespace[entrypoint]
        f_check = namespace["check"]
        f_check(f)
        return True
    except:
        return False


async def f_with_timeout(checker, candidate, entrypoint, timeout):
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(loop.run_in_executor(executor, f, checker, candidate, entrypoint), timeout)
    except (TimeoutError, asyncio.TimeoutError):
        return False


@app.post("/validate")
async def validate(request: Request, args: ValidateRequest):
    return {"res": await f_with_timeout(**args.model_dump())}

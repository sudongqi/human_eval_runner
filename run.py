import os
import aiohttp
import asyncio
from mbp.llm import *
from mbp import *


MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"

EOS = [
    "\nif __name__",
    "\ndef main",
    "\nprint(",
    "\n#",
    "\n```"
]


async def f(session, data, idx):
    prompt = f"""<|im_start|>system
You are an intelligent programming assistant to produce Python algorithmic solutions<|im_end|>
<|im_start|>user
Can you complete the following Python function?
```python
{data[idx]["prompt"]}
```
<|im_end|>
<|im_start|>assistant
```python
"""
    async with session.post(
        "http://localhost:8000/v1/completions",
        headers={"Content-Type": "application/json"},
        json={"model": MODEL, "max_tokens": 512, "temperature": 0, "prompt": prompt, "stop": EOS}
    ) as resp:
        try:
            res = await resp.json()
            return res["choices"][0]["text"]
        except:
            return ""


async def infer():
    data = list(load_jsonl(this_dir("HumanEval.jsonl.gz"), compression="gz"))
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[f(session, data, i) for i, _ in enumerate(data)])
    save_jsonl(this_dir("output.jsonl"), [{**d, "output": r} for d, r in zip(data, results)])


async def validate(session, d):
    async with session.post(
        "http://localhost:8001/validate",
        headers={"Content-Type": "application/json"},
        json={"candidate": d["output"], "checker": d["test"], "entrypoint": d["entry_point"], "timeout": 3}
    ) as response:
        return await response.json()


async def eval():
    async with aiohttp.ClientSession() as session:
        tasks = [validate(session, d) for d in load_jsonl("output.jsonl")]
        results = await asyncio.gather(*tasks)
        print(sum(int(r["res"]) for r in results))


if __name__ == "__main__":
    args = get_args("action?")
    if args.action == "vllm":
        os.system(f"docker run --gpus all -p 8000:8000 vllm/vllm-openai --model {MODEL}")
    elif args.action == "validator":
        os.system(f"docker build -t validator .")
        os.system(f"docker run -it -p 8001:80 validator bash")
    elif args.action == "infer":
        asyncio.run(infer())
    elif args.action == "eval":
        asyncio.run(eval())

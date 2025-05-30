import os
import json
import aiohttp
import asyncio
from mbp.llm import *
from mbp import *


MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
MSG = build_system_message_from_yaml(this_dir("code_completion.yaml"))


async def f(session, prompt):
    async with session.post(
        "http://localhost:8000/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": MODEL,
            "response_format": {"type": "json_object"},
            "messages": build_messages(MSG, {"prompt": prompt})
        }
    ) as resp:
        try:
            res = await resp.json()
            return json.loads(res["choices"][0]["message"]["content"])
        except:
            return "pass"


async def infer():
    data = list(load_jsonl(this_dir("HumanEval.jsonl.gz"), compression="gz"))
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[f(session, d["prompt"]) for d in data])
    save_jsonl(this_dir("output.jsonl"), [{**d, "output": r["completion"]} for d, r in zip(data, results)])


def eval():
    num_pass = 0
    for d in load_jsonl("output.jsonl"):
        f_str = d["prompt"] + "\n".join(["    " + l.strip() for l in d["output"].split("\n")])
        try:
            namespace = {}
            exec(f_str + "\n" + d["test"], namespace)
            f = namespace[d["entry_point"]]
            f_check = namespace["check"]
            f_check(f)
            num_pass += 1
        except:
            continue
    print(num_pass)


if __name__ == "__main__":
    args = get_args("action?")
    if args.action == "run-vllm":
        os.system(f"docker run --gpus all -p 8000:8000 vllm/vllm-openai --model {MODEL}")
    elif args.action == "infer":
        asyncio.run(infer())
    elif args.action == "eval":
        eval()

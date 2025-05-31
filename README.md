# Human Eval Runner

### Resources

- [qwen-2.5-repo](https://github.com/QwenLM/Qwen2.5-Coder/tree/main)
- [qwen-2.5-technical-report](https://arxiv.org/pdf/2409.12186)
- [human-eval-repo](https://github.com/openai/human-eval)

### Setup

`python -m pip install mbp`

make sure Docker is running in the background

### How to Run

```
python run.py vllm
python run.py validator
python run.py infer
python run.py eval
```

### Benchmark

- Qwen/Qwen2.5-Coder-0.5B-Instruct: 0.604

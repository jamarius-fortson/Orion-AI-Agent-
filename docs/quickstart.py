# -*- coding: utf-8 -*-
"""
OrionAgent â€” Basic Agent Invocation Example
============================================

Demonstrates the minimal setup required to run an OrionAgent query
using OpenAI's GPT models or a locally hosted MAT fine-tuned model.
"""

import os
import subprocess
import sys

# â”€â”€â”€ Example 1: Run via CLI (OpenAI) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def run_openai_example():
    """
    Execute an OrionAgent query using OpenAI's GPT-3.5-turbo.
    Ensure OPENAI_API_KEY is set in your environment or .env file.
    """
    query = "What are the latest breakthroughs in large language model research?"
    cmd = [
        "orionagent",
        f"--query={query}",
        "--llm_name=gpt-3.5-turbo",
        "--lang=en",
    ]
    print(f"[OrionAgent] Running: {' '.join(cmd)}\n")
    subprocess.run(cmd, check=True)


# â”€â”€â”€ Example 2: Run via CLI (Local MAT Model) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def run_local_model_example():
    """
    Execute an OrionAgent query using a locally deployed MAT model.
    Requires the model to be served via vLLM + FastChat or llama-cpp-python.

    See README.md for model serving instructions.
    """
    query = "Summarize the key findings from the OrionAgent research paper."
    cmd = [
        "orionagent",
        f"--query={query}",
        "--llm_name=OrionAgentlms_qwen_14b_mat",
        "--use_local_llm",
        "--local_llm_host=localhost",
        "--local_llm_port=8888",
        "--lang=en",
    ]
    print(f"[OrionAgent] Running: {' '.join(cmd)}\n")
    subprocess.run(cmd, check=True)


# â”€â”€â”€ Example 3: Programmatic API Usage â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def run_programmatic_example():
    """
    Demonstrates direct programmatic usage of the OrionAgent system.
    """
    try:
        from orionagent.agent_start import main as orion_main
        import sys

        # Simulate CLI arguments programmatically
        sys.argv = [
            "orionagent",
            "--query=Who won the Nobel Prize in Physics in 2023?",
            "--llm_name=gpt-4",
            "--lang=en",
        ]
        orion_main()
    except ImportError as e:
        print(f"[Error] OrionAgent not installed. Run: pip install -e .")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("  OrionAgent â€” Quick Start Examples")
    print("=" * 60)

    mode = sys.argv[1] if len(sys.argv) > 1 else "openai"

    if mode == "openai":
        run_openai_example()
    elif mode == "local":
        run_local_model_example()
    elif mode == "api":
        run_programmatic_example()
    else:
        print(f"Usage: python quickstart.py [openai|local|api]")


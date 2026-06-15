"""
executor.py — Docker sandbox for safe code execution.

Each submission spins up a fresh python:3.11-slim container with:
  - No network access
  - 128MB memory limit
  - 50% CPU quota
  - 3-second hard timeout (SIGKILL)
  - Code passed as a `python -c` argument — no shared filesystem with
    the host needed (works correctly even when Docker is accessed via
    a mounted socket from inside another container)

Results are streamed back one test at a time via an async generator,
so the WebSocket layer can forward each result the moment it completes.
"""

import asyncio
import json
import textwrap
import docker
from typing import AsyncIterator
from app.config import settings


# One Docker client, reused across requests
_docker_client = docker.from_env(timeout=settings.sandbox_timeout + 5)

def _build_runner_script(code: str, test_cases: list[dict]) -> str:
    """
    Generates the Python script that runs inside the container.
    It imports the user's solution, runs each test, and prints a
    JSON result line per test to stdout.
    """
    # Escape the user's code to embed safely as a string
    escaped_code = code.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

    tests_json = json.dumps(test_cases)

    return textwrap.dedent(f'''
import sys, json, time, traceback, io, contextlib

USER_CODE = """{escaped_code}"""

TEST_CASES = json.loads({tests_json!r})

# Execute the user code in a fresh namespace
user_namespace = {{}}
try:
    exec(compile(USER_CODE, "<submission>", "exec"), user_namespace)
except Exception as e:
    # Syntax or import error — fail all tests immediately
    for i, tc in enumerate(TEST_CASES):
        result = {{
            "index": i,
            "status": "error",
            "input": tc["input"],
            "expected": tc["expected"],
            "actual": None,
            "error": f"{{type(e).__name__}}: {{e}}",
            "elapsed_ms": 0,
        }}
        print(json.dumps(result), flush=True)
    sys.exit(0)

# The user must define a function called `solution`
solution_fn = user_namespace.get("solution")
if solution_fn is None:
    for i, tc in enumerate(TEST_CASES):
        result = {{
            "index": i,
            "status": "error",
            "input": tc["input"],
            "expected": tc["expected"],
            "actual": None,
            "error": "No function named `solution` found. Make sure your function is named `solution`.",
            "elapsed_ms": 0,
        }}
        print(json.dumps(result), flush=True)
    sys.exit(0)

# Run each test case
for i, tc in enumerate(TEST_CASES):
    raw_input = tc["input"]
    expected  = tc["expected"]
    start = time.perf_counter()
    try:
        # Parse input — support multi-arg via comma separation
        args = eval(f"({{raw_input}},)", {{}}, {{}}) if "," in raw_input else (eval(raw_input, {{}}, {{}}),)
        actual = solution_fn(*args)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        actual_str = repr(actual)
        passed = actual_str == expected.strip() or str(actual) == expected.strip()
        result = {{
            "index": i,
            "status": "passed" if passed else "failed",
            "input": raw_input,
            "expected": expected,
            "actual": actual_str,
            "error": None,
            "elapsed_ms": elapsed,
        }}
    except Exception as e:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        result = {{
            "index": i,
            "status": "error",
            "input": raw_input,
            "expected": expected,
            "actual": None,
            "error": f"{{type(e).__name__}}: {{e}}",
            "elapsed_ms": elapsed,
        }}
    print(json.dumps(result), flush=True)
''')


async def run_tests_streamed(
    code: str,
    test_cases: list[dict],
) -> AsyncIterator[dict]:
    """
    Async generator that yields one test result dict at a time.
    The WebSocket handler consumes this and forwards each result
    to the client as soon as it arrives.
    """
    runner_script = _build_runner_script(code, test_cases)

    # Run the container in a thread pool (docker SDK is sync)
    loop = asyncio.get_event_loop()
    container_output = await loop.run_in_executor(
        None, _run_container_sync, runner_script
    )

    # Parse output line by line — each line is a JSON test result
    for line in container_output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            result = json.loads(line)
            yield result
            # Small yield to let WebSocket flush each result
            await asyncio.sleep(0)
        except json.JSONDecodeError:
            # Unexpected output — skip silently
            continue


def _run_container_sync(runner_script: str) -> str:
    """
    Synchronous Docker execution (runs in thread pool).
    The runner script is passed directly as a `python -c` argument —
    this avoids bind-mounting a file, which would require the path to
    exist on the HOST (since we're talking to the host Docker daemon
    via the mounted socket, a classic Docker-out-of-Docker gotcha).
    Returns stdout as a string.
    """
    try:
        output = _docker_client.containers.run(
            image=settings.sandbox_image,
            command=["python", "-c", runner_script],
            network_disabled=True,           # No network access
            mem_limit=settings.sandbox_mem_limit,
            cpu_quota=settings.sandbox_cpu_quota,
            cpu_period=100000,
            remove=True,                      # Auto-cleanup container
            stdout=True,
            stderr=True,
        )
        return output.decode("utf-8") if isinstance(output, bytes) else output

    except Exception as e:
        error_type = type(e).__name__
        if "Timeout" in error_type or "timeout" in str(e).lower():
            return _timeout_results()
        return _error_results(f"{error_type}: {e}")


def _timeout_results() -> str:
    return json.dumps({
        "index": 0,
        "status": "timeout",
        "input": "",
        "expected": "",
        "actual": None,
        "error": "Execution timed out (3s limit). Check for infinite loops.",
        "elapsed_ms": 3000,
    })


def _error_results(msg: str) -> str:
    return json.dumps({
        "index": 0,
        "status": "error",
        "input": "",
        "expected": "",
        "actual": None,
        "error": f"Sandbox error: {msg}",
        "elapsed_ms": 0,
    })
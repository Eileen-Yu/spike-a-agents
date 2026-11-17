"""Order-status agent built with HolmesGPT, served over HTTP.

HolmesGPT is a CLI agent, so this calls `holmes ask` with a custom toolset
(toolsets.yaml) and reads the answer from its JSON output.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TOOLSETS = Path(__file__).with_name("toolsets.yaml")


async def ask(prompt: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "result.json"
        proc = await asyncio.create_subprocess_exec(
            "holmes", "ask", prompt,
            "--model", MODEL,
            "--custom-toolsets", str(TOOLSETS),
            "--no-interactive",
            "--json-output-file", str(out),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await proc.communicate()
        if proc.returncode != 0 or not out.exists():
            raise HTTPException(status_code=500, detail=output.decode()[-2000:])
        return json.loads(out.read_text()).get("result") or ""


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

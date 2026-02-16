#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
uv run uvicorn app.main:app --reload --port 8000

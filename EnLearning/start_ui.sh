#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
REQ_FILE="${ROOT_DIR}/requirements.txt"
APP_FILE="${ROOT_DIR}/ui/app.py"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

pip install -r "${REQ_FILE}"

if [[ -z "${DASHSCOPE_API_KEY:-}" ]]; then
  echo "错误：请先设置环境变量 DASHSCOPE_API_KEY"
  echo "示例：export DASHSCOPE_API_KEY=\"你的Key\""
  exit 1
fi

python "${APP_FILE}"

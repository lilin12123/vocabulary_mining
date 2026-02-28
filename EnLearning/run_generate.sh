#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${ROOT_DIR}/config.env"
VENV_DIR="${ROOT_DIR}/.venv"
REQ_FILE="${ROOT_DIR}/requirements.txt"
APP_FILE="${ROOT_DIR}/cli/generate.py"

if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "错误：未找到配置文件 ${CONFIG_FILE}"
  echo "请先复制 ${ROOT_DIR}/config.env.example -> ${CONFIG_FILE} 并填写参数"
  exit 1
fi

# shellcheck disable=SC1090
source "${CONFIG_FILE}"

USE_WEB_TOOLS_FLAG=""
ENABLE_THINKING_FLAG=""
USE_CODE_INTERPRETER_FLAG=""

if [[ "${USE_WEB_TOOLS:-}" == "1" || "${USE_WEB_TOOLS:-}" == "true" ]]; then
  USE_WEB_TOOLS_FLAG="--use-web-tools"
fi
if [[ "${ENABLE_THINKING:-}" == "1" || "${ENABLE_THINKING:-}" == "true" ]]; then
  ENABLE_THINKING_FLAG="--enable-thinking"
fi
if [[ "${USE_CODE_INTERPRETER:-}" == "1" || "${USE_CODE_INTERPRETER:-}" == "true" ]]; then
  USE_CODE_INTERPRETER_FLAG="--use-code-interpreter"
fi

if [[ -z "${OUTPUT_DIR:-}" ]]; then
  echo "错误：OUTPUT_DIR 不能为空"
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
pip install -r "${REQ_FILE}"

python "${APP_FILE}" \
  --input-file "${INPUT_FILE:-}" \
  --input-url "${INPUT_URL:-}" \
  --output-dir "${OUTPUT_DIR}" \
  --date "${DATE:-}" \
  --word-count "${WORD_COUNT:-70}" \
  --phrase-count "${PHRASE_COUNT:-50}" \
  --model "${MODEL:-qwen-plus}" \
  --base-url "${BASE_URL:-}" \
  --temperature "${TEMPERATURE:-0.2}" \
  ${USE_WEB_TOOLS_FLAG} \
  ${ENABLE_THINKING_FLAG} \
  ${USE_CODE_INTERPRETER_FLAG} \
  ${TIMEOUT:+--timeout "${TIMEOUT}"} \
  ${REGION:+--region "${REGION}"} \
  --api-key "${DASHSCOPE_API_KEY:-}"

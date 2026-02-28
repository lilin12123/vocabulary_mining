# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path

from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parents[2]))

from EnLearning.lib import deduper
from EnLearning.prompts.prompt import DPOGenerationPrompts

DEFAULT_MODEL = "qwen-plus"
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_BASE_URL_TOOLS = "https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1"
DEFAULT_TIMEOUT = 60
MAX_MATERIAL_CHARS = 12000


def _normalize_date(date_str: str | None) -> str:
    if not date_str:
        return _dt.date.today().strftime("%Y%m%d")
    if re.fullmatch(r"\d{8}", date_str):
        return date_str
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str.replace("-", "")
    raise ValueError("日期格式应为 YYYY-MM-DD 或 YYYYMMDD")


def _render_prompt(template: str, material: str, count: int) -> str:
    if "$1" not in template and "$2" not in template:
        return f"{template}\n\nMaterial:\n{material}\n\nCount: {count}".strip()
    return template.replace("$1", material).replace("$2", str(count))


def _call_llm_chat(
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
    timeout_s: int,
) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_s)
    print(f"[LLM] chat.completions model={model} base_url={base_url} temp={temperature}")
    print(f"[LLM] prompt_chars={len(prompt)}")
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return completion.choices[0].message.content or ""


def _call_llm_with_tools(
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
    enable_thinking: bool,
    use_code_interpreter: bool,
    timeout_s: int,
) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_s)
    tools = [
        {"type": "web_search"},
        {"type": "web_extractor"},
    ]
    if use_code_interpreter:
        tools.append({"type": "code_interpreter"})
    print(f"[LLM] responses.create model={model} base_url={base_url} temp={temperature}")
    print(f"[LLM] tools={','.join(t['type'] for t in tools)} enable_thinking={enable_thinking}")
    print(f"[LLM] prompt_chars={len(prompt)}")
    response = client.responses.create(
        model=model,
        input=prompt,
        tools=tools,
        temperature=temperature,
        extra_body={"enable_thinking": enable_thinking},
    )
    return response.output_text or ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate EnLearning words/phrases via LLM.")
    parser.add_argument("--input-file", default="", help="输入文本文件路径")
    parser.add_argument("--input-url", default="", help="输入 URL（HTML 或 PDF）")
    parser.add_argument("--output-dir", required=True, help="输出目录（YYYYMMDD 子目录会创建在其下）")
    parser.add_argument("--date", default="", help="日期 YYYYMMDD 或 YYYY-MM-DD（默认今天）")
    parser.add_argument("--word-count", type=int, default=70)
    parser.add_argument("--phrase-count", type=int, default=50)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--use-web-tools", action="store_true", help="启用百炼网页检索/抓取工具")
    parser.add_argument("--enable-thinking", action="store_true", help="启用思考模式（某些模型需要）")
    parser.add_argument("--use-code-interpreter", action="store_true", help="启用代码解释器工具（可选）")
    parser.add_argument("--region", default="CN", help="百炼地域：CN 或 INTL")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="请求超时（秒）")
    parser.add_argument("--api-key", default="", help="阿里云百炼 API Key")
    args = parser.parse_args()

    material = ""
    if args.input_file:
        material = Path(args.input_file).read_text(encoding="utf-8")
    if args.input_url:
        # 仅将 URL 交给 LLM 处理
        material = f"{material}\n\nURL: {args.input_url}".strip()

    if not material:
        raise SystemExit("错误：未提供输入文件或 URL。")

    if len(material) > MAX_MATERIAL_CHARS:
        print(f"[Input] material_chars={len(material)} 超过上限 {MAX_MATERIAL_CHARS}，已截断")
        material = material[:MAX_MATERIAL_CHARS]
    print(f"[Input] material_chars={len(material)}")
    if args.input_url:
        print(f"[Input] input_url={args.input_url}")

    yyyymmdd = _normalize_date(args.date)
    api_key = args.api_key.strip() or os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("错误：未提供 API Key。")

    prompts = DPOGenerationPrompts()
    word_prompt = _render_prompt(
        prompts.english_word_extraction.strip(), material, args.word_count
    )
    phrase_prompt = _render_prompt(
        prompts.english_phrases_extraction.strip(), material, args.phrase_count
    )

    use_tools = args.use_web_tools or bool(args.input_url)
    base_url = args.base_url
    if use_tools and not base_url:
        base_url = DEFAULT_BASE_URL_TOOLS
    if not use_tools and not base_url:
        base_url = DEFAULT_BASE_URL

    if use_tools and args.region.upper() == "INTL":
        raise SystemExit("错误：网页检索/网页阅读工具在 Responses API 中仅支持中国内地地域。请设置 REGION=CN。")

    enable_thinking = args.enable_thinking
    if use_tools and args.model == "qwen3-max-2026-01-23" and not enable_thinking:
        print("提示：qwen3-max-2026-01-23 需要 enable_thinking，已自动开启。")
        enable_thinking = True
    use_code_interpreter = args.use_code_interpreter
    if use_tools and args.model not in {"qwen3-max", "qwen3-max-2026-01-23"}:
        print("提示：Responses API 网页工具优先支持 qwen3-max / qwen3-max-2026-01-23，当前模型可能不兼容。")
    print(f"[Config] use_tools={use_tools} model={args.model} base_url={base_url}")
    print(f"[Config] enable_thinking={enable_thinking} use_code_interpreter={use_code_interpreter} region={args.region}")
    print(f"[Config] timeout_s={args.timeout}")

    print("开始生成 words...")
    if use_tools:
        try:
            words_md = _call_llm_with_tools(
                api_key,
                base_url,
                args.model,
                word_prompt,
                args.temperature,
                enable_thinking,
                use_code_interpreter,
                args.timeout,
            )
        except Exception as exc:
            raise SystemExit(f"words 生成失败：{exc}") from exc
    else:
        try:
            words_md = _call_llm_chat(
                api_key, base_url, args.model, word_prompt, args.temperature, args.timeout
            )
        except Exception as exc:
            raise SystemExit(f"words 生成失败：{exc}") from exc
    print("开始生成 phrases...")
    if use_tools:
        try:
            phrases_md = _call_llm_with_tools(
                api_key,
                base_url,
                args.model,
                phrase_prompt,
                args.temperature,
                enable_thinking,
                use_code_interpreter,
                args.timeout,
            )
        except Exception as exc:
            raise SystemExit(f"phrases 生成失败：{exc}") from exc
    else:
        try:
            phrases_md = _call_llm_chat(
                api_key, base_url, args.model, phrase_prompt, args.temperature, args.timeout
            )
        except Exception as exc:
            raise SystemExit(f"phrases 生成失败：{exc}") from exc

    output_root = Path(args.output_dir)
    output_dir = output_root / yyyymmdd
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "words.md").write_text(words_md, encoding="utf-8")
    (output_dir / "phrases.md").write_text(phrases_md, encoding="utf-8")
    print(f"[Output] words_chars={len(words_md)} phrases_chars={len(phrases_md)}")

    stats = deduper.process_directory(yyyymmdd, output_root, output_root / "duplicate")
    if "error" in stats:
        print(f"去重失败：{stats['error']}")
    else:
        print("去重完成。")
        print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

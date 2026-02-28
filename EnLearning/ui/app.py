# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as _dt
import html
import os
import re
import sys
import textwrap
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import httpx
from openai import OpenAI
from pypdf import PdfReader

sys.path.append(str(Path(__file__).resolve().parents[2]))

from EnLearning.lib import deduper
from EnLearning.prompts.prompt import DPOGenerationPrompts

APP_TITLE = "EnLearning · Vocabulary Mining UI"
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_BASE = BASE_DIR
DEFAULT_MODEL = "qwen-plus"
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_TIMEOUT = 60
MAX_MATERIAL_CHARS = 12000
URL_FETCH_TIMEOUT = 20
MAX_URL_BYTES = 2_000_000


def _load_default_prompts() -> tuple[str, str]:
    prompts = DPOGenerationPrompts()
    return prompts.english_word_extraction.strip(), prompts.english_phrases_extraction.strip()


DEFAULT_WORD_PROMPT, DEFAULT_PHRASE_PROMPT = _load_default_prompts()


class _HTMLTextExtractor:
    def __init__(self) -> None:
        self._chunks: list[str] = []

    def feed(self, html_text: str) -> str:
        # Very small HTML-to-text extraction; keeps whitespace readable.
        text = re.sub(r"(?is)<(script|style).*?>.*?(</\\1>)", " ", html_text)
        text = re.sub(r"(?is)<br\\s*/?>", "\n", text)
        text = re.sub(r"(?is)</p>|</div>|</li>|</h\\d>", "\n", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = re.sub(r"[ \\t\\r\\f]+", " ", text)
        text = re.sub(r"\\n\\s+\\n", "\n\n", text)
        return text.strip()


def _fetch_url_text(url: str) -> str:
    print(f"开始抓取 URL: {url}")
    headers = {"User-Agent": "EnLearning/1.0 (+local)"}
    with httpx.Client(timeout=URL_FETCH_TIMEOUT, follow_redirects=True) as client:
        with client.stream("GET", url, headers=headers) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").lower()
            chunks = []
            total = 0
            for chunk in resp.iter_bytes():
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_URL_BYTES:
                    raise ValueError("URL 内容过大，已超过读取上限，请改用文本粘贴。")
                chunks.append(chunk)
            raw = b"".join(chunks)

    if url.lower().endswith(".pdf") or "application/pdf" in content_type:
        reader = PdfReader(BytesIO(raw))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        print(f"URL 抓取完成（PDF），字数：{len(text)}")
        return text

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="ignore")

    extractor = _HTMLTextExtractor()
    cleaned = extractor.feed(text)
    print(f"URL 抓取完成（HTML），字数：{len(cleaned)}")
    return cleaned


def _normalize_date(date_str: Optional[str]) -> str:
    if not date_str:
        return _dt.date.today().strftime("%Y%m%d")
    # Accept YYYY-MM-DD or YYYYMMDD
    if re.fullmatch(r"\d{8}", date_str):
        return date_str
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str.replace("-", "")
    raise ValueError("日期格式应为 YYYY-MM-DD 或 YYYYMMDD")


def _render_prompt(template: str, material: str, count: int) -> str:
    # If template doesn't contain placeholders, append a minimal block.
    if "$1" not in template and "$2" not in template:
        return textwrap.dedent(
            f"""{template}

Material:
{material}

Count: {count}
"""
        ).strip()
    return template.replace("$1", material).replace("$2", str(count))


def _call_llm(
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=DEFAULT_TIMEOUT)
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return completion.choices[0].message.content or ""


def _render_page(
    *,
    material_text: str = "",
    material_url: str = "",
    word_prompt: str = DEFAULT_WORD_PROMPT,
    phrase_prompt: str = DEFAULT_PHRASE_PROMPT,
    word_count: int = 70,
    phrase_count: int = 50,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    temperature: float = 0.2,
    date_str: str = _dt.date.today().strftime("%Y-%m-%d"),
    error: str = "",
    words_md: str = "",
    phrases_md: str = "",
    stats: Optional[dict] = None,
) -> str:
    def esc(s: str) -> str:
        return html.escape(s or "")

    stats_html = ""
    if stats and "error" not in stats:
        stats_html = f"""
        <div class="stat-grid">
          <div class="stat">
            <div class="label">Words · 新增</div>
            <div class="value">{stats['words']['new']}</div>
            <div class="meta">提取 {stats['words']['extracted']} / 去除重复 {stats['words']['removed_from_md']}</div>
          </div>
          <div class="stat">
            <div class="label">Phrases · 新增</div>
            <div class="value">{stats['phrases']['new']}</div>
            <div class="meta">提取 {stats['phrases']['extracted']} / 去除重复 {stats['phrases']['removed_from_md']}</div>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{APP_TITLE}</title>
  <style>
    :root {{
      --bg: #f5f2ea;
      --card: #ffffff;
      --ink: #1b1c1f;
      --muted: #6b6f76;
      --accent: #0f5b8c;
      --accent-2: #e07a5f;
      --border: #e7e1d4;
      --shadow: 0 18px 40px rgba(15, 25, 35, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Space Grotesk", "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at top left, #fdf7ec 0%, #f3efe4 40%, #eae7db 100%);
    }}
    .hero {{
      padding: 32px 28px 12px;
    }}
    .hero h1 {{
      margin: 0 0 6px;
      font-size: 28px;
      letter-spacing: 0.2px;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      max-width: 720px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 20px;
      padding: 12px 28px 40px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 20px;
    }}
    label {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--muted);
      display: block;
      margin-bottom: 6px;
    }}
    input[type="text"], input[type="number"], input[type="date"], textarea {{
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 14px;
      background: #fffdf9;
    }}
    textarea {{
      min-height: 140px;
      resize: vertical;
    }}
    .row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .row-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
    }}
    .actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 16px;
    }}
    .btn {{
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 999px;
      padding: 12px 18px;
      font-size: 14px;
      cursor: pointer;
    }}
    .btn.secondary {{
      background: #f1ede2;
      color: var(--ink);
      border: 1px solid var(--border);
    }}
    .hint {{
      font-size: 12px;
      color: var(--muted);
    }}
    .error {{
      background: #fff1f1;
      border: 1px solid #f1b8b8;
      color: #9a1f1f;
      padding: 10px 12px;
      border-radius: 12px;
      margin-bottom: 12px;
    }}
    pre {{
      background: #111015;
      color: #f0f0f0;
      padding: 16px;
      border-radius: 12px;
      overflow-x: auto;
      min-height: 120px;
    }}
    .stat-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin: 12px 0 0;
    }}
    .stat {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px;
      background: #faf7f0;
    }}
    .stat .label {{
      text-transform: uppercase;
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 1px;
    }}
    .stat .value {{
      font-size: 22px;
      margin: 6px 0;
      color: var(--accent-2);
    }}
    .stat .meta {{
      font-size: 12px;
      color: var(--muted);
    }}
    @media (max-width: 960px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      .row, .row-3 {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>EnLearning · 词汇抽取工作台</h1>
    <p>输入原材料或 URL，编辑 Prompt，点击生成后自动写入当天目录，并进行去重合并。</p>
  </div>
  <div class="grid">
    <form class="card" method="post" action="/generate">
      {f'<div class="error">{esc(error)}</div>' if error else ''}

      <label>原材料（粘贴文本）</label>
      <textarea name="material_text" placeholder="粘贴论文或正文文本...">{esc(material_text)}</textarea>

      <label style="margin-top:12px;">或输入 URL（支持 HTML / PDF）</label>
      <input type="text" name="material_url" value="{esc(material_url)}" placeholder="https://...">

      <div class="row" style="margin-top:16px;">
        <div>
          <label>单词数量</label>
          <input type="number" name="word_count" value="{word_count}" min="1" max="500">
        </div>
        <div>
          <label>短语数量</label>
          <input type="number" name="phrase_count" value="{phrase_count}" min="1" max="500">
        </div>
      </div>

      <div class="row-3" style="margin-top:12px;">
        <div>
          <label>模型</label>
          <input type="text" name="model" value="{esc(model)}">
        </div>
        <div>
          <label>Base URL</label>
          <input type="text" name="base_url" value="{esc(base_url)}">
        </div>
        <div>
          <label>日期</label>
          <input type="date" name="date_str" value="{esc(date_str)}">
        </div>
      </div>

      <div class="row" style="margin-top:12px;">
        <div>
          <label>温度</label>
          <input type="number" name="temperature" value="{temperature}" step="0.1" min="0" max="1">
        </div>
        <div>
          <label>API Key（可留空，使用环境变量）</label>
          <input type="text" name="api_key" value="" placeholder="DASHSCOPE_API_KEY">
        </div>
      </div>

      <label style="margin-top:16px;">单词 Prompt</label>
      <textarea name="word_prompt">{esc(word_prompt)}</textarea>

      <label style="margin-top:12px;">短语 Prompt</label>
      <textarea name="phrase_prompt">{esc(phrase_prompt)}</textarea>

      <div class="actions">
        <button class="btn" type="submit">生成并写入</button>
        <div class="hint">生成后会写入 `EnLearning/YYYYMMDD/words.md` 和 `phrases.md`，并自动去重</div>
      </div>
    </form>

    <div class="card">
      <h3 style="margin-top:0;">生成预览</h3>
      {stats_html}
      <div style="margin-top:16px;">
        <label>Words (markdown)</label>
        <pre>{esc(words_md) or '等待生成...'}</pre>
      </div>
      <div style="margin-top:16px;">
        <label>Phrases (markdown)</label>
        <pre>{esc(phrases_md) or '等待生成...'}</pre>
      </div>
    </div>
  </div>
</body>
</html>"""


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return _render_page()


@app.post("/generate", response_class=HTMLResponse)
def generate(
    material_text: str = Form(""),
    material_url: str = Form(""),
    word_prompt: str = Form(DEFAULT_WORD_PROMPT),
    phrase_prompt: str = Form(DEFAULT_PHRASE_PROMPT),
    word_count: int = Form(70),
    phrase_count: int = Form(50),
    model: str = Form(DEFAULT_MODEL),
    base_url: str = Form(DEFAULT_BASE_URL),
    temperature: float = Form(0.2),
    date_str: str = Form(""),
    api_key: str = Form(""),
):
    try:
        material_text = (material_text or "").strip()
        material_url = (material_url or "").strip()
        material = material_text

        if material_url:
            url_text = _fetch_url_text(material_url)
            if material:
                material = material + "\n\n" + url_text
            else:
                material = url_text

        if not material:
            raise ValueError("请提供原材料文本或 URL。")

        if len(material) > MAX_MATERIAL_CHARS:
            material = material[:MAX_MATERIAL_CHARS]

        yyyymmdd = _normalize_date(date_str)
        api_key = api_key.strip() or os.getenv("DASHSCOPE_API_KEY", "").strip()
        if not api_key:
            raise ValueError("未提供 API Key，请填写或设置环境变量 DASHSCOPE_API_KEY。")

        words_prompt = _render_prompt(word_prompt, material, word_count)
        phrases_prompt = _render_prompt(phrase_prompt, material, phrase_count)

        print("开始生成 words...")
        words_md = _call_llm(api_key, base_url, model, words_prompt, temperature)
        print("开始生成 phrases...")
        phrases_md = _call_llm(api_key, base_url, model, phrases_prompt, temperature)

        output_dir = OUTPUT_BASE / yyyymmdd
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "words.md").write_text(words_md, encoding="utf-8")
        (output_dir / "phrases.md").write_text(phrases_md, encoding="utf-8")

        print("开始去重合并...")
        stats = deduper.process_directory(yyyymmdd, OUTPUT_BASE, OUTPUT_BASE / "duplicate")

        return _render_page(
            material_text=material_text,
            material_url=material_url,
            word_prompt=word_prompt,
            phrase_prompt=phrase_prompt,
            word_count=word_count,
            phrase_count=phrase_count,
            model=model,
            base_url=base_url,
            temperature=temperature,
            date_str=(
                _dt.datetime.strptime(yyyymmdd, "%Y%m%d").strftime("%Y-%m-%d")
            ),
            words_md=words_md,
            phrases_md=phrases_md,
            stats=stats,
        )
    except Exception as exc:
        return _render_page(
            material_text=material_text,
            material_url=material_url,
            word_prompt=word_prompt,
            phrase_prompt=phrase_prompt,
            word_count=word_count,
            phrase_count=phrase_count,
            model=model,
            base_url=base_url,
            temperature=temperature,
            date_str=date_str or _dt.date.today().strftime("%Y-%m-%d"),
            error=str(exc),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "EnLearning.ui.app:app",
        host="127.0.0.1",
        port=7860,
        reload=False,
    )

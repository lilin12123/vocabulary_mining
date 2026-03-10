# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import html

APP_TITLE = "EnLearning · Vocab RPG"
DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DEFAULT_TIMEOUT = 60

BASE_DIR = Path(__file__).resolve().parent
ENLEARNING_DIR = BASE_DIR.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CACHE_DIR = BASE_DIR / "cache"
DATA_DIR = BASE_DIR / "data"
CACHE_FILE = CACHE_DIR / "questions.json"
USERS_FILE = DATA_DIR / "users.json"
RECORDS_FILE = DATA_DIR / "records.json"
MAX_USERS = 100

QUESTION_PROMPT = """
You are helping build a vocabulary learning game.
Given the word/phrase, its correct Chinese meaning, and one example sentence, generate:
1) Three correct English example sentences using the word naturally.
2) Two WRONG Chinese meanings that are the SAME part of speech, but semantically incorrect.
3) The part of speech (pos) of the word as a short label, e.g. noun/verb/adj/adv.

Constraints:
- The 3 example sentences must be clearly different (different subjects/contexts/structures).
- Avoid repeating the example sentence verbatim.
- Ensure the word appears in each example sentence.
- The wrong meanings should be plausible and close to the correct meaning (same domain, similar length),
  but must NOT be true synonyms.
- Avoid overly generic or silly meanings.
- Keep meanings concise (no more than 12 Chinese characters each).

Return ONLY valid JSON with the following shape:
{"pos": "noun", "sentences": ["...", "...", "..."], "wrong_meanings": ["...", "..."]}

Word: {word}
Correct meaning: {meaning}
Example sentence: {example}
""".strip()

PROMPT_HASH = hashlib.sha1(QUESTION_PROMPT.encode("utf-8")).hexdigest()

app = FastAPI(title=APP_TITLE)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class PreloadRequest(BaseModel):
    book_id: str
    count: int = 10
    token: Optional[str] = None


class AuthRequest(BaseModel):
    username: str
    password: str


class RecordRequest(BaseModel):
    token: str
    book_id: str
    difficulty: str
    score: int
    accuracy: int
    max_combo: int
    hp_left: int
    total: int


def _load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_api_key() -> str | None:
    return os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")


def _call_llm(prompt: str, model: str, base_url: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=DEFAULT_TIMEOUT)
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return completion.choices[0].message.content or ""


def _extract_json(text: str) -> Dict[str, Any] | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _list_wordbooks() -> List[Dict[str, str]]:
    books: List[Dict[str, str]] = []
    for path in sorted(ENLEARNING_DIR.iterdir()):
        if not path.is_dir():
            continue
        if not re.fullmatch(r"\d{8}", path.name):
            continue
        words_md = path / "words.md"
        phrases_md = path / "phrases.md"
        if words_md.exists() or phrases_md.exists():
            books.append(
                {
                    "id": path.name,
                    "has_words": words_md.exists(),
                    "has_phrases": phrases_md.exists(),
                }
            )
    return books


def _parse_words_md(md_path: Path) -> List[Dict[str, str]]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines()]
    entries: List[Dict[str, str]] = []

    headers: List[str] | None = None
    for line in lines:
        if not line or line.startswith("```"):
            continue
        if "|" not in line:
            headers = None
            continue

        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]
        if not cells:
            continue

        if any("---" in c for c in cells):
            continue

        if any("英文" in c for c in cells) and any("中文" in c for c in cells):
            headers = cells
            continue

        if headers:
            row = {headers[i]: cells[i] if i < len(cells) else "" for i in range(len(headers))}
            word = row.get("英文", "").strip()
            phonetic = row.get("美式音标", "").strip()
            meaning = row.get("中文含义", "").strip()
            example = row.get("示例", "").strip()
            if word and meaning and example:
                entries.append(
                    {
                        "word": word,
                        "phonetic": phonetic,
                        "meaning": meaning,
                        "example": example,
                        "synonyms": row.get("近义词", "").strip(),
                        "type": "word",
                    }
                )
    return entries


def _parse_phrases_md(md_path: Path) -> List[Dict[str, str]]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines()]
    entries: List[Dict[str, str]] = []

    headers: List[str] | None = None
    for line in lines:
        if not line or line.startswith("```"):
            continue
        if "|" not in line:
            headers = None
            continue

        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]
        if not cells:
            continue

        if any("---" in c for c in cells):
            continue

        if any("英文" in c for c in cells) and any("中文" in c for c in cells):
            headers = cells
            continue

        if headers:
            row = {headers[i]: cells[i] if i < len(cells) else "" for i in range(len(headers))}
            phrase = row.get("英文", "").strip() or row.get("英文短语", "").strip()
            phonetic = row.get("美式音标", "").strip()
            meaning = row.get("中文含义", "").strip()
            example = row.get("示例", "").strip()
            if phrase and meaning and example:
                entries.append(
                    {
                        "word": phrase,
                        "phonetic": phonetic,
                        "meaning": meaning,
                        "example": example,
                        "synonyms": row.get("近义词", "").strip(),
                        "type": "phrase",
                    }
                )
    return entries


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _create_token() -> str:
    return secrets.token_urlsafe(24)


def _load_users() -> Dict[str, Any]:
    return _load_json(USERS_FILE)


def _save_users(data: Dict[str, Any]) -> None:
    _save_json(USERS_FILE, data)


def _load_records() -> Dict[str, Any]:
    return _load_json(RECORDS_FILE)


def _save_records(data: Dict[str, Any]) -> None:
    _save_json(RECORDS_FILE, data)


def _require_user(token: str) -> str:
    users = _load_users()
    sessions = users.get("sessions", {})
    username = sessions.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="invalid token")
    return username


def _fallback_sentences(word: str, example: str) -> List[str]:
    sentences = []
    if example:
        sentences.append(example)
    template_pool = [
        f"{word.capitalize()} is frequently used in academic discussions about modern technology.",
        f"Many reports highlight the role of {word} in shaping real-world systems.",
        f"Students should understand {word} before moving to advanced topics.",
        f"In business contexts, {word} can influence key decisions and outcomes.",
    ]
    for s in template_pool:
        if len(sentences) >= 3:
            break
        if s not in sentences:
            sentences.append(s)
    return sentences[:3]


def _sentence_contains_word(sentence: str, word: str) -> bool:
    return word.lower() in sentence.lower()


def _pick_similar_meanings(correct: str, pool: List[str], k: int) -> List[str]:
    correct_chars = set(correct)
    candidates = []
    for meaning in pool:
        if meaning == correct:
            continue
        overlap = len(correct_chars.intersection(set(meaning)))
        candidates.append((overlap, meaning))
    candidates.sort(key=lambda x: x[0], reverse=True)
    picked = []
    for _, meaning in candidates:
        if meaning not in picked:
            picked.append(meaning)
        if len(picked) >= k:
            break
    return picked


def _build_question(
    entry: Dict[str, str],
    distractor_pool: List[str],
    model: str,
    base_url: str,
    api_key: str | None,
    cache: Dict[str, Any],
) -> Dict[str, Any]:
    cache_key = f"{entry['word']}|{model}|{PROMPT_HASH}"
    cached = cache.get(cache_key)
    if cached:
        data = cached
    else:
        data = None
        if api_key:
            prompt = QUESTION_PROMPT.format(
                word=entry["word"],
                meaning=entry["meaning"],
                example=entry["example"],
            )
            try:
                raw = _call_llm(prompt, model, base_url, api_key)
                parsed = _extract_json(raw)
                if parsed and parsed.get("sentences") and parsed.get("wrong_meanings"):
                    data = parsed
            except Exception:
                data = None

        if not data:
            wrongs = [m for m in distractor_pool if m != entry["meaning"]]
            random.shuffle(wrongs)
            data = {
                "pos": "unknown",
                "sentences": _fallback_sentences(entry["word"], entry["example"]),
                "wrong_meanings": wrongs[:2],
            }

        cache[cache_key] = {
            "pos": data.get("pos", "unknown"),
            "sentences": data.get("sentences", []),
            "wrong_meanings": data.get("wrong_meanings", []),
            "model": model,
            "prompt_hash": PROMPT_HASH,
            "updated_at": datetime.utcnow().isoformat(),
        }

    raw_sentences = data.get("sentences", [])
    sentences: List[str] = []
    for s in raw_sentences:
        if s and _sentence_contains_word(s, entry["word"]) and s not in sentences:
            sentences.append(s)
        if len(sentences) >= 3:
            break
    if len(sentences) < 3:
        for s in _fallback_sentences(entry["word"], entry["example"]):
            if s not in sentences:
                sentences.append(s)
            if len(sentences) >= 3:
                break

    wrong_meanings = []
    for m in data.get("wrong_meanings", []):
        if not m or m == entry["meaning"]:
            continue
        if m not in wrong_meanings:
            wrong_meanings.append(m)
        if len(wrong_meanings) >= 2:
            break
    if len(wrong_meanings) < 2:
        extra = _pick_similar_meanings(entry["meaning"], distractor_pool, 2)
        for m in extra:
            if m not in wrong_meanings and m != entry["meaning"]:
                wrong_meanings.append(m)
            if len(wrong_meanings) >= 2:
                break
    if len(wrong_meanings) < 2:
        extra = [m for m in distractor_pool if m != entry["meaning"] and m not in wrong_meanings]
        wrong_meanings.extend(extra[: 2 - len(wrong_meanings)])

    options = [
        {"text": entry["meaning"], "correct": True},
        *[{"text": m, "correct": False} for m in wrong_meanings[:2]],
    ]
    random.shuffle(options)

    return {
        "word": entry["word"],
        "phonetic": entry.get("phonetic", ""),
        "meaning": entry["meaning"],
        "example": entry["example"],
        "pos": data.get("pos", "unknown"),
        "sentences": sentences,
        "options": options,
    }


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/api/wordbooks")
def api_wordbooks() -> Dict[str, Any]:
    return {"books": _list_wordbooks()}


@app.get("/api/wordbooks/{book_id}")
def api_wordbook(book_id: str) -> Dict[str, Any]:
    words_path = ENLEARNING_DIR / book_id / "words.md"
    phrases_path = ENLEARNING_DIR / book_id / "phrases.md"
    if not (words_path.exists() or phrases_path.exists()):
        raise HTTPException(status_code=404, detail="wordbook not found")
    words = _parse_words_md(words_path) if words_path.exists() else []
    phrases = _parse_phrases_md(phrases_path) if phrases_path.exists() else []
    entries = words + phrases
    return {"id": book_id, "count": len(entries), "words": entries}


@app.post("/api/register")
def api_register(req: AuthRequest) -> Dict[str, Any]:
    username = req.username.strip()
    password = req.password.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="username/password required")
    users = _load_users()
    accounts = users.get("accounts", {})
    if username in accounts:
        raise HTTPException(status_code=400, detail="username exists")
    if len(accounts) >= MAX_USERS:
        raise HTTPException(status_code=400, detail="user limit reached")
    accounts[username] = {"password_hash": _hash_password(password), "created_at": datetime.utcnow().isoformat()}
    users["accounts"] = accounts
    users.setdefault("sessions", {})
    _save_users(users)
    return {"ok": True}


@app.post("/api/login")
def api_login(req: AuthRequest) -> Dict[str, Any]:
    username = req.username.strip()
    password = req.password.strip()
    users = _load_users()
    accounts = users.get("accounts", {})
    account = accounts.get(username)
    if not account or account.get("password_hash") != _hash_password(password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = _create_token()
    sessions = users.get("sessions", {})
    sessions[token] = username
    users["sessions"] = sessions
    _save_users(users)
    return {"token": token, "username": username}


@app.get("/api/records")
def api_records(token: str) -> Dict[str, Any]:
    username = _require_user(token)
    records = _load_records()
    user_records = records.get(username, [])
    return {"username": username, "records": user_records[-50:]}


@app.get("/api/leaderboard")
def api_leaderboard(difficulty: Optional[str] = None) -> Dict[str, Any]:
    records = _load_records()
    rows: List[Dict[str, Any]] = []
    for username, items in records.items():
        for r in items:
            if difficulty and r.get("difficulty") != difficulty:
                continue
            rows.append({**r, "username": username})
    rows.sort(key=lambda r: (r.get("score", 0), r.get("accuracy", 0)), reverse=True)
    return {"difficulty": difficulty or "all", "rows": rows[:10]}


@app.get("/api/stats")
def api_stats(token: Optional[str] = None) -> Dict[str, Any]:
    records = _load_records()
    total_users = len(records)
    all_rows = [r for items in records.values() for r in items]
    total_games = len(all_rows)
    avg_score = round(sum(r.get("score", 0) for r in all_rows) / total_games, 2) if total_games else 0
    avg_accuracy = round(sum(r.get("accuracy", 0) for r in all_rows) / total_games, 2) if total_games else 0
    best_score = max((r.get("score", 0) for r in all_rows), default=0)
    best_accuracy = max((r.get("accuracy", 0) for r in all_rows), default=0)
    payload = {
        "global": {
            "total_users": total_users,
            "total_games": total_games,
            "avg_score": avg_score,
            "avg_accuracy": avg_accuracy,
            "best_score": best_score,
            "best_accuracy": best_accuracy,
        }
    }
    if token:
        username = _require_user(token)
        user_rows = records.get(username, [])
        user_games = len(user_rows)
        payload["user"] = {
            "total_games": user_games,
            "avg_score": round(sum(r.get("score", 0) for r in user_rows) / user_games, 2) if user_games else 0,
            "avg_accuracy": round(sum(r.get("accuracy", 0) for r in user_rows) / user_games, 2) if user_games else 0,
            "best_score": max((r.get("score", 0) for r in user_rows), default=0),
            "best_accuracy": max((r.get("accuracy", 0) for r in user_rows), default=0),
        }
        payload["username"] = username
    return payload


@app.post("/api/preload")
def api_preload(req: PreloadRequest) -> Dict[str, Any]:
    if req.token:
        _require_user(req.token)
    words_path = ENLEARNING_DIR / req.book_id / "words.md"
    phrases_path = ENLEARNING_DIR / req.book_id / "phrases.md"
    if not (words_path.exists() or phrases_path.exists()):
        raise HTTPException(status_code=404, detail="wordbook not found")

    words = _parse_words_md(words_path) if words_path.exists() else []
    phrases = _parse_phrases_md(phrases_path) if phrases_path.exists() else []
    entries = words + phrases
    if not entries:
        raise HTTPException(status_code=400, detail="wordbook empty")

    count = min(req.count, len(entries))
    selected = random.sample(entries, count)
    distractor_pool = [w["meaning"] for w in selected]

    cache = _load_cache()
    api_key = _get_api_key()
    questions = [
        _build_question(
            entry,
            distractor_pool,
            DEFAULT_MODEL,
            DEFAULT_BASE_URL,
            api_key,
            cache,
        )
        for entry in selected
    ]
    _save_cache(cache)

    return {
        "book_id": req.book_id,
        "count": count,
        "words": selected,
        "questions": questions,
        "model": DEFAULT_MODEL,
        "base_url": DEFAULT_BASE_URL,
    }


@app.post("/api/record")
def api_record(req: RecordRequest) -> Dict[str, Any]:
    username = _require_user(req.token)
    record = {
        "book_id": req.book_id,
        "difficulty": req.difficulty,
        "score": req.score,
        "accuracy": req.accuracy,
        "max_combo": req.max_combo,
        "hp_left": req.hp_left,
        "total": req.total,
        "timestamp": datetime.utcnow().isoformat(),
    }
    records = _load_records()
    records.setdefault(username, []).append(record)
    _save_records(records)
    return {"ok": True}


def _render_entries_table(title: str, entries: List[Dict[str, str]]) -> str:
    if not entries:
        return f"<h3>{html.escape(title)}</h3><p>暂无内容</p>"
    rows = []
    header = "<tr><th>英文</th><th>音标</th><th>中文含义</th><th>示例</th><th>近义词</th></tr>"
    rows.append(header)
    for e in entries:
        rows.append(
            "<tr>"
            f"<td>{html.escape(e.get('word', ''))}</td>"
            f"<td>{html.escape(e.get('phonetic', ''))}</td>"
            f"<td>{html.escape(e.get('meaning', ''))}</td>"
            f"<td>{html.escape(e.get('example', ''))}</td>"
            f"<td>{html.escape(e.get('synonyms', ''))}</td>"
            "</tr>"
        )
    table = "<table>" + "".join(rows) + "</table>"
    return f"<h3>{html.escape(title)}</h3>" + table


@app.get("/book/{book_id}", response_class=HTMLResponse)
def view_book(book_id: str) -> HTMLResponse:
    words_path = ENLEARNING_DIR / book_id / "words.md"
    phrases_path = ENLEARNING_DIR / book_id / "phrases.md"
    words = _parse_words_md(words_path) if words_path.exists() else []
    phrases = _parse_phrases_md(phrases_path) if phrases_path.exists() else []
    body = (
        f"<h1>{html.escape(book_id)} · 词库预览</h1>"
        f"{_render_entries_table('Words', words)}"
        f"{_render_entries_table('Phrases', phrases)}"
    )
    html_page = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{APP_TITLE} · {html.escape(book_id)}</title>
      <style>
        body {{ font-family: "Space Grotesk", "Avenir Next", sans-serif; background: #0f1117; color: #f2f6ff; margin: 0; padding: 32px; }}
        h1 {{ margin-top: 0; }}
        h3 {{ margin-top: 32px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: #141a24; }}
        th, td {{ border: 1px solid #2a3345; padding: 8px 10px; text-align: left; }}
        th {{ background: #1f2735; }}
        tr:nth-child(even) td {{ background: #121824; }}
      </style>
    </head>
    <body>
      {body}
    </body>
    </html>
    """
    return HTMLResponse(html_page)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7870)

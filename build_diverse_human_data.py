"""
Option D — Diverse Human Text Data Builder
Sources:
  1. AG News (news articles) — via HuggingFace Parquet API
  2. Wikipedia Simple English — via HuggingFace Parquet API
  3. WritingPrompts (creative fiction) — via HuggingFace Parquet API
  4. IMDB Reviews (opinion/informal) — via HuggingFace Parquet API
  5. SQuAD Human Answers — via HuggingFace Parquet API

Goal: Add 3000 more diverse human text files to dataset_text/human
"""

import os, re, requests, pandas as pd, random, io
from pathlib import Path

HUMAN_DIR = Path("dataset_text") / "human"
HUMAN_DIR.mkdir(parents=True, exist_ok=True)

# Count existing files
existing = list(HUMAN_DIR.glob("*.txt"))
start_idx = len(existing)
print(f"Existing human files: {start_idx}")
print("=" * 60)

TARGET_NEW = 3000
collected  = []

def clean(text):
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', str(text)).strip()
    # Remove very short texts
    words = text.split()
    if len(words) < 15 or len(words) > 600:
        return None
    return text


# ─────────────────────────────────────────────────
# Source 1: AG News (news articles — formal writing)
# ─────────────────────────────────────────────────
print("\n[1/5] Fetching AG News articles...")
try:
    url = "https://huggingface.co/datasets/fancyzhx/ag_news/resolve/main/data/train-00000-of-00001.parquet"
    resp = requests.get(url, timeout=60)
    df_news = pd.read_parquet(io.BytesIO(resp.content))
    # Combine title+text for richer content
    if 'text' in df_news.columns:
        texts_news = df_news['text'].dropna().tolist()
    else:
        texts_news = []
    random.shuffle(texts_news)
    for t in texts_news[:1500]:
        c = clean(t)
        if c:
            collected.append(c)
    print(f"  AG News collected so far: {len(collected)}")
except Exception as e:
    print(f"  AG News failed: {e}")


# ─────────────────────────────────────────────────
# Source 2: IMDB Movie Reviews (informal opinion)
# ─────────────────────────────────────────────────
print("\n[2/5] Fetching IMDB reviews...")
try:
    url = "https://huggingface.co/datasets/stanfordnlp/imdb/resolve/main/plain_text/train-00000-of-00001.parquet"
    resp = requests.get(url, timeout=60)
    df_imdb = pd.read_parquet(io.BytesIO(resp.content))
    imdb_texts = df_imdb['text'].dropna().tolist()
    random.shuffle(imdb_texts)
    for t in imdb_texts[:1200]:
        c = clean(t)
        if c:
            collected.append(c)
    print(f"  IMDB collected so far: {len(collected)}")
except Exception as e:
    print(f"  IMDB failed: {e}")


# ─────────────────────────────────────────────────
# Source 3: ELI5 Reddit (casual/informal writing)
# ─────────────────────────────────────────────────
print("\n[3/5] Fetching ELI5 Reddit answers...")
try:
    url = "https://huggingface.co/datasets/Pavithree/eli5/resolve/main/data/train-00000-of-00001.parquet"
    resp = requests.get(url, timeout=60)
    df_eli5 = pd.read_parquet(io.BytesIO(resp.content))
    # Extract answers from the answers column if it exists
    eli5_texts = []
    if 'answers' in df_eli5.columns:
        for row in df_eli5['answers'].dropna().tolist():
            try:
                if isinstance(row, dict) and 'text' in row:
                    for ans in row['text']:
                        eli5_texts.append(str(ans))
                elif isinstance(row, list):
                    for item in row:
                        if isinstance(item, dict) and 'text' in item:
                            for ans in item.get('text', []):
                                eli5_texts.append(str(ans))
            except Exception:
                pass
    elif 'text' in df_eli5.columns:
        eli5_texts = df_eli5['text'].dropna().tolist()

    random.shuffle(eli5_texts)
    for t in eli5_texts[:800]:
        c = clean(t)
        if c:
            collected.append(c)
    print(f"  ELI5 collected so far: {len(collected)}")
except Exception as e:
    print(f"  ELI5 failed: {e}")


# ─────────────────────────────────────────────────
# Source 4: Multi-News (journalism/long-form)
# ─────────────────────────────────────────────────
print("\n[4/5] Fetching Multi-News articles...")
try:
    url = "https://huggingface.co/datasets/alexfabbri/multi_news/resolve/main/data/train-00000-of-00001.parquet"
    resp = requests.get(url, timeout=60)
    df_mnews = pd.read_parquet(io.BytesIO(resp.content))
    if 'document' in df_mnews.columns:
        mnews_texts = df_mnews['document'].dropna().tolist()
    elif 'summary' in df_mnews.columns:
        mnews_texts = df_mnews['summary'].dropna().tolist()
    else:
        mnews_texts = []
    random.shuffle(mnews_texts)
    for t in mnews_texts[:600]:
        # Split long articles into chunks
        words = str(t).split()
        for i in range(0, min(len(words), 600), 120):
            chunk = ' '.join(words[i:i+120])
            c = clean(chunk)
            if c:
                collected.append(c)
    print(f"  Multi-News collected so far: {len(collected)}")
except Exception as e:
    print(f"  Multi-News failed: {e}")


# ─────────────────────────────────────────────────
# Source 5: XSum (BBC journalism summaries)
# ─────────────────────────────────────────────────
print("\n[5/5] Fetching XSum BBC articles...")
try:
    url = "https://huggingface.co/datasets/EdinburghNLP/xsum/resolve/main/data/train-00000-of-00001.parquet"
    resp = requests.get(url, timeout=60)
    df_xsum = pd.read_parquet(io.BytesIO(resp.content))
    if 'document' in df_xsum.columns:
        xsum_texts = df_xsum['document'].dropna().tolist()
    else:
        xsum_texts = []
    random.shuffle(xsum_texts)
    for t in xsum_texts[:1000]:
        c = clean(t)
        if c:
            collected.append(c)
    print(f"  XSum collected so far: {len(collected)}")
except Exception as e:
    print(f"  XSum failed: {e}")


# ─────────────────────────────────────────────────
# Save to dataset_text/human
# ─────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Total diverse human texts collected: {len(collected)}")

# Deduplicate
collected = list(set(collected))
random.shuffle(collected)
collected = collected[:TARGET_NEW]

saved = 0
for i, text in enumerate(collected):
    fname = HUMAN_DIR / f"diverse_human_{start_idx + i:05d}.txt"
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(text)
        saved += 1
    except Exception as e:
        print(f"  Save error: {e}")

print(f"Saved {saved} new diverse human text files to dataset_text/human/")
print(f"Total human files now: {start_idx + saved}")
print("=" * 60)
print("Option D — Diverse Human Data COMPLETE ✅")

import json
from pathlib import Path
from rapidfuzz import fuzz, process

FAQ_PATH = Path(__file__).parent.parent / "data" / "faq.json"

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

# Слова, которые встречаются почти в каждом вопросе про беременность и поэтому
# только мешают точному сравнению — убираем их перед сравнением
STOPWORDS = {
    "можно", "ли", "что", "делать", "если", "при", "беременности",
    "беременность", "как", "нужно", "стоит", "это", "во", "время",
    "какие", "какой", "есть", "быть", "когда", "я",
}


def _clean(text: str) -> str:
    words = [w for w in text.lower().split() if w not in STOPWORDS]
    return " ".join(words) if words else text.lower()


def search_faq(query: str, threshold: int = 70):
    faq_items = FAQ_DATA["faq"]
    query_clean = _clean(query)

    choices = []
    for i, item in enumerate(faq_items):
        texts = [item["question"]] + item.get("aliases", [])
        for t in texts:
            choices.append((_clean(t), i))

    if not choices:
        return []

    strings = [c[0] for c in choices]

    results = process.extract(
        query_clean,
        strings,
        scorer=fuzz.token_set_ratio,
        limit=5,
        score_cutoff=threshold,
    )

    if not results:
        return []

    best_matches = {}
    for match_text, score, idx in results:
        original_idx = choices[idx][1]
        if original_idx not in best_matches or score > best_matches[original_idx][1]:
            best_matches[original_idx] = (match_text, score)

    # Возвращаем оригинальный (не "очищенный") текст вопроса — для показа пользователю
    return [
        (idx, faq_items[idx]["question"], score)
        for idx, (match_text, score) in best_matches.items()
    ]
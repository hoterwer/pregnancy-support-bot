import json
from pathlib import Path
from rapidfuzz import fuzz, process

# Эта строка вычисляет путь: поднимаемся на уровень выше от этого файла, заходим в data, берем faq.json
FAQ_PATH = Path(__file__).parent.parent / "data" / "faq.json"

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

def search_faq(query: str, threshold: int = 60):
    choices = []
    for i, item in enumerate(FAQ_DATA):
        # Берем основной вопрос и все алиасы (синонимы)
        texts = [item["question"]] + item.get("aliases", [])
        for t in texts:
            choices.append((t.lower(), i))
    
    # Ищем совпадения даже с опечатками
    results = process.extract(
        query.lower(),
        [c for c in choices],
        scorer=fuzz.WRatio,
        limit=5,
        score_cutoff=threshold
    )
    
    if not results:
        return []
    
    # Убираем дубликаты (чтобы один вопрос не выпал дважды)
    best_matches = {}
    for match_text, score, idx in results:
        original_idx = choices[idx]
        if original_idx not in best_matches or score > best_matches[original_idx]:
            best_matches[original_idx] = (match_text, score)
    
    return [(idx, match_text, score) for idx, (match_text, score) in best_matches.items()]

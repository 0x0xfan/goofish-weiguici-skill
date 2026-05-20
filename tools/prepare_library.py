from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "违规库"
OUTPUT_DIR = ROOT / "违规库_整理"

CATEGORIES = [
    ("copyright", "商品版权词", "商品版权词"),
    ("prohibited", "商品违禁词", "商品违禁词"),
    ("piracy", "平台盗版违规词", "平台盗版违规词"),
]


def clean_term(term: str) -> str:
    term = term.replace("\ufeff", "")
    term = re.sub(r"\s+", " ", term).strip()
    return term.strip(" \t\r\n,，;；")


def normalize_key(term: str) -> str:
    value = unicodedata.normalize("NFKC", term)
    value = value.lower()
    value = re.sub(r"\s+", "", value)
    return value.strip(" ,，;；")


def split_terms(text: str) -> list[str]:
    """Split comma-delimited libraries while preserving commas inside brackets."""
    pairs = {
        "(": ")",
        "[": "]",
        "{": "}",
        "（": "）",
        "【": "】",
        "《": "》",
        "“": "”",
        "‘": "’",
    }
    items: list[str] = []
    buf: list[str] = []
    stack: list[str] = []

    for ch in text.replace("\r", "\n"):
        if ch in pairs:
            stack.append(pairs[ch])
            buf.append(ch)
        elif stack and ch == stack[-1]:
            stack.pop()
            buf.append(ch)
        elif ch in {",", "\n"} and not stack:
            term = clean_term("".join(buf))
            if term:
                items.append(term)
            buf = []
        else:
            buf.append(ch)

    term = clean_term("".join(buf))
    if term:
        items.append(term)
    return items


def find_source_file(marker: str) -> Path:
    files = [
        path
        for path in SOURCE_DIR.glob("*.txt")
        if marker in path.stem and "ocr" not in path.stem
    ]
    if len(files) != 1:
        raise RuntimeError(f"Expected 1 source file for {marker}, got {files}")
    return files[0]


def clean_official_rules() -> None:
    candidates = list(SOURCE_DIR.glob("*_ocr.txt"))
    if not candidates:
        return

    official = max(candidates, key=lambda path: path.stat().st_size)
    lines = [clean_term(line) for line in official.read_text(encoding="utf-8-sig").splitlines()]
    noise = {"1.10 5G., 5G.", "1.10 5G., 5G", "08:26", "196", "96", "KB/s"}
    lines = [line for line in lines if line and line not in noise]

    joined: list[str] = []
    for line in lines:
        is_heading = bool(
            re.match(
                r"^(第[一二三四五六七八九十]+[章节条]|[（(][一二三四五六七八九十]+[）)])",
                line,
            )
        )
        if (
            not joined
            or is_heading
            or joined[-1].endswith(("。", "：", ":", "；", ";"))
            or re.match(r"^[（(][一二三四五六七八九十]+[）)]", line)
        ):
            joined.append(line)
        else:
            joined[-1] += line

    (OUTPUT_DIR / "闲鱼官方规则2025-12月版.txt").write_text(
        "\n".join(joined) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    stats: list[tuple[str, int, int, int, str]] = []
    combined: dict[str, dict[str, object]] = {}
    internal_dupes: dict[str, list[tuple[str, int, int]]] = {}

    for key, label, marker in CATEGORIES:
        source = find_source_file(marker)
        terms = split_terms(source.read_text(encoding="utf-8-sig"))
        seen: dict[str, int] = {}
        unique_terms: list[str] = []
        duplicate_terms: list[tuple[str, int, int]] = []

        for index, term in enumerate(terms, start=1):
            norm = normalize_key(term)
            if not norm:
                continue

            if norm in seen:
                duplicate_terms.append((term, seen[norm], index))
                continue

            seen[norm] = index
            unique_terms.append(term)
            entry = combined.setdefault(
                norm,
                {
                    "term": term,
                    "categories": [],
                    "sources": [],
                    "variants": set(),
                },
            )
            categories = entry["categories"]
            sources = entry["sources"]
            variants = entry["variants"]
            if isinstance(categories, list) and label not in categories:
                categories.append(label)
            if isinstance(sources, list) and source.name not in sources:
                sources.append(source.name)
            if isinstance(variants, set):
                variants.add(term)

        (OUTPUT_DIR / f"{label}.txt").write_text(
            "\n".join(unique_terms) + "\n",
            encoding="utf-8",
        )
        stats.append((label, len(terms), len(unique_terms), len(duplicate_terms), source.name))
        internal_dupes[label] = duplicate_terms

    clean_official_rules()

    with (OUTPUT_DIR / "combined_terms.tsv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["term", "normalized", "categories", "sources", "variants"])
        for norm, entry in combined.items():
            categories = entry["categories"]
            sources = entry["sources"]
            variants = entry["variants"]
            writer.writerow(
                [
                    entry["term"],
                    norm,
                    "|".join(categories) if isinstance(categories, list) else "",
                    "|".join(sources) if isinstance(sources, list) else "",
                    "|".join(sorted(variants)) if isinstance(variants, set) else "",
                ]
            )

    cross_file_dupes = [
        entry for entry in combined.values() if isinstance(entry["categories"], list) and len(entry["categories"]) > 1
    ]
    report = [
        "# 违规库整理报告",
        "",
        "## 清理统计",
        "",
        "| 来源 | 原始分词数 | 去重后 | 删减重复 | 原文件 |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for label, total, unique, dupes, filename in stats:
        report.append(f"| {label} | {total} | {unique} | {dupes} | {filename} |")
    report.append(f"| 合并词库 | - | {len(combined)} | - | combined_terms.tsv |")
    report.extend(["", "## 跨文件重复", ""])

    if cross_file_dupes:
        report.extend(["| 词条 | 来源分类 | 原文件 |", "| --- | --- | --- |"])
        for entry in cross_file_dupes:
            categories = entry["categories"]
            sources = entry["sources"]
            report.append(
                f"| {entry['term']} | {' / '.join(categories)} | {' / '.join(sources)} |"
            )
    else:
        report.append("未发现跨文件重复词条。")

    report.extend(["", "## 文件内重复删减"])
    for label, dupes in internal_dupes.items():
        report.extend(["", f"### {label}"])
        if not dupes:
            report.append("未发现重复。")
            continue
        for term, first, index in dupes:
            report.append(f"- {term}（首次位置 {first}，重复位置 {index}）")

    (OUTPUT_DIR / "duplicate_report.md").write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )

    print(f"output_dir={OUTPUT_DIR}")
    for row in stats:
        print(row)
    print(f"combined_unique={len(combined)}")
    print(f"cross_file_duplicates={len(cross_file_dupes)}")


if __name__ == "__main__":
    main()

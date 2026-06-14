from __future__ import annotations

import csv
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "reference_list.psv"
OUTPUT = ROOT / "src" / "output" / "reference_list.md"
README = ROOT / "README.md"

START = "<!-- REFERENCES:START -->"
END = "<!-- REFERENCES:END -->"


def load_rows() -> list[dict[str, str]]:
    with SOURCE.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="|"))


def grouped(rows: list[dict[str, str]]) -> OrderedDict[str, OrderedDict[str, list[dict[str, str]]]]:
    data: OrderedDict[str, OrderedDict[str, list[dict[str, str]]]] = OrderedDict()
    for row in rows:
        category = row["Category"].strip()
        subdomain = row["Subdomain"].strip()
        data.setdefault(category, OrderedDict()).setdefault(subdomain, []).append(row)
    return data


def format_item(row: dict[str, str]) -> str:
    work = row["Work"].strip()
    link = row["Link"].strip()
    venue = row["Venue"].strip()
    year = row["Year"].strip()
    role = row["Role"].strip()

    title = f"[{work}]({link})" if link else work
    suffix = f" - *{venue} {year}*" if venue or year else ""
    if role:
        suffix += f" - {role}"
    return f"- {title}{suffix}"


def render(rows: list[dict[str, str]]) -> str:
    data = grouped(rows)
    lines: list[str] = []

    lines.append("This categorized reading list is generated from")
    lines.append("[src/reference_list.psv](src/reference_list.psv) using")
    lines.append("[src/extract_references.py](src/extract_references.py).")
    lines.append("")
    lines.append("| Category | References |")
    lines.append("| --- | ---: |")
    for category, subdomains in data.items():
        count = sum(len(items) for items in subdomains.values())
        lines.append(f"| {category} | {count} |")
    lines.append(f"| **Total** | **{len(rows)}** |")
    lines.append("")

    for category, subdomains in data.items():
        lines.append(f"### {category}")
        lines.append("")
        for subdomain, items in subdomains.items():
            lines.append(f"#### {subdomain}")
            for item in items:
                lines.append(format_item(item))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_readme(markdown: str) -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(f"{before}{START}\n{markdown}{END}{after}", encoding="utf-8")


def main() -> None:
    rows = load_rows()
    markdown = render(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(markdown, encoding="utf-8")
    update_readme(markdown)
    print(f"Generated {OUTPUT.relative_to(ROOT)} with {len(rows)} references.")


if __name__ == "__main__":
    main()

import re
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

# Source of truth: docs/sprint-4/burndown-fact.md
FACT_MD = Path(__file__).resolve().parents[1] / "burndown-fact.md"


def parse_plan_line(text: str) -> list[int]:
    match = re.search(r"линия\s+([\d\s\->→]+)\s*SP", text)
    if not match:
        raise ValueError("Не найдена план-линия в burndown-fact.md")
    points = [int(n) for n in re.findall(r"\d+", match.group(1))]
    if len(points) < 2:
        raise ValueError(f"План-линия содержит мало точек: {points}")
    return points


def parse_gates(text: str) -> list[dict]:
    gate_re = re.compile(
        r"###\s+\d+\.\s+Факт\s+(G\d+)\s+\((\d{2}\.\d{2})\s*[–-]\s*(\d{2}\.\d{2})\)",
        re.MULTILINE,
    )
    gates = []
    for match in gate_re.finditer(text):
        gate, start, end = match.group(1), match.group(2), match.group(3)
        remaining_match = re.search(
            rf"Остаток спринта после {re.escape(gate)}:\s*(\d+)\s*SP", text
        )
        gates.append(
            {
                "gate": gate,
                "start": start,
                "end": end,
                "remaining": int(remaining_match.group(1)) if remaining_match else None,
            }
        )
    if not gates:
        raise ValueError("Не найдены гейты в burndown-fact.md")
    return gates


def next_version(out_dir: Path) -> int:
    versions = []
    for path in out_dir.glob("burndown-chart-v*.png"):
        match = re.fullmatch(r"burndown-chart-v(\d+)\.png", path.name)
        if match:
            versions.append(int(match.group(1)))
    return max(versions, default=0) + 1


def main() -> None:
    text = FACT_MD.read_text(encoding="utf-8")
    plan = parse_plan_line(text)
    gates = parse_gates(text)

    expected_points = len(gates) + 1
    if len(plan) != expected_points:
        raise ValueError(
            f"План-линия содержит {len(plan)} точек, ожидается {expected_points} "
            f"(старт + {len(gates)} гейта)"
        )

    labels = [f"Старт\n{gates[0]['start']}"] + [f"{g['gate']}\n{g['end']}" for g in gates]
    fact = [plan[0]] + [g["remaining"] for g in gates]
    generated = date.today().strftime("%d.%m")

    plt.figure(figsize=(8, 4))
    plt.plot(labels, plan, "o-", label="План, SP")
    fact_x = [i for i, value in enumerate(fact) if value is not None]
    fact_y = [value for value in fact if value is not None]
    plt.plot(fact_x, fact_y, "s--", color="tab:orange", label="Факт, SP")

    max_y = max(plan + [v for v in fact if v is not None])
    plt.ylim(0, max(10, ((max_y + 9) // 10) * 10))
    plt.ylabel("Остаток, SP")
    plt.title("Sprint 4 burndown по гейтам")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.figtext(
        0.99,
        0.01,
        f"Сгенерировано: {generated}",
        ha="right",
        va="bottom",
        fontsize=8,
        color="gray",
    )
    plt.tight_layout(rect=(0, 0.03, 1, 1))

    out_dir = Path(__file__).parent
    out = out_dir / f"burndown-chart-v{next_version(out_dir)}.png"
    plt.savefig(out, dpi=150)
    print(f"wrote {out.as_posix()}")
    print(f"plan={plan}")
    print(f"fact={fact}")
    print(f"labels={[l.replace(chr(10), ' ') for l in labels]}")


if __name__ == "__main__":
    main()

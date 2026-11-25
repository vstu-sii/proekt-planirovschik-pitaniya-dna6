import re
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

# Source: docs/sprint-4/burndown-plan.md:74-78 and burndown-fact.md:32
labels = ["Старт\n23.11", "G1\n27.11", "G2\n04.12", "G3\n11.12"]
plan = [82, 65, 33, 0]
fact = [82, 79, None, None]  # 79 SP after G1 (24.11); G2/G3 pending
generated = date.today().strftime("%d.%m")

plt.figure(figsize=(8, 4))
plt.plot(labels, plan, "o-", label="План, SP")
fact_x = [i for i, v in enumerate(fact) if v is not None]
fact_y = [v for v in fact if v is not None]
plt.plot(fact_x, fact_y, "s--", color="tab:orange", label="Факт, SP")

plt.ylim(0, 90)
plt.ylabel("Остаток, SP")
plt.title("Sprint 4 burndown по гейтам")
plt.grid(alpha=0.3)
plt.legend()
plt.figtext(0.99, 0.01, f"Сгенерировано: {generated}", ha="right", va="bottom", fontsize=8, color="gray")
plt.tight_layout(rect=(0, 0.03, 1, 1))

out_dir = Path(__file__).parent
versions = []
for p in out_dir.glob("burndown-chart-v*.png"):
    m = re.fullmatch(r"burndown-chart-v(\d+)\.png", p.name)
    if m:
        versions.append(int(m.group(1)))
next_v = max(versions, default=0) + 1
out = out_dir / f"burndown-chart-v{next_v}.png"
plt.savefig(out, dpi=150)
print(f"wrote {out.as_posix()}")

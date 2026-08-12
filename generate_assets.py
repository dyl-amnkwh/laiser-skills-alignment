import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os # Import the os module

np.random.seed(42)

# Define the base directory for saving files
base_dir = "/home/claude/laiser_portfolio"
data_dir = os.path.join(base_dir, "data")
figures_dir = os.path.join(base_dir, "figures")

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)

# ---------------------------------------------------------------
# 1. Fabricated sample dataset
# ---------------------------------------------------------------

credentials = [
    ("Medical Coding Certificate",       "Health",        "outcomes"),
    ("Practical Nursing Diploma",        "Health",        "outcomes"),
    ("CNA Certification",                "Health",        "course"),
    ("Full Stack Web Development",       "Technology",    "course"),
    ("Network Support Associate",        "Technology",    "outcomes"),
    ("AWS Cloud Practitioner Prep",      "Technology",    "course"),
    ("HVAC Technician Certificate",      "Trade",         "course"),
    ("Electrical Apprenticeship",        "Trade",         "outcomes"),
    ("Welding Technology Certificate",   "Trade",         "course"),
    ("General Business Administration",  "Business",      "outcomes"),
    ("Project Management Fundamentals",  "Business",      "course"),
    ("Liberal Arts Associate Degree",    "Liberal Arts",  "outcomes"),
    ("General Arts Certificate",         "Liberal Arts",  "course"),
    ("Early Childhood Education Cert.",  "Education",     "outcomes"),
    ("Culinary Arts Certificate",        "Trade",         "course"),
]

rows = []
for name, category, desc_type in credentials:
    # base extraction counts differ a bit by description style
    base_skill = np.random.randint(4, 10)
    base_knowledge = np.random.randint(2, 8)
    base_task = np.random.randint(5, 12)

    # enhancement effect: knowledge benefits most from outcomes-style text,
    # skills/tasks benefit most from course-style text, tasks are least
    # sensitive overall (mirrors the real finding)
    if desc_type == "outcomes":
        skill_mult = np.random.uniform(1.3, 1.7)
        knowledge_mult = np.random.uniform(1.9, 2.6)
        task_mult = np.random.uniform(1.1, 1.4)
    else:
        skill_mult = np.random.uniform(1.7, 2.3)
        knowledge_mult = np.random.uniform(1.3, 1.8)
        task_mult = np.random.uniform(1.2, 1.5)

    enh_skill = int(round(base_skill * skill_mult))
    enh_knowledge = int(round(base_knowledge * knowledge_mult))
    enh_task = int(round(base_task * task_mult))

    rows.append({
        "credential_name": name,
        "industry": category,
        "description_type": desc_type,
        "original_skill_count": base_skill,
        "enhanced_skill_count": enh_skill,
        "original_knowledge_count": base_knowledge,
        "enhanced_knowledge_count": enh_knowledge,
        "original_task_count": base_task,
        "enhanced_task_count": enh_task,
    })

df = pd.DataFrame(rows)

# introduce two "anomaly" rows, mirroring the real QA finding that a couple
# of credentials saw counts *drop* after enhancement (flagged as data
# quality issues, not genuine model regressions)
df.loc[df["credential_name"] == "Medical Coding Certificate", "enhanced_skill_count"] -= 2
df.loc[df["credential_name"] == "CNA Certification", "enhanced_task_count"] -= 5

df.to_csv(os.path.join(data_dir, "sample_extraction_output.csv"), index=False)
print(df)

# ---------------------------------------------------------------
# 2. Chart 1 — overall extraction volume, original vs enhanced, by category
# ---------------------------------------------------------------

totals = {
    "Skill": (df["original_skill_count"].sum(), df["enhanced_skill_count"].sum()),
    "Knowledge": (df["original_knowledge_count"].sum(), df["enhanced_knowledge_count"].sum()),
    "Task": (df["original_task_count"].sum(), df["enhanced_task_count"].sum()),
}

categories = list(totals.keys())
original_vals = [totals[c][0] for c in categories]
enhanced_vals = [totals[c][1] for c in categories]
pct_change = [round((e - o) / o * 100) for o, e in zip(original_vals, enhanced_vals)]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(7, 5))
bars1 = ax.bar(x - width/2, original_vals, width, label="Original description", color="#8899aa")
bars2 = ax.bar(x + width/2, enhanced_vals, width, label="Enhanced description", color="#2f6f9f")

for i, (o, e, pct) in enumerate(zip(original_vals, enhanced_vals, pct_change)):
    ax.text(i + width/2, e + 2, f"+{pct}%", ha="center", fontsize=10, color="#2f6f9f", fontweight="bold")

ax.set_ylabel("Total extracted items (across sample credentials)")
ax.set_title("Extraction Volume by Category: Original vs. Enhanced Descriptions\n(fabricated sample data)")
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "extraction_volume_comparison.png"), dpi=150)
plt.close()

# ---------------------------------------------------------------
# 3. Chart 2 — enhancement gain by description type (course vs outcomes)
# ---------------------------------------------------------------

df["skill_pct_change"] = (df["enhanced_skill_count"] - df["original_skill_count"]) / df["original_skill_count"] * 100
df["knowledge_pct_change"] = (df["enhanced_knowledge_count"] - df["original_knowledge_count"]) / df["original_knowledge_count"] * 100
df["task_pct_change"] = (df["enhanced_task_count"] - df["original_task_count"]) / df["original_task_count"] * 100

grouped = df.groupby("description_type")[["skill_pct_change", "knowledge_pct_change", "task_pct_change"]].mean()
grouped = grouped.rename(columns={
    "skill_pct_change": "Skill",
    "knowledge_pct_change": "Knowledge",
    "task_pct_change": "Task",
})
grouped = grouped.reindex(["course", "outcomes"])

fig, ax = plt.subplots(figsize=(7, 5))
grouped.T.plot(kind="bar", ax=ax, color=["#c98a3e", "#5a8f5a"], width=0.6)

ax.set_ylabel("Average % increase after enhancement")
ax.set_title("Enhancement Gain by Description Style\n(fabricated sample data)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.legend(title="Description style")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "enhancement_by_description_style.png"), dpi=150)
plt.close()

print("\nDone. Files written:")
print(f" - {os.path.join(data_dir, 'sample_extraction_output.csv')}")
print(f" - {os.path.join(figures_dir, 'extraction_volume_comparison.png')}")
print(f" - {os.path.join(figures_dir, 'enhancement_by_description_style.png')}")

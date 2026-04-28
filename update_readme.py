import requests
import os
from datetime import datetime
from collections import Counter

USERNAME = os.getenv("USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {"Authorization": f"token {TOKEN}"}

# -------- FETCH DATA -------- #

user = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers).json()
repos = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=headers).json()

total_stars = sum(repo["stargazers_count"] for repo in repos)
total_forks = sum(repo["forks_count"] for repo in repos)
public_repos = user["public_repos"]
followers = user["followers"]

# -------- LANGUAGE STATS -------- #

languages = Counter()

for repo in repos:
    if repo["language"]:
        languages[repo["language"]] += 1

top_languages = [lang for lang, _ in languages.most_common(4)]
top_languages_str = ", ".join(top_languages) if top_languages else "N/A"

# fallback values (GitHub API limitations unless extended)
prs_merged = 58
issues_opened = 6
streak = 0
contributions = 1559

# -------- SCORING -------- #

def bar(score, max_score):
    filled = int((score / max_score) * 20)
    return "█" * filled + "░" * (20 - filled)

stars_score = min(total_stars / 70, 2.0)
commit_score = 2.15
pr_score = 1.15
repo_score = 1.0
follower_score = min(followers / 80, 1.0)
streak_score = 0.0
activity_score = 1.0

total_score = round(
    stars_score
    + commit_score
    + pr_score
    + repo_score
    + follower_score
    + streak_score
    + activity_score,
    2,
)

level = "Advanced Developer" if total_score >= 7 else "Intermediate Developer"

# -------- BUILD BLOCK -------- #

updated = f"""
<!-- DEVELOPER-RATING:START -->

<div align="center">

### 🚀 {level}
## 🎯 {total_score}/10.0
*Strong skills with significant project experience*

</div>

<table align="center">
<tr>
<td width="50%" valign="top">

#### 📊 GitHub Statistics
| Metric | Value |
|--------|-------|
| ⭐ Total Stars | **{total_stars}** |
| 🍴 Total Forks | **{total_forks}** |
| 📦 Public Repos | **{public_repos}** |
| 🔀 PRs Merged | **{prs_merged}** |
| 🐛 Issues Opened | **{issues_opened}** |
| 🔥 Current Streak | **{streak} days** |
| 👥 Followers | **{followers}** |
| 📅 Total Contributions | **{contributions}** |

</td>
<td width="50%" valign="top">

#### 🎯 Score Breakdown
| Category | Progress | Score |
|----------|----------|-------|
| ⭐ Stars | {bar(stars_score, 2.0)} | {stars_score:.2f}/2.0 |
| 🔥 Commits | {bar(commit_score, 2.5)} | {commit_score:.2f}/2.5 |
| 🔀 PRs | {bar(pr_score, 1.5)} | {pr_score:.2f}/1.5 |
| 📦 Repos | {bar(repo_score, 1.0)} | {repo_score:.2f}/1.0 |
| 👥 Followers | {bar(follower_score, 1.0)} | {follower_score:.2f}/1.0 |
| 🔥 Streak | {bar(streak_score, 1.0)} | {streak_score:.2f}/1.0 |
| 📅 Activity | {bar(activity_score, 1.0)} | {activity_score:.2f}/1.0 |

</td>
</tr>
</table>

<div align="center">

**🌐 Top Languages:** {top_languages_str}  
*Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*

</div>

<!-- DEVELOPER-RATING:END -->
"""

# -------- REPLACE IN README -------- #

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start = "<!-- DEVELOPER-RATING:START -->"
end = "<!-- DEVELOPER-RATING:END -->"

new_content = content.split(start)[0] + updated + content.split(end)[1]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

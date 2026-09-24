import os
import requests

# ---------------- CONFIGURATION ----------------
USERNAME = "hyalokeraun"
TOKEN = os.environ.get("GH_TOKEN")
TEMPLATE_PATH = "pic2_stats_template.svg"
OUTPUT_PATH = "pic2_stats.svg"
# -----------------------------------------------

if not TOKEN:
    print("Error: GH_TOKEN environment variable not set.")
    print("Skipping SVG generation in local environment without token.")
    exit(0)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Fetch data from GitHub GraphQL API
query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
            }
          }
        }
      }
    }
    latestRepos: repositories(first: 3, orderBy: {field: PUSHED_AT, direction: DESC}, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        name
      }
    }
  }
}
"""

variables = {"login": USERNAME}
print(f"Fetching data for {USERNAME}...")
response = requests.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})

if response.status_code != 200:
    print(f"Error fetching data: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json().get("data", {}).get("user", {})
if not data:
    print("Error parsing data. Make sure the username is correct and token is valid.")
    exit(1)

# 2. Process Contributions (System Load)
total_contributions = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
# Calculate a rough "Load Percent" - scale 0-1000 contributions to 0-100%
load_percent = min(100, int((total_contributions / 1000.0) * 100))
# Max width of the bar is 480
load_width = int((load_percent / 100.0) * 480)
print(f"Total Contributions: {total_contributions} -> Load: {load_percent}%")

# 3. Process Languages
language_sizes = {}
total_size = 0

for repo in data["repositories"]["nodes"]:
    for edge in repo["languages"]["edges"]:
        lang = edge["node"]["name"]
        size = edge["size"]
        language_sizes[lang] = language_sizes.get(lang, 0) + size
        total_size += size

sorted_langs = sorted(language_sizes.items(), key=lambda x: x[1], reverse=True)
top_4_langs = sorted_langs[:4]

# If we don't have 4 languages, pad the rest
while len(top_4_langs) < 4:
    top_4_langs.append(("None", 0))

lang_data = []
for name, size in top_4_langs:
    percent = (size / total_size * 100) if total_size > 0 else 0
    # Max width for language bars is 340
    width = int((percent / 100.0) * 340)
    lang_data.append({"name": name, "percent": f"{percent:.1f}", "width": width})
    print(f"Language: {name} ({percent:.1f}%)")

# 4. Process Latest Repos
latest_repos = data["latestRepos"]["nodes"]
repos = [r["name"] for r in latest_repos]
while len(repos) < 3:
    repos.append("idle_process")

# 5. Read Template & Replace
print("Generating SVG...")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    svg_content = f.read()

# Replace Values
svg_content = svg_content.replace("{{LOAD_PERCENT}}", str(load_percent))
svg_content = svg_content.replace("{{LOAD_WIDTH}}", str(load_width))

for i in range(4):
    name = lang_data[i]["name"][:10].ljust(10) # Format string padding
    percent_str = lang_data[i]["percent"].rjust(5)
    
    svg_content = svg_content.replace(f"{{{{LANG{i+1}_NAME}}}}", name)
    svg_content = svg_content.replace(f"{{{{LANG{i+1}_PERCENT}}}}", percent_str)
    svg_content = svg_content.replace(f"{{{{LANG{i+1}_WIDTH}}}}", str(lang_data[i]["width"]))

for i in range(3):
    svg_content = svg_content.replace(f"{{{{PROC{i+1}_NAME}}}}", repos[i][:20])

# 6. Write output
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Successfully updated {OUTPUT_PATH}!")

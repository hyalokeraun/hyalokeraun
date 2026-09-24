import os
import requests

# ---------------- CONFIGURATION ----------------
USERNAME = "hyalokeraun"
TOKEN = os.environ.get("GH_TOKEN")
OUTPUT_PATH = "stats.svg"
# -----------------------------------------------

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="460" viewBox="0 0 1000 460">
  <defs>
    <style>
      <![CDATA[
      .txt { font-family: monospace; font-size: 16px; fill: #ebdbb2; }
      .bold { font-weight: 700; }
      .sym { fill: #928374; }
      .c-green { fill: #b8bb26; }
      .c-red { fill: #fb4934; }
      .c-yellow { fill: #fabd2f; }
      .c-blue { fill: #83a598; }
      .c-orange { fill: #fe8019; }
      .c-purple { fill: #d3869b; }
      .c-aqua { fill: #8ec07c; }
      .cmd { fill: #fabd2f; }
      ]]>
    </style>
  </defs>

  <!-- Background -->
  <rect width="1000" height="460" fill="#1d2021" stroke="#3c3836" stroke-width="10"/>

  <!-- Command Prompt -->
  <text x="20" y="32" class="txt">
    <tspan class="c-green">root@hyalokeraun</tspan><tspan class="sym">:~$ </tspan><tspan class="cmd">top</tspan> -u hyalokeraun --sort-by activity
  </text>

  <!-- ═══ SYSTEM LOAD ═══ -->
  <text x="20" y="72" class="txt"><tspan class="cmd bold">SYSTEM LOAD</tspan> <tspan class="sym">(Commit Graph Activity)</tspan></text>
  <rect x="20" y="84" width="480" height="18" rx="2" fill="#3c3836"/>
  <rect x="20" y="84" width="{{LOAD_WIDTH}}" height="18" rx="2" fill="#b8bb26"/>
  <text x="510" y="98" class="txt"><tspan class="c-green">{{LOAD_PERCENT}}%</tspan> <tspan class="sym">(Active)</tspan></text>

  <!-- ═══ MEMORY ALLOCATION ═══ -->
  <text x="20" y="140" class="txt"><tspan class="cmd bold">MEMORY ALLOCATION</tspan> <tspan class="sym">(Language Breakdown)</tspan></text>

  <!-- Lang 1 -->
  <text x="20" y="170" class="txt c-red">{{LANG1_NAME}}</text>
  <rect x="130" y="156" width="340" height="18" rx="2" fill="#3c3836"/>
  <rect x="130" y="156" width="{{LANG1_WIDTH}}" height="18" rx="2" fill="#fb4934"/>
  <text x="480" y="170" class="txt c-red">{{LANG1_PERCENT}}%</text>

  <!-- Lang 2 -->
  <text x="20" y="197" class="txt c-green">{{LANG2_NAME}}</text>
  <rect x="130" y="183" width="340" height="18" rx="2" fill="#3c3836"/>
  <rect x="130" y="183" width="{{LANG2_WIDTH}}" height="18" rx="2" fill="#b8bb26"/>
  <text x="480" y="197" class="txt c-green">{{LANG2_PERCENT}}%</text>

  <!-- Lang 3 -->
  <text x="20" y="224" class="txt c-orange">{{LANG3_NAME}}</text>
  <rect x="130" y="210" width="340" height="18" rx="2" fill="#3c3836"/>
  <rect x="130" y="210" width="{{LANG3_WIDTH}}" height="18" rx="2" fill="#fe8019"/>
  <text x="480" y="224" class="txt c-orange">{{LANG3_PERCENT}}%</text>

  <!-- Lang 4 -->
  <text x="20" y="251" class="txt c-blue">{{LANG4_NAME}}</text>
  <rect x="130" y="237" width="340" height="18" rx="2" fill="#3c3836"/>
  <rect x="130" y="237" width="{{LANG4_WIDTH}}" height="18" rx="2" fill="#83a598"/>
  <text x="480" y="251" class="txt c-blue">{{LANG4_PERCENT}}%</text>

  <!-- ═══ CURRENT PROCESSES ═══ -->
  <text x="20" y="295" class="txt cmd bold">CURRENT PROCESSES:</text>
  <rect x="20" y="303" width="780" height="1" fill="#504945"/>

  <!-- Table Header -->
  <text x="20" y="325" class="txt sym" xml:space="preserve">PID    USER         PR  NI  VIRT  RES  SHR S  %CPU  %MEM  COMMAND</text>

  <!-- Process 1 -->
  <text x="20" y="350" class="txt" xml:space="preserve"><tspan class="sym">001</tspan>    <tspan class="c-green">hyalokeraun</tspan>  20   0  784M  12M  8M  <tspan class="c-green">R</tspan>  <tspan class="c-red">99.9</tspan>   4.2  <tspan class="cmd">{{PROC1_NAME}}</tspan></text>

  <!-- Process 2 -->
  <text x="20" y="375" class="txt" xml:space="preserve"><tspan class="sym">002</tspan>    <tspan class="c-green">hyalokeraun</tspan>  20   0  512M  10M  4M  <tspan class="c-yellow">S</tspan>  <tspan class="c-orange">45.0</tspan>   2.1  <tspan class="cmd">{{PROC2_NAME}}</tspan></text>

  <!-- Process 3 -->
  <text x="20" y="400" class="txt" xml:space="preserve"><tspan class="sym">003</tspan>    <tspan class="c-green">hyalokeraun</tspan>  39  19  204M   8M  2M  <tspan class="c-yellow">S</tspan>  <tspan class="sym">00.0</tspan>   1.0  <tspan class="cmd">{{PROC3_NAME}}</tspan></text>

</svg>"""

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
load_percent = min(100, int((total_contributions / 1000.0) * 100))
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

while len(top_4_langs) < 4:
    top_4_langs.append(("None", 0))

lang_data = []
for name, size in top_4_langs:
    percent = (size / total_size * 100) if total_size > 0 else 0
    width = int((percent / 100.0) * 340)
    lang_data.append({"name": name, "percent": f"{percent:.1f}", "width": width})
    print(f"Language: {name} ({percent:.1f}%)")

# 4. Process Latest Repos
latest_repos = data["latestRepos"]["nodes"]
repos = [r["name"] for r in latest_repos]
while len(repos) < 3:
    repos.append("idle_process")

# 5. Replace Values in SVG Template
print("Generating SVG...")
svg_content = SVG_TEMPLATE
svg_content = svg_content.replace("{{LOAD_PERCENT}}", str(load_percent))
svg_content = svg_content.replace("{{LOAD_WIDTH}}", str(load_width))

for i in range(4):
    name = lang_data[i]["name"][:10].ljust(10)
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

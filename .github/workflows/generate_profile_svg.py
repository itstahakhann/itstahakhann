import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

USERNAME = "itstahakhann"
OUTPUT = Path("assets")
OUTPUT.mkdir(exist_ok=True)

TOKEN = os.environ.get("GITHUB_TOKEN")

API = "https://api.github.com"


def github_get(path):
    request = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def github_graphql(query):
    body = json.dumps({"query": query}).encode()

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_header(width, height):
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="14" fill="#0d1117"/>
<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}"
rx="14" fill="none" stroke="#30363d"/>
'''


def write_stats():
    user = github_get(f"/users/{USERNAME}")
    repos = github_get(f"/users/{USERNAME}/repos?per_page=100&sort=updated")

    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)

    query = """
    query {
      user(login: "itstahakhann") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """

    data = github_graphql(query)
    contributions = (
        data["data"]["user"]["contributionsCollection"]
        ["contributionCalendar"]["totalContributions"]
    )

    svg = svg_header(760, 210)

    svg += '''
    <text x="36" y="42" fill="#8b949e"
          font-family="monospace" font-size="14">// github stats</text>

    <text x="36" y="91" fill="#ffffff"
          font-family="monospace" font-size="30" font-weight="700">
      Taha Khan
    </text>
    '''

    cards = [
        ("PUBLIC REPOS", public_repos),
        ("FOLLOWERS", followers),
        ("STARS", stars),
        ("CONTRIBUTIONS", contributions),
    ]

    x_positions = [36, 218, 400, 582]

    for (label, value), x in zip(cards, x_positions):
        svg += f'''
        <rect x="{x}" y="118" width="160" height="62"
              rx="9" fill="#161b22" stroke="#30363d"/>

        <text x="{x+14}" y="140"
              fill="#8b949e"
              font-family="monospace"
              font-size="10">{label}</text>

        <text x="{x+14}" y="165"
              fill="#ffffff"
              font-family="monospace"
              font-size="21"
              font-weight="700">{value}</text>
        '''

    svg += "</svg>"

    (OUTPUT / "github-stats.svg").write_text(svg, encoding="utf-8")


def write_contributions():
    query = """
    query {
      user(login: "itstahakhann") {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
                contributionLevel
              }
            }
          }
        }
      }
    }
    """

    data = github_graphql(query)

    weeks = (
        data["data"]["user"]["contributionsCollection"]
        ["contributionCalendar"]["weeks"]
    )

    width = 760
    height = 190

    svg = svg_header(width, height)

    svg += '''
    <text x="28" y="32"
          fill="#8b949e"
          font-family="monospace"
          font-size="13">// contribution activity</text>
    '''

    level_colors = {
        "NONE": "#161b22",
        "FIRST_QUARTILE": "#3d444d",
        "SECOND_QUARTILE": "#6e7681",
        "THIRD_QUARTILE": "#aab1bb",
        "FOURTH_QUARTILE": "#ffffff",
    }

    start_x = 28
    start_y = 54

    cell = 11
    gap = 3

    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week["contributionDays"]):
            x = start_x + week_index * (cell + gap)
            y = start_y + day_index * (cell + gap)

            level = day["contributionLevel"]
            fill = level_colors.get(level, "#161b22")

            svg += f'''
            <rect x="{x}" y="{y}"
                  width="{cell}" height="{cell}"
                  rx="2" fill="{fill}">
              <title>{esc(day["date"])}: {day["contributionCount"]} contributions</title>
            </rect>
            '''

    svg += '''
    <text x="28" y="172"
          fill="#8b949e"
          font-family="monospace"
          font-size="11">
      Less
    </text>

    <rect x="65" y="163" width="11" height="11" rx="2" fill="#161b22"/>
    <rect x="82" y="163" width="11" height="11" rx="2" fill="#3d444d"/>
    <rect x="99" y="163" width="11" height="11" rx="2" fill="#6e7681"/>
    <rect x="116" y="163" width="11" height="11" rx="2" fill="#aab1bb"/>
    <rect x="133" y="163" width="11" height="11" rx="2" fill="#ffffff"/>

    <text x="153" y="172"
          fill="#8b949e"
          font-family="monospace"
          font-size="11">
      More
    </text>
    '''

    svg += "</svg>"

    (OUTPUT / "contribution-graph.svg").write_text(
        svg, encoding="utf-8"
    )


def write_repositories():
    repos = github_get(
        f"/users/{USERNAME}/repos?per_page=8&sort=updated"
    )

    repos = [
        repo for repo in repos
        if not repo.get("fork", False)
    ][:6]

    svg = svg_header(760, 370)

    svg += '''
    <text x="28" y="35"
          fill="#8b949e"
          font-family="monospace"
          font-size="13">// latest repositories</text>
    '''

    y = 70

    for repo in repos:
        name = esc(repo["name"])
        description = esc(
            repo.get("description") or "No description"
        )

        if len(description) > 62:
            description = description[:59] + "..."

        svg += f'''
        <rect x="28" y="{y}"
              width="704" height="42"
              rx="7"
              fill="#161b22"
              stroke="#30363d"/>

        <text x="44" y="{y+18}"
              fill="#ffffff"
              font-family="monospace"
              font-size="12"
              font-weight="700">
          {name}
        </text>

        <text x="44" y="{y+33}"
              fill="#8b949e"
              font-family="monospace"
              font-size="9">
          {description}
        </text>
        '''

        y += 49

    svg += "</svg>"

    (OUTPUT / "latest-repositories.svg").write_text(
        svg, encoding="utf-8"
    )


def main():
    print("Generating GitHub profile visuals...")

    write_stats()
    write_contributions()
    write_repositories()

    print("Done.")


if __name__ == "__main__":
    main()

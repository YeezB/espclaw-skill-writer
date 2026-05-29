#!/usr/bin/env python3
"""Create an ESPCLAW sensor skill scaffold from DFRobot GitHub repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
import html
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

GITHUB_ORG = "DFRobot"
GITHUB_API_REPOS = "https://api.github.com/orgs/DFRobot/repos"
GITHUB_ORG_REPO_SEARCH = "https://github.com/search"
DEFAULT_CLONE_ROOT = Path("third_party") / "dfrobot"
DEFAULT_SKILLS_ROOT = Path("components") / "common" / "skill_builder" / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ESPCLAW skill scaffold from DFRobot repo")
    parser.add_argument("--sensor", required=True, help="Sensor keyword, for example bmm350")
    parser.add_argument("--repo", help="Selected repo full name, for example DFRobot/DFRobot_BMM350")
    parser.add_argument("--list-only", action="store_true", help="Only list matching repositories")
    parser.add_argument("--clone-root", default=str(DEFAULT_CLONE_ROOT), help="Local root folder for cloned repos")
    parser.add_argument("--skills-root", default=str(DEFAULT_SKILLS_ROOT), help="ESPCLAW skills root folder")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    return parser.parse_args()


def api_get_json(url: str) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "espclaw-skill-writer",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc}") from exc


def fetch_all_repos() -> List[Dict[str, object]]:
    repos: List[Dict[str, object]] = []
    page = 1
    per_page = 100

    while True:
        url = f"{GITHUB_API_REPOS}?per_page={per_page}&page={page}"
        data = api_get_json(url)
        if not isinstance(data, list):
            raise RuntimeError("Unexpected GitHub API response shape")
        if not data:
            break
        repos.extend(item for item in data if isinstance(item, dict))
        page += 1
        if page > 20:
            break

    return repos


def fetch_repos_via_html_search(sensor_keyword: str) -> List[Dict[str, object]]:
    q = urllib.parse.quote(f"org:{GITHUB_ORG} {sensor_keyword}")
    url = f"{GITHUB_ORG_REPO_SEARCH}?q={q}&type=repositories"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html",
            "User-Agent": "espclaw-skill-writer",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            page = resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub HTML search request failed: {exc}") from exc

    pattern = re.compile(r'href="(?:https://github\.com)?/(DFRobot/[A-Za-z0-9_.-]+)"')
    seen = set()
    repos: List[Dict[str, object]] = []
    for match in pattern.finditer(page):
        full_name = html.unescape(match.group(1))
        if full_name in seen:
            continue
        seen.add(full_name)
        repo_name = full_name.split("/", 1)[1]
        repos.append(
            {
                "name": repo_name,
                "full_name": full_name,
                "description": "",
                "stargazers_count": 0,
                "html_url": f"https://github.com/{full_name}",
                "clone_url": f"https://github.com/{full_name}.git",
            }
        )
    return repos


def filter_repos(repos: List[Dict[str, object]], sensor_keyword: str) -> List[Dict[str, object]]:
    keyword = sensor_keyword.lower().strip()
    matches: List[Dict[str, object]] = []

    for repo in repos:
        name = str(repo.get("name", ""))
        full_name = str(repo.get("full_name", ""))
        description = str(repo.get("description", "") or "")
        hay = f"{name} {full_name} {description}".lower()
        if keyword in hay:
            matches.append(repo)

    matches.sort(key=lambda r: str(r.get("full_name", "")))
    return matches


def print_matches(matches: List[Dict[str, object]], sensor_keyword: str) -> None:
    print(f"Found {len(matches)} DFRobot repos matching '{sensor_keyword}':")
    for idx, repo in enumerate(matches, start=1):
        full_name = str(repo.get("full_name", ""))
        stars = repo.get("stargazers_count", 0)
        desc = str(repo.get("description", "") or "")
        print(f"{idx:>2}. {full_name} | stars={stars}")
        if desc:
            print(f"    {desc}")


def select_repo(matches: List[Dict[str, object]], repo_full_name: Optional[str]) -> Dict[str, object]:
    if not matches:
        raise RuntimeError("No matching repositories found")

    if repo_full_name:
        for repo in matches:
            if str(repo.get("full_name", "")).lower() == repo_full_name.lower():
                return repo
        raise RuntimeError(f"Selected repo '{repo_full_name}' is not in the match list")

    if not sys.stdin.isatty():
        raise RuntimeError("No repo selected. Re-run with --repo 'DFRobot/<repo>'")

    print("Enter repository number to continue (or press Enter to cancel): ", end="", flush=True)
    choice = input().strip()
    if not choice:
        raise RuntimeError("Cancelled by user")
    if not choice.isdigit():
        raise RuntimeError("Invalid selection, expected a number")

    idx = int(choice)
    if idx < 1 or idx > len(matches):
        raise RuntimeError(f"Invalid selection index: {idx}")
    return matches[idx - 1]


def run_git_clone(clone_url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and any(destination.iterdir()):
        print(f"Clone skipped: destination already exists: {destination}")
        return

    cmd = ["git", "clone", clone_url, str(destination)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def slugify(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "sensor"


def derive_skill_id(sensor_keyword: str, repo_name: str) -> str:
    repo_base = repo_name
    if repo_base.lower().startswith("dfrobot_"):
        repo_base = repo_base[len("dfrobot_") :]
    sensor_slug = slugify(sensor_keyword)
    repo_slug = slugify(repo_base)

    if sensor_slug in repo_slug:
        return f"dfrobot_{repo_slug}_i2c"
    return f"dfrobot_{sensor_slug}_{repo_slug}_i2c"


def render_skill_md(skill_id: str, sensor_keyword: str, repo_full_name: str, repo_url: str) -> str:
    return textwrap.dedent(
        f"""\
        ---
        {{
          "name": "{skill_id}",
          "description": "Read {sensor_keyword} sensor data over I2C on UNIHIKER using DFRobot library source from {repo_full_name}. Use this skill when user asks to read {sensor_keyword} data or sensor values.",
          "author": "ESPCLAW Skill Writer",
          "metadata": {{
            "category": ["sensor"],
            "tags": ["dfrobot", "{sensor_keyword}", "i2c", "unihiker"],
            "cap_groups": ["cap_lua"],
            "manage_mode": "web"
          }}
        }}
        ---

        # {skill_id}

        Generated from repository: {repo_full_name}
        Source: {repo_url}

        Use this skill when the user asks to read {sensor_keyword} sensor data.

        Run exactly one bundled Lua script with `lua_run_script`.

        ## Script Args Schema

        ```json
        {{
          "type": "object",
          "properties": {{
            "i2c_port": {{ "type": "integer", "minimum": 0, "maximum": 1 }},
            "sda": {{ "type": "integer", "minimum": 0, "maximum": 63 }},
            "scl": {{ "type": "integer", "minimum": 0, "maximum": 63 }},
            "i2c_freq_hz": {{ "type": "integer", "minimum": 10000, "maximum": 1000000 }},
            "addr": {{ "type": "integer", "minimum": 8, "maximum": 119 }}
          }}
        }}
        ```

        ## Tool Call Inputs

        ```json
        {{"path":"{{CUR_SKILL_DIR}}/scripts/read_sensor_data.lua","args":{{}}}}
        ```

        ## Recommended Flow

        1. Confirm sensor wiring and I2C address.
        2. Use defaults unless user provides custom wiring.
        3. Run `{{CUR_SKILL_DIR}}/scripts/read_sensor_data.lua`.
        4. Report script output directly.
        """
    )


def render_lua_script(skill_id: str, sensor_keyword: str) -> str:
    return textwrap.dedent(
        f"""\
        -- Generated scaffold for {skill_id}
        -- TODO: map registers/protocol from cloned DFRobot repo example and library sources.

        local i2c = require("i2c")

        local DEFAULT_I2C_PORT = 0
        local DEFAULT_SDA = 47
        local DEFAULT_SCL = 48
        local DEFAULT_I2C_FREQ_HZ = 400000
        local DEFAULT_ADDR = 0x00

        local function read_arg(name, default)
          if type(args) == "table" and args[name] ~= nil then
            return args[name]
          end
          return default
        end

        local function parse_int_arg(name, default, min_value, max_value)
          local value = read_arg(name, default)
          if type(value) ~= "number" or value % 1 ~= 0 then
            error(name .. " must be an integer")
          end
          if min_value ~= nil and value < min_value then
            error(string.format("%s must be >= %d", name, min_value))
          end
          if max_value ~= nil and value > max_value then
            error(string.format("%s must be <= %d", name, max_value))
          end
          return value
        end

        local function cleanup(dev, bus)
          if dev then
            pcall(function() dev:close() end)
          end
          if bus then
            pcall(function() bus:close() end)
          end
        end

        local function run()
          local i2c_port = parse_int_arg("i2c_port", DEFAULT_I2C_PORT, 0, 1)
          local sda = parse_int_arg("sda", DEFAULT_SDA, 0, 63)
          local scl = parse_int_arg("scl", DEFAULT_SCL, 0, 63)
          local i2c_freq_hz = parse_int_arg("i2c_freq_hz", DEFAULT_I2C_FREQ_HZ, 10000, 1000000)
          local addr = parse_int_arg("addr", DEFAULT_ADDR, 0x08, 0x77)

          local bus = nil
          local dev = nil

          local ok, err = xpcall(function()
            bus = i2c.new(i2c_port, sda, scl, i2c_freq_hz)
            dev = bus:device(addr)

            -- TODO: Replace this placeholder with real sensor init + read flow.
            print(string.format(
              "[{skill_id}] scaffold ready sensor={sensor_keyword} addr=0x%02X port=%d sda=%d scl=%d freq=%d",
              addr,
              i2c_port,
              sda,
              scl,
              i2c_freq_hz
            ))
            print("[{skill_id}] TODO: implement register/protocol reads based on cloned repo")
          end, debug.traceback)

          cleanup(dev, bus)

          if not ok then
            print("[{skill_id}] ERROR: " .. tostring(err))
            error(err)
          end
        end

        run()
        """
    )


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"Skip existing file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Wrote: {path}")


def main() -> int:
    args = parse_args()

    sensor_keyword = args.sensor.strip()
    if not sensor_keyword:
        raise RuntimeError("--sensor must not be empty")

    try:
        repos = fetch_all_repos()
    except RuntimeError as exc:
        message = str(exc).lower()
        if "rate limit" in message or "403" in message:
            print("GitHub API rate limited, falling back to HTML repository search...")
            repos = fetch_repos_via_html_search(sensor_keyword)
        else:
            raise

    matches = filter_repos(repos, sensor_keyword)
    print_matches(matches, sensor_keyword)

    if args.list_only:
        return 0

    selected = select_repo(matches, args.repo)
    repo_full_name = str(selected.get("full_name", ""))
    repo_name = str(selected.get("name", ""))
    clone_url = str(selected.get("clone_url", ""))
    html_url = str(selected.get("html_url", ""))

    skill_id = derive_skill_id(sensor_keyword, repo_name)
    skills_root = Path(args.skills_root)
    skill_dir = skills_root / skill_id
    if skill_dir.exists() and not args.force:
        raise RuntimeError(
            f"Skill directory already exists: {skill_dir}. "
            "Use --force to overwrite scaffold files."
        )

    clone_root = Path(args.clone_root)
    clone_dir = clone_root / repo_name
    run_git_clone(clone_url, clone_dir)

    skill_md = render_skill_md(skill_id, sensor_keyword, repo_full_name, html_url)
    lua_script = render_lua_script(skill_id, sensor_keyword)

    write_file(skill_dir / "SKILL.md", skill_md, args.force)
    write_file(skill_dir / "scripts" / "read_sensor_data.lua", lua_script, args.force)

    print("Done.")
    print(f"Selected repo: {repo_full_name}")
    print(f"Cloned to: {clone_dir}")
    print(f"Skill scaffold: {skill_dir}")
    print("Tip: re-run with --force to overwrite existing scaffold files.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""日報（nippo.md か nippo.adoc）に、自分が担当で「完了」以外の Backlog 課題のうち載っていないものを足し、
載っている課題ごとに、Backlog のステータス行を最新にし、足りない PR とブランチを足す。

使い方: nippo_only_update.py [日報のパス]
  パスを省くと nippo/ の nippo.md、なければ nippo.adoc を使う。
  書き換える前の内容を <file>.bak に残し、差分を標準出力へ出す。
  Backlog の接続先は環境変数 BACKLOG_DOMAIN・BACKLOG_API_KEY、なければ ~/.claude.json の backlog MCP の env を使う。
  終了コード: 0 = 成功（変更なしを含む）、1 = 取得に失敗した課題や PR がある、2 = 設定やファイルがない
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

NIPPO_DIR = Path.home() / "develop/github.com.sogen/seiei-sogen/enterprise-agent-ssot/enterprises/ai-cross-memo/nippo"
# 日報の書式は拡張子によらず同じ。両方あるときは md を使う。
DEFAULT_FILES = [NIPPO_DIR / "nippo.md", NIPPO_DIR / "nippo.adoc"]
OWNER = "AICROSS"
# リポジトリと日報の見出し。並びが、課題の中で見出しを置く順になる。
REPOS = {
    "rcs_richme_tickets": "チケット",
    "rcs_richme_backend": "BE",
    "rcs_richme_frontend": "FE",
    "rcs_richme_bot_frontend": "bot-FE",
    "rcs_richme_survey_frontend": "survey-FE",
    "rcs_richme_chatbot_api": "chatbot-api",
    "rcs_richme_brain": "brain",
    "IaC_richme": "IaC",
}
LABEL_ORDER = list(REPOS.values())
DONE = "完了"  # このステータスの課題は日報に足さない
JST = ZoneInfo("Asia/Tokyo")
ISSUE_LINE = re.compile(r"^- ([A-Z][A-Z0-9_]*-\d+)(?!\d)")
PR_URL = re.compile(r"^( *)- (https://github\.com/[^/]+/[^/]+/pull/\d+)\s*$")


def related(key, pr):
    """ブランチ名かタイトルが課題キーで始まる PR だけを関連とみなす。本文やタイトル途中の言及（「RICHME-4757 から分割」など）は数えない。"""
    starts = re.compile(re.escape(key) + r"(?!\d)")
    return bool(starts.match(pr["headRefName"]) or starts.match(pr["title"]))


def md(iso):
    return f"{int(iso[5:7])}/{int(iso[8:10])}"


def status_line(issue):
    # 開始日・期限日は日付だけの値なので時差を足さない。更新日時は UTC なので日本時間に直す。
    parts = [issue["status"]["name"]]
    if issue.get("priority"):
        parts.append(f"優先度 {issue['priority']['name']}")
    if issue.get("milestone"):
        parts.append(", ".join(m["name"] for m in issue["milestone"]))
    if issue.get("startDate"):
        parts.append(f"開始 {md(issue['startDate'])}")
    if issue.get("dueDate"):
        parts.append(f"期限 {md(issue['dueDate'])}")
    updated = datetime.fromisoformat(issue["updated"].replace("Z", "+00:00")).astimezone(JST)
    parts.append(f"更新 {updated.month}/{updated.day} {updated:%H:%M}")
    return " / ".join(parts)


def pr_lines(indent, pr):
    pad = " " * indent
    return [f"{pad}- {pr['url']}", f"{pad}    - ブランチ", f"{pad}        - {pr['headRefName']}"]


def blocks(lines):
    """課題の塊を (課題キー, 開始行, 終了行) で返す。塊は `- KEY` の行から、次に字下げなしで始まる行の手前まで。"""
    found = []
    for i, line in enumerate(lines):
        if line and not line[0].isspace() and found and found[-1][2] is None:
            found[-1][2] = i
        m = ISSUE_LINE.match(line)
        if m:
            found.append([m.group(1), i, None])
    if found and found[-1][2] is None:
        found[-1][2] = len(lines)
    return [tuple(b) for b in found]


def update_block(block, key, issue, prs, by_url, statuses):
    """1つの課題の塊を書き換えて、(新しい行, 報告) を返す。block は課題の行から次の課題の手前まで。"""
    out = list(block)
    notes = []
    while out and not out[-1].strip():  # 末尾の空行は最後に戻す
        out.pop()
    tail = block[len(out):]

    # 1. ステータス行: Backlog の URL の次の行が、Backlog のステータス名そのものか ` / ` 区切りなら置き換え、違えば URL の次に入れる。
    #    手書きのメモ（「〇〇さんに確認中」など）を上書きしないよう、ステータス名と照らす。
    if issue:
        new = "    - " + status_line(issue)
        at = next((i for i, l in enumerate(out) if l.startswith("    - http") and "/view/" in l), 0) + 1
        old = out[at][6:].strip() if at < len(out) and out[at].startswith("    - ") and out[at][6:7] != " " else None
        if old is None or not (old in statuses or " / " in old):
            out.insert(at, new)
            notes.append(f"ステータス行を追加: {new[6:]}")
        elif out[at] != new:
            notes.append(f"ステータス行を更新: {old} → {new[6:]}")
            out[at] = new

    # 2. ブランチがない PR の行に、ブランチを足す。
    i = 0
    while i < len(out):
        m = PR_URL.match(out[i])
        if m and not (i + 1 < len(out) and out[i + 1].strip() == "- ブランチ") and m.group(2) in by_url:
            indent = len(m.group(1))
            out[i:i + 1] = pr_lines(indent, by_url[m.group(2)])
            notes.append(f"ブランチを追加: {m.group(2)} → {by_url[m.group(2)]['headRefName']}")
        i += 1

    # 3. 載っていない PR を、リポジトリの見出しの下へ足す。見出しがなければ並び順の位置に作る。
    listed = {u for l in out for u in re.findall(r"https://github\.com/\S+?/pull/\d+", l)}  # pull/46 と pull/468 を区別する
    for pr in prs:
        if pr["url"] in listed:
            continue
        if pr["state"] == "CLOSED":  # マージせずに閉じた PR は足さない。載っているものは消さない。
            notes.append(f"マージせずに閉じた PR は足さない: {pr['url']}")
            continue
        label = REPOS[pr["repo"]]
        head = f"    - {label}"
        if head in out:
            at = out.index(head) + 1
            while at < len(out) and out[at].startswith("     "):
                at += 1
            out[at:at] = pr_lines(8, pr)
        else:
            rank = LABEL_ORDER.index(label)
            at = next((i for i, l in enumerate(out) if l.startswith("    - ") and l[6:].strip() in LABEL_ORDER
                       and LABEL_ORDER.index(l[6:].strip()) > rank), len(out))
            out[at:at] = [head] + pr_lines(8, pr)
        notes.append(f"PR を追加: {label} {pr['url']}（{pr['headRefName']}）")
    return out + tail, notes


def add_issues(text, new, domain):
    """日報にない課題を足す。new は (課題キー, 件名, 親課題のキーか None) の並び。
    親課題が「親子課題：KEY」の見出しにあればその節の末尾へ、なければ「個別の課題」の節の末尾へ、見出し行と Backlog の URL だけを足し、
    見出しの件数を1増やす。ステータス・PR・ブランチは update が書く。"""
    lines = text.split("\n")
    notes = []
    for key, summary, parent in new:
        # 節の見出しは ◼︎ の行に挟まれた1行。
        titles = [i for i in range(1, len(lines) - 1) if lines[i - 1].startswith("◼") and lines[i + 1].startswith("◼")]
        title = next((i for i in titles if parent and lines[i].startswith(f"親子課題：{parent}（")), None)
        if title is None:
            title = next((i for i in titles if lines[i].startswith("個別の課題")), None)
        if title is None:
            notes.append(f"{key}: 「個別の課題」の見出しがないので足さない")
            continue
        end = next((i - 1 for i in titles if i > title), len(lines))
        last = max(i for i in range(title + 1, end) if lines[i].strip())
        lines[last + 1:last + 1] = ["", f"- {key} {summary}", f"    - https://{domain}/view/{key}"]
        lines[title] = re.sub(r"(\d+)件）", lambda m: f"{int(m.group(1)) + 1}件）", lines[title], count=1)
        notes.append(f"{key}: 課題を追加: {lines[title]}")
    return "\n".join(lines), notes


def update(text, issues, prs_by_key, by_url, statuses):
    """日報の本文を書き換える。issues と prs_by_key は課題キーごとの Backlog 課題と関連 PR、by_url は PR の URL から PR への表、
    statuses は Backlog のステータス名の集合。"""
    lines = text.split("\n")
    report = []
    for key, start, end in reversed(blocks(lines)):
        new, notes = update_block(lines[start:end], key, issues.get(key), prs_by_key.get(key, []), by_url, statuses)
        lines[start:end] = new
        report[:0] = [f"{key}: {n}" for n in notes]
    return "\n".join(lines), report


def backlog_config():
    domain, api_key = os.environ.get("BACKLOG_DOMAIN"), os.environ.get("BACKLOG_API_KEY")
    if domain and api_key:
        return domain, api_key

    def find(node):
        if isinstance(node, dict):
            env = node.get("backlog", {}).get("env") if isinstance(node.get("backlog"), dict) else None
            if env and env.get("BACKLOG_DOMAIN") and env.get("BACKLOG_API_KEY"):
                return env["BACKLOG_DOMAIN"], env["BACKLOG_API_KEY"]
            return next(filter(None, map(find, node.values())), None)
        if isinstance(node, list):
            return next(filter(None, map(find, node)), None)
        return None

    path = Path.home() / ".claude.json"
    return find(json.loads(path.read_text())) if path.exists() else None


def backlog_get(domain, api_key, path, params=()):
    # Backlog の API キー認証はクエリ文字列だけが使える。URL はログや例外に出さない。
    req = f"https://{domain}/api/v2/{path}?" + urllib.parse.urlencode([("apiKey", api_key), *params])
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.load(res)
    except Exception as e:  # noqa: BLE001 例外の文字列に URL が入ることがあるので種類だけ返す
        return {"error": f"{type(e).__name__} {getattr(e, 'code', '')}".strip()}


def fetch_prs(repo):
    res = subprocess.run(["gh", "pr", "list", "-R", f"{OWNER}/{repo}", "--state", "all", "--limit", "5000",
                          "--json", "number,url,headRefName,title,state"], capture_output=True, text=True)
    if res.returncode:
        return repo, None, res.stderr.strip()
    return repo, [dict(pr, repo=repo) for pr in json.loads(res.stdout)], ""


def main():
    paths = [Path(sys.argv[1]).expanduser()] if len(sys.argv) > 1 else DEFAULT_FILES
    path = next((p for p in paths if p.exists()), None)
    if not path:
        print("日報がありません: " + "、".join(map(str, paths)), file=sys.stderr)
        return 2
    config = backlog_config()
    if not config:
        print("Backlog の接続先がありません。BACKLOG_DOMAIN と BACKLOG_API_KEY を設定してください。", file=sys.stderr)
        return 2
    text = path.read_text()
    keys = sorted({key for key, _, _ in blocks(text.split("\n"))})

    projects = sorted({k.rsplit("-", 1)[0] for k in keys})
    with ThreadPoolExecutor(8) as pool:
        issue_jobs = {k: pool.submit(backlog_get, *config, f"issues/{k}") for k in keys}
        status_jobs = {p: pool.submit(backlog_get, *config, f"projects/{p}/statuses") for p in projects}
        me_job = pool.submit(backlog_get, *config, "users/myself")
        pr_results = list(pool.map(fetch_prs, REPOS))
        fetched = {k: j.result() for k, j in issue_jobs.items()}
        fetched_statuses = {p: j.result() for p, j in status_jobs.items()}
        me = me_job.result()

    failed = [f"{k}: Backlog から取得できない（{v['error']}）"
              for k, v in {**fetched, **fetched_statuses, "users/myself": me}.items() if isinstance(v, dict) and "error" in v]
    failed += [f"{repo}: gh pr list に失敗（{err}）" for repo, prs, err in pr_results if prs is None]
    statuses = {s["name"] for v in fetched_statuses.values() if isinstance(v, list) for s in v}
    # ステータス名が取れないと既存のステータス行を見分けられず二重に足すので、そのプロジェクトの課題は更新しない。
    issues = {k: v for k, v in fetched.items() if "error" not in v and isinstance(fetched_statuses[k.rsplit("-", 1)[0]], list)}

    # 0. 自分が担当で「完了」以外の課題のうち、日報にないものを足す。対象のプロジェクトは日報に載っている課題のプロジェクト。
    open_ids = [s["id"] for v in fetched_statuses.values() if isinstance(v, list) for s in v if s["name"] != DONE]
    project_ids = sorted({v["projectId"] for v in issues.values()})
    if "error" not in me and open_ids and project_ids:
        # shortcut: 1回で取れる上限の100件まで。担当の未完了課題が100件を超えたら offset で続きを取る。
        mine = backlog_get(*config, "issues", [("assigneeId[]", me["id"]), ("count", 100), ("sort", "issueKey"),
                                               ("order", "asc"), *[("projectId[]", p) for p in project_ids],
                                               *[("statusId[]", s) for s in open_ids]])
        if isinstance(mine, dict):
            failed.append(f"担当の課題一覧: Backlog から取得できない（{mine['error']}）")
            mine = []
        key_by_id = {v["id"]: v["issueKey"] for v in [*issues.values(), *mine]}
        new = [v for v in mine if v["issueKey"] not in keys]
        text_with_new, report = add_issues(text, [(v["issueKey"], v["summary"], key_by_id.get(v["parentIssueId"]))
                                                  for v in new], config[0])
        issues.update({v["issueKey"]: v for v in new})
        keys = sorted({*keys, *(v["issueKey"] for v in new)})
    else:
        text_with_new, report = text, []

    all_prs = [pr for _, prs, _ in pr_results for pr in prs or []]
    by_url = {pr["url"]: pr for pr in all_prs}
    prs_by_key = {k: sorted((p for p in all_prs if related(k, p)), key=lambda p: p["number"]) for k in keys}

    new_text, notes = update(text_with_new, issues, prs_by_key, by_url, statuses)
    report += notes
    if new_text != text:
        shutil.copyfile(path, path.with_name(path.name + ".bak"))
        path.write_text(new_text)
        sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new_text.splitlines(True), str(path), str(path)))
    print("\n".join(["== 報告"] + (report or ["変更なし"]) + ["== 失敗"] + (failed or ["なし"])))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

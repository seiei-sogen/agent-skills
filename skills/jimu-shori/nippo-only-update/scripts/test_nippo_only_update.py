"""nippo_only_update.update の振る舞いを確かめる。実行: python3 -m unittest <このファイル>"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nippo_only_update import add_issues, related, update  # noqa: E402

GH = "https://github.com/AICROSS"
BEFORE = f"""◼︎◼︎◼︎
個別の課題（2件）
◼︎◼︎◼︎

- RICHME-1 一つめ
    - https://aosmobile.backlog.jp/view/RICHME-1
    - 設計中
    - チケット
        - {GH}/rcs_richme_tickets/pull/10

▼ 子課題
- RICHME-2（RICHME-1 の子課題）二つめ
    - https://aosmobile.backlog.jp/view/RICHME-2
    - チケット
        - {GH}/rcs_richme_tickets/pull/11
            - ブランチ
                - RICHME-2

- chore: 課題に紐づかない
    - FE
        - {GH}/rcs_richme_frontend/pull/9
"""


def issue(status):
    return {"status": {"name": status}, "priority": {"name": "中"}, "milestone": [{"name": "ver1.8.1"}],
            "startDate": "2026-11-13T00:00:00Z", "dueDate": None, "updated": "2026-11-25T06:16:17Z"}


def pr(repo, number, branch, title="", state="OPEN"):
    return {"repo": repo, "number": number, "url": f"{GH}/{repo}/pull/{number}", "headRefName": branch,
            "title": title, "state": state}


PRS = [pr("rcs_richme_tickets", 10, "RICHME-1"), pr("rcs_richme_tickets", 11, "RICHME-2"),
       pr("rcs_richme_backend", 20, "RICHME-1"), pr("IaC_richme", 30, "RICHME-1-iac"),
       pr("rcs_richme_frontend", 21, "feature/x", title="RICHME-1: 画面"), pr("rcs_richme_frontend", 9, "chore/x"),
       pr("rcs_richme_backend", 22, "RICHME-1-abandoned", state="CLOSED")]
BY_URL = {p["url"]: p for p in PRS}
ISSUES = {"RICHME-1": issue("マージ済み"), "RICHME-2": issue("処理中")}
STATUSES = {"未対応", "処理中", "設計中", "マージ済み"}
PRS_BY_KEY = {k: [p for p in PRS if related(k, p)] for k in ISSUES}


class UpdateTest(unittest.TestCase):
    def test_fills_status_branches_and_missing_prs_in_label_order(self):
        after, _ = update(BEFORE, ISSUES, PRS_BY_KEY, BY_URL, STATUSES)
        self.assertIn(f"""- RICHME-1 一つめ
    - https://aosmobile.backlog.jp/view/RICHME-1
    - マージ済み / 優先度 中 / ver1.8.1 / 開始 11/13 / 更新 11/25 15:16
    - チケット
        - {GH}/rcs_richme_tickets/pull/10
            - ブランチ
                - RICHME-1
    - BE
        - {GH}/rcs_richme_backend/pull/20
            - ブランチ
                - RICHME-1
    - FE
        - {GH}/rcs_richme_frontend/pull/21
            - ブランチ
                - feature/x
    - IaC
        - {GH}/IaC_richme/pull/30
            - ブランチ
                - RICHME-1-iac

▼ 子課題
- RICHME-2（RICHME-1 の子課題）二つめ
    - https://aosmobile.backlog.jp/view/RICHME-2
    - 処理中 / 優先度 中 / ver1.8.1 / 開始 11/13 / 更新 11/25 15:16
    - チケット
""", after)

    def test_does_not_add_closed_unmerged_pr(self):
        after, report = update(BEFORE, ISSUES, PRS_BY_KEY, BY_URL, STATUSES)
        self.assertNotIn("pull/22", after)
        self.assertIn(f"RICHME-1: マージせずに閉じた PR は足さない: {GH}/rcs_richme_backend/pull/22", report)

    def test_keeps_handwritten_note_under_the_url(self):
        text = "- RICHME-1 一つめ\n    - https://aosmobile.backlog.jp/view/RICHME-1\n    - 菅谷さんに仕様を確認中\n"
        after, _ = update(text, ISSUES, {}, {}, STATUSES)
        self.assertEqual(after, "- RICHME-1 一つめ\n    - https://aosmobile.backlog.jp/view/RICHME-1\n"
                                "    - マージ済み / 優先度 中 / ver1.8.1 / 開始 11/13 / 更新 11/25 15:16\n"
                                "    - 菅谷さんに仕様を確認中\n")

    def test_adds_pr_whose_url_is_a_prefix_of_a_listed_one(self):
        short = pr("rcs_richme_tickets", 1, "RICHME-1")
        after, _ = update(BEFORE, {}, {"RICHME-1": [short]}, BY_URL, STATUSES)
        self.assertIn(f"        - {GH}/rcs_richme_tickets/pull/1\n", after)

    def test_leaves_unlinked_pr_section_alone(self):
        after, _ = update(BEFORE, ISSUES, PRS_BY_KEY, BY_URL, STATUSES)
        self.assertTrue(after.endswith(f"- chore: 課題に紐づかない\n    - FE\n        - {GH}/rcs_richme_frontend/pull/9\n"))

    def test_second_run_changes_nothing(self):
        once, _ = update(BEFORE, ISSUES, PRS_BY_KEY, BY_URL, STATUSES)
        twice, report = update(once, ISSUES, PRS_BY_KEY, BY_URL, STATUSES)
        self.assertEqual(once, twice)
        self.assertEqual([n for n in report if "足さない" not in n], [])

    def test_related_ignores_mentions_in_the_middle_of_a_title(self):
        self.assertFalse(related("RICHME-1", pr("rcs_richme_tickets", 12, "RICHME-2", title="RICHME-2: 本体（RICHME-1 から分割）")))
        self.assertFalse(related("RICHME-1", pr("rcs_richme_tickets", 13, "RICHME-12")))


SECTIONS = """◼︎◼︎◼︎
個別の課題（1件）
◼︎◼︎◼︎

- RICHME-1 一つめ
    - https://aosmobile.backlog.jp/view/RICHME-1

◼︎◼︎◼︎
親子課題：RICHME-5（子課題 1件）
◼︎◼︎◼︎

▼ 親課題
- RICHME-5 親
    - https://aosmobile.backlog.jp/view/RICHME-5

▼ 子課題
- RICHME-6 子
    - https://aosmobile.backlog.jp/view/RICHME-6
"""


class AddIssuesTest(unittest.TestCase):
    def test_adds_child_under_its_parent_section_and_others_under_individual(self):
        after, report = add_issues(SECTIONS, [("RICHME-7", "子の二つめ", "RICHME-5"), ("RICHME-8", "単独", None)],
                                   "aosmobile.backlog.jp")
        self.assertEqual(after, SECTIONS.replace("個別の課題（1件）", "個別の課題（2件）")
                         .replace("子課題 1件", "子課題 2件")
                         .replace("view/RICHME-1\n", "view/RICHME-1\n\n- RICHME-8 単独\n"
                                  "    - https://aosmobile.backlog.jp/view/RICHME-8\n")
                         + "\n- RICHME-7 子の二つめ\n    - https://aosmobile.backlog.jp/view/RICHME-7\n")
        self.assertEqual(len(report), 2)

    def test_parent_not_in_nippo_goes_to_individual(self):
        after, _ = add_issues(SECTIONS, [("RICHME-9", "親が日報にない", "RICHME-99")], "aosmobile.backlog.jp")
        self.assertIn("個別の課題（2件）", after)
        self.assertIn("view/RICHME-1\n\n- RICHME-9 親が日報にない\n", after)

    def test_added_issue_gets_status_and_prs_from_update(self):
        added, _ = add_issues(SECTIONS, [("RICHME-2", "二つめ", None)],
                              "aosmobile.backlog.jp")
        after, _ = update(added, {"RICHME-2": issue("処理中")}, {"RICHME-2": [PRS[1]]}, BY_URL, STATUSES)
        self.assertIn(f"""- RICHME-2 二つめ
    - https://aosmobile.backlog.jp/view/RICHME-2
    - 処理中 / 優先度 中 / ver1.8.1 / 開始 11/13 / 更新 11/25 15:16
    - チケット
        - {GH}/rcs_richme_tickets/pull/11
            - ブランチ
                - RICHME-2
""", after)


if __name__ == "__main__":
    unittest.main()

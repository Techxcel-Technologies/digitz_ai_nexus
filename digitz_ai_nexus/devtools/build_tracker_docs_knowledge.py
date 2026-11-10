"""Build Tracker's replacement in the Nexus help seed, without a Frappe runtime."""
import argparse
import hashlib
import json
import re
from pathlib import Path

APP = "DIGITZ Tracker"
DEFAULT_TARGET = Path(__file__).resolve().parents[1] / "data/digitz_docs_knowledge.json"


def chapter(root, pattern, only=None, exclude=()):
    paths = sorted((root / "digitz_tracker/documentation/docs").glob(pattern))
    if len(paths) != 1:
        raise ValueError(f"Expected one chapter for {pattern}, found {len(paths)}")
    path = paths[0]
    raw = path.read_text()
    version = re.search(r"<!-- digitz-doc-version: ([\d.]+) -->", raw)
    if not version:
        raise ValueError(f"Missing documentation version in {path}")
    body = re.split(r"^# .+\n", raw, maxsplit=1, flags=re.M)[1]
    selected = []
    found = set()
    for section in re.split(r"(?=^## )", body, flags=re.M):
        heading = section.splitlines()[0].removeprefix("## ") if section.strip() else ""
        found.add(heading)
        if (only is None or heading in only) and heading not in exclude:
            selected.append(section.strip())
    if only is not None and not set(only).issubset(found):
        raise ValueError(f"Missing selected headings in {path}: {set(only) - found}")
    body = "\n\n".join(part for part in selected if part)
    if not body:
        raise ValueError(f"No content selected from {path}")
    # These repository Markdown paths are not public web routes.
    body = re.sub(r"\[([^\]]+)\]\((?!https?://|/)[^)]+\)", r"\1", body)
    return body, {
        "path": str(path.relative_to(root)),
        "sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "documentation_version": version.group(1),
    }


def tracker_entries(root):
    # Keep all eight existing source identities to overwrite legacy bodies in place.
    specifications = [
        ("Overview", "Getting Started", "01-*.md", {"What the app does"}, ()),
        ("Key Concepts", "Getting Started", "01-*.md", {"Two kinds of holder", "Roles"}, ()),
        ("Quick Start", "Getting Started", "02-*.md", None, {"Installation", "Demo data"}),
        ("Document Registration", "Features", "03-*.md", {"The Document register (`/tracker/documents`)", "Who sees what"}, ()),
        ("Expiry Automation & Alerts", "Features", "04-*.md", None, ()),
        ("Employee Assignments", "Features", "09-*.md", None, ()),
        ("Status Tracking", "Features", "03-*.md", {"The document panel", "My work (`/tracker/work`)"}, ()),
        ("Renewal Workflow", "Features", "03-*.md", {"A document and its cycles"}, ()),
        ("Files and AI Assistant", "Features", "03-*.md", {"Files (`/tracker/files`)", "AI assistant"}, ()),
        ("Add-ons", "Administration", "05-*.md", None, ()),
        ("Client Portal", "Features", "06-*.md", None, ()),
        ("Expiry and Home Overview", "Features", "07-*.md", None, ()),
        ("Classic Navigation and Desk Access", "Getting Started", "08-*.md", None, ()),
        ("Mobile App", "Features", "12-*.md", None, ()),
        ("DIGITZ PRIME Workspaces", "Administration", "13-*.md", None, ()),
        ("Services Add-on", "Add-ons", "addons/services.md", None, ()),
    ]
    entries = []
    for topic, group, pattern, only, exclude in specifications:
        body, source = chapter(root, pattern, only, exclude)
        entries.append({
            "app": APP, "context": "DIGITZ-TRACKER", "sub_context": group,
            "topic": topic, "entity": topic,
            "anchor": re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-"),
            "title": f"{APP} — {topic}",
            "content": f"# {APP} — {topic}\n\n{body}",
            "source_document": source,
        })
    return entries


def replace_tracker(payload, entries):
    titles = [entry["title"] for entry in entries]
    if not entries or len(titles) != len(set(titles)):
        raise ValueError("Tracker replacement must have unique nonempty entries")
    old_titles = {e["title"] for e in payload["entries"] if e["app"] == APP}
    if not old_titles.issubset(titles):
        raise ValueError("Replacement would orphan existing Tracker source titles")
    result = dict(payload)
    others = [e for e in payload["entries"] if e["app"] != APP]
    result["entries"] = others + entries
    all_titles = [e["title"] for e in result["entries"]]
    if len(all_titles) != len(set(all_titles)):
        raise ValueError("Duplicate Knowledge Source title")
    result["count"] = len(result["entries"])
    result["tracker_generated_from"] = "digitz_tracker/documentation/docs (source_document hashes identify exact input)"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracker-root", type=Path, required=True)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    payload = json.loads(args.target.read_text())
    entries = tracker_entries(args.tracker_root.resolve())
    updated = replace_tracker(payload, entries)
    args.target.write_text(json.dumps(updated, indent="\t", ensure_ascii=False) + "\n")
    print(f"Replaced Tracker with {len(entries)} sections; {updated['count']} total entries")


if __name__ == "__main__":
    main()

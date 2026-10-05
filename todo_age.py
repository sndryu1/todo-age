#!/usr/bin/env python3
"""todo-age: list TODO/FIXME comments in a git repo, oldest first, with author and age."""
import argparse, json, re, subprocess, sys, time

TAGS = ("TODO", "FIXME", "HACK", "XXX")
PATTERN = re.compile(r"\b(%s)\b[:\s(]*(.*)" % "|".join(TAGS))


def git(*args, cwd="."):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def find_todos(cwd="."):
    """Yield (path, lineno, tag, text) for every tagged line in tracked files."""
    try:
        out = git("grep", "-nIE", r"\b(%s)\b" % "|".join(TAGS), cwd=cwd)
    except subprocess.CalledProcessError:
        return
    for line in out.splitlines():
        path, lineno, content = line.split(":", 2)
        m = PATTERN.search(content)
        if m:
            yield path, int(lineno), m.group(1), m.group(2).strip()


def blame(path, lineno, cwd="."):
    out = git("blame", "--porcelain", "-L", f"{lineno},{lineno}", "--", path, cwd=cwd)
    info = {}
    for l in out.splitlines():
        if l.startswith("author "):
            info["author"] = l[7:]
        elif l.startswith("author-time "):
            info["time"] = int(l[12:])
    return info.get("author", "?"), info.get("time", int(time.time()))


def collect(cwd=".", now=None):
    now = now or time.time()
    items = []
    for path, lineno, tag, text in find_todos(cwd):
        try:
            author, ts = blame(path, lineno, cwd)
        except subprocess.CalledProcessError:
            continue  # uncommitted / untracked line
        items.append({"file": path, "line": lineno, "tag": tag, "text": text,
                      "author": author, "days": int((now - ts) // 86400)})
    return sorted(items, key=lambda i: -i["days"])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-days", type=int, default=0, help="only show items at least this old")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("--fail-over", type=int, metavar="DAYS", help="exit 1 if any item is older than DAYS (for CI)")
    a = p.parse_args(argv)
    items = [i for i in collect() if i["days"] >= a.min_days]
    if a.json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        for i in items:
            print(f"{i['days']:>5}d  {i['tag']:<5} {i['file']}:{i['line']}  ({i['author']})  {i['text']}")
        print(f"\n{len(items)} item(s)", file=sys.stderr)
    if a.fail_over is not None and any(i["days"] > a.fail_over for i in items):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

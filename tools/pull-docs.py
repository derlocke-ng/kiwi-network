#!/usr/bin/env python3
"""Assemble the docs site: kiwi-network's own docs/ plus the docs/ folders of
the repositories in docs-sources.yml, at their latest release tags.

Writes build/src/ (the combined pages) and build/mkdocs.yml (the site config
with the pulled pages in the menu). Then build with:

    mkdocs build --strict -f build/mkdocs.yml      # output in build/docs/

Options:
    --offline            skip pulling; build/mkdocs.yml then equals mkdocs.yml
    --local REPO=PATH    use a local checkout for REPO instead of cloning (testing)

A source that cannot be used is skipped with a message; the build goes on.
"""
import os
import re
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
SRC = os.path.join(BUILD, "src")
PULL = os.path.join(BUILD, "pull")
CHECKER = os.path.join(ROOT, "plugins/kiwi-docs/skills/kiwi-docs/scripts/check-docs.py")
RELEASE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
IN_CI = bool(os.environ.get("GITHUB_ACTIONS"))


def log(msg, level="notice"):
    print(f"::{level}::{msg}" if IN_CI else f"[{level}] {msg}", flush=True)


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def latest_release(url):
    tags = []
    for line in git("ls-remote", "--tags", "--refs", url).splitlines():
        name = line.split("refs/tags/", 1)[-1]
        m = RELEASE.match(name)
        if m:
            tags.append((tuple(int(x) for x in m.groups()), name))
    return max(tags)[1] if tags else None


def read_nav(path):
    pages = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\s*-\s+([A-Za-z0-9._/-]+\.md)\s*:\s*(.+?)\s*$", line)
            if m:
                pages.append((m.group(1), m.group(2).strip("'\"")))
    return pages


def place(nav, overview, title_for_section, entries):
    """Replace the menu entry of `overview` with a section (or add a subsection)."""
    for i, item in enumerate(nav):
        if isinstance(item, dict):
            (title, value), = item.items()
            if value == overview:
                if title == "Overview":
                    nav.insert(i + 1, {title_for_section: entries})
                else:
                    nav[i] = {title: [{"Overview": overview}] + entries}
                return True
            if isinstance(value, list) and place(value, overview, title_for_section, entries):
                return True
    return False


def pull_source(src, local, nav):
    repo, overview = src["repo"], src["overview"]
    name = repo.split("/")[-1]
    if not os.path.exists(os.path.join(SRC, overview)):
        log(f"{repo}: overview page {overview} does not exist; skipped", "warning")
        return
    if repo in local:
        checkout, ref = local[repo], "local"
    else:
        url = f"https://github.com/{repo}"
        try:
            ref = src.get("ref") or latest_release(url)
        except subprocess.CalledProcessError as e:
            log(f"{repo}: cannot list tags ({e.stderr.strip()}); skipped", "warning")
            return
        if not ref:
            log(f"{repo}: no release tag yet; skipped")
            return
        checkout = os.path.join(PULL, name)
        shutil.rmtree(checkout, ignore_errors=True)
        try:
            git("clone", "-q", "--depth", "1", "--branch", ref, "--filter=blob:none", url, checkout)
        except subprocess.CalledProcessError as e:
            log(f"{repo}: cannot clone {ref} ({e.stderr.strip()}); skipped", "warning")
            return
    docs = os.path.join(checkout, "docs")
    if not os.path.isfile(os.path.join(docs, "kiwi-docs.yml")):
        log(f"{repo} {ref}: no docs/kiwi-docs.yml at this release; skipped")
        return
    check = subprocess.run([sys.executable, "-I", CHECKER, checkout, "--docs-only", "--no-upstream"],
                           capture_output=True, text=True)
    if check.returncode != 0:
        errors = [l for l in check.stdout.splitlines() if l.startswith("ERROR")]
        log(f"{repo} {ref}: docs/ has errors, skipped: " + " | ".join(errors[:5]), "warning")
        return
    # desktop/kiwi-updater.md -> desktop/kiwi-updater/; an index.md overview (server/index.md)
    # gets a folder named after the repository instead (server/kiwi-server/).
    if os.path.basename(overview) == "index.md":
        target_rel = os.path.join(os.path.dirname(overview), name)
    else:
        target_rel = overview[:-3]
    target = os.path.join(SRC, target_rel)
    if os.path.exists(target):
        log(f"{repo}: {target_rel}/ already exists in docs/; skipped", "warning")
        return
    back = os.path.relpath(os.path.join(SRC, overview), os.path.join(SRC, target_rel))
    tree = f"https://github.com/{repo}/tree/{ref}/docs" if ref != "local" else f"https://github.com/{repo}"
    for d, _, files in os.walk(docs):
        for f in files:
            rel = os.path.relpath(os.path.join(d, f), docs)
            if f == "kiwi-docs.yml" or re.match(r"^README(\.[a-z]{2})?\.md$", rel):
                continue
            dst = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not f.endswith(".md"):
                shutil.copy2(os.path.join(d, f), dst)
                continue
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                text = fh.read()
            depth = "../" * rel.count("/")
            text = re.sub(r"\]\(\s*(?:\./)?README(?:\.[a-z]{2})?\.md(?:#[^)\s]*)?\s*\)", f"]({depth}{back})", text)
            text = text.rstrip("\n") + (f"\n\n---\n\n<small>This page comes from the `docs/` folder of "
                                        f"[{repo}]({tree}) at `{ref}`.</small>\n")
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
    pages = read_nav(os.path.join(docs, "kiwi-docs.yml"))
    entries = [{title: f"{target_rel}/{page}"} for page, title in pages]
    if not place(nav, overview, src.get("menu", f"{name} reference"), entries):
        log(f"{repo}: {overview} is not in the menu of mkdocs.yml; pages added without a menu entry", "warning")
    log(f"{repo} {ref}: {len(pages)} page(s) under {target_rel}/")


def main(argv):
    local = dict(a.split("=", 1) for a in argv[argv.index("--local") + 1:argv.index("--local") + 2]) \
        if "--local" in argv else {}
    with open(os.path.join(ROOT, "mkdocs.yml"), encoding="utf-8") as f:
        config = yaml.safe_load(f)
    shutil.rmtree(SRC, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, config.get("docs_dir", "docs")), SRC)
    if "--offline" not in argv:
        with open(os.path.join(ROOT, "docs-sources.yml"), encoding="utf-8") as f:
            sources = yaml.safe_load(f)["sources"]
        os.makedirs(PULL, exist_ok=True)
        for src in sources:
            pull_source(src, local, config["nav"])
    config["docs_dir"] = "src"
    config["site_dir"] = "docs"
    with open(os.path.join(BUILD, "mkdocs.yml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False, width=200)
    print("wrote build/mkdocs.yml and build/src/")


if __name__ == "__main__":
    main(sys.argv[1:])

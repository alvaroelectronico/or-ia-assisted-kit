"""Install, update and promote the methodology kit across repositories.

The kit (this directory) is the single source of truth for the reusable layer:
the playbook, the templates, the phase skills and the agents. A *target*
repository receives a copy of those files plus a lock file
(`.methodology-kit.lock.json`) recording, per file, the hash of the kit version
it was installed from. That base hash gives a three-way comparison:

    local  = the file in the target now
    base   = the kit file as it was when installed/last synced (lock hash)
    kit    = the kit file now

    local == base, kit == base  -> ok
    local != base, kit == base  -> local      (template matured in the target)
    local == base, kit != base  -> upstream   (the kit improved; `update` applies it)
    local != base, kit != base  -> conflict   (`update` writes <file>.kit-new)

Commands (run with the kit checkout you want to sync against):

    python kit.py install  <target> [--adopt | --force]
    python kit.py status   <target>
    python kit.py update   <target> [--dry-run]
    python kit.py resolve  <target> <path> [<path> ...]
    python kit.py promote  <target> [<path> ...] [--apply] [--force]
    python kit.py doctor   [--forbid TERM ...]

Standard library only; Python 3.10+.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent
LOCK_NAME = ".methodology-kit.lock.json"
CONFLICT_SUFFIX = ".kit-new"

# Files kept in sync with the kit (relative to the kit root / target root).
MANAGED_DIRS = (".claude/skills", ".claude/agents", "docs/methodology/templates")
MANAGED_FILES = ("docs/methodology/README.md",)
# Copied once on install, then owned by the target (never updated or promoted).
SEED_FILES = ("docs/methodology/registry.md",)

CLAUDE_MD = "CLAUDE.md"
CLAUDE_SNIPPET = "claude-snippet.md"
BLOCK_START = "<!-- methodology-kit:start -->"
BLOCK_END = "<!-- methodology-kit:end -->"


class KitError(Exception):
    """A user-facing error: printed without a traceback."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def file_hash(path: Path) -> str:
    """sha256 of the file with line endings normalized (immune to autocrlf)."""
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def kit_version(kit_root: Path) -> str:
    return (kit_root / "VERSION").read_text(encoding="utf-8").strip()


def kit_commit(kit_root: Path) -> str | None:
    """Current kit commit (suffixed `-dirty` if the kit has local changes)."""
    try:
        head = subprocess.run(
            ["git", "-C", str(kit_root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(kit_root), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return f"{head}-dirty" if dirty else head


def managed_files(kit_root: Path) -> list[str]:
    """Relative POSIX paths of every kit-managed file, sorted."""
    paths = [p for p in MANAGED_FILES if (kit_root / p).is_file()]
    for d in MANAGED_DIRS:
        base = kit_root / d
        if base.is_dir():
            paths += [
                p.relative_to(kit_root).as_posix()
                for p in base.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            ]
    return sorted(set(paths))


def load_lock(target: Path) -> dict:
    lock_path = target / LOCK_NAME
    if not lock_path.is_file():
        raise KitError(
            f"{target} has no {LOCK_NAME}; run `kit.py install {target}` first."
        )
    return json.loads(lock_path.read_text(encoding="utf-8"))


def save_lock(target: Path, lock: dict) -> None:
    lock["files"] = dict(sorted(lock["files"].items()))
    (target / LOCK_NAME).write_text(
        json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def stamp_lock(lock: dict, kit_root: Path) -> None:
    lock["kit_version"] = kit_version(kit_root)
    lock["kit_commit"] = kit_commit(kit_root)
    lock["synced_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def render_claude_block(kit_root: Path) -> str:
    snippet = (kit_root / CLAUDE_SNIPPET).read_text(encoding="utf-8").strip()
    return f"{BLOCK_START}\n{snippet}\n{BLOCK_END}"


def sync_claude_md(target: Path, kit_root: Path) -> str:
    """Insert or refresh the kit block in the target's CLAUDE.md."""
    path = target / CLAUDE_MD
    block = render_claude_block(kit_root)
    if not path.is_file():
        path.write_text(block + "\n", encoding="utf-8")
        return "created"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END), re.S)
    if pattern.search(text):
        new = pattern.sub(lambda _: block, text, count=1)
        if new == text:
            return "unchanged"
        path.write_text(new, encoding="utf-8")
        return "refreshed"
    path.write_text(text.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8")
    return "appended"


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify(target: Path, kit_root: Path, lock: dict) -> dict[str, str]:
    """State of every file known to the kit or the lock (see module docstring).

    Extra states: `missing` (deleted in the target), `new` (added to the kit
    since the last sync), `removed` (dropped from the kit since the last sync).
    """
    states: dict[str, str] = {}
    kit_paths = set(managed_files(kit_root))
    for rel in sorted(kit_paths | set(lock["files"])):
        local, kit = target / rel, kit_root / rel
        base = lock["files"].get(rel)
        if base is None:
            states[rel] = "new"
        elif rel not in kit_paths:
            states[rel] = "removed"
        elif not local.is_file():
            states[rel] = "missing"
        else:
            local_changed = file_hash(local) != base
            kit_changed = file_hash(kit) != base
            states[rel] = {
                (False, False): "ok",
                (True, False): "local",
                (False, True): "upstream",
                (True, True): "conflict",
            }[(local_changed, kit_changed)]
            # A local edit that happens to equal the new kit file is in sync.
            if states[rel] == "conflict" and file_hash(local) == file_hash(kit):
                states[rel] = "ok-stale-lock"
    return states


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_install(
    target: Path, kit_root: Path, adopt: bool = False, force: bool = False
) -> int:
    if (target / LOCK_NAME).exists():
        raise KitError(f"{target} already has {LOCK_NAME}; use `update` instead.")
    if not target.is_dir():
        raise KitError(f"target {target} is not a directory.")

    files = managed_files(kit_root)
    clashes = [
        rel
        for rel in files
        if (target / rel).is_file()
        and file_hash(target / rel) != file_hash(kit_root / rel)
    ]
    if clashes and not (adopt or force):
        listing = "\n  ".join(clashes)
        raise KitError(
            f"{len(clashes)} file(s) already exist in the target with different "
            f"content:\n  {listing}\nRe-run with --adopt (keep them, track them as "
            "local changes) or --force (overwrite them with the kit version)."
        )

    lock = {"files": {}, "forbidden_terms": []}
    copied = kept = 0
    for rel in files:
        src, dst = kit_root / rel, target / rel
        if rel in clashes and adopt:
            kept += 1
        else:
            copy_file(src, dst)
            copied += 1
        lock["files"][rel] = file_hash(src)

    for rel in SEED_FILES:
        if not (target / rel).exists():
            copy_file(kit_root / rel, target / rel)
            print(f"seeded   {rel}")
        else:
            print(f"kept     {rel} (already present; owned by the target)")

    stamp_lock(lock, kit_root)
    save_lock(target, lock)
    print(f"CLAUDE.md {sync_claude_md(target, kit_root)}")
    print(
        f"installed kit {lock['kit_version']} into {target}: {copied} copied, "
        f"{kept} adopted as local changes; lock written to {LOCK_NAME}."
    )
    return 0


def cmd_status(target: Path, kit_root: Path) -> int:
    lock = load_lock(target)
    states = classify(target, kit_root, lock)
    print(
        f"target lock: kit {lock.get('kit_version')} ({lock.get('kit_commit')}), "
        f"synced {lock.get('synced_at')}"
    )
    print(f"kit now:     {kit_version(kit_root)} ({kit_commit(kit_root)})")
    counts: dict[str, int] = {}
    for rel, state in states.items():
        counts[state] = counts.get(state, 0) + 1
        if state != "ok":
            pending = " [.kit-new pending]" if _has_conflict_file(target, rel) else ""
            print(f"  {state:<14} {rel}{pending}")
    print("summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


def _has_conflict_file(target: Path, rel: str) -> bool:
    return (target / (rel + CONFLICT_SUFFIX)).exists()


def cmd_update(target: Path, kit_root: Path, dry_run: bool = False) -> int:
    lock = load_lock(target)
    states = classify(target, kit_root, lock)
    conflicts = 0
    for rel, state in states.items():
        local, kit = target / rel, kit_root / rel
        action = None
        if state in ("upstream", "missing"):
            action = "updated" if state == "upstream" else "restored"
            if not dry_run:
                copy_file(kit, local)
                lock["files"][rel] = file_hash(kit)
        elif state == "ok-stale-lock":
            action = "relocked"
            if not dry_run:
                lock["files"][rel] = file_hash(kit)
        elif state == "new":
            if local.is_file() and file_hash(local) != file_hash(kit):
                action = f"conflict (new kit file; wrote {rel}{CONFLICT_SUFFIX})"
                conflicts += 1
                if not dry_run:
                    copy_file(kit, target / (rel + CONFLICT_SUFFIX))
            else:
                action = "added"
                if not dry_run:
                    copy_file(kit, local)
                    lock["files"][rel] = file_hash(kit)
        elif state == "conflict":
            action = f"conflict (wrote {rel}{CONFLICT_SUFFIX})"
            conflicts += 1
            if not dry_run:
                copy_file(kit, target / (rel + CONFLICT_SUFFIX))
        elif state == "removed":
            if local.is_file() and file_hash(local) == lock["files"][rel]:
                action = "deleted (dropped from the kit)"
                if not dry_run:
                    local.unlink()
            else:
                action = "untracked (dropped from the kit; local copy kept)"
            if not dry_run:
                del lock["files"][rel]
        if action:
            print(f"  {action:<16} {rel}")

    if not dry_run:
        stamp_lock(lock, kit_root)
        save_lock(target, lock)
        print(f"CLAUDE.md {sync_claude_md(target, kit_root)}")
    print(
        ("[dry-run] " if dry_run else "")
        + f"update to kit {kit_version(kit_root)} done; {conflicts} conflict(s)."
    )
    if conflicts:
        print(
            "Merge each <file>.kit-new into <file> by hand, then run "
            "`kit.py resolve <target> <file> ...`."
        )
    return 1 if conflicts else 0


def cmd_resolve(target: Path, kit_root: Path, paths: list[str]) -> int:
    """Mark merged conflicts: the current kit file becomes the new base."""
    lock = load_lock(target)
    for rel in (_to_rel(target, p) for p in paths):
        if not (kit_root / rel).is_file():
            raise KitError(f"{rel} is not a kit-managed file.")
        lock["files"][rel] = file_hash(kit_root / rel)
        pending = target / (rel + CONFLICT_SUFFIX)
        if pending.exists():
            pending.unlink()
        print(f"  resolved  {rel}")
    save_lock(target, lock)
    return 0


def _to_rel(target: Path, path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        p = p.resolve().relative_to(target.resolve())
    rel = p.as_posix()
    return rel[: -len(CONFLICT_SUFFIX)] if rel.endswith(CONFLICT_SUFFIX) else rel


def binding_terms(target: Path) -> list[str]:
    """Concrete slug/package values from the target registry's Project binding."""
    registry = target / "docs/methodology/registry.md"
    if not registry.is_file():
        return []
    terms = []
    for line in registry.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(Problem slug|Code package)[^|]*\|\s*`([^`]+)`", line)
        if m and not m.group(2).startswith("<"):
            terms.append(m.group(2))
    return terms


def find_forbidden(text: str, terms: list[str]) -> list[str]:
    return [t for t in terms if re.search(re.escape(t), text, re.I)]


def cmd_promote(
    target: Path,
    kit_root: Path,
    paths: list[str] | None = None,
    apply: bool = False,
    force: bool = False,
) -> int:
    """Send locally-matured managed files back into the kit."""
    lock = load_lock(target)
    states = classify(target, kit_root, lock)
    wanted = {_to_rel(target, p) for p in paths} if paths else None
    terms = list(lock.get("forbidden_terms", [])) + binding_terms(target)
    blocked = 0
    candidates = [
        rel
        for rel, s in states.items()
        if s in ("local", "conflict") and (wanted is None or rel in wanted)
    ]
    if wanted:
        for rel in sorted(wanted - set(candidates)):
            print(f"  skip      {rel} (state: {states.get(rel, 'not managed')})")
    for rel in candidates:
        local, kit = target / rel, kit_root / rel
        if states[rel] == "conflict":
            print(f"  blocked   {rel} (kit changed too: run `update` and merge first)")
            blocked += 1
            continue
        hits = find_forbidden(local.read_text(encoding="utf-8"), terms)
        if hits and not force:
            print(f"  blocked   {rel} (case-specific terms: {', '.join(hits)})")
            blocked += 1
            continue
        if not apply:
            diff = difflib.unified_diff(
                kit.read_text(encoding="utf-8").splitlines(),
                local.read_text(encoding="utf-8").splitlines(),
                fromfile=f"kit/{rel}",
                tofile=f"target/{rel}",
                lineterm="",
            )
            print("\n".join(diff))
            continue
        copy_file(local, kit)
        lock["files"][rel] = file_hash(kit)
        print(f"  promoted  {rel}")
    if apply:
        save_lock(target, lock)
        print(
            "Promoted files are now uncommitted changes in the kit: review, bump "
            "VERSION, add a CHANGELOG entry, and commit them in the kit repo."
        )
    elif candidates:
        print("(preview only; re-run with --apply to copy into the kit)")
    else:
        print("nothing to promote.")
    return 1 if blocked else 0


def cmd_doctor(kit_root: Path, forbid: list[str] | None = None) -> int:
    """Self-consistency checks on the kit itself."""
    problems: list[str] = []
    agents_dir = kit_root / ".claude/agents"
    agents = {p.stem for p in agents_dir.glob("*.md")}
    skills_dir = kit_root / ".claude/skills"

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill = skill_dir / "SKILL.md"
        if not skill.is_file():
            problems.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        front = _frontmatter(skill.read_text(encoding="utf-8"))
        if front.get("name") != skill_dir.name:
            problems.append(f"{skill_dir.name}: frontmatter name={front.get('name')!r}")
        if "description" not in front:
            problems.append(f"{skill_dir.name}: frontmatter has no description")
        if front.get("agent") and front["agent"] not in agents:
            problems.append(f"{skill_dir.name}: unknown agent {front['agent']!r}")

    for agent in sorted(agents_dir.glob("*.md")):
        front = _frontmatter(agent.read_text(encoding="utf-8"))
        if front.get("name") != agent.stem:
            problems.append(
                f"agents/{agent.name}: frontmatter name={front.get('name')!r}"
            )

    # Every templates/<file> mentioned anywhere must exist.
    templates = kit_root / "docs/methodology/templates"
    texts = {
        rel: (kit_root / rel).read_text(encoding="utf-8")
        for rel in managed_files(kit_root)
    }
    texts["docs/methodology/registry.md"] = (
        kit_root / "docs/methodology/registry.md"
    ).read_text(encoding="utf-8")
    texts["README.md"] = (kit_root / "README.md").read_text(encoding="utf-8")
    for rel, text in texts.items():
        for name in sorted(set(re.findall(r"templates/([\w.-]+\.\w+)", text))):
            if not (templates / name).is_file():
                problems.append(f"{rel}: references missing templates/{name}")
        # `/skill-name` and `skill-name` references to p*/known skills.
        for name in sorted(set(re.findall(r"`/?(p\d+-[a-z-]+)`", text))):
            if not (skills_dir / name).is_dir():
                problems.append(f"{rel}: references missing skill {name}")
        if forbid:
            for term in find_forbidden(text, forbid):
                problems.append(f"{rel}: contains forbidden term {term!r}")

    # Registry asset rows must point at shipped files.
    registry = texts["docs/methodology/registry.md"]
    for path in re.findall(
        r"^\|\s*A-[\w-]+\s*\|[^|]*\|[^|]*\|\s*`([^`]+)`", registry, re.M
    ):
        full = (
            (kit_root / path)
            if path.startswith(".claude")
            else (kit_root / "docs/methodology" / path)
        )
        if not full.is_file():
            problems.append(f"registry.md: asset path {path} does not exist")

    for p in problems:
        print(f"  problem   {p}")
    print(f"doctor: {len(problems)} problem(s) in kit {kit_version(kit_root)}.")
    return 1 if problems else 0


def _frontmatter(text: str) -> dict[str, str]:
    """Top-level `key: value` pairs of a YAML frontmatter (folded values skipped)."""
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            out[km.group(1)] = km.group(2).strip()
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kit.py", description=__doc__.split("\n\n")[0]
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("install", help="first-time install into a target repo")
    p.add_argument("target", type=Path)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--adopt", action="store_true", help="keep differing files")
    g.add_argument("--force", action="store_true", help="overwrite differing files")

    p = sub.add_parser("status", help="three-way state of every managed file")
    p.add_argument("target", type=Path)

    p = sub.add_parser("update", help="pull kit changes into a target repo")
    p.add_argument("target", type=Path)
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("resolve", help="mark merged conflicts as resolved")
    p.add_argument("target", type=Path)
    p.add_argument("paths", nargs="+")

    p = sub.add_parser("promote", help="send local template improvements to the kit")
    p.add_argument("target", type=Path)
    p.add_argument("paths", nargs="*")
    p.add_argument("--apply", action="store_true", help="copy (default: preview diff)")
    p.add_argument("--force", action="store_true", help="ignore forbidden terms")

    p = sub.add_parser("doctor", help="self-consistency checks on the kit")
    p.add_argument("--forbid", nargs="*", default=[], help="terms that must not appear")

    args = parser.parse_args(argv)
    # Templates contain non-ASCII (—, →, ≈); never crash on a cp1252 console.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        if args.cmd == "install":
            return cmd_install(args.target, KIT_ROOT, args.adopt, args.force)
        if args.cmd == "status":
            return cmd_status(args.target, KIT_ROOT)
        if args.cmd == "update":
            return cmd_update(args.target, KIT_ROOT, args.dry_run)
        if args.cmd == "resolve":
            return cmd_resolve(args.target, KIT_ROOT, args.paths)
        if args.cmd == "promote":
            return cmd_promote(
                args.target, KIT_ROOT, args.paths, args.apply, args.force
            )
        return cmd_doctor(KIT_ROOT, args.forbid)
    except KitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

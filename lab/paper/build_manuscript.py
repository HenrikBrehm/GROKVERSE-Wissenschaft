"""Assemble a clean English manuscript (main text only) from the working drafts (session 51, rule 20d).

Reads lab/paper/draft_short.md (abstract, sections 1-7, figure captions), the AI-use disclosure of lab/paper/draft.md and the
reference list lab/paper/references.md; writes lab/paper/manuscript.md (generated, do not edit by hand: edit the drafts and
rebuild). Headings lose their German process notes ("(Kurzfassung, Sitzung ...)"), German check notes ("*Prüfung ...*") are
dropped. Text of the paragraphs is copied verbatim. Also prints word counts and a citation check: every "Author (year)" /
"Author et al., year" in the main text must match an entry of the reference list (by first surname and year).
  python lab/paper/build_manuscript.py            (no training, reads and writes markdown only)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TITLE = "Training-set composition steers and locks in the Fourier features of grokking transformers"
SECTIONS = ["Abstract", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 "]


def sections(md: str) -> dict[str, tuple[str, list[str]]]:
    """'## heading' -> (heading, paragraphs) for the level-2 sections of a markdown file."""
    out, cur = {}, None
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if b.startswith("## "):
            cur = b[3:].split("\n")[0]
            out[cur] = (cur, [])
            rest = b.split("\n", 1)[1:] if "\n" in b else []
            if rest and rest[0].strip():
                out[cur][1].append(rest[0].strip())
        elif cur is not None and b:
            out[cur][1].append(b)
    return out


def clean_heading(h: str) -> str:
    """Drop the trailing German process note: '3 Result 1: ... (Kurzfassung, Sitzung 43; ...)' -> '3 Result 1: ...'."""
    m = re.search(r"\s*\(([^()]*?)(;\s*)?(Kurzfassung|Entwurf|draft)[^()]*(\([^()]*\)[^()]*)*\)\s*$", h)
    if m:
        kept = m.group(1).strip().rstrip(";").strip()
        h = h[:m.start()] + (f" ({kept})" if kept else "")
    return h.strip()


def is_process_note(p: str) -> bool:
    return bool(re.match(r"^\*{1,2}(Prüfung|Nachtrag|Hinweis|Stand|Korrektur)", p))


def find(secs: dict, prefix: str) -> tuple[str, list[str]]:
    hits = [v for k, v in secs.items() if k.startswith(prefix)]
    if len(hits) != 1:
        sys.exit(f"expected exactly one section starting with {prefix!r}, found {len(hits)}")
    return hits[0]


CITE = re.compile(r"([A-Z][A-Za-zÀ-ÿ'\-]+(?: [A-Z][A-Za-zÀ-ÿ'\-]+)?)(?: et al\.| and [A-Z][A-Za-zÀ-ÿ'\-]+| & [A-Z][A-Za-zÀ-ÿ'\-]+)?,? \(?((?:19|20)\d\d[ab]?)\)?")


def citations(text: str) -> set[tuple[str, str]]:
    skip = {"Figure", "Section", "Appendix", "Table", "Result", "Sitzung", "September", "Session", "In", "The", "At", "On", "By", "For"}
    return {(m.group(1).split()[-1], m.group(2)) for m in CITE.finditer(text) if m.group(1).split()[0] not in skip}


def clean_ref(line: str) -> str:
    """Drop working notes from a reference line: text after " — ", German parentheticals, and all of a provenance tag except
    its letter codes (A, L, K, S, F; see paper/references for the full tags)."""
    line = line.split(" — ")[0]
    line = re.sub(r" \((?:Titelzusatz|laut|nicht)[^)]*\)", "", line)

    def tag(m: re.Match) -> str:
        codes = [t.strip() for t in re.split(r"[;,]", m.group(1)) if re.fullmatch(r"[A-Z](?:/[A-Z])*", t.strip())]
        return "[" + ", ".join(codes) + "]" if codes else "[untagged]"

    return re.sub(r"\[([^\]]*)\]\s*$", tag, line.rstrip())


def ref_keys(refs_md: str) -> set[tuple[str, str]]:
    keys = set()
    for line in refs_md.splitlines():
        m = re.match(r"^- (.+?) \(((?:19|20)\d\d[ab]?)\)\.", line)
        if m:
            first = re.split(r",| and | & |\(", m.group(1))[0].strip()
            keys.add((first.split()[-1], m.group(2)))
    return keys


# Appendix plan (draft_short, "Abbildungen ... und Anhang"): letter -> (title, sources). "L:3.7" = long-draft subsection,
# "L2:4 " = long-draft level-2 section, "S:Anhang J" = draft_short section. Copied verbatim; cross-references not yet edited.
APPENDIX = [
    ("A", "Robustness (R1/C1, P4/C3, R7, R2/C2, R14, R15)", ["L:3.7", "L:3.11", "L:3.12", "L:3.13"]),
    ("B", "Functional measures and their limit (P2d/P2e)", ["L:3.2"]),
    ("C", "Lock-in in detail (K4/K4b, K4c, resets K4d/K4e, R6/R8)", ["L:3.3", "L:3.4", "L:3.5", "L:3.8"]),
    ("D", "The clock of the lock-in (R3, R9/K5, R10, R11)", ["L:3.10", "L:3.15", "L:3.16", "L:3.17"]),
    ("E", "D59 (P2f, C4)", ["L:3.6"]),
    ("F", "Explorations and negative results", ["L2:4 "]),
    ("G", "First-order theory", ["L2:5 "]),
    ("H", "Reproduction from scratch", ["S:Anhang R"]),
    ("J", "Minibatch training and the lock-in clock in detail", ["S:Anhang J"]),
    ("K", "Towards language models (explorations and one confirmation, LM1; not among the main results)", ["S:Anhang K"]),
    ("M", "Additional details for the main text (passages shortened in Sections 1-7, verbatim)", ["S:Anhang M"]),
]


def subsection(md: str, num: str) -> list[str]:
    """Verbatim lines of the long-draft subsection '### {num} ...' up to the next '### ' or '## ' heading."""
    lines = md.splitlines()
    start = [i for i, ln in enumerate(lines) if ln.startswith(f"### {num} ")]
    if len(start) != 1:
        sys.exit(f"expected one subsection {num}, found {len(start)}")
    end = next((j for j in range(start[0] + 1, len(lines)) if lines[j].startswith(("### ", "## "))), len(lines))
    head = "#### " + re.sub(r";\s*short version:[^)]*", "", clean_heading(lines[start[0]][4:]))
    body = "\n".join(lines[start[0] + 1:end]).strip()
    return [head] + [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not is_process_note(p.strip())]


LONG_TO_MAIN = {"1": "Section 1", "1b": "Section 1", "2": "Section 2", "3.1": "Section 3", "3.9": "Section 4", "3.14": "Section 3",
                "3.18": "Section 6", "3.19": "Appendix J", "4": "Appendix F", "5": "Appendix G", "5b": "Section 7", "6": "Section 7"}


def long_map() -> dict[str, str]:
    """Long-draft section numbers -> manuscript labels (A.1, ...), for cross-references inside long-draft text."""
    m = dict(LONG_TO_MAIN)
    for letter, _, srcs in APPENDIX:
        for k, src in enumerate(s for s in srcs if s.startswith("L:")):
            m[src[2:]] = f"{letter}.{k + 1}"
    return m


def relabel(p: str, m: dict[str, str]) -> str:
    """Rewrite '§3.4' -> 'Appendix C.2' (or 'Section 3') and a leading '#### 3.4 ' -> '#### C.2 ' in long-draft text."""
    def sub(mt: re.Match) -> str:
        tgt = m.get(mt.group(1)) or ("Appendix G" if mt.group(1).startswith("5.") else None)   # theory sub-items
        if tgt is None:
            return mt.group(0)
        return tgt if tgt.startswith(("Section", "Appendix")) else f"Appendix {tgt}"
    p = re.sub(r"^#### (\d+\.\d+) ", lambda mt: f"#### {m.get(mt.group(1), mt.group(1))} ", p)
    return re.sub(r"§\s?(\d+(?:\.\d+)?b?)(?![\d.]*\d)", sub, p)


def appendix(short: dict, long_md: str, long_secs: dict) -> list[str]:
    out = ["# Appendix (assembled verbatim from the working drafts; §-references of the long draft are rewritten to manuscript labels)"]
    lm = long_map()
    for letter, title, srcs in APPENDIX:
        out.append(f"## Appendix {letter}: {title}")
        for src in srcs:
            kind, key = src.split(":", 1)
            if kind == "L":
                out.extend(relabel(p, lm) for p in subsection(long_md, key))
            else:
                paras = find(long_secs if kind == "L2" else short, key)[1]
                if key == "Anhang M":
                    paras = [moved_label(p) for p in paras if p.startswith("**")]
                paras = [re.sub(r"^(#{1,3}) ", "#### ", p) for p in paras if not is_process_note(p)]
                out.extend(relabel(p, lm) if kind == "L2" else p for p in paras)
    return [strip_session(p) for p in out]


def moved_label(p: str) -> str:
    """Appendix M: replace the German bookkeeping label '**§5 R6, ... (ersetzt ...):**' by a neutral English one."""
    label, sep, rest = p.partition(":**")
    if not sep:
        return p
    where = re.search(r"§\s?\d", label)
    src = f"Section {where.group(0)[-1]}" if where else ("Figure caption" if "Abb" in label or "Bildunterschrift" in label else "main text")
    return f"**For {src}:**{rest}"


def strip_session(p: str) -> str:
    """Drop lab bookkeeping such as '; Sitzung 46' or '(Sitzung 50)' inside English text."""
    p = re.sub(r";\s*Sitzung \d+", "", p)
    return re.sub(r"\s*\(Sitzung \d+\)", "", p)


def main() -> None:
    short = sections((HERE / "draft_short.md").read_text(encoding="utf-8"))
    long_ = sections((HERE / "draft.md").read_text(encoding="utf-8"))
    refs_md = (HERE / "references.md").read_text(encoding="utf-8")
    front = '---\nid: paper-manuscript\nstatus: generiert\ntags: [lab/paper]\nverwandt: ["[[paper/draft_short]]", "[[paper/STATUS]]"]\n---'
    parts = [front, f"# {TITLE}", "*Authors: to be added.*",
             "*Generated by `lab/paper/build_manuscript.py` from `draft_short.md`; do not edit by hand.*"]
    main_words = 0
    for pre in SECTIONS:
        head, paras = find(short, pre)
        body = [p for p in paras if not is_process_note(p)]
        parts.append(f"## {clean_heading(head)}")
        parts.extend(body)
        if pre != "Abstract":
            main_words += sum(len(p.split()) for p in body)
    abstract = [p for p in find(short, "Abstract")[1] if not is_process_note(p)][0]
    _, fig_paras = find(short, "Abbildungen")
    captions = [p for p in fig_paras if p.startswith("*Figure ")]
    parts.append("## Figures")
    parts.extend(captions)
    cap_words = sum(len(p.split()) for p in captions)
    table = [ln for ln in (HERE / "figures/table_registrations.md").read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    parts.append("## Table 1")
    parts.append("*Table 1.* Confirmation blocks behind the claims (generated from the frozen manifests by "
                 "`figures/table_registrations.py`). Claim labels: K2 = Result 1 (steering; K2-function = its functional test); "
                 "R5 = Result 2; K4, K4b, K4c, R6, R8 = Result 3; K4d, K4e = resets (Appendix C); K5 = the window rule "
                 "(Appendix D); lock-in = persistence of the choice.")
    parts.append("\n".join(table))
    _, disc = find(long_, "AI use disclosure")
    parts.append("## AI use disclosure (draft wording, to be confirmed by the user)")   # s52: not a lettered appendix (review)
    parts.extend(disc)
    ref_lines = sorted(ln for ln in refs_md.splitlines() if re.match(r"^- .+? \((?:19|20)\d\d[ab]?\)\.", ln))
    ref_lines = [clean_ref(ln) for ln in ref_lines]   # session 52: no German working notes in the manuscript
    parts.append("## References (unchecked draft list; provenance tags in brackets, see paper/references)")
    parts.append("\n".join(ref_lines))
    app = appendix(short, (HERE / "draft.md").read_text(encoding="utf-8"), long_)
    parts.extend(app)
    text_out = "\n\n".join(parts) + "\n"
    # s52 (review): the AI use disclosure is no longer a lettered appendix, so letters I and L were unused;
    # reletter J -> I, K -> J, M -> K in one pass so the appendix runs A-K without gaps.
    assert not re.search(r"Appendix [IL]\b", text_out)
    text_out = re.sub(r"Appendix ([JKM])\b", lambda m: "Appendix " + {"J": "I", "K": "J", "M": "K"}[m.group(1)], text_out)
    # s53: figures that are only scripts (not in the Figures list) are named as supplementary; the old pilot
    # caption of Figure 4 kept verbatim in Appendix K is marked as superseded (Figure 4 is now fig13).
    for old, new in (("Fig. 12 in `", "supplementary figure `"),
                     ("per-seed values in Figure 9, `", "per-seed values in supplementary figure `"),
                     ("*Figure K1* (`", "*Supplementary figure* (`"),
                     ("**For Figure caption:** *Figure 4.* **L0:",
                      "**Superseded caption of an earlier Figure 4 (pilot version; the current Figure 4 is above):** **L0:")):
        assert text_out.count(old) == 1, old
        text_out = text_out.replace(old, new)
    # s67 (review): appendix figures follow the relettering of their appendix (Figure J1 sits in Appendix I).
    assert not re.search(r"Fig(?:ure|\.) [ILM]\d", text_out)
    text_out = re.sub(r"(Fig(?:ure|\.) )([JK])(\d)", lambda m: m.group(1) + {"J": "I", "K": "J"}[m.group(2)] + m.group(3), text_out)
    (HERE / "manuscript.md").write_text(text_out, encoding="utf-8")

    text = "\n".join(p for pre in SECTIONS for p in find(short, pre)[1]) + "\n".join(captions)
    missing = sorted(citations(text) - ref_keys(refs_md))
    print(f"abstract characters: {len(abstract)}")
    print(f"main text words (sections 1-7): {main_words}; caption words: {cap_words}; total {main_words + cap_words}")
    print(f"figures: {len(captions)}; references listed: {len(ref_lines)}")
    print("cited in main text but no reference entry (surname, year):", missing if missing else "none")
    missing_app = sorted(citations("\n".join(app)) - ref_keys(refs_md) - set(missing))   # session 52: appendix too
    print("cited in the appendix but no reference entry (surname, year; may include false positives):",
          missing_app if missing_app else "none")


if __name__ == "__main__":
    main()

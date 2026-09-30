"""Session 63 helper: insert the ready Pythia paragraph (paper/PYTHIA_DEUTUNGEN.md, section "Einsetzfertig") into draft_short.md
Appendix K before **Context.**, add the limitation (ii) half-sentence and the Biderman et al. 2023 reference. Tested on a copy.
  python lab/paper/insert_pythia_s63.py <X = highest held-out accuracy of the four EXP-133 runs, e.g. 0.002>
Run from the repository root. Refuses to run twice (asserts)."""
import pathlib, re, sys
X = sys.argv[1]
root = pathlib.Path('lab/paper')
para = root.joinpath('PYTHIA_DEUTUNGEN.md').read_bytes().decode('utf-8').replace('\r\n', '\n')
m = re.search(r"\n(\*\*Fine-tuning a pretrained model.*?)\n", para)
text = m.group(1).replace('≤ X', '≤ ' + X)
assert ' X ' not in text
p = root / 'draft_short.md'; t = p.read_bytes().decode('utf-8')
a = '**Context.** Pretrained language models compute addition'
assert t.count(a) == 1 and t.count('**Fine-tuning a pretrained model') == 0
t = t.replace(a, text + '\r\n\r\n' + a, 1)
b = 'and about 8.7 % arithmetic tokens (LM3; ablation LM3-F; Appendix K).'
assert t.count(b) == 1
t = t.replace(b, 'and about 8.7 % arithmetic tokens (LM3; ablation LM3-F; Appendix K); it was not found when fine-tuning a pretrained 160 M-parameter model (two-seed pilot; Appendix K).', 1)
p.write_bytes(t.encode('utf-8'))
r = root / 'references.md'; u = r.read_bytes().decode('utf-8')
nl = '\r\n' if u.count('\r\n') > u.count('\n') / 2 else '\n'
c = '\n*Nachtrag (Sitzung 52, 2026-09-29):*'.replace('\n', nl)
assert u.count(c) == 1 and 'Biderman, Schoelkopf' not in u
entry = "- Biderman, Schoelkopf, Anthony, Bradley, O'Brien, Hallahan, Khan, Purohit, Prashanth, Raff, Skowron, Sutawika, van der Wal (2023). *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling*. arXiv:2304.01373. https://arxiv.org/abs/2304.01373. [A]" + nl
i = u.index(c)
j = u.rindex(nl, 0, i) + len(nl)   # start of the line before the blank line
u = u[:i] + entry.rstrip(nl) + nl + u[i:]
r.write_bytes(u.encode('utf-8'))
print('inserted; paragraph chars', len(text))

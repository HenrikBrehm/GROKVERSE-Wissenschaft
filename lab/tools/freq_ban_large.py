"""Large-p wrapper around the hash-locked EXP-001 trainer (session 70, BACKLOG 7: LeDoux regime, p up to ~10^4).

freq_ban.py builds all p^2 pairs in make_dataset and evaluates train and test sets in one forward pass; at p = 9973
that is ~10^8 pairs and a 300k x 9973 logit matrix (~12 GB). The trainer is bound by hash to open frozen blocks, so it
is NOT edited. This wrapper imports it by file path and replaces four module globals before calling its main():

  make_dataset  -> lazy pair tables: rows (a, b, '=') and labels are computed from flat indices a*p+b on demand.
                   Needs --split-file AND --test-file (the complement of the train set is never materialised).
  evaluate      -> the same loss/accuracy in chunks of --eval-chunk rows (summed loss / n, correct / n). Sets with
                   n <= chunk call the original evaluate, so small runs are bit-identical.
  get_config    -> optional --eval-every E sets eval_every_train = eval_every_test = E (default: preset 10 / 25).
  SPECTRUM_EVERY-> optional --spectrum-every S (default: preset 250). The p x p Fourier basis is built once.

Training itself (init, data order, optimizer, minibatches) is untouched: with --eval-every / --spectrum-every left at
the preset values the trajectory equals a plain freq_ban.py run (CPU: bit-identical weights; see the equivalence test
lab/tools/test_freq_ban_large.py). The run id and fingerprint of freq_ban.py do NOT see the wrapper settings, so the
wrapper refuses an --out-root that was not created by it with the same settings (marker WRAPPER.json), and it records
its full argv (wrapper flags included) in result.json["argv"] and in <run dir>/wrapper.json.

Usage (same flags as freq_ban.py, plus the wrapper flags, which must come first):
  python lab/tools/freq_ban_large.py [--eval-chunk 8192] [--eval-every E] [--spectrum-every S] -- <freq_ban.py flags>
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
TRAINER = ROOT / "lab" / "experiments" / "EXP-001-freq-ban" / "freq_ban.py"
MARKER = "WRAPPER.json"
WRAPPER_VERSION = 1


class LazyPairs:
    """Index-only stand-in for make_dataset's all_x / all_y over the p^2 flat indices a*p+b."""

    def __init__(self, p: int, task: str, equals_token: int, labels: bool) -> None:
        if task not in ("add", "mul"):
            raise ValueError(f"unknown task {task!r}")
        self.p, self.task, self.eq, self.labels = p, task, equals_token, labels

    def __len__(self) -> int:
        return self.p * self.p

    def __getitem__(self, idx) -> torch.Tensor:
        idx = torch.as_tensor(idx).long()
        if idx.ndim != 1 or (len(idx) and (int(idx.min()) < 0 or int(idx.max()) >= self.p * self.p)):
            raise IndexError("LazyPairs needs a 1-d index tensor in [0, p*p)")
        a, b = idx // self.p, idx % self.p
        if self.labels:
            return ((a + b) if self.task == "add" else (a * b)) % self.p
        return torch.stack([a, b, torch.full_like(a, self.eq)], dim=1)


def parse_wrapper_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    if "--" not in argv:
        raise SystemExit("usage: freq_ban_large.py [wrapper flags] -- <freq_ban.py flags>")
    cut = argv.index("--")
    ap = argparse.ArgumentParser(description="large-p wrapper for freq_ban.py")
    ap.add_argument("--eval-chunk", type=int, default=8192, help="rows per evaluation forward pass")
    ap.add_argument("--eval-every", type=int, default=None, help="eval_every_train = eval_every_test (default: preset)")
    ap.add_argument("--spectrum-every", type=int, default=None, help="steps between W_E spectra (default: preset 250)")
    w = ap.parse_args(argv[:cut])
    if w.eval_chunk < 1 or (w.eval_every is not None and w.eval_every < 1) or (
            w.spectrum_every is not None and w.spectrum_every < 1):
        raise SystemExit("--eval-chunk / --eval-every / --spectrum-every must be >= 1")
    return w, argv[cut + 1:]


def trainer_flag(rest: list[str], name: str) -> str | None:
    for i, tok in enumerate(rest):
        if tok == name and i + 1 < len(rest):
            return rest[i + 1]
        if tok.startswith(name + "="):
            return tok.split("=", 1)[1]
    return None


def check_out_root(out_root: Path, settings: dict) -> None:
    """Refuse an out-root shared with plain freq_ban.py runs or with other wrapper settings (fingerprint is blind to them)."""
    marker = out_root / MARKER
    if marker.exists():
        have = json.loads(marker.read_text())
        if have != settings:
            raise SystemExit(f"[large] {out_root} holds wrapper runs with other settings {have}; use another --out-root")
        return
    if out_root.exists() and any(out_root.iterdir()):
        raise SystemExit(f"[large] {out_root} is not empty and has no {MARKER}; use a fresh --out-root")
    out_root.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(settings, indent=1))


def load_trainer():
    spec = importlib.util.spec_from_file_location("freq_ban_locked", TRAINER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def install(fb, w: argparse.Namespace) -> None:
    orig_eval, orig_cfg = fb.evaluate, fb.get_config

    def make_dataset_lazy(cfg) -> dict:
        return {"all_x": LazyPairs(cfg.p, cfg.task, cfg.equals_token, labels=False),
                "all_y": LazyPairs(cfg.p, cfg.task, cfg.equals_token, labels=True)}

    @torch.no_grad()
    def evaluate_chunked(model, x: torch.Tensor, y: torch.Tensor, p: int) -> tuple[float, float]:
        n = len(x)
        if n <= w.eval_chunk:
            return orig_eval(model, x, y, p)
        loss_sum, correct = 0.0, 0
        for i in range(0, n, w.eval_chunk):
            logits = model.logits_last(x[i:i + w.eval_chunk])[:, :p]
            yy = y[i:i + w.eval_chunk]
            loss_sum += F.cross_entropy(logits, yy, reduction="sum").item()
            correct += int((logits.argmax(-1) == yy).sum().item())
        return loss_sum / n, correct / n

    def get_config_cadence(*args, **kw):
        cfg = orig_cfg(*args, **kw)
        if w.eval_every is not None:
            cfg = dataclasses.replace(cfg, eval_every_train=w.eval_every, eval_every_test=w.eval_every)
        return cfg

    fb.make_dataset, fb.evaluate, fb.get_config = make_dataset_lazy, evaluate_chunked, get_config_cadence
    if w.spectrum_every is not None:
        fb.SPECTRUM_EVERY = w.spectrum_every


def main(argv: list[str] | None = None) -> None:
    full_argv = list(sys.argv if argv is None else [sys.argv[0], *argv])
    w, rest = parse_wrapper_args(full_argv[1:])
    if trainer_flag(rest, "--split-file") is None or trainer_flag(rest, "--test-file") is None:
        raise SystemExit("[large] needs --split-file and --test-file (the test complement is never built)")
    if "--switch-split-file" in rest or "--split-seed" in rest:
        raise SystemExit("[large] --switch-split-file / --split-seed are not supported (not checked for large p)")
    out_root = trainer_flag(rest, "--out-root")
    if out_root is None:
        raise SystemExit("[large] needs an explicit --out-root (never the default raw/ of EXP-001)")
    settings = {"wrapper": "freq_ban_large", "version": WRAPPER_VERSION, "eval_chunk": w.eval_chunk,
                "eval_every": w.eval_every, "spectrum_every": w.spectrum_every}
    check_out_root(Path(out_root), settings)
    fb = load_trainer()
    install(fb, w)
    orig_run = fb.run

    def run_recorded(a):
        sys.argv = full_argv              # result.json["argv"] shows the wrapper and its flags
        res = orig_run(a)
        run_dir = Path(a.out_root) / res["run_id"]
        (run_dir / "wrapper.json").write_text(json.dumps({**settings, "argv": full_argv}, indent=1))
        return res

    fb.run = run_recorded
    sys.argv = [str(TRAINER), *rest]      # freq_ban.main() parses sys.argv[1:]
    fb.main()


if __name__ == "__main__":
    main()

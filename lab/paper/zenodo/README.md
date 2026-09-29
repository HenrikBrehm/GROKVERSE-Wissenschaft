---
id: paper-zenodo
status: entwurf
datum: 2026-09-28
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[paper/repro/README]]"]
---
# Zenodo-Paket (Regel 20d): Entwurf, NICHT hochladen

Zurück zu [[paper/STATUS]]. Angelegt Sitzung 43 (2026-09-28). Hochladen braucht das Konto des Nutzers und seine Entscheidungen zu Autorschaft, Lizenz und den Rechten an der ursprünglichen Studie ([[paper/STATUS]], „Offen für den Nutzer“). Das Labor lädt nichts hoch.

## Vorgesehener Inhalt (Größen gemessen 28.09.)

| Teil | Pfad | Größe | Bemerkung |
|---|---|---|---|
| Kurzfassung + Langfassung des Papers | `lab/paper/draft_short.md`, `lab/paper/draft.md` | < 1 MB | Stand zum Zeitpunkt des Hochladens einfrieren (Commit-ID) |
| Registrierungen, Manifeste, Zusammenfassungen | `lab/confirm/*REGISTRATION*.md`, `*_manifest.json`, `*_summary.json` | ≈ 1.6 MB | 26 Zusammenfassungen; Manifeste enthalten Code-Hashes und Commit |
| Analyse- und Blockcode | `lab/tools/confirm_*.py`, `bound_block.py`, `result_loader.py`, `trainer_guard.py` | klein | ohne Nutzer-Runner-Dateien |
| Trainer | `lab/experiments/EXP-001-freq-ban/freq_ban.py`, `training/grokverse/` | klein | `training/` gehört zur ursprünglichen Studie → Rechte klären |
| Reproduktionspaket | `lab/paper/repro/*.py` + README | klein | **ohne** `repro/out/` (511 MB Rohläufe) oder nur als eigenes Archiv |
| Abbildungsskripte + Bilder | `lab/paper/figures/` | ≈ 2 MB | |
| Splits der Bestätigungen | `lab/confirm/*_splits/`, `lab/confirm/splits/` | ≈ 87 MB | nötig, damit die Läufe exakt reproduzierbar sind |

**Nicht enthalten:** Rohläufe (`raw/`, `*_raw/`), `.venv-gpu`, `lab/external/rfm-grokking` (GPL-3.0, Dritte), Runner-Dateien des Nutzers.

**Metadaten:** `zenodo_metadata_DRAFT.json` (Felder `<NUTZER>` offen).

**Werkzeug:** `make_package.py` packt nur git-verfolgte Dateien eines Commits (Trockenlauf Sitzung 43: 4753 Dateien, 81.9 MB) in ein ZIP mit `SHA256SUMS` unter `out/` (git-ignoriert). Hochladen gibt es nicht. **Nächste Schritte:** Trockenlauf durchsehen (enthält `training/grokverse` der ursprünglichen Studie → Rechte klären), Geheimnis-Scan vor jedem Bau.

**Scan (Sitzung 43, 20:05, alle 4758 Nicht-npy-Dateien des Trockenlaufs):** keine Schlüssel oder Passwörter (ein Fehltreffer: der Regex-Name `_SEED_TOKEN`), keine E-Mail-Adresse. **Aber:** 7 Dateien enthalten absolute Pfade mit dem Benutzernamen (`C:/Users/…`): `lab/paper/repro/README.md`, `k2.py`, `k2_function.py`, `k2_function_p2e.py`, `k4_resets.py`, `k4b.py`, `k4c.py` (venv-Pfad für die GPU). **Vor dem Paketbau** diese Pfade relativ machen oder über eine Umgebungsvariable setzen und die Skripte danach einmal im Smoke-Modus prüfen. Die Nutzerin/der Nutzer entscheidet, ob der Name im Paket stehen darf.

**Nachtrag Sitzung 44 (≈ 20:25):** In 6 der 7 Dateien (`README.md`, `k2_function.py`, `k2_function_p2e.py`, `k4_resets.py`, `k4b.py`, `k4c.py`) ist der absolute venv-Pfad durch `$PWD/.venv-gpu/Scripts/python.exe` ersetzt (nur Docstrings/Befehlszeilen; Git Bash im Repo-Wurzelordner, `$PWD` wird dort zu `/c/...` und beim Aufruf von python.exe umgewandelt). **Ungetestet** (Fenster zu): einmal einen Smoke-Befehl so aufrufen. **`k2.py` bleibt unverändert**, weil R7 seinen Hash bindet (`lab/confirm/R7_manifest.json`); eine Änderung würde die R7-Nachrechnung am aktuellen Stand brechen. Optionen für den Nutzer: Pfad im Paket belassen, oder `k2.py` nach Rücksprache ändern und R7 nur noch am Manifest-Commit nachrechnen (`git worktree add`).

**Nachtrag Sitzung 49 (2026-09-29):** Die neuen Repro-Skripte (`l0.py`, `r4.py`, `r5.py`, `r6.py`, `r8.py`) importieren über die `confirm_*`-Werkzeuge Module aus `lab/experiments/` (`EXP-053…/overlap_split.py` + `calibration.json`, `EXP-043…/analyze.py` + `make_split.py`, `EXP-046…`, `EXP-051…/analyze.py`, `EXP-055…/analyze.py`). Diese fehlten in `INCLUDE` und sind ergänzt (Musterabgleich gegen `git ls-files` geprüft). Offen: ein Import-Test aus einem frisch entpackten Paket (nur die Paketdateien auf dem Pfad), bevor das Paket als vollständig gilt.

*Import-Test erledigt (Sitzung 49, 09:52):* Paketdateien ohne Split-Daten nach `lab/paper/repro/out/pkgtest` entpackt; `l0/r4/r5/r6/r8.py --smoke --jobs-out` und `train.py --help` laufen allein aus dem Paket.

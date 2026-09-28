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

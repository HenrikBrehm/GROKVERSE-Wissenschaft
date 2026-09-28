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
| Splits der Bestätigungen | `lab/confirm/*_splits/` | zu messen | nötig, damit die Läufe exakt reproduzierbar sind |

**Nicht enthalten:** Rohläufe (`raw/`, `*_raw/`), `.venv-gpu`, `lab/external/rfm-grokking` (GPL-3.0, Dritte), Runner-Dateien des Nutzers.

**Metadaten:** `zenodo_metadata_DRAFT.json` (Felder `<NUTZER>` offen).

**Nächste Schritte (Labor):** Größe der Split-Verzeichnisse messen; ein Skript `make_package.py`, das aus einer Commit-ID ein ZIP mit genau diesen Pfaden und einer Prüfsummenliste baut (ohne Hochladen); Prüfung, dass keine Geheimnisse oder Nutzerdateien enthalten sind.

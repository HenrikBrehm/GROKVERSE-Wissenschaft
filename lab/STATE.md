# lab/STATE.md — aktueller Stand

_Zuletzt aktualisiert: 2026-09-25, ~14:00 Berlin (Sitzung 1, interaktiv)._

## Kurzlage

- **Repo:** Das Projektverzeichnis war **kein Git-Repo** (Kopie ohne `.git`; Studien-Historie und
  Freeze-Commit `0b55e1d` sind hier nicht vorhanden). In Sitzung 1 wurde lokal `git init` ausgeführt:
  `main` = unveränderter Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
- **Umgebung:** Windows 11, 12 logische CPUs, globales Python 3.12 mit torch **2.13.0**, numpy 2.5.1,
  matplotlib 3.11.1 und tzdata 2026.3. Die Studie lief mit torch 2.12.1 / numpy 2.4.6
  (`training/requirements.txt`). Es gibt kein venv. Folge: Bit-Gleichheit mit gespeicherten Läufen
  ist nicht zu erwarten, deshalb eigene Baseline-Läufe.
- **Daten vorhanden:** `training/runs/` (2,0 GB, 51 Studienläufe inkl. Checkpoints), `training/external/`
  (2,7 GB, externe 100k- und Two-hot-Bündel), beide gitignored.
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Gate `neither_passes`, H3 widerlegt,
  H4 (Struktur vor Generalisierung) nur korrelativ. Offene Autorenentscheidungen D5–D9 bleiben
  bei den Menschen.
- **Runner:** **vorbereitet, NICHT aktiviert.** Der Auto-Mode-Klassifikator hat die Aktivierung
  blockiert („Create Unsafe Agents“). Dateien und Aktivierungsbefehl: `lab/runner/README.md`.
  Die Entscheidung liegt beim Nutzer.
- **Zeitfenster-Wächter:** `lab/tools/guarded_run.py`. **Ungetestet**, weil Sitzung 1 außerhalb
  des Fensters lag.

## Letzter abgeschlossener Versuch

Keiner. Im Labor wurde noch nichts ausgeführt.

## Vorbereitet, noch nicht ausgeführt

- **EXP-001 Frequenzverbot** (`lab/experiments/EXP-001-freq-ban/`). Definition fixiert, Code
  ungetestet. Grund für die Nicht-Ausführung: Sitzung 1 lief um 13:04–14:30 Berlin, also
  außerhalb von 00:00–13:00.

## Nächste konkrete Aktion (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`
2. `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/test_freq_ban.py`
3. Vorhandene Studientests als Baseline der Funktionsfähigkeit:
   `python lab/tools/guarded_run.py -- python training/tests/run_all.py` (Laufzeit unbekannt; falls
   Refusal/Timeout, mit einzelnen Testdateien).
4. Funktionstest von EXP-001 (Befehl in dessen README, Schritt 2). s/Schritt notieren und das
   Abbruchkriterium anwenden.
5. EXP-001 Hauptläufe in der README-Reihenfolge, **einer nach dem anderen**, dann `analyze.py`.

## Wiederaufnahme nach Abbruch

- EXP-001-Läufe schreiben alle 500 Schritte `raw/<run_id>/result.json` mit `status: running`. Ein
  abgebrochener Lauf (Status bleibt `running`) wird **neu** gestartet (`--force`), nicht fortgesetzt:
  Der Adam-Zustand wird nicht gespeichert.
- `lab/runner/logs/guarded_runs.jsonl` protokolliert jeden Start und jede Verweigerung.

## Blocker

- Runner-Aktivierung braucht eine Nutzerentscheidung (s. o.).

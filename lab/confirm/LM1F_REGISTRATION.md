---
id: LM1F
status: registriert
datum: 2026-09-29
tags: [confirm, lm-leiter]
---
# LM1-F: Tragen die gesteuerten Frequenzen in den LM1-Modellen die Fakten? (funktionale Zusatzregistrierung, Sitzung 51)

Zurück: [[LAB]] · [[FINDINGS]] (K2-Funktion, Programm A) · Grundblock [[confirm/LM1_REGISTRATION|LM1]] · Pilot [[experiments/EXP-118-lm-ablation/README|EXP-118]] · Code `lab/confirm/confirm_lm1f.py`

## Fassung 1 (Sitzung 51, 15:47 Berlin gemessen, vor jeder Ablation an einem LM1-Modell)

**Frage.** LM1 prüft, ob die Faktenauswahl die Energie der Zahl-Vektoren steuert. Tragen diese Frequenzen auch die Vorhersage? Im Spielzeugmodell: Nanda-Ablation „Ziele funktional“ 20/20 je Aufgabe; im LM an bekannten Modellen (EXP-118, Seed 3862, K 19 und K 8): eigene Ziele entfernt → 0.03–0.30, fremde/Kontrollen → 0.93–0.99.

**Modelle.** Die 20 LM1-Läufe (Seeds 4000–4009, F/G, Modell-Seed + 100, Schritt 6000, `checkpoint.pt` am Laufende), unverändert eingefroren durch LM1 (2b70d8b9). Kein neues Training.

**Eingriff und Messgröße.** Aus den 113 Zahl-Zeilen (gebundene Einbettung: die Ablation trifft Ein- und Ausgabe zugleich) der gebundenen Einbettung wird der Fourier-Unterraum (cos/sin über den Zahlindex, Konstante unberührt) einer Frequenzmenge entfernt: eigene Ziele, fremde Ziele (anderer Split desselben Seeds), 4 Kontrollmengen (5 Frequenzen aus 1..56 ohne beide Zielmengen, `SeedSequence([4011, seed])`). Genauigkeit auf der gemeinsamen zurückgehaltenen Testmenge des Seeds (Prompt T0, argmax über die 113 Zahl-Tokens, wie der Trainer). Je Lauf C = acc(fremd) − acc(eigen); je Seed C̄ = Mittel aus F und G.

**H1F (einzige primäre Hypothese).** Mittleres C̄ über 10 Seeds > 0.1 (Mindesteffekt: 10 Prozentpunkte). „bestätigt“, wenn die untere Grenze des 95-%-Perzentil-Bootstrap-KI (10 000 Ziehungen über Seeds, rng 4011) > 0.1 **und** der einseitige exakte Vorzeichen-Permutationstest von C̄ − 0.1 (2¹⁰ Vorzeichen) p < 0.05; „unter Mindesteffekt“, wenn die obere KI-Grenze < 0.1 und der gespiegelte Test p < 0.05; sonst „unklar“. Seeds mit ungelernten Fakten zählen mit (konservativ).

**Auswertbarkeit.** Nur wenn alle 20 Läufe fertig sind (result.json + checkpoint.pt) und das LM1-Tor bestanden ist (zurückgehaltene Genauigkeit laut Log ≥ 0.5 in ≥ 16/20); sonst „nicht auswertbar“. LM1-F wird unabhängig vom LM1-Ergebnis (H1) ausgewertet und berichtet. Bindung: Die Läufe sind dieselben, die LM1 bindet; LM1-F liest nur Läufe, die LM1 als gültig akzeptiert (vor der Auswertung `confirm_lm1.py --analyze` laufen lassen; ein dort „defekter“ Lauf macht LM1-F „nicht auswertbar“).

**Sekundär (beschreibend).** acc(Basis), acc(eigen), Mittel der Kontrollen je Lauf; Seeds mit C̄ > 0; Kontrollmittel − acc(eigen).

**Stichprobengröße.** Durch LM1 festgelegt (10 Seeds). Pilot EXP-118: C 0.69–0.96 (4 Modelle) → bei wahrem Mittel ≥ 0.5 und SD ≤ 0.3 ist „bestätigt“ fast sicher; Fehler 1. Art durch den Mindesteffekt 0.1 konservativ.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen.** EXP-118 (Seed 3862, andere Splits, EXP-113/114-Modelle) → Wahl der Ablation, der Kontrollen und des Mindesteffekts. Von LM1 gesehen: Logzeilen (Trainings-/Testgenauigkeit) der fertigen Läufe 0–3 und Fortschrittszeilen laufender Läufe; keine LM1-Auswertung, kein Δ_pow, keine Ablation an LM1-Modellen.

**Laufzeit.** CPU (4 Threads) ≈ 3–5 min je Modell → 1–1.5 h; über den GPU-Dienst als Job (gpu_gb 1, CPU-lastig) oder im Hintergrund einer Sitzung.

**Befehl (nach LM1 --analyze).** `python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/confirm/confirm_lm1f.py` → `LM1F_summary.json`. Selbsttest der Statistik: `--selftest` (grün, Sitzung 51).

**Unabhängige Prüfung vor dem Einfrieren (Claude-Agent, nur lesend; Codex ohne Guthaben):** kein Blocker; Statistik, Auswertung wie im Trainer, Projektor (gleiche Frequenzachse wie `power()`) und die Ablation der gebundenen Einbettung bestätigt. Übernommen: (1) Checkpoint gebunden (Schritt 6000 und Konfig-Hash des Laufs, sonst „defekt“); (2) LM1-Annahme erzwungen (`LM1_summary.json`: 10 gültige Seeds, kein Defekt, sonst „nicht auswertbar“), Skript-Hash und LM1-Manifest-Commit in der Zusammenfassung; (3) Fehler je Lauf abgefangen, Zusammenfassung wird immer geschrieben; Kontrollgröße acc(Basis) − geloggte Genauigkeit. Hinweise: Der Vorzeichen-Permutationstest setzt Symmetrie von C̄ um 0.1 unter H0 voraus (wie LM1); ungelernte Läufe (höchstens 4 nach dem Tor) sind konservativ für „bestätigt“, ziehen aber Richtung „unter Mindesteffekt“.

**Smoke (15:59 gemessen):** `evaluate_run` an einem bekannten Modell (EXP-114 K 19 F, nicht LM1) über den Wächter, CPU, 86 s: Basis 0.98316 (geloggt auf der GPU 0.98316, Differenz 1·10⁻⁸), eigene Ziele entfernt 0.29836, identisch mit EXP-118. Selbsttest der Statistik grün.

**Eingefroren:** Code-Commit und Manifest `LM1F_manifest.json` (sha256 von `confirm_lm1f.py`) im folgenden Commit; `status: registriert`.

---
id: R4
status: entwurf
datum: 2026-09-27
tags: [lab/confirm, programm/A, paper, exp/vorbereitet]
---
# R4: Formt ein gewöhnlicher Zufallssplit die gelernten Frequenzen? (gekreuztes Init × Split-Design): Registrierungsentwurf

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, K2) · [[paper/STATUS]] · Pilot: [[experiments/EXP-014-split-vs-init/README|EXP-014]] · Vorgänger (Assoziation): [[experiments/EXP-015-mask-spectrum/README|EXP-015]] · [[JOURNAL]] Sitzung 30.

**Status:** Entwurf, Sitzung 30 (2026-09-27, erste Fassung vor 18:35 Berlin, gemessen; überarbeitet nach der Codex-Prüfung, siehe unten), **vor jedem R4-Lauf und vor dem EXP-014-Pilot**. Code `lab/tools/confirm_r4.py`, **ungetestet**. Nicht eingefroren: vor dem Einfrieren Selbsttest im Fenster und Nachprüfung der geänderten Punkte durch Codex (Regel 18c), danach Manifest mit Commit-ID.

## Warum

Gutachter-Einwand O1 zum [[paper/draft]]: Alle bestätigten Steuerbefunde (K2) nutzen **konstruierte** Splits (Gewichte 0.05–3). Offen ist, ob schon ein **gewöhnlicher** 30-%-Zufallssplit mitbestimmt, welche der gleich guten Frequenzen ein Netz lernt. EXP-015 zeigt dafür nur eine Assoziation, bei der Split und Init aus gleich geseedeten Generatoren stammen. EXP-014 (CPU) ist ein Pilot mit 5 Einheiten (kleinstes p = 1/32). R4 ist die Bestätigung mit unabhängigen Zufallsströmen.

## Aufbau

- add 113, 1-Schicht-Transformer (arch25k), AdamW lr 1e-3, wd 1, 30 % der Paare (3831), `freq_ban.py --split-file`, Test = Komplement (Standard; wirkt nur auf die Auswertung, nicht aufs Training), GPU, `--threads 1`, **8000 Schritte** (`--stop-after-gen 8000`), Spektren bei 250, 1000, 2000, 4000, 8000.
- **Einheit u** (60 Einheiten): zwei Inits (Seeds 2600 + 2u, 2601 + 2u; reserviert 2600–2719) × zwei Zufallssplits (s1, s2) = 4 Läufe, alle Kombinationen. Splits: `numpy.random.default_rng(SeedSequence([R4_TAG, u, j]))`, gleichverteilte Auswahl von 3831 der 12 769 Paare, ohne Bezug zu Frequenzen; kein Split wird aus einem Init-Seed gezogen (Regel 18a6).
- **Ähnlichkeit** zweier Läufe über das W_E-Leistungsspektrum (k = 1..56, `spectra.npy`). Je Einheit: S_split = Mittel der zwei Paare mit gleichem Split und verschiedener Init; S_init = gleiche Init, verschiedener Split; S_none = keine Gemeinsamkeit. Δ_split = S_split − S_none.
- **Primärfamilie (Holm über 2, einseitiger t-Test auf Δ − MDE, 95-%-Bootstrap-KI über Einheiten; „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze von Δ − MDE ≥ 0):**
  - **H1a (frühe Rangsignatur):** Spearman der Spektren bei **Schritt 2000**, Δ_split > **0.05**. Behauptet wird nur eine reproduzierbare Split-Signatur im vollen Rangspektrum bei 2000 Schritten (vor dem Grokking: Zufallssplits generalisieren bei ≈ 3900 Schritten, EXP-003d), nicht eine Wahl der Schlüsselfrequenzen.
  - **H1b (gelernte Wahl nach dem Grokking):** Kosinus der Leistungsspektren (energiegewichtet, von den dominanten Frequenzen getragen) bei **Schritt 8000**, Δ_split > **0.04**.
- **MDE aus der Nullstreuung** (Sitzung 30, gespeicherte Studienläufe Seeds 0–9, 45 Paare ohne Gemeinsamkeit, gleiche Rechnung): Spearman bei 2000 −0.02 ± 0.149, Kosinus bei 8000 0.16 ± 0.125 (bei 2000 ist der Kosinus unbrauchbar: 0.78 ± 0.055, vom flachen Sockel bestimmt). **Nullstreuung der Einheitenstatistik** (Codex-Nachprüfung: die Paar-SD ist nicht die SD von Δ): vier fremde Studienläufe besetzen die vier Zellen, alle 5040 geordneten Zuordnungen (überlappend, also eine Resampling-Schätzung): SD(Δ_split) = 0.145 (Spearman, 2000) und 0.085 (Kosinus, 8000). MDE 0.05 ≈ ⅓ bzw. 0.04 ≈ ½ dieser SD. Vorbehalt: Die Studienläufe stammen aus dem Studientrainer (gleiches Modell-Preset arch25k, CPU); die Übertragung auf R4 (freq_ban, GPU) und die Streuung unter einem echten Effekt sind nicht geprüft.
- **„Relevanter Effekt ausgeschlossen“** für eine Hypothese: obere KI-Grenze von Δ unter ihrem MDE. Sonst, wenn nicht bestätigt: *unentschieden*.
- **Beschreibend (kein Urteil):** Init-Kontraste Δ_init = S_init − S_none (bei Spearman teils bloße Erhaltung des gemeinsamen Init-Spektrums schwacher Frequenzen, darum kein Primärtest), Δ_split − Δ_init, alle drei Maße (Spearman, Kosinus, Top-5-Überlappung) bei allen fünf Schritten, Anteil generalisierter Läufe (Test ≥ 0.9 bei 8000), Mittel und SD von S_none je Maß und Schritt (Übertragungsprüfung der Nullkalibrierung: Studienläufe Spearman −0.02/0.15 bei 2000, Kosinus 0.16/0.125 bei 8000; stark abweichende Werte werden berichtet, ändern aber kein Urteil).
- **Stichprobe (fest):** 60 Einheiten, 240 Läufe. Normalnäherung mit der Null-SD der Einheitenstatistik, α = 0.025 einseitig (Holm-Ungünstigstfall): 80 % Power ab einem wahren Δ_split ≈ 0.102 (H1a) bzw. ≈ 0.071 (H1b) (mit der SD der Einheitenstatistik; eine frühere Angabe 0.105/0.085 beruhte auf der Paar-SD). Kleinere wahre Effekte sind mit n = 60 **gering gepowert**; so wird es berichtet. Keine Anpassung nach dem Pilot; `lab/confirm/R4_pilot_n.py` berichtet nach EXP-014 nur beschreibend die Pilotstreuung (nur H1a schätzbar).
- **Gültigkeit:** Alle 4 Läufe einer Einheit gebunden, geladen (gemeinsamer Lader), Spektren endlich und von der Form (56,), Split-Hash = Split-Datei, **Init-Prüfsummen** gleich bei gleicher Init und verschieden zwischen den Inits. Sonst ist die Einheit technisch defekt, und ganz R4 ist *nicht auswertbar* (wie N29/R3).
- **Budget:** 240 Läufe × 8000 Schritte, GPU ≈ 0.03 s/Schritt bei 10 parallel → ≈ 1.6 h. Nur in einer Nacht mit genug Restzeit starten.

## Designprüfung (numpy, vor jedem Lauf, Sitzung 30)

`python lab/confirm/R4_design_lever.py` an den 120 R4-Splits: M0c (zentriert, kohärent) über k schwankt je Split um den Faktor 1.85 (Median; 1.57–2.64). Die fünf stärksten Frequenzen liegen im Mittel 1.28-fach über den übrigen 51. Die beiden Splits einer Einheit sind unabhängig (Spearman der M0c +0.01 ± 0.12, Top-5-Überlappung 0.52, Zufall 0.45). Ein gewöhnlicher Split hat also einen Hebel grob in der Größenordnung der natürlichen Schwankung, die nach C1 (Exploration) die Rangfolge der Ziele mitordnet: 1.30 innerhalb von fünf Zielen, eine andere Bezugsmenge, darum nur grob vergleichbar. Er liegt deutlich unter einer konstruierten Abstufung (EXP-082 strong 3.8). Erwartung vor dem Lauf: kleine Effekte.

## Was dagegen spräche

- H1a und H1b mit „relevanter Effekt ausgeschlossen“: Ein gewöhnlicher Zufallssplit formt die Frequenzwahl in diesem Aufbau (add 113, eine Architektur, eine Optimierer-Einstellung) nicht in relevanter Größe mit. Die EXP-015-Assoziation wäre dann eher über die Seed-Kopplung zu erklären. Das würde als eigener Befund berichtet, ohne es über diesen Aufbau hinaus zu verallgemeinern.
- H1a bestätigt, H1b nicht: Der Split prägt die frühe Rangsignatur, aber nicht messbar die Wahl nach dem Grokking.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-015 (Seeds 0–19, Assoziation Maske ↔ Frequenzen, Seed-Kopplung), EXP-014-Gradient-Vorschau (Seeds 0–9: erster Gradient folgt dem Split, ρ 0.34 gegen −0.01), EXP-009 (Init-Spektrum sagt Frequenzen voraus), EXP-003d (Grokking der Zufallssplits bei ≈ 3900 Schritten), **Nullkalibrierung** an den Studienläufen Seeds 0–9 (Sitzung 30: MDE, Wahl Kosinus bei 8000). Beeinflusst: gekreuztes Design, Maße, einseitige Richtung, Schritte 2000/8000, MDE, n. Kein Lauf mit Seeds 2600–2719, kein R4-Split existiert. Der EXP-014-Pilot ändert an R4 nichts.

## Änderungen nach der Codex-Prüfung (Sitzung 30, `lab/confirm/R4_codex_review_s30.txt`, vor jedem Lauf)

1. BLOCKER übernommen: Das Code-Tor enthielt die transitiven Importe von `confirm_p1` nicht (`confirm_splits.py`, EXP-043/046 `make_split.py`, `dihedral.py`); der Selbsttest wäre gescheitert. Ergänzt.
2. MAJOR übernommen: Spearman über alle 56 Frequenzen misst die Wahl der Schlüsselfrequenzen nicht sauber. Deshalb gilt H1a nur als Rangsignatur bei 2000; neu ist H1b (Kosinus, energiegewichtet) bei 8000. H2 (Init) ist nur noch beschreibend, weil sie bei Spearman bloße Erhaltung des Init-Spektrums messen kann.
3. MAJOR übernommen: Schritt 2000 liegt vor dem Grokking der Zufallssplits (selbst geprüft: EXP-003d, Generalisierung bei 3925). Darum der zweite Zeitpunkt 8000; es gibt keine Bedingung auf die Generalisierung.
4. MAJOR übernommen: MDE und n begründet über die Nullstreuung; n von 40 auf 60 erhöht; „ausreichend große Bestätigung“ gestrichen; die Power ist offen angegeben.
5. MAJOR übernommen: Tore für Init-Prüfsummen und die Spektrumsform.
6. MINOR übernommen: „KI eng um 0“ ersetzt durch „relevanter Effekt ausgeschlossen“; die Negativaussage ist auf den Aufbau beschränkt.
Erste Fassung (40 Einheiten, 2000 Schritte, H2 primär) damit ersetzt; es gab keinen Lauf.

**Codex-Nachprüfung** (`lab/confirm/R4_codex_recheck_s30.txt`): Punkte 1–3, 5, 6 behoben; 4 teilweise. Neuer Major: Die Power beruhte auf der SD der Paar-Ähnlichkeiten, nicht auf der Einheitenstatistik. Übernommen und nachgerechnet (siehe MDE-Absatz). MDE und n bleiben unverändert, die Begründung und die Power-Angaben sind korrigiert. Der Kosinus-Selbsttest ist noch nicht ausgeführt (erst im Fenster).

## Grenzen (vorab)

Eine Aufgabe (add 113), eine Architektur, eine Optimierer-Einstellung; zwei Zeitpunkte; „formt mit“ heißt nicht „entscheidet allein“; kein Eingriff in den Mechanismus (ob M0c den Effekt vermittelt, bräuchte eine eigene Registrierung).

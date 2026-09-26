---
id: EXP-052
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[BEFUND-split-mechanismus]]"]
---
# EXP-052: Sagt der Split allein das W_E-Spektrum auch bei add mod 97 und mul mod 113 voraus? (eingefrorene Vorhersage)

**Status:** vorbereitet. **Vorhersagen eingefroren** in `predictions.json` (Sitzung 14, 2026-09-26, vor 21:27 Berlin gemessen), **bevor**
irgendein R-Lauf von EXP-043 existierte. Kein eigenes Training: nutzt die 20 Zufallssplit-Läufe (Arm R, ε = 0) von
[[experiments/EXP-043-generalize-steering/README|EXP-043]] (GPU, 2000 Schritte, Seeds 70–79 je Aufgabe), die das Nachtprogramm ohnehin
fährt. Zurück zu [[LAB]] · [[FINDINGS]].

## Bezug zu [[FINDINGS]]

Paket **A**, Verallgemeinerung (Regel 15c): K1 (Masken-Spektrum M0 sagt die gelernten Frequenzen voraus) ist nur für add mod 113
belegt ([[experiments/EXP-015-mask-spectrum/README|EXP-015]]). Hier wird K1 an **unberührten Fällen** mit anderem Modulus (97) und
zusammengesetzter Gruppe (Z_112 über den diskreten Logarithmus) geprüft. Nebenbei entscheidet der Versuch zwischen drei ausdrücklich
genannten Konkurrenzmodellen für den Mechanismus (erste Ordnung: M0c; EXP-015: M0; Häufigkeiten CNT) und gegen die Init (E0).

| | |
|---|---|
| **Fragestellung** | Sagt das nur aus dem Trainingssplit berechnete M0 (in Gruppenkoordinaten) das W_E-Leistungsspektrum bei Schritt 2000 voraus, auch bei add 97 und mul 113? |
| **H52 (primär, je Aufgabe)** | Spearman ρ(M0 des eigenen Splits, W_E-Spektrum) ist größer als mit dem M0 fremder Splits derselben Aufgabe |
| **Test** | Permutation der Split-Zuordnung (20 000, einseitig), Statistik = mittleres ρ auf der Diagonalen; Holm über die zwei Aufgaben, α 0.05 |
| **Urteil je Aufgabe** | *K1 gilt hier*: Holm-p < 0.05 · sonst *nicht bestätigt* · < 8 gültige Läufe: *nicht auswertbar* |
| **Sekundär (gepoolt, 20 Läufe, Vorzeichentest einseitig)** | S1 ρ(M0c) > ρ(M0) (Vorhersage der Rechnung erster Ordnung, [[BEFUND-split-mechanismus]]); S2 ρ(M0) > ρ(E0) (Split schlägt Init-Spektrum, vgl. K3); S3 ρ(M0) > ρ(CNT) (Häufigkeiten fallen in erster Ordnung heraus) |
| **Beschreibend** | r̄ und Top-5-Überlappung je Prädiktor (vergleichbar mit EXP-015), ρ(M0) bei 50/250/500/1000 Schritten |
| **Gültig** | wie EXP-043 über den gemeinsamen Lader: `completed`, cuda, 2000 Schritte, Split-Hash = Datei, p/Aufgabe, endliche Schnappschüsse bei 0, 50, 250, 500, 1000, 2000. Zusätzlich: Split-Datei unverändert (sha256 aus `predictions.json`), eingefrorene Spektren = heutige Rechnung |
| **Erwartung** | beide Aufgaben *K1 gilt hier*, matched ρ ≈ 0.4–0.5 (siehe gesehene Daten), fremd ≈ 0; S1 ja (schwach), S2 ja, S3 ja |
| **Was dagegen spräche** | kein Unterschied eigen/fremd bei mul 113: Die Maskenwirkung hinge dann an der additiven Zahlenanordnung, nicht an der Gruppenstruktur. S1 umgekehrt: die Rechnung erster Ordnung beschreibt die Wahl nach 2000 Schritten nicht |
| **Grenzen** | Assoziation, kein Eingriff (der Eingriff ist EXP-043 F/G). Eine Architektur. W_E-Energie, nicht funktionale Nutzung. M0 und M0c korrelieren in diesen Splits (mittleres ρ 0.69), S1 hat deshalb begrenzte Trennschärfe |
| **Budget** | keine eigenen Läufe; Auswertung Sekunden |

**Bereits gesehene Daten und davon beeinflusste Entscheidungen (Regel 18c):** EXP-015 (add 113, Seeds 0–19, K = Endfrequenzen) und
der Zeitverlauf `EXP-015-mask-spectrum/posthoc_m0_timecourse.json` (Seeds 0–9: ρ(M0, W_E) im Mittel −0.02 bei Init, 0.19 vor der
Memorisierung, **0.47 während der Memorisierung**, 0.14 am Ende) bestimmten die Wahl von ρ bei Schritt 2000 als Primärgröße (dort
ist der Abdruck am stärksten) und die Erwartung. Die EXP-043-R-Splits und ihre M0-Top-5 (in den Split-JSONs von `make_split.py`) waren
bekannt, **keine** Läufe. M0c/CNT/M0-Korrelationen der 20 Splits habe ich nach dem Einfrieren angesehen (ρ(M0, M0c) 0.69,
ρ(M0, CNT) 0.12); nichts wurde danach geändert.

## Befehle

```
python lab/experiments/EXP-052-oos-mask-prediction/exp052.py --predict      # erledigt (reine Rechnung auf Split-Dateien), eingefroren
python lab/tools/guarded_run.py -- python lab/experiments/EXP-052-oos-mask-prediction/exp052.py --selftest   # ab 03:00
python lab/tools/guarded_run.py -- python lab/experiments/EXP-052-oos-mask-prediction/exp052.py              # nach EXP-043 „random“
```

Nicht in `night_program.py` eingetragen (gemeinsamer Orchestrator bleibt unverändert); die Auswertung wird von Hand gestartet,
sobald `night_status.json` für EXP-043 den Schritt „random“ als erfolgreich zeigt.

## Nachtrag a (Sitzung 14, 2026-09-26 21:27 Berlin gemessen, **vor jedem Lauf**): dritter Fall D₅₉, Prüfung eingearbeitet

**Dritter Fall, nicht abelsch:** die 10 Zufallssplits (Arm R, ε = 0, Seeds 140–149) von
[[experiments/EXP-046-dihedral-steering/README|EXP-046]] (D₅₉, 29 zweidimensionale Irreps). M0 = nicht-abelsches Masken-Spektrum aus
`dihedral.mask_power` (EXP-046), M0c = dieselbe Rechnung mit N_L + N_R vor der Norm, CNT = Irrep-Leistung der Token-Zählvektoren.
Eingefroren in `predictions_d59.json` (`--predict-d59`; M0-Top-5 = die von `make_split.py` notierten in 10/10). W_E-Spektrum = die
von `group_train.py` protokollierte Irrep-Leistung (`spectra.npy`) bei 2000, E0 bei 0; Verlauf bei 250/500/1000. `predictions.json`
(add 97, mul 113) ist unverändert. **Die Primärfamilie hat damit drei Glieder, Holm über drei** (vorher zwei). Gesehen nach dem
Einfrieren: ρ(M0, M0c) 0.77, ρ(M0, CNT) 0.03, fremde Splits untereinander ρ(M0) 0.00.

**Unabhängige Prüfung (Claude-Subagent, nur lesend; Codex ohne Guthaben):** kein Blocker. „Hoch“ 1/2 (nicht committet, README fehlt)
waren zum Prüfzeitpunkt richtig, sind mit Commit 7c6492a erledigt. Übernommen: Glob endet jetzt auf `_{task}{p}_devcuda` (ein CPU-Lauf
desselben Splits machte die Suche sonst mehrdeutig → „fehlt“). Vermerkt: (i) Fällt ein Fall als *nicht auswertbar* aus, läuft Holm
über die übrigen; (ii) die Primärgröße trennt M0 nicht von einem Häufigkeitsmechanismus, das tut S3 (ρ(M0, CNT) klein, also trennscharf);
(iii) Spearman mit Ordinalrängen: in keinem eingefrorenen Vektor gibt es Bindungen. Bestätigt: gleiche Koordinaten/Basis wie EXP-043
(Zeile i = W_E[g^i] = Log-Koordinate i), Schnappschuss bei 0 vorhanden, Statistik korrekt, fremde M0 untereinander unkorreliert
(−0.015 / −0.012), kein Pfad, auf dem ein Fehler ein falsch-positives Urteil erzeugt.

## Nachtrag b (Sitzung 14, 2026-09-26  Berlin gemessen, **vor jedem Lauf**): vierter Fall, nicht-modulare Addition

**Vierter Fall:** die 10 Zufallssplits (Arm R, ε = 0, Seeds 160–169) von [[experiments/EXP-048-intadd-steering/README|EXP-048]]
(a + b ohne Modulo, Ausgabe 0..224). M0 wie `EXP-048/make_split.mask_power` (Ganzzahlversion), M0c kohärent, CNT aus den a/b-Häufigkeiten.
Wegen der Zahlengerade (EXP-048 Nachtrag a) **nur k = 6..56** und das W_E-Spektrum **trendbereinigt** (`we_final.npy` bei 2000, je Spalte die
Kleinste-Quadrate-Gerade in a entfernt, wie die Primärgröße von EXP-048). E0 gibt es hier nicht (kein W_E bei Schritt 0 gespeichert):
S2 ohne diesen Fall. Eingefroren in `predictions_intadd.json` (`--predict-intadd`). **Primärfamilie jetzt vier Glieder, Holm über vier.**
Gesehen nach dem Einfrieren: ρ(M0, M0c) 0.71, ρ(M0, CNT) 0.03, fremde Splits untereinander ρ(M0) **0.06** (Rest des dreieckigen Trägers bei
k ≥ 6; betrifft eigen und fremd gleich, der Permutationstest bleibt gültig, verliert aber etwas Trennschärfe).
**Erwartung hier offen:** Der Mechanismus erster Ordnung braucht keine Gruppe, aber das Netz kann bei a + b eine Zahlengerade statt Fourier-
Merkmalen lernen; dann ist der Rest-W_E nach der Trendbereinigung womöglich Rauschen und der Fall *nicht bestätigt*, ohne dass K1 dort falsch ist.

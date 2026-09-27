---
id: C1-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/C]
verwandt: ["[[FINDINGS]]", "[[confirm/R1_REGISTRATION_DRAFT|R1]]", "[[paper/draft]]", "[[JOURNAL]]"]
---
# C1: Sagt das Masken-Spektrum voraus, WELCHES der fünf Ziele zurückbleibt? (Programm C, Vorhersage an unberührten Fällen)

Zurück zu [[FINDINGS]] (Programm C) · Datenquelle: [[confirm/R1_REGISTRATION_DRAFT|R1]] (frische Seeds 2420–2509, noch **kein** Lauf). Registriert Sitzung 28 (2026-09-27, 16:5x Berlin),
vor jedem R1-Lauf; gilt mit dem Commit dieser Datei.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- P1 (50 Seeds je Aufgabe, gesehen und ausgewertet) → Exploration `lab/confirm/P1_posthoc_within.py` (sha256 d62db4c5…1f57f), Ergebnis `P1_posthoc_within.json`:
  mittlere Rangkorrelation je Arm zwischen Masken-Spektrum der Ziele und ihrer W_E-Energie bei Schritt 2000: add 113 M0c 0.44, M0 0.32, Init 0.13; mul 113 M0 0.21; add 97 M0 0.29; D₅₉ M0 0.43
  (Permutation innerhalb der Arme, M0/M0c jeweils p < 5·10⁻⁵).
- **Davon beeinflusst:** Wahl von M0c (zentriertes kohärentes Spektrum, Transformer-Pfad aus Entwurf §5) als primärem Prädiktor, weil es bei add 113 am stärksten war; Mindesteffekt und n aus der
  P1-Streuung (Mittel je Seed 0.438, SD 0.305, 44/50 positiv).

## Aussage C1

In einem grokkenden Ein-Schicht-Transformer (add 113) folgt die Rangfolge der fünf vorgegebenen Ziele in der W_E-Energie nach 2000 Schritten der Rangfolge ihrer Energie im zentrierten
kohärenten Masken-Spektrum M0c des Trainingssplits, auch wenn Lernrate, Weight Decay oder Trainingsanteil vom Standard abweichen.
Deutung, falls bestätigt: Die Theorie erster Ordnung sagt nicht nur die Menge, sondern auch die Feinordnung innerhalb der Menge voraus. Das ist eine Korrelation zwischen Spektrum und Ergebnis, keine
direkte Wirkung einzelner Ziele.

## Daten, Maß, Test (fest)

- **Daten:** alle 180 R1-Läufe (6 Zellen × 15 Seeds × F/G), geladen über den eingefrorenen R1-Lader (nur Läufe, die R1 als gültig wertet). Ziele je Arm aus der Split-Metadatei, Split-Indizes aus `lab/confirm/r1_splits/`.
- **Maß je Arm:** Spearman über die 5 Ziele zwischen M0c(Ziel) und der W_E-Gruppenenergie bei Schritt 2000 (`group_power`, wie P1). M0c exakt wie `m0c_add` in `P1_posthoc_within.py`.
  **Einheit = Seed:** Mittel der beiden Arme (F und G teilen die Init).
- **Primärtest:** gepoolt über alle 90 Seeds; einseitiger Vorzeichen-Permutationstest Mittel > 0 (200 000 Ziehungen), α = 0.05; 95-%-Bootstrap-KI über Seeds (10 000).
  **Bestätigt** = p < 0.05 **und** KI-Untergrenze ≥ 0.10 (Mindesteffekt). Eigene Familie (Programm C, eine Hypothese), nicht in der R1-Holm-Familie.
- **Nicht auswertbar**, wenn weniger als 60 Seeds mit zwei gültigen Armen vorliegen. Seeds ohne zwei gültige Arme fallen heraus (Zahl berichten).
- **Power:** P1-Streuung (SD 0.305) bei halbiertem Mittel (0.22): SE bei n = 90 ≈ 0.032, erwartete KI-Untergrenze ≈ 0.16 → deutlich über 0.10; Simulation mit halbierten P1-Werten, n = 30: Power 0.99.
- **Beschreibend (kein Test):** Mittel je Zelle; Prädiktoren M0 und Init-Energie (Schritt 0) wie in der Exploration; Anteil „schwächstes gelerntes Ziel = Ziel mit kleinstem M0c“ (Zufall 0.2).
- **Was dagegen spräche:** Mittel ≤ 0 oder KI-Untergrenze < 0.10. Ein Zusammenbruch nur in einzelnen Zellen ist ein beschreibender Befund („gilt nur in einem Bereich“).

## Umsetzung

Kein neues Training: die Auswertung liest R1-Läufe. Das Auswerteskript `lab/confirm/C1_analyze.py` wird **vor** dem Öffnen der R1-Ergebnisse geschrieben und committet und darf nichts an Maß,
Einheit, Test oder Schwellen oben ändern. Wird R1 nicht gerechnet oder geändert (andere Seeds, Schrittzahl, Aufgabe), gilt C1 nicht automatisch weiter und muss neu registriert werden.

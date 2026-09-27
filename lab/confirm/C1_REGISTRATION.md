---
id: C1-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/C]
verwandt: ["[[FINDINGS]]", "[[confirm/R1_REGISTRATION_DRAFT|R1]]", "[[paper/draft]]", "[[JOURNAL]]"]
---
# C1: Sagt das Masken-Spektrum voraus, WELCHES der fünf Ziele zurückbleibt? (Programm C, Vorhersage an unberührten Fällen)

Zurück zu [[FINDINGS]] (Programm C) · Datenquelle: [[confirm/R1_REGISTRATION_DRAFT|R1]] (frische Seeds 2420–2509, noch **kein** Lauf).
**Fassung 2 (gilt)**, Sitzung 28, 2026-09-27, nach der Codex-Prüfung (`C1_codex_review_s28.txt`), vor jedem R1-Lauf; gilt mit dem Commit dieser Datei und dem Code-Tor `C1_manifest.json`.
Fassung 1 (Commit d330f1c) ist ersetzt; Änderungen unten unter „Änderungen gegenüber Fassung 1“.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- **Direkt motivierend:** P1 (50 Seeds je Aufgabe, gesehen) → Exploration `lab/confirm/P1_posthoc_within.py`, Ergebnis `P1_posthoc_within.json`: mittlere Rangkorrelation je Arm zwischen
  Masken-Spektrum der Ziele und ihrer W_E-Energie bei Schritt 2000: add 113 M0c 0.44, M0 0.32, Init 0.13; mul 113 M0 0.21; add 97 M0 0.29; D₅₉ M0 0.43 (Permutation innerhalb der Arme, M0/M0c jeweils p < 5·10⁻⁵).
  Bereinigt um k und Init-Rang (add 113): Koeffizient 0.433 (`C1_predictor_diag.json`). Kontrollen: ρ(gelernt, k) 0.008, vertauschte Arme −0.08.
- **Verwandte, teils gegenläufige gesehene Analysen:** Über Seeds sagt der M0-Zielkontrast die Größe von Δ_pow besser voraus als das zentrierte M0c (Spearman 0.39, p 0.006 gegen 0.26, p 0.07;
  `P1_posthoc_m0_strength.py`, Sitzung 25). EXP-015: M0 sagt die gelernten Frequenzen voraus; EXP-050: der erste W_E-Gradient folgt M0c (Transformer), erklärt aber nur einen Teil
  ([[BEFUND-split-mechanismus]]). Diese betreffen die Auswahl bzw. den ersten Gradienten, nicht die Rangfolge bei Schritt 2000. **C1 behauptet nicht, M0c sei besser als M0**; der Vergleich bleibt beschreibend.
- **Davon beeinflusst:** Wahl von M0c als Prädiktor (bei add 113 am stärksten), Mindesteffekt, Stichprobe.
- **Nur Prädiktoren, vor jedem Lauf gerechnet** (`C1_predictor_diag.py`, aus der deterministischen R1-Split-Konstruktion, nichts geschrieben): in den 180 R1-Splits ρ(M0c, k) im Mittel 0.05 (SD 0.53),
  keine Bindungen, M0c max/min im Median 1.30. Die Ziele werden sortiert gespeichert, die Listenposition hat also dieselben Ränge wie k.

## Aussage C1 (eng)

Im gleich gewichteten Mittel über die sechs R1-Zellen (add 113; je eine Abweichung in Lernrate, Weight Decay oder Trainingsanteil) folgt die Rangfolge der fünf vorgegebenen Ziele in der
W_E-Energie nach 2000 Schritten der Rangfolge ihrer Energie im zentrierten kohärenten Masken-Spektrum M0c des Trainingssplits, auch nach Bereinigung um den Frequenzindex k und den Init-Rang.
Keine Aussage über jede einzelne Zelle; eine Zelle mit Mittel ≤ 0 wird als Grenze berichtet („gilt dort nicht“). Deutung, falls bestätigt: vereinbar mit der Theorie erster Ordnung
(Entwurf §5), die dann auch die Feinordnung in der Zielmenge trifft; keine direkte Wirkung einzelner Ziele gezeigt (Korrelation).

## Daten, Maß, Test (fest)

- **Daten:** alle 180 R1-Läufe, Schritt-2000-Energie über den eingefrorenen R1-Lader (`confirm_r1.power`), W_E bei Schritt 0 über einen vollständigen Ladevorgang desselben Laufs (gleiche Erwartungen + Snapshot 0).
- **Maß je Arm:** Spearman über die 5 Ziele zwischen M0c(Ziel) (`m0c_add` in `P1_posthoc_within.py`) und W_E-Gruppenenergie. Exakte Bindungen in M0c oder Energie → Arm technisch ausgefallen.
- **Einheit = Seed:** Mittel der beiden Arme (F und G teilen die Init); ein Seed zählt nur mit zwei gültigen Armen.
- **Statistik S** = gleich gewichtetes Mittel der sechs Zellmittel.
- **Bestätigt**, wenn alle drei gelten: (i) einseitiger Vorzeichen-Permutationstest auf S (Vorzeichen je Seed, 200 000 Ziehungen, p = (Überschreitungen + 1)/(B + 1); Annahme: unter H0
  symmetrisch um 0) < 0.05; (ii) Untergrenze des 95-%-Bootstrap-KI von S (Seeds innerhalb der Zellen gezogen, 10 000) ≥ 0.10; (iii) Untergrenze des 95-%-Bootstrap-KI (gleich gezogen) des
  bereinigten Koeffizienten > 0: Kleinste Quadrate über alle Arme mit Schritt-0-Snapshot, zentrierte Ränge innerhalb jedes Arms, Energie ~ M0c + k + Init.
  Eigene Familie (Programm C, eine Hypothese), nicht in der R1-Holm-Familie.
- **Nicht auswertbar**, wenn eine Zelle weniger als 10 von 15 Seeds mit zwei gültigen Armen hat. Fehlende Seeds werden gezählt; zusätzlich wird S berichtet, als hätten sie ρ = −1 (Empfindlichkeitsschranke, kein Urteil).
- **Beschreibend (kein Test):** Zellmittel; Prädiktoren M0 und Init; Anteil „schwächstes gelerntes Ziel = Ziel mit kleinstem M0c“ (Zufall 0.2).
- **Power:** P1 (SD je Seed 0.305): bei halbiertem Mittel (0.22) und n = 90 SE ≈ 0.032, erwartete KI-Untergrenze ≈ 0.16 > 0.10; Bootstrap-Simulation mit halbierten P1-Werten, n = 30: 0.99.
- **Was dagegen spräche:** S ≤ 0, KI-Untergrenze < 0.10, oder der bereinigte Koeffizient nicht > 0 (dann folgt die Ordnung eher k oder der Init).

## Umsetzung und Code-Tor

`lab/confirm/C1_analyze.py` (Fassung 2) mit `rank_tools.py` und `P1_posthoc_within.py`; Hashes in `lab/confirm/C1_manifest.json`, von der Auswertung geprüft. Eine vorhandene `C1_summary.json` wird nie überschrieben.
Selbsttest (nur im Fenster): Handwerte der Rangstatistik, synthetische Zellen (bestätigt / nicht bestätigt, wenn die Ordnung k folgt / nicht auswertbar / Fehlschranke), M0c gegen eine unabhängige Brute-Force-Rechnung.
Wird R1 geändert (Seeds, Schritte, Aufgabe, Zellen), gilt C1 nicht weiter und muss neu registriert werden.

## Änderungen gegenüber Fassung 1 (Codex, Sitzung 28)

Übernommen: Aussage auf das gepoolte Zellmittel eingeengt (Blocker 1); bereinigter Koeffizient als dritte Bedingung (Blocker 2; M0c-gegen-M0 bleibt beschreibend, keine Mechanismus-Aussage);
Prädiktor-Diagnosen vor dem Lauf; p mit +1; Zellmindestzahl, gleich gewichtete Zellmittel, geschichtetes Bootstrap, Fehlschranke; Code-Tor und Überschreibschutz; vollständige Offenlegung;
Selbsttest nicht mehr zirkulär; Bindungen → technisch; Schritt 0 mit vollen Erwartungen. Verworfen: keiner. Nicht übernommen: ein studentisierter Test statt der Vorzeichenpermutation
(die Symmetrieannahme ist genannt, und Bedingung ii verlangt zusätzlich das Bootstrap-KI).

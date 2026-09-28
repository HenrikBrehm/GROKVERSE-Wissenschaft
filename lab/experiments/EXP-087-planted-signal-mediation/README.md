---
id: EXP-087
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/unklar, neu/kandidat]
verwandt: ["[[NOVEL_DIRECTIONS]]", "[[confirm/R5_REGISTRATION_DRAFT|R5]]", "[[experiments/EXP-040-we-init-scale/README|EXP-040]]", "[[FINDINGS]]", "[[JOURNAL]]"]
---
# EXP-087: Läuft die Split-Beschleunigung ganz über das frühe W_E-Zielsignal? Eingepflanztes Signal auf einem Zufallssplit (Pilot, Entwurf)

Zurück: [[LAB]] · [[NOVEL_DIRECTIONS]] N47 · Anlass [[confirm/R5_REGISTRATION_DRAFT|R5]] (bestätigt) und `lab/confirm/R5_posthoc_share_speed_s38.py` · [[JOURNAL]] Sitzung 38.

**Status:** Entwurf, Sitzung 38 (2026-09-28, 06:45 Berlin gemessen), vor jedem Lauf. **Kein Code.** Braucht eine Trainer-Option in `freq_ban.py` (gemeinsamer Trainer → Tests; Codex-Regel 18c, bei leerem Guthaben unabhängige Claude-Prüfung). **Zeitliche Sperre:** Trainer erst ändern, wenn die eingefrorenen Blöcke R2 und R4 gerechnet und ausgewertet sind (beide Manifeste hashen den Trainer).

**Ziel in FINDINGS:** Programm C (mechanistische Vorhersage) und Einordnung von R5 im Paper: Ist die bestätigte Beschleunigung durch konstruierte Splits eine Anwendung des bekannten Mechanismus „frühe aufgabenrichtige Einbettungsstruktur verkürzt die Verzögerung“ (Howe 2026, arXiv 2607.04333; GrokTransfer, arXiv 2504.13292) oder braucht sie den fortlaufenden Datengradienten?

## Konkurrenzmodelle

- **M-med (volle Mediation):** Der konstruierte Split wirkt nur, weil er früh W_E-Energie auf die Ziele legt. Ein Zufallssplit mit gleich großem eingepflanztem Zielsignal groks so früh wie E2.
- **M-data (Datengradient nötig):** Das frühe Signal hilft, aber der Split wirkt auch danach (z. B. über die Paarverteilung beim Aufbau des Schaltkreises). R+P bleibt deutlich langsamer als E2; E2+P ist schneller als E2 oder gleich.
- **M-marker (reiner Fortschrittsmarker):** Das frühe Signal ist nur ein Begleiter. Einpflanzen beschleunigt R kaum.

## Versuch (Entwurf)

| Punkt | Festlegung |
|---|---|
| **Eingriff** | `--plant-targets k1,…,k5 --plant-amp α` (neu): direkt nach der Init W_E[:p] += α · Σ_k (cos(2πka/p) u_k + sin(2πka/p) v_k), u_k, v_k zufällige Einheitsvektoren aus einem eigenen Strom (nicht aus dem Init-Seed); Prüfsumme der unveränderten Init bleibt gespeichert |
| **Kalibrierung (vor dem Piloten, eigene Seeds, nicht im Urteil)** | α so wählen, dass der W_E-Zielanteil bei Schritt 250 auf R+P im Mittel dem von E2 in R5 entspricht (0.30); Gitter α ∈ {0.5, 1, 2, 4} × Median-Init-Amplitude, 3 Kalibrier-Seeds; gewählt wird das α mit dem nächstgelegenen Mittel |
| **Arme (je Einheit gleiche Init und Testmenge wie R5-Konstruktion)** | R, R+P, E2, E2+P, dazu **R+N** (Normkontrolle: gleiche Frobenius-Norm des Zusatzes, aber zufällige Nicht-Fourier-Struktur) |
| **Ereignis** | wie R5: Test ≥ 0.95 bei s, s + 25, s + 50 nach Train ≥ 0.99; b = min(Ereignis, 8000) |
| **Primär (Exploration, kein Bestätigungsurteil)** | L_med = log2 b(R+P) − log2 b(E2) und L_plant = log2 b(R) − log2 b(R+P), gepaart je Einheit, Vorzeichentest, Bootstrap-KI |
| **Lesart vorab** | *M-med gestützt:* L_plant-KI > 1 und L_med-KI in [−0.5, +0.5]. *M-data gestützt:* L_plant-KI > 0 und L_med-KI-Untergrenze > 0.5. *M-marker gestützt:* L_plant-KI < 0.5. Sonst *unklar*. R+N muss langsamer oder gleich R sein (sonst wirkt nur die Norm → *nicht auswertbar* für die Mediationsfrage) |
| **Sekundär** | L_E = log2 b(E2) − log2 b(E2+P); Zielanteil bei 250 je Arm (Kalibrierungskontrolle); Endfrequenzen von R+P (steuert das eingepflanzte Signal auch K2 ohne Datensteuerung?) |
| **Seeds** | Pilot 3200–3209 (vor Nutzung in [[FINDINGS_DETAILS]] reservieren), Kalibrierung 3210–3212 |
| **Budget** | 5 Arme × 10 Einheiten × ≤ 8000 Schritte ≈ 50 GPU-Läufe ≈ 30–40 min bei 6 Workern; Kalibrierung 4 × 3 kurze Läufe (≤ 500 Schritte) |
| **Was dagegen spräche** | M-marker (Einpflanzen hilft nicht): dann ist der frühe Zielanteil in R5 nur ein Fortschrittsmarker |
| **Grenzen** | Das eingepflanzte Signal hat andere Phasen/Richtungen als ein gelerntes; die Norm von W_E ändert sich (R+N kontrolliert nur die Norm, nicht die Richtung); Zielanteil nach Kalibrierung ist keine unabhängige Messung; add 113, eine Architektur; Pilot mit 10 Einheiten |

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

R5 (Seeds 2720–2779, bestätigt; Zielanteil je Arm), R5 post hoc innerhalb der Arme (ρ −0.64 bis −0.79), EXP-040 (W_E-Init-Skala verschiebt das Festlegungsfenster nicht), EXP-042/EXP-084 (Dosis). Beeinflusst: Wahl der Kalibriergröße (Anteil bei 250), Horizont 8000, Ereignisdefinition. Keine Läufe mit den Seeds 3200–3212.

## Nachtrag a (Sitzung 39, 2026-09-28, vor jedem EXP-087-Lauf): Code

- `plant.py`: Eingriff (Selbsttest grün über den Wächter, 08:17). Parametrisierung: eingepflanzte Leistung je Zielfrequenz = C × Median der Init-Frequenzleistung, α = √(C·Median/2). Das Amplitudengitter {0.5, 1, 2, 4} × Median-Amplitude entspricht **C ∈ {0.5, 2, 8, 32}** (Leistung 2m²). R+N: zufällige, über die Zahlen mittelwertfreie Matrix mit derselben Frobenius-Norm wie der Einpflanz-Zusatz (eigener Strom).
- `design.py`: Splits (eigener Strom `TAG 20261087`, Konstruktion E2 mit den R5-Helfern `wave`/`keyed`), Kalibrierjobs (3 Einheiten × 4 C, 250 Schritte, nur R+P), Wahl von C (Mittel am nächsten an 0.30, Gleichstand → kleineres C), Pilotjobs, Auswertung mit Ereignis und Dichteprüfung aus R5, Lesart wie oben. **Präzisierung der Lesart (vorab):** M-med nur, wenn R+P in ≥ 8/10 Einheiten beobachtet (sonst ist L_med durch Zensur zu 0 verzerrt → *unklar*); R+N gilt als „nicht schneller als R“, wenn die untere KI-Grenze von L_noise ≤ 0 oder das Mittel ≤ 0.5 ist. Selbsttest grün (08:19). Eine Einheit mit einem technischen Ausfall → ganzer Pilot *nicht auswertbar* (streng, wie R5).
- Offen: Trainer-Option (`--plant-targets`, `--plant-c`, `--plant-noise`) erst nach R4.

## Nachtrag b (Sitzung 39, committet 09:11:20 Berlin laut `git log` (f05e4e50); Pilot lief, **kein Pilotergebnis gelesen**)

Nach der unabhängigen Code-Prüfung (Claude-Agent, nur lesend; Codex ohne Guthaben): kein Blocker. Übernommen, vor jeder Auswertung festgelegt:
1. **Zensur des R-Arms** drückt L_plant Richtung 0 und begünstigt fälschlich M-marker → *M-marker* nur, wenn R in ≥ 8/10 Einheiten beobachtet ist, sonst *unklar*. Beobachtete Zahl je Arm wird berichtet.
2. **Keine Rangfolge der Lesarten:** Sind mehrere Lesarten zugleich erfüllt (z. B. M-marker und M-data), lautet das Urteil *unklar*.
3. **Sekundär ergänzt** (war registriert, fehlte im Code): finale Top-5-Frequenzen je Arm, Überlappung mit den eingepflanzten/gesteuerten Zielen.
4. **Kalibrierung überschießt** (R+P bei 250: 0.40 gegen E2 ≈ 0.30): das schiebt L_med nach unten; ein L_med-KI unter −0.5 ergibt *unklar*, keine falsche Lesart. Wird beim Lesen genannt.
5. **Herkunft der Kalibrierung:** Die 12 Kalibrierläufe tragen `git_commit cf66d125`, weil der Trainer-Diff noch nicht committet war; der Diff war derselbe wie in c8b59b48 (danach unverändert committet). Die Pilotläufe tragen c8b59b48.
6. Nicht übernommen (nur Hinweis, betrifft EXP-087 nicht): Kombination `--plant-*` mit Warmup/Reset/Rewind wird nicht abgelehnt (ein Reset stellt dann das *eingepflanzte* W_E wieder her); Run-ID enthält die Ziele nicht (der Fingerprint verhindert Verwechslungen).

## Nächste Schritte

1. Nach R2/R4: Option `--plant-targets/--plant-amp` in `freq_ban.py` (Standard aus, alte Run-IDs unverändert, Fingerprint nur bei Nutzung), Test, unabhängige Prüfung.
2. `jobs.txt`, `analyze.py` mit Selbsttest (Lesart oben fest), Kalibrierung, dann Pilot.

## Ergebnis (Sitzung 39, 2026-09-28; Pilot 50 GPU-Läufe, C = 2, `design.py --analyze 2` über den Wächter; Exploration, keine Kernaussage)

10/10 Einheiten gültig, keine technischen Ausfälle, Init-Prüfsummen je Einheit gleich. Beobachtet (Ereignis ≤ 8000): R 7/10, R+P 10/10, E2 10/10, E2+P 10/10, R+N 8/10.

| Größe (log2, gepaart) | Mittel | 95-%-KI | Vorzeichen |
|---|---|---|---|
| L_plant = b(R) − b(R+P) | **+3.42** | [3.08, 3.75] | 10/10 > 0 (p = 2⁻¹⁰); untere Schranke, R 3× zensiert |
| L_med = b(R+P) − b(E2) | **−0.63** | [−0.99, −0.20] | 1/10 > 0: R+P *schneller* als E2 |
| L_E = b(E2) − b(E2+P) | +1.45 | [1.20, 1.67] | 10/10 |
| L_noise = b(R) − b(R+N) | −0.09 | [−0.33, 0.12] | Normkontrolle ohne Wirkung → gültig |

**Registrierte Lesart: *unklar*.** L_plant erfüllt M-med (Untergrenze > 1), aber das L_med-KI liegt teilweise unter −0.5, also außerhalb des Fensters [−0.5, 0.5]; M-data (L_med-Untergrenze > 0.5) und M-marker (L_plant-Obergrenze < 0.5) sind klar verfehlt. Nachtrag b, Punkt 4 hatte genau diesen Fall vorhergesehen: Die Kalibrierung überschoss (R+P hatte bei 250 einen Zielanteil von 0.40, E2 0.31).

Beschreibend je Arm (Zielanteil bei 250 / geometrisches Mittel der Zeit / finale Top-5 auf den Zielen): R 0.085 / 5222 / 0.7 · R+N 0.084 / 5574 / 0.3 · E2 0.310 / 757 / 3.7 · **R+P 0.401 / 489 / 3.3** · E2+P 0.502 / 276 / 3.5.
- Das Einpflanzen allein (ohne Datensteuerung) **reicht**, um die Beschleunigung des konstruierten Splits zu erreichen und zu übertreffen. Es steuert auch die finalen Frequenzen fast so stark wie der Split (3.3 gegen 3.7 von 5 Zielen). Eine gleich große unstrukturierte Änderung (R+N) bewirkt nichts.
- **Über alle fünf Arme ordnet der Zielanteil bei 250 die Zeit exakt**, egal ob der Anteil aus den Daten, aus dem Eingriff oder aus beidem kommt. *Post hoc, über Versuche hinweg (andere Einheiten):* Die R5-Dosisarme liegen auf derselben Linie (E1 0.12 / 5283, E2 0.30 / 920, E8 0.48 / 368). Log-linear zwischen E2 und E8 interpoliert ergibt ein Anteil von 0.40 ≈ 550 Schritte, R+P brauchte 489.
- **Lesart (Interpretation, nicht registriert):** Die Daten passen zu einem gemeinsamen Mittler „früher W_E-Zielanteil“. Ein zusätzlicher Datenbeitrag des Splits ist nicht zu sehen (M-data verfehlt). Der vorab festgelegte Mediationstest ist aber wegen der Dosis-Fehlanpassung formal unentschieden. Der saubere Test ist ein Vergleich auf gleicher Dosis-Achse: Liegen eingepflanzte und datengesteuerte Arme auf derselben Kurve „Anteil bei 250 → Zeit“? → Folgeversuch [[experiments/EXP-088-common-dose-curve/README|EXP-088]] (Entwurf).
- **Literatur:** Dass gut ausgerichtete Einbettungen das Grokking beschleunigen, ist bekannt (Howe 2026, arXiv 2607.04333; GrokTransfer, arXiv 2504.13292; siehe N47). Neu wäre höchstens die quantitative Gleichwertigkeit von datengetriebenem und eingepflanztem Frühsignal, und auch das nur nach unserer Suche.
- **Grenzen:** Pilot, n = 10, add 113, eine Architektur, ein C; R 3/10 zensiert (L_plant ist eine untere Schranke); der Anteilsvergleich über R5 und EXP-087 hinweg ist post hoc und nutzt verschiedene Einheiten.


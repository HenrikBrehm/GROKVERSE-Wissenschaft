---
id: EXP-036
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
---
# EXP-036: Kommen die „fremden“ Frequenzen der Mischzustände aus der Initialisierung?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Grundlage [[experiments/EXP-020-data-switch/README|EXP-020]] (Nachtrag d) ·
verwandt [[experiments/EXP-012-init-gradient/README|EXP-012]], [[experiments/EXP-035-warmup-lockin/README|EXP-035]].

## Anlass

EXP-020 (Seeds 30–32, Exploration, `conflict_freqs.py`): Wird nach t ≤ 50 Schritten von Split F auf Split G gewechselt,
enthält das Endnetz Frequenzen, die weder zu F, G, deren 2k-Oberwellen noch zu den Endfrequenzen der reinen Läufe gehören
(z. B. Seed 30: 34, 39). Bei t ≥ 150 nie. Ihre Ränge im Init-Spektrum von W_E sind auffällig klein (Median 8 von 56).
Deutung (Spekulation): Im noch nicht festgelegten Netz heben sich die Datensignale von F und G teilweise auf, und das
Init-Spektrum setzt sich durch. Rangvergleich allein ist nur eine Assoziation; die Init ist hier der Eingriff.

## Versuch (vorab festgelegt 2026-09-26 14:53 Berlin (commit 5730b38), vor jedem EXP-036-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Folgen die fremden Frequenzen der Init (Eingriff: neue Init, gleicher Split) oder dem Split? |
| **H36** | Sie sind init-getrieben: Unter der neuen Init stehen die neuen fremden Frequenzen im **neuen** Init-Spektrum höher als im alten |
| **Alternative** | Split-getrieben: Die fremden Frequenzen hängen nicht von der Init ab; dann ist rank_new < rank_old ein Münzwurf, und die fremden Mengen alt/neu überlappen |
| **Kontrolle** | EXP-020-Läufe derselben Splits mit der alten Init (Seed s); die Init ist der einzige Unterschied |
| **Eingriff** | `--seed s + 100` (130, 131, 132) bei den Splits von Seed s ∈ {30, 31, 32}. Mit `--split-file` bestimmt `--seed` nur Init (und Reihenfolge, full batch) |
| **Läufe je Paar** | nur F (2000 Schritte), nur G (2000), Wechsel F → G bei t = 25, 50, 10 (+ 2000 G-Schritte). 15 Läufe, ≈ 4.3 min je Lauf, ≈ 65 min (ersetzt durch Nachtrag a: 7 Paare, 35 Läufe) |
| **Messung** | A = F ∪ G ∪ fold(2k) ∪ K_nurF ∪ K_nurG (reine Läufe **dieser** Init, Top-5 von W_E bei Schritt 2000); fremd = ⋃_{t∈{10,25,50}} Top-5(t + 2000) \ A. Je verschiedene fremde Frequenz k: Erfolg, wenn Rang im neuen Init-Spektrum < Rang im alten (Schritt 0, Rang 1 = stärkste) |
| **Test** | gepoolt über die drei Paare, einseitiger Vorzeichentest (Bin(n, ½)) |
| **Urteil** | n < 5 → *nicht auswertbar*; Anteil ≥ 0.75 und p < 0.05 → *init-getrieben*; Anteil ≤ 0.5 → *nicht init-getrieben*; sonst *unklar*. Fehlt ein Lauf oder ist das Init-Spektrum identisch → *nicht auswertbar* |
| **Sekundär (beschreibend)** | Überlappung der fremden Mengen alt/neu je Split; Median des neuen Init-Rangs; ob die neue Init überhaupt Mischzustände zeigt (Festlegung könnte bei anderer Init früher/später fallen) |
| **Budget / Abbruch** | ≈ 65 min, ein Job; Abbruch bei NaN oder Stillstand. Queue stoppt bei jedem Fehler |

**Was gegen H36 spräche:** Anteil ≤ 0.5, oder die gleichen fremden Frequenzen wie unter der alten Init.
**Grenzen:** n ist klein (erwartet ≈ 5–10 fremde Frequenzen); ein positives Urteil zeigt nur, dass die Init die Wahl im
Mischzustand mitbestimmt, nicht den Mechanismus. Die neue Init kann ein anderes Festlegungsintervall haben; zeigt sie bei
t ∈ {10, 25, 50} keine Mischzustände, ist n klein und der Versuch eher *nicht auswertbar*.

## Nachtrag a (2026-09-26 15:01 Berlin, nach Codex-Review, **vor jedem EXP-036-Lauf**): Paar als Einheit, strenge Prüfung

Codex (`codex_review_2026-09-26.txt`, needs-attention) fand vier Schwächen; alle übernommen:
1. **Frequenzen sind keine unabhängigen Versuche** (sie teilen dieselben Läufe und Top-5-Plätze). Neu: Einheit = Paar
   (Split, neue Init). **7 Paare:** Splits 30–34 mit Init s + 100, Splits 30, 31 zusätzlich mit Init s + 200. 35 Läufe,
   ≈ 150 min. Je Paar d_p = Mittel über die neuen fremden Frequenzen von (Rang_alt − Rang_neu); Erfolg, wenn d_p > 0.
   Vorzeichentest über die auswertbaren Paare (auswertbar: alle Läufe gültig und mindestens eine neue fremde Frequenz).
2. **Die alte fremde Menge ging nicht ins Urteil ein**, gleiche Mengen alt/neu hätten *init-getrieben* ergeben können.
   Neu: J_p = Jaccard(fremd_neu, fremd_alt); *init-getrieben* verlangt zusätzlich mittleres J < 0.5.
   Eine symmetrische Statistik (auch die alte Menge im neuen Init-Spektrum) ist nur für die Splits 33, 34 frisch
   (30–32 sind Exploration) und wird dort nur berichtet.
3./4. **Läufe wurden ohne `result.json`-Prüfung akzeptiert.** Neu: gemeinsamer Lader `load_run` in
   `EXP-020-data-switch/conflict_freqs.py` (Status, Seed, exakte Schritte, Split-/Test-/Wechsel-Hash, eine Init-Prüfsumme je
   Init, endliche Spektren); die neue Init muss eine andere Prüfsumme haben als die alte.
**Urteil (ersetzt die Tabelle oben):** m < 5 auswertbare Paare → *nicht auswertbar*; einseitiger Vorzeichentest über Paare
p < 0.05 **und** mittleres J < 0.5 → *init-getrieben* (bei m = 7 heißt das 7/7, bei m = 6 6/6, bei m = 5 5/5);
Erfolgsanteil ≤ 0.5 → *nicht init-getrieben*; sonst *unklar*. Die Frequenz-Ebene wird nur beschreibend berichtet.
**Nullhypothese:** Hängen die fremden Frequenzen nicht von der Init ab, sind die Ränge in zwei unabhängig gezogenen Inits
austauschbar, d_p ist symmetrisch um 0. A enthält die Endfrequenzen der reinen Läufe derselben Init; falls diese
init-bevorzugte Frequenzen enthalten, werden solche aus der fremden Menge entfernt, was gegen H36 wirkt (konservativ).
**Nicht übernommen:** Nur W_E zu verpflanzen (bei sonst gleicher Init) wäre der schärfere Test für „das Init-Spektrum von W_E“;
hier wird nur „die Init“ als Ganzes geprüft. Das bleibt ein möglicher Folgeversuch.

## Nachtrag b (2026-09-26 17:05 Berlin, **vor jedem EXP-036-Lauf**): zweite, datenbasierte Vorhersage P36b

Aus EXP-037 und EXP-020 (Exploration, post hoc, JOURNAL Sitzung 9): Alle beobachteten „Konfliktfrequenzen“ (34; 22, 42, 36;
8, 13; 38) liegen unter den Kandidaten außerhalb A auf Platz 1–7 (von ≈ 37), wenn man nach der frühen Unterstützung in
**beiden** reinen Läufen ordnet (Rang im W_E-Spektrum bei Schritt 250 im Lauf „nur F“ + Rang im Lauf „nur G“).
Deutung (Spekulation): Im Konflikt gewinnen Frequenzen, die beide Datensätze früh als Zweitbeste stützen; die Init wirkt nur
darüber mit. **P36b (sekundär, ändert das Urteil zu H36 nicht):** gepoolt über die auswertbaren Paare haben ≥ 75 % der
verschiedenen neuen fremden Frequenzen einen solchen Unterstützungsrang ≤ 5 (berechnet mit den reinen Läufen **derselben
neuen Init**) → *erfüllt*; Zufall ≈ 5/37 ≈ 14 %. Code: `shared_support_ranks` in `analyze.py`, geprüft an den
Explorationsdaten (Seed 30: 34 → 1; Seed 32: 13 → 2, 8 → 4).

## Nachtrag c (17:15 Berlin, nach Codex, **vor jedem EXP-036-Lauf**): P36b nur beschreibend

Codex: P36b ist kein kalibrierter Test (abhängige Frequenzen gepoolt, keine Mindestzahl, Zufallsniveau 5/37 nicht realistisch
bei der Auswahl über Top-5 und A, Summe der Ränge verlangt keine Unterstützung durch beide, Schritt 250 liegt nach dem
Festlegungsfenster). **Übernommen:** P36b wird **nur beschreibend** berichtet, ohne Urteil. Eine kalibrierte Fassung (Paar als
Einheit, Permutations-Null, die A und die Top-5-Auswahl nachbildet, konjunktives Maß wie max(Rang_F, Rang_G), Vergleich mit dem
Init-Rang, Messung vor dem Festlegungsfenster: dafür wären Spektren alle 10 Schritte nötig) gehört in einen eigenen Nachtrag
**vor** dem Start von EXP-036. Das Haupturteil zu H36 ist davon unberührt.

## Reproduktion

```
sh lab/experiments/EXP-036-init-conflict/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-036-init-conflict/analyze.py
python lab/experiments/EXP-036-init-conflict/analyze.py --selftest   # Urteilslogik
```

## Status

Vorbereitet (Nachtrag a), nicht ausgeführt. Warteschlange `queue_s9.sh`: nach `queue_s8.sh` (EXP-020 → EXP-035 → EXP-034) bzw. im nächsten Fenster.

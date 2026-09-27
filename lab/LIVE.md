---
tags: [lab/live]
---
# LIVE: Laborsitzung 32

- **Sitzungsstart:** 2026-09-27 20:29 Berlin (18:29Z, vom Runner)
- **Deadline:** 2026-09-27 23:29 Berlin (21:29Z)
- **Zuletzt aktualisiert:** 21:26 Berlin
- **Run-Fenster:** zu bis 00:00: kein Training, keine Tests.

## Gerade

Ein Skeptiker-Agent greift die Deutung der Wechselkosten an (Alternativerklärungen, trennende Prüfungen an gespeicherten Daten).

## Als Nächstes

Ab 00:00 laut [[STATE]]: EXP-018, dann **EXP-084 direkt danach** (Vorhersage vor dem Lauf, Commit 6d0231f); R6-Selbsttest; R6 nach R1 einfrieren und rechnen.

## Verlauf dieser Sitzung

- 21:26 STATE auf 67 Zeilen gekürzt; R6 bekommt eine beschreibende Zerlegung (vor dem Lauf).
- 21:24 Verzögerung = Plateau vor der Generalisierung (90 % in der Lücke nach der Memorisation), keine Rückschläge.
- 21:22 Streuung der Kosten: kritisches Verlangsamen nicht belegt (unklar).
- 21:21 Befund hängt nicht an der Ereignisdefinition (strenge Definition praktisch gleich).
- 21:20 [[experiments/EXP-085-mlp-switch-cost/README|EXP-085]] vorbereitet (Wechselkosten im MLP, Nachtschritt 5).
- 21:18 EXP-074: Zeitvorhersage der Resets vor dem Lauf festgelegt.
- 21:16 Resets: unmittelbarer Verlustschaden erklärt die Verzögerung nicht.
- 21:14 N29: Wechsel @25 in 20/20 Seeds langsamer als @50; Resets verzögern in der Reihenfolge von K4d/K4e.
- 21:13 Paper-Abbildung 6 (Kostenkurve und Persistenz).
- 21:12 Feine Kostenkurve (Seeds 400–409): Spitze bei 25, negativ ab 50, wo π ≈ 1.
- 21:09 R6 um S2 ergänzt (Kosten verschwinden bei π ≈ 1), Codex ohne Befund.
- 21:08 Wechselkosten auch in add 97 / mul 113 (EXP-044), Fenster dort bis 50. Paper-Absatz nach Quellenprüfung vorsichtiger gefasst.
- 21:05 Unentschiedenheit π(25) sagt die Kosten je Seed nicht voraus (negativ).
- 21:04 Mehr gemeinsame Paare → höhere Kosten (EXP-056 8/10, n. s.).
- 21:02 [[confirm/R6_REGISTRATION_DRAFT|R6]] registriert (30 frische Seeds, Codex: kein Blocker, alle Punkte eingearbeitet, Nachprüfung erledigt).
- 20:44 **Neu (Exploration):** Wechsel bei t = 25 verzögert das Grokking (N28 28/30 Seeds, Replikation P3 28/30), bei t = 50 nicht. Das ist die Spitze im Festlegungsfenster ([[NOVEL_DIRECTIONS]] N43).
- 20:39 AlQuabeh-Autorenliste: Artefakt in den arXiv-Metadaten; EXP-084 statisch geprüft.
- 20:37 Zufallssplits: Maskenspektrum erklärt die Streuung der Grokking-Zeit nicht erkennbar (ρ −0.25, p 0.15).
- ≈ 20:35 M_share gibt die gesehenen ε-2-Gruppen wieder (±0.13 log2), verfehlt ε 1 und die Steigung innerhalb der Stufe.
- 20:32 [[experiments/EXP-084-dose-curve/README|EXP-084]]: Vorhersage vor dem Lauf festgehalten (Sättigung gegen weitere Beschleunigung).
- 20:29 Start: kein STOP, keine Prozesse, Fenster zu.

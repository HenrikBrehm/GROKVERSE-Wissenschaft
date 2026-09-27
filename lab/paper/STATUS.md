---
id: paper-status
status: laufend
datum: 2026-09-27
tags: [lab/paper]
verwandt: ["[[LAB]]", "[[FINDINGS]]", "[[paper/draft]]", "[[paper/related_work]]", "[[paper/robustness_plan]]"]
---
# Preprint: Stand (Regel 19)

Zurück zu [[LAB]] · Kernaussagen: [[FINDINGS]] · Entwurf: [[paper/draft]] · Literatur: [[paper/related_work]] · Robustheit: [[paper/robustness_plan]]

Arbeitstitel: *Training-set composition steers and locks in the Fourier features of grokking transformers* (vorläufig).
Angelegt 2026-09-27, Sitzung 24 (Laborsitzung, vom Runner gestartet), nach Regel 19 der Präambel.

## Offen für den Nutzer (nicht vom Labor zu entscheiden)

1. **Autorschaft und Rechte an der ursprünglichen GROKVERSE-Studie** (RESULTS.md, docs/, training/): Wer sind die Autoren? Darf der Trainingscode der Studie im Reproduktionspaket veröffentlicht werden, unter welcher Lizenz?
2. **Einreichung/Veröffentlichung:** ob, wann und wo (arXiv, Workshop). Das Labor lädt nichts hoch und legt keine Konten an.
3. **Venue** (z. B. ein Workshop zu Mechanistic Interpretability oder Science of Deep Learning): Entscheidung beim Nutzer.
4. **Offenlegung der KI-Nutzung:** Vorschlag im Entwurf (Abschnitt „AI use disclosure“); Wortlaut und Verantwortungsübernahme bestätigt der Nutzer.
5. **Menschliche Prüfung der Literatur** ([[paper/related_work]]) durch den Nutzer oder eine Fachperson, bevor irgendetwas als neu bezeichnet wird.

## Punkte (a–f)

| Punkt | Stand | Nächster Schritt |
|---|---|---|
| a Robustheit (lr, wd, train_frac) | Plan [[paper/robustness_plan]] (Sitzung 24); braucht Trainer-Optionen `--lr`, `--weight-decay`, `--train-frac` (gemeinsamer Trainer → Codex) | Optionen einbauen und prüfen lassen; Registrierung R1 einfrieren; frühestens in der Nacht 28./29.09. rechnen (Nacht 27./28. ist belegt) |
| b Piloten bestätigen (EXP-048, 049, 045) | offen; EXP-075 (MLP-Persistenz) als Pilot für heute Nacht festgelegt | kleinen Bestätigungsblock für K2 an MLP/4× Breite/Integer-Addition registrieren, oder im Paper als Pilot berichten |
| c Reproduktionspaket `lab/paper/repro/` | Ordner angelegt, leer | je Abbildung ein schlankes Skript (Training + Auswertung) mit Smoke-Modus; einmal im Fenster voll laufen lassen |
| d Entwurf `lab/paper/draft.md` | Gerüst mit allen bestätigten Kernaussagen und Zahlen aus FINDINGS_DETAILS (Sitzung 24) | Abbildungen 1–3 fertig (`figures/fig1_mask_vs_learned.py`, `fig2_p1_delta_pow.py`, `fig3_ablation_contrast.py`; aus gespeicherten Läufen bzw. eingefrorenen Zusammenfassungen); Abbildung 4 (π-Pilotkurve) offen; Theorie-Abschnitt; nach P2f (D₅₉) ergänzen |
| e Literatur `lab/paper/related_work.md` | in Arbeit (Sitzung 24, gründliche Suche mit Protokoll) | menschliche Prüfung |
| f Entscheidungen des Nutzers | oben vorgelegt | — |

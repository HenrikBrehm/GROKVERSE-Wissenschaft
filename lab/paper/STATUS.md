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
| a Robustheit (lr, wd, train_frac) | Plan [[paper/robustness_plan]]; Trainer-Optionen `--lr`, `--weight-decay`, `--train-frac` eingebaut, Codex-Blocker behoben, Tests ab 00:00. [[confirm/R1_REGISTRATION_DRAFT|R1]]: Registrierungsentwurf + `confirm_r1.py` (Split-Pipeline mit Anteil als Parameter, ε kalibriert, Codex: 3 Blocker behoben, Nachprüfung ohne Befund), Selbsttest ab 00:00 | Seeds reservieren, Manifest einfrieren (nach Selbsttest), Smoke; frühestens Nacht 28./29.09. rechnen (Nacht 27./28. ist belegt) |
| b Piloten bestätigen (EXP-048, 049, 045) | Registrierungsentwurf [[confirm/P4_REGISTRATION_DRAFT|P4]] (Sitzung 24); EXP-075 (MLP-Persistenz) als Pilot für heute Nacht festgelegt | kleinen Bestätigungsblock für K2 an MLP/4× Breite/Integer-Addition registrieren, oder im Paper als Pilot berichten |
| c Reproduktionspaket `lab/paper/repro/` | [[paper/repro/README|README]]: Umgebung, Zuordnung Abbildung → Block → Befehle, Plan für schlanke Skripte (Sitzung 24) | je Abbildung ein schlankes Skript (Training + Auswertung) mit Smoke-Modus; einmal im Fenster voll laufen lassen |
| d Entwurf `lab/paper/draft.md` | Gerüst mit allen bestätigten Kernaussagen und Zahlen aus FINDINGS_DETAILS (Sitzung 24) | Abbildungen 1–4 fertig (`figures/fig1_mask_vs_learned.py`, `fig2_p1_delta_pow.py`, `fig3_ablation_contrast.py`, `fig4_pi_curve.py`; aus gespeicherten Läufen bzw. eingefrorenen Zusammenfassungen); Abbildung 4 (`fig4_pi_curve.py`) fertig; Theorie-Abschnitt; nach P2f (D₅₉) ergänzen |
| e Literatur [[paper/related_work]] | Entwurf fertig (Sitzung 24): ≈ 50 Arbeiten, 37 Suchbegriffe, Prüfgrad je Eintrag ([A] Abstract, [L] Volltext früher, [K] Klassiker, [S] nur Snippet), Einordnung je Kernaussage. Lücken: Google Scholar/Semantic Scholar nicht direkt abgefragt. Stichprobe LeDoux 2026 selbst am Abstract geprüft (Reihenfolge, nicht Menge) | **menschliche Prüfung**; vorrangig LeDoux (Volltext), Marchetti et al. und He et al. 2026b (Anhänge: nicht-uniforme Paare?), Lyle et al. 2025 (Frequenzanalyse nach Datenwechsel?), Vorwärtszitate |
| f Entscheidungen des Nutzers | oben vorgelegt | — |

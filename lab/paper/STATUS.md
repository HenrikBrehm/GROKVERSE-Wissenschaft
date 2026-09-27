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

## Kurzfassung für den Nutzer (Stand 2026-09-27, Sitzung 24)

**Was das Paper heute tragen würde (alle an frischen, vorab reservierten Seeds bestätigt):** (1) Welche Fourier-Frequenzen ein grokkender Transformer lernt, lässt sich allein über die Auswahl der
Trainingspaare steuern, bei drei modularen Aufgaben und der nicht-abelschen Gruppe D₅₉. (2) Das Netz reagiert empfindlicher auf Störungen entlang dieser Frequenzen (mit der Einschränkung, dass das der
Energie folgt). (3) Die Wahl legt sich nach 25–50 Trainingsschritten fest: nach einem Datenwechsel bei 50 Schritten hängt das fertige Netz an den alten Frequenzen, bei 25 an den neuen. (4) Ein Reset der
Attention, vor allem ihres Wertepfads, hebt dieses Festhalten auf, ein MLP-Reset kaum.

**Was vor einer Einreichung fehlt:** Robustheit gegen Lernrate/Weight Decay/Trainingsanteil (R1, vorbereitet); Bestätigung der Piloten zu MLP, Breite, Integer-Addition (P4, Entwurf); D₅₉-Funktion (P2f,
läuft ab 00:00); Persistenz außerhalb von add 113 (EXP-074/075 als Piloten ab 00:00); menschliche Prüfung der Literatur (engste Arbeiten: LeDoux 2026, Marchetti et al. 2026, Lyle et al. 2025);
ein schlankes Reproduktionspaket; deine Entscheidungen unten.

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
| d Entwurf `lab/paper/draft.md` | Gerüst mit allen bestätigten Kernaussagen und Zahlen aus FINDINGS_DETAILS (Sitzung 24) | Abbildungen 1–5 fertig (`figures/fig1_mask_vs_learned.py`, `fig2_p1_delta_pow.py`, `fig3_ablation_contrast.py`, `fig4_pi_curve.py`, `fig5_margin_sensitivity.py`; aus gespeicherten Läufen bzw. eingefrorenen Zusammenfassungen); Abbildung 4 (`fig4_pi_curve.py`) fertig; Theorie-Abschnitt; nach P2f (D₅₉) ergänzen | Zahlenprüfung (Sitzung 24): alle Zahlen korrekt, 15 Formulierungen enger gefasst.
| e Literatur [[paper/related_work]] | Entwurf fertig (Sitzung 24): ≈ 50 Arbeiten, 37 Suchbegriffe, Prüfgrad je Eintrag ([A] Abstract, [L] Volltext früher, [K] Klassiker, [S] nur Snippet), Einordnung je Kernaussage. Lücken: Google Scholar/Semantic Scholar nicht direkt abgefragt. Stichprobe LeDoux 2026 selbst am Abstract geprüft (Reihenfolge, nicht Menge) | **menschliche Prüfung**; vorrangig LeDoux (Volltext), Marchetti et al. und He et al. 2026b (Anhänge: nicht-uniforme Paare?), Lyle et al. 2025 (Frequenzanalyse nach Datenwechsel?), Vorwärtszitate |
| f Entscheidungen des Nutzers | oben vorgelegt | — |

## Nachtrag Sitzung 25 (2026-09-27, 14:36)

- **a/b:** `lab/tools/confirm_p4.py` geschrieben, Codex (1 Blocker: Testangabe, behoben), ungetestet bis 00:00; Seeds 2360–2419 (P4), 2420–2509 (R1) reserviert.
- **c:** schlanker Trainer `lab/paper/repro/train.py` mit Vergleich gegen gespeicherte Läufe; Prüfbefehle in [[paper/repro/README]] (ab 00:00).
- **d:** Theorie §5 ausformuliert (numerisch geprüft; dabei eine falsche Aussage zu Token-Häufigkeiten gefunden und korrigiert).
- **e:** Volltextprüfung [[paper/fulltext_check_2026-09-27]]: **K4d eingeschränkt** durch Dong 2026 (Sprachmodelle: QK-Reset hilft, Value nicht; bei uns umgekehrt), Khanh 2026 Pflichtzitat.
  Für die menschliche Prüfung vorrangig: Dong 2026 und Khanh 2026 im Volltext.

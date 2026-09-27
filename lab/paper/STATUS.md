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

**Nachtrag zur Kurzfassung (Sitzung 26):** Zu (1) gibt es einen engen Vorläufer auf der Kernel-Seite: Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316) zeigen, dass eine absichtlich symmetrische Trainingsmenge bestimmt, welche Gruppenstruktur ein Feature-Learning-Kernel lernt. Unser Beitrag ist damit enger zu formulieren: Auswahl *vorgegebener Fourier-Frequenzen* in *Transformern* über das Spektrum einer Paarmaske ohne eingebaute Symmetrie. Vor jeder Einreichung bitte diese Arbeit selbst lesen. Zu (3)/(4) fand die Suche nach zitierenden Arbeiten (Semantic Scholar, bis 2026-09-23) nichts Einschränkendes.

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

## Nachtrag Sitzung 26 (2026-09-27, vor 15:22, gemessen)

- **a:** Registrierungsentwurf [[confirm/R2_REGISTRATION_DRAFT|R2]] (K4c bei lr 2e-3 und wd 0.3, n = 30, Seeds 2510–2539) und `confirm_r2.py` (ungetestet bis 00:00; Codex-Prüfung Sitzung 26).
- **e:** Vorwärtszitate über die Semantic-Scholar-API gesichtet (9 Ausgangsarbeiten): nichts schränkt K2/K4 ein; neu zu zitieren v. a. Tomàs Bernal et al. 2026 (Kernel-Vorläufer zu K2) und Jia 2026 (Komponentenrollen, gleiche Modellfamilie). Nachtrag in [[paper/related_work]].
- **a/b (15:40):** [[confirm/R3_REGISTRATION_DRAFT|R3]] (Λ- gegen Schrittuhr der Festlegung, 80 Läufe) und Pilot [[experiments/EXP-078-two-layer-steering/README|EXP-078]] (K2 mit zwei Schichten) vorbereitet; §3.7 im Entwurf listet alle ausstehenden Robustheitsblöcke.
- **c/d (15:40):** `repro/k4c.py` (geprüft, keine Blocker); Einleitung als Fließtext, unabhängig gegen die Quellen geprüft (13 Korrekturen).
- **e (Korrektur, Sitzung 26):** Tomàs Bernal et al. 2026 (arXiv 2604.00316) schränkt K2 **teilweise** ein (Kernel: symmetrische Trainingsmengen wählen die kodierte Untergruppe). Für die menschliche Prüfung neu vorrangig: diese Arbeit im PDF lesen.

## Nachtrag Sitzung 27 (2026-09-27, bis 16:20, gemessen)

- **d:** §2 (Methoden) als Fließtext, unabhängig gegen den Code geprüft (9 Korrekturen). §3.3 um die Größenabschätzung von K4b ergänzt (Momentum-Schwanz, post hoc) und die Vorarbeiten zitiert.
- **e:** Volltext/Abstract nachgeprüft: Salah & Yevick 2024 (schränkt K2 nicht ein, im Paper zitiert), Sweeney 2026, Pracher et al. 2026, Yang 2026, Xu 2026, Sevetlidis & Pavlidis 2026. **Die Deutung von K4b (erstes Moment trägt die frühe Exposition) ist bekannt**; K2 und K4/K4c bleiben nach unserer Suche nicht gefunden.
- **c:** neue Repro-Skripte `repro/k4_resets.py` (K4d/K4e) und `repro/k4b.py` (K4/K4b), je unabhängig gegen die eingefrorenen Auswertungen gelesen; ungetestet. Fehlt noch: K2-Funktion (P2d/P2e).
- **a/c:** Nachtbefehle statisch geprüft; zwei Befehlsfehler und vier kleinere Punkte vor der Nacht behoben (Details im JOURNAL).

## Nachtrag Sitzung 28 (2026-09-27, ab 16:49, gemessen)

- **d:** §3.1 um absolute Anteile ergänzt (add 113: 80 % der W_E-Energie auf den 5 Zielen, Init 8.9 %); §4 und §5.3: Das Paarspektrum ordnet auch die Ziele innerhalb der Menge (Exploration, alle Aufgaben, Breite, MLP), aber nicht architekturspezifisch wie in Vorhersage 2 hergeleitet.
- **a/b:** Drei kleine Zusatzregistrierungen auf noch nicht gelaufenen Blöcken, ohne zusätzliches Training: [[confirm/C1_REGISTRATION|C1]] (an R1), [[confirm/C2_REGISTRATION|C2]] (an R2, feine Persistenz nach dem Wechsel), [[confirm/C3_REGISTRATION|C3]] (an P4), [[confirm/C4_REGISTRATION|C4]] (an P2f, D₅₉ bei 12 000 Schritten). Alle Codex-geprüft; Auswertungen ungetestet. Pilot [[experiments/EXP-082-graded-targets/README|EXP-082]] (Eingriff: vorgegebene Zielstärken) vorbereitet.
- **e:** Suche zu N39 ohne einschränkenden Treffer; Abgrenzung zu He et al. 2026a in [[paper/related_work]].

## Nachtrag Sitzung 29 (2026-09-27, ab 17:59, gemessen)

- **e:** Lücke „Google Scholar nicht direkt abgefragt“ teilweise geschlossen: vier Scholar-Abfragen (Nachtrag in [[paper/related_work]]); nichts Einschränkendes zu K2/K4. **Neu für die menschliche Prüfung:** Stevinson & Prieto 2026 (ICML-Workshop, Angriffe konzentrieren sich auf genutzte Fourier-Merkmale): Kontext für K2-Funktion, Volltext nicht zugänglich (OpenReview-Anmeldung). Init-Skala/Festlegungszeit (für EXP-040): Khanh et al. 2026 (2606.13753) als Kontext, nichts Einschränkendes.
- **a (Vorbereitung EXP-040):** H40 an gesehenen EXP-039-Läufen vorgeprüft (Festlegung bei ≈ 1/3–2/3 der Init-Amplitude; Lesehinweis in [[LESART-nacht-2026-09-28]]).

## Nachtrag Sitzung 30 (2026-09-27, ab 18:19, gemessen)

- **d:** Gutachter-Durchgang (unabhängiger Prüfagent, danach selbst an den Dateien geprüft): 10 Textkorrekturen im [[paper/draft]] (Abstract enger: konstruierte Splits, D₅₉ vor dem Grokking, eine Optimierer-Einstellung; fehlende Armmittel und Werte nur über generalisierte Seeds in §3.4/§3.5 aus den eingefrorenen Analysen; LeDoux-Abgrenzung; Grenzen). Keine Zahl geändert. Offen und bewusst verschoben: Strukturumbau (Gliederungen löschen, Lab-IDs in einen Anhang, Schluss und Literaturliste), sobald die Nachtergebnisse feststehen.
- **a:** Gegen den Einwand „der Attention-Reset nimmt nur mehr Bewegung zurück“: [[experiments/EXP-083-reset-displacement/README|EXP-083]] vorbereitet (Exploration, ≈ 5 min GPU heute Nacht).
- **a (18:56):** [[confirm/R4_REGISTRATION_DRAFT|R4]] entworfen und zweimal von Codex geprüft (1 Blocker, 5 Major, alle eingearbeitet): gekreuzt Init × Zufallssplit, 60 Einheiten, 240 GPU-Läufe ≈ 1.6 h; H1a Spearman bei 2000, H1b Kosinus bei 8000. Selbsttest im Fenster, dann einfrieren; rechnen frühestens in der Nacht 28./29.
- **Für dich, Gutachtersicht:** Der stärkste verbleibende Einwand ist der Rahmen: Wir zeigen Steuerung durch *konstruierte* Splits, nicht, dass gewöhnliche Zufallssplits die Frequenzwahl entscheiden (Pilot EXP-014 heute Nacht).
- **d/e (19:07):** Literaturliste [[paper/references]] (35 Zitate, aus related_work erzeugt) und Venue-Abgleich [[paper/references_venues_check]] (arXiv-Seiten). Abbildung 0 (Aufbau) `figures/fig0_setup.py`. Unabhängige Quellenprüfung aller heutigen Entwurfsänderungen: 4 Fehler gefunden und korrigiert. **Für dich:** Namensform „Tomàs Bernal“ vs. arXiv „Bernal, Marcel Tomàs“ und „Gharda“ Sokar (Lyle et al. 2025) bitte selbst entscheiden.

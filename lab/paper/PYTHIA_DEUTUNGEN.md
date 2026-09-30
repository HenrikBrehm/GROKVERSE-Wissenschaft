---
id: PYTHIA_DEUTUNGEN
datum: 2026-09-30
tags: [lab/paper]
---
# Pythia-Reihe (EXP-127, EXP-130, EXP-133): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[LAB]] · [[experiments/EXP-127-pretrained-lm/README|EXP-127]] · [[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]] · [[experiments/EXP-133-pythia-reset-numbers/README|EXP-133]]

**Geschrieben in Sitzung 62 (30.09., 19:12 Berlin gemessen), bevor ein EXP-130-Ergebnis ausgewertet und bevor ein EXP-133-Lauf gestartet war.** Bekannt war nur EXP-127 („bricht“, Pilot). Alles hier ist Exploration (2 Seeds je Versuch), gehört höchstens in Anhang K („Towards language models“) und einen Halbsatz in die Grenzen (ii); **keine neue Kernaussage**, kein Abstract (Regel 20 e2: „erst nach Bestätigung mehr“). Zahlen werden nach der Auswertung eingesetzt und unabhängig geprüft.

## Grundsatz (fest, unabhängig vom Ausgang)

*Fine-tuning a pretrained model (exploration, two seeds each).* When Pythia-160M (Biderman et al. 2023) was fine-tuned on the same engineered fact splits (addition mod 113, neutral operator, 4000 steps; held-out accuracy 0.97–0.99), the fact selection did not steer the change of the number-token input embedding (Δ_pow of the residual change +0.13 and −0.17; pre-set threshold 1). **The steering result of the main text is therefore a from-scratch result; we did not find it when fine-tuning this pretrained model.**

## EXP-130 (welche Frequenzen braucht das nachtrainierte Modell?)

- **„Wiederverwendung“:** *Single-frequency ablations on two fresh splits showed that the fine-tuned model relies mainly on frequencies that were already strong in the pretrained number embeddings (≥ 3 of the 5 most important input frequencies in ≥ 3 of 4 models), not on the split's targets; this is consistent with the reuse of pretrained number features reported by Zhou et al. (2024), here for a modulus that is not aligned with the decimal periods.*
- **„Datenwahl“:** *Single-frequency ablations nevertheless showed that the fine-tuned models rely on their own split's target frequencies (≥ 3 of the top 5 in ≥ 3 of 4 models), so the fact selection shaped what the model uses even though the embedding change did not concentrate on the targets.* (Dann Widerspruch zu EXP-127 offen benennen: Nutzung ohne Energie-Steuerung.)
- **„gemischt“:** *… relied on both pretrained frequencies and its own targets (at least two of each among the top 5 in ≥ 3 of 4 models).*
- **„unklar“ / „nicht auswertbar“:** kein Satz im Paper außer „single-frequency ablations were inconclusive“.

## EXP-133 (Zahlzeilen neu, Rumpf vortrainiert)

- **„gesteuert (neue Zahlzeilen)“:** *When only the number-specific part of the number-token rows was re-initialised (mean row kept) and the rest of the model stayed pretrained, the fact selection steered the embedding change again (Δ_pow … and …). In this pilot, the pretrained number rows, not the pretrained body, prevented the steering.*
- **„nicht gesteuert (Rumpf)“:** *Re-initialising the number-specific part of the number-token rows did not restore the steering (Δ_pow … and …) [falls zutreffend: the change again concentrated on …]; in this pilot, the pretrained body rather than the pretrained number rows determined which frequencies the embeddings acquired.*
- **„unklar“:** *… gave mixed results (Δ_pow … and …).* **„nicht auswertbar“:** *With re-initialised number rows the model did not learn the task within 4000 steps.*

## Grenze (ii), Halbsatz (bei jedem Ausgang)

„… and it was not found when fine-tuning a pretrained 160 M-parameter model (two-seed pilot; Appendix K).“

**Beim Einsetzen:** Literatureintrag Biderman et al. 2023 (Pythia) fehlt in [[paper/references]] → ergänzen und Titel/Autoren/ID am arXiv-Abstract prüfen (nicht aus dem Gedächtnis).

**Literatureintrag, geprüft (Sitzung 62, arXiv-Abstract 2304.01373 abgerufen):** `- Biderman, Schoelkopf, Anthony, Bradley, O'Brien, Hallahan, Khan, Purohit, Prashanth, Raff, Skowron, Sutawika, van der Wal (2023). *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling*. arXiv:2304.01373. https://arxiv.org/abs/2304.01373. [A]` – die arXiv-Seite nennt keine Venue (Kommentarfeld nur Code-Link); keine Venue aus dem Gedächtnis ergänzen. Erst mit dem Absatz in [[paper/references]] eintragen (sonst unzitierter Eintrag).

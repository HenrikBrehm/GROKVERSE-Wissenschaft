---
id: EXP134_135_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# EXP-134 (Text-Vortraining des Rumpfs) und EXP-135 (Faktenwechsel im LM): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[LAB]] · [[experiments/EXP-134-text-pretrain-steering/README|EXP-134]] · [[experiments/EXP-135-lm-switch-lockin/README|EXP-135]] · Vorlagen [[paper/EXP125_DEUTUNGEN]], [[paper/PYTHIA_DEUTUNGEN]]

**Geschrieben in Sitzung 64 (01.10., 00:12 Berlin gemessen), bevor ein Lauf der beiden Piloten gestartet war** (beide warten beim Dienst hinter L0b und EXP-125). Beide sind **Explorationen mit 2 Seeds**: höchstens je ein Satz in Anhang K (Manuskript: Appendix J, Sprachmodelle), keine neue Kernaussage, nichts im Abstract.

## EXP-134: Satz in Anhang K (nach dem Pythia-Absatz), je Lesart

- **„K2 haelt im LM“:** *To separate a pretrained body from pretrained number features, we first trained the LM1 model for 6000 steps on text alone (the number tokens never occur in the text) and then on the LM1 facts; the fact selection still steered the tied number embeddings (Δ_pow … and …; two seeds, exploration), so a text-pretrained body of this size did not by itself remove the steering. The Pythia result may therefore reflect its pretrained number features, its size or its far longer pretraining; these are not separated.*
- **„bricht“:** *… the models learned the facts (held-out accuracy …–…) but the fact selection no longer steered the number embeddings (Δ_pow … and …; pre-set threshold 1). In this pilot, 6000 steps of text pretraining of the body sufficed to suppress the steering even though the number rows had never been trained on numbers.*
- **„nur Repraesentation“:** *… the fact selection steered the number embeddings (Δ_pow … and …), but the models did not generalize to held-out facts within 6000 steps (…–…).*
- **„unklar“:** *… gave mixed results (Δ_pow … and …; held-out accuracy …–…).*
- **„nicht gelernt (Budget)“:** *… the text-pretrained models did not learn the facts within 6000 steps (training accuracy …), so this pilot says nothing about steering after pretraining.*

## EXP-135: Satz in Anhang K (nach dem LM1/LM3-Absatz), je Lesart

- **„Festlegung mit dem Lernen“:** *In the language model the early lock-in of Section 3.4 did not appear at a fixed early step: after a switch from facts F to disjoint facts G at step 250 or 1000 the final number embeddings followed G (persistence π … ; 0 = as G only, 1 = as F only), after a switch at step 3000, when the F steering had already emerged, they kept F (π …; two seeds, exploration). Here the choice was fixed when the facts were learned, not within the first steps.*
- **„Festlegung vor dem Lernen“:** *… a switch at step 1000, before the steering was visible in the embedding energy (held-out accuracy still near chance), already left the final embeddings on F (π … and …), as a transfer of the minibatch lock-in law (Section 6) predicts (half lock-in ≈ 340 steps); the early commitment therefore precedes its visible effect in the language model as well.*
- **„keine Festlegung“:** *… after every switch, even at step 3000 when the F steering had emerged, the final embeddings followed G (π …), so this language model did not lock in within a 6000-step post-switch budget; lock-in is a limit of the toy setting in this pilot.*
- **„unklar“:** *… gave mixed persistence values (π …).*
- **„nicht auswertbar (lernt G nicht)“:** *… the models did not learn the second fact set (held-out accuracy …), so the pilot is not evaluable.*

## Was ausdrücklich nicht gesagt wird

- keine Aussage über große vortrainierte Modelle aus EXP-134 (6000 Schritte Text sind weit weg von Pythia; Größe, Daten, Dauer nicht getrennt);
- in EXP-135 kein „kritische Periode“ im neurowissenschaftlichen Sinn, keine Schrittzahl als allgemeine Grenze (eine Konfiguration, 2 Seeds); der Übertrag des Spielzeuggesetzes ist eine Rechnung mit Vorbehalten (anderes Maß, andere Architektur, Fakten je Schritt als B);
- Abschnittsnummern („Section 3.4“, „Section 6“) beim Einsetzen gegen das Manuskript prüfen (Kurz- und Langfassung nummerieren verschieden);
- π > 1 bei t = 3000 ist möglich (die F-Neigung der LM1-Referenz fällt von 3000 bis 6000) und heißt nicht „stärker als F“.

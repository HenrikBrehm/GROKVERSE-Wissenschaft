---
id: lit-grokking-speed
status: entwurf
datum: 2026-09-27
tags: [lab/paper, neu/kandidat]
---
# Literaturrecherche: Beschleunigt die Zusammensetzung des Trainingssatzes (bei fester Größe) Grokking?

Fragestellung: Gibt es Arbeiten, die zeigen, dass die *Auswahl* der Trainingspaare (bei fester Trainingsmenge) Grokking auf modularer Arithmetik / Gruppenoperationen stark beschleunigt, insbesondere durch Paare, deren Struktur auf wenige Fourier-Frequenzen konzentriert ist? Eigene Beobachtung: 1-Layer-Transformer, (a+b) mod 113, 30 % der Paare, Full-Batch AdamW; Gewichtung 1 + 2*mean_k cos(2πk·a/p + φ_k(c)) über 5 Zielfrequenzen -> Generalisierung nach ca. 700 Schritten vs. ca. 6000 (bzw. nicht innerhalb 2150) bei uniformem Split gleicher Größe, gemeinsamer Test-Satz.

Methode: WebSearch + WebFetch (arXiv-Abstracts/HTML). "Gelesen" bedeutet unten: A = nur Abstract gelesen, H = Volltext-HTML (teilweise, per Abfrage) gelesen, S = nur Suchsnippet.

## Suchanfragen (alle am 2026-09-27)

1. grokking data selection training set composition modular arithmetic accelerate
2. grokking curriculum learning modular arithmetic faster generalization
3. data pruning grokking which training examples speed
4. grokking non-uniform sampling training data distribution modular addition Fourier frequencies
5. "Grokking Explained: A Statistical Phenomenon" distribution shift training test
6. "Controlling Grokking with Nonlinearity and Data Symmetry" 2411.05353
7. grokking modular addition training set structure "which pairs" subset selection faster grokking
8. importance sampling grokking data efficiency coreset algorithmic tasks
9. data augmentation commutativity grokking modular arithmetic faster
10. Omnigrok data size grokking representation modular addition training fraction
11. Structure-Specific Representational Priors Causally Control the Grokking Delay
12. grokking modular arithmetic training data spectrum "Fourier" training mask sampled pairs generalization speed theory
13. structured training data faster generalization algorithmic tasks grokking data selection informative examples 2025
14. "Critical data size" grokking data efficiency modular addition subset
15. grokking "training distribution" biased sampling residues modular addition accelerate delay
16. active learning or data selection strategy reduces grokking delay modular addition training pairs chosen
17. grokking sample complexity modular addition kernel theory "Why do you grok" training set
18. "Guiding Grokking" curriculum learning shapes algorithmic understanding
19. grokking train/test split design "Fourier" frequency-weighted sampling training pairs modular addition speedup
20. grokking "data composition" OR "dataset composition" accelerates generalization modular arithmetic transformer
21. group operations learning training subset chosen by representation theory characters faster generalization neural network grokking

## Gefundene Arbeiten

Kategorie: (a) zeigt unsere Beobachtung bereits, (b) teilweise Überschneidung, (c) sagt das Gegenteil voraus, (d) nur Kontext.

| # | Titel | Autoren | Jahr | Link | Was gezeigt wird (Quelle) | Kat. |
|---|---|---|---|---|---|---|
| 1 | Mechanistic Insights into Grokking from the Embedding Layer | AlQuabeh, Bojkovic, Nwadike, Inui | 2025 | arXiv:2505.15624 | Embeddings treiben Grokking; schlagen "frequency-aware sampling" vor. "Frequency" = Token-Häufigkeit (nicht Fourier). Bei fester Trainingsgröße (30 %) beschleunigt ein token-balancierter ("uniform") Split die Generalisierung gegenüber zufälligem Split; Minibatch, Effekt schwindet bei Batch >= 512 (H) | b |
| 2 | A rationale from frequency perspective for grokking in training neural network | Zhou, Zhang, Xu | 2024 | arXiv:2405.17479 | Netze lernen zuerst weniger saliente/spurious Niederfrequenzkomponenten des Trainingsspektrums; "when maintaining the data size but uniformly sampling the data, the grokking phenomenon disappears". Aufgaben: 1D-Regression, Parität, MNIST, keine modulare Addition (H) | c (für Nicht-Uniformität allgemein; keine Aussage zu modularer Addition) |
| 3 | Grokking Explained: A Statistical Phenomenon | Carvalho, d'Avila Garcez, Lamb, Vital Brazil | 2025 | arXiv:2502.01774 | Grokking als Verteilungsverschiebung Train/Test; durch unausgewogenes Unterabtasten von Subklassen reproduzierbar. Synthetische Datensätze + MNIST, keine modulare Arithmetik; kein Vergleich "Auswahl beschleunigt" (H) | c/d (Nicht-Uniformität induziert Grokking) |
| 4 | Acceleration of Grokking in Learning Arithmetic Operations via Kolmogorov-Arnold Representation | Park, Kim, Kim | 2024 | arXiv:2405.16658 | Datenaugmentation für kommutative Operationen (ca. 2x schneller laut Snippet) und Transfer (ca. 5x) beschleunigen Grokking (A, S) | b (verändert Trainingsdaten, aber Augmentation, nicht Auswahl bei fester Größe) |
| 5 | The AI Scientist (enthält KI-generiertes Paper zu Augmentation bei Grokking) | Lu et al. (Sakana) | 2024 | arXiv:2408.06292 | Snippet: Operand-Reversal/Negation-Augmentation, Addition 2363 -> 920 Schritte bis 99 % Val. (S; KI-generiertes Beispielpaper, nicht begutachtet) | b/d |
| 6 | Guiding Grokking: How Curriculum Learning Shapes Algorithmic Understanding in Neural Networks | (IEEE, Autoren nicht geprüft) | 2025 | IEEE Xplore doc 11009497 | Curricula (linear, exponentiell, stufenweise, graduell) auf modularer Arithmetik; nur Addition profitiert deutlich (S) | b (Reihenfolge der Daten, nicht Frequenz-Auswahl) |
| 7 | Structure-Specific Representational Priors Causally Control the Grokking Delay | (nicht geprüft) | 2026 | arXiv:2607.04333 | Kontrastiver Hilfsverlust mit wahrer Struktur (a+b mod p) beschleunigt Grokking bis 2.75x; falsche/zufällige Struktur nicht (S) | b (strukturausgerichtete Information beschleunigt, aber über Verlust, nicht Datenauswahl) |
| 8 | What Makes a Representational Prior Work? Feature Families, Label-Free Invariances, and Critical Windows in Grokking | Howe | 2026 | arXiv:2607.12735 | Priors müssen zur Feature-Familie der Aufgabe passen; label-freier Kommutativitäts-Prior; frühes Einbringen am wirksamsten (A) | b/d |
| 9 | Critical Data Size of Language Models from a Grokking Perspective | Zhu et al. | 2024 | arXiv:2401.10463 | Kritische Datenmenge Memorieren -> Generalisieren; nutzen bewusst *uniformes* Pruning (S) | d |
| 10 | Omnigrok: Grokking Beyond Algorithmic Data | Liu, Michaud, Tegmark | 2023 | arXiv:2210.01117 | LU-Mechanismus; Trainingsanteil bestimmt Grokking-Geschwindigkeit (S) | d |
| 11 | Towards Understanding Grokking: An Effective Theory of Representation Learning | Liu, Kitouni, Nolte, Michaud, Tegmark, Williams | 2022 | arXiv:2205.10343 | Strukturierte Repräsentationen, Phasendiagramm (A). Die Volltext-Analyse, die Generalisierung an Parallelogramme im Trainingssatz knüpft, wurde in dieser Suche NICHT erneut geprüft | d (möglicherweise b; ungeprüft) |
| 12 | Why Do You Grok? A Theoretical Analysis of Grokking Modular Addition | Mohamadi et al. | 2024 | arXiv:2407.12332 (ICML) | Im Kernel-Regime braucht jedes permutationsäquivariante Modell einen konstanten Anteil aller Daten; Feature-Lernen erlaubt weniger (S) | d |
| 13 | Controlling Grokking with Nonlinearity and Data Symmetry | Salah, Yevick | 2024 | arXiv:2411.05353 | Grokking über Aktivierungsprofil, Tiefe, Breite steuerbar; PCA-Muster der Gewichte (S/A) | d |
| 14 | Progress measures for grokking via mechanistic interpretability | Nanda et al. | 2023 | arXiv:2301.05217 | Fourier-Algorithmus mit wenigen Schlüsselfrequenzen; Standard-Setup p=113, 30 % (S) | d |
| 15 | On the Mechanism and Dynamics of Modular Addition: Fourier Features, Lottery Ticket, and Grokking | (nicht geprüft) | 2026 | arXiv:2602.16849 | Frequenzwettbewerb in Neuronen; Weight Decay beschneidet Nicht-Feature-Frequenzen (S) | d |
| 16 | Grokking modular arithmetic | Gromov | 2023 | arXiv:2301.02679 | Analytische Lösung (S) | d |
| 17 | Learning to grok: in-context learning and skill composition in modular arithmetic | He et al. | 2024 | arXiv:2406.02550 | Anzahl der Aufgaben steuert Generalisierung (S) | d |
| 18 | Provable Scaling Laws of Feature Emergence from Learning Dynamics of Grokking | Tian | 2025 | arXiv:2509.21519 | Theorie: Grokking-Schritte fallen mit Datenmenge (S) | d |
| 19 | Exploring Grokking: Experimental and Mechanistic Investigations | Hu, Zhou, Yu | 2024 | arXiv:2412.10898 | Experimente zu Trainingsanteil, Modell, Optimierung (A) | d |
| 20 | Grokfast / NeuralGrok / Muon | Lee et al.; (weitere Autoren nicht geprüft) | 2024-2025 | arXiv:2405.20233, 2504.17243, 2504.16041 | Beschleunigung über Optimierer/Gradienten, nicht über Daten (S) | d |

## Fazit (vorläufig)

Nach unserer Suche vom 2026-09-27 (21 Anfragen, Abstracts und teilweise Volltext-HTML, keine systematische Zitationsverfolgung) wurde **keine** Arbeit gefunden, die zeigt, dass eine nach wenigen Fourier-Frequenzen gewichtete Auswahl der Trainingspaare bei fester Trainingsgröße Grokking auf modularer Addition stark beschleunigt. Am nächsten kommt AlQuabeh et al. 2025 (arXiv:2505.15624): Dort beschleunigt bei fester Größe (30 %) ein nach *Token-Häufigkeit* balancierter Split die Generalisierung gegenüber einem zufälligen Split, also ist "Zusammensetzung bei fester Größe beeinflusst die Geschwindigkeit" bereits gezeigt, allerdings mit Balancierung statt Fourier-Konzentration, mit Minibatches und mit anderer Richtung der Nicht-Uniformität. Datenaugmentation (Park et al. 2024), Curricula (IEEE 2025) und strukturausgerichtete Hilfsverluste (arXiv:2607.04333, 2607.12735) beschleunigen Grokking ebenfalls über "aufgabenausgerichtete" Information, aber nicht über die Auswahl der Paare. Zhou/Zhang/Xu 2024 und Carvalho et al. 2025 verknüpfen nicht-uniforme Stichproben mit dem *Entstehen* bzw. Verstärken von Grokking (spurious Frequenzen, Verteilungsverschiebung); das steht in Spannung zu unserer Beobachtung, betrifft aber nicht modulare Addition. Dies ist ausdrücklich kein Neuheitsnachweis: nicht gefunden heißt nicht nicht vorhanden (Workshop-Paper, Blogposts, LessWrong und nicht indizierte Arbeiten wurden kaum abgedeckt; Arbeit 11 wurde nicht im Volltext geprüft).

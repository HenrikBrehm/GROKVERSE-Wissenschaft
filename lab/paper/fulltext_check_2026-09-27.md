---
id: fulltext-check
status: entwurf
datum: 2026-09-27
tags: [lab/paper, lab/literatur]
verwandt: ["[[paper/related_work]]", "[[paper/draft]]", "[[FINDINGS]]"]
---
# Volltextprüfung der nächstverwandten Arbeiten (2026-09-27)

**Zweck.** Prüfpunkte 1–3 und 5 aus [[paper/related_work]] §9 („Offene Prüfpunkte“) abarbeiten: Enthalten die nächstverwandten Arbeiten schon
- **(a)** eine Steuerung der gelernten Frequenzen/Irreps über die **Zusammensetzung der Trainingsmenge** (welche Paare, nicht Reihenfolge, nicht Eingabekodierung),
- **(b)** eine frühe **Festlegung/Persistenz** der gelernten Frequenzen nach einem **Datenwechsel**,
- **(c)** **Teil-Resets** (Attention vs. MLP), die in diesem Setting Plastizität wiederherstellen?

**Status.** Zusammengestellt von einem KI-Agenten am 2026-09-27, **Grundlage für eine menschliche Prüfung**. Urteile: „enthält“ / „teilweise“ / „nicht gefunden“. „Nicht gefunden“ heißt: im gelesenen Text nicht gefunden, nicht „sicher nicht vorhanden“.

## 0. Methode und Grenzen

- **Volltextzugriff:** arXiv-HTML-Fassung (`https://arxiv.org/html/<id>`, jeweils neueste Version) per `curl` geladen, lokal in Text umgewandelt und abschnittsweise gelesen bzw. nach Schlüsselwörtern durchsucht (u. a. subset, training set, uniform, split, switch, reset, attention, frequenc). Ergänzend WebFetch für LeDoux.
- **Grenze 1:** Bei der Umwandlung gingen **Formeln verloren** (MathML entfernt). Prosa, Abschnittstitel, Bildunterschriften und Anhänge waren lesbar; Aussagen, die nur in Formeln stehen, wurden nicht geprüft. **Abbildungen wurden nicht angesehen.** PDFs wurden nicht separat gelesen (die HTML-Fassungen enthielten die Anhänge).
- **Grenze 2:** Beweise in den Anhängen (He et al. 2026a/b, Marchetti et al., Tian) nur überflogen, nicht nachvollzogen.
- **Vorwärtszitate:** Semantic-Scholar-API, Endpunkt `citations`, für LeDoux, He 2026a, He 2026b, Marchetti et al., Lyle et al. 2025 und Nanda et al. 2023 (für Nanda lieferte die API **991 Einträge**; ob das alle sind, ist unklar). Die Semantic-Scholar-**Suche** war nicht nutzbar (HTTP 429, dreimal). Stattdessen arXiv-API-Suche (5 Suchstrings, u. a. `abs:grokking AND abs:frequencies`, `abs:grokking AND (abs:reset OR abs:reinitialization OR abs:plasticity)`) und 3 WebSearch-Anfragen.
- **Verifikation der IDs:** Alle unten genannten arXiv-IDs wurden per arXiv-API (Titel, Autoren, Datum) und per Abruf der HTML-Fassung geprüft.

---

## 1. LeDoux (2026), *The Order Is The Message*

- **Link:** https://arxiv.org/abs/2603.25047 (v1, 2026-03-24; Jordan LeDoux, unabhängiger Forscher; 51 Seiten)
- **Gelesen:** Abstract, §1–§7 vollständig (u. a. §3.4 „Basin Selection and the Critical Learning Period“, §4.1.2 Setup, §5.1–5.4, §6.6 „Reinterpreting Grokking“ inkl. „Full-batch gradient descent as a limiting case“, §6.8), Anhang A und B (Überschriften und Prosa).
- **Setup:** Addition mod p = 9973; 2-Schicht-Pre-LN-Transformer; **Minibatch 256**; 300 000 Trainingspaare (≈ 0,3 %); vier Reihenfolge-Strategien (Stride, Fixed-Random, Random, Target).

**(a) Mengenzusammensetzung → Frequenz: nicht gefunden.** Variiert wird ausschließlich die Reihenfolge bei fester Menge:
> „All four models share the same architecture, parameter initialization (via a shared random seed), training set, optimizer, hyperparameters, and compute budget. The only variable is the ordering of training examples within each epoch.“ (§4.1.2)

Wichtiger Zusatzbefund: Zufällig gezogene Teilmengen ändern die Frequenz dort **nicht**:
> „Notably, F=101 emerged as the peak embedding frequency on every seed tested […] despite each seed selecting a different random subset of 300,000 training pairs.“ (§4.2.3)
> „The frequency is not an artifact of a particular initialization geometry or dataset composition; it is a deterministic consequence of the stride ordering's structure“ (§5.3)

Das ist kein Widerspruch zu K2: LeDoux prüft nur **zufällige** Teilmengen unter einer dominanten Stride-Reihenfolge, wir **konstruierte** Masken unter Full-Batch. Zum Full-Batch-Fall sagt LeDoux selbst, der Reihenfolgekanal sei dort „degeneriert“:
> „The mechanism is not absent in full-batch training; it is degenerate, collapsing the combinatorial richness of inter-batch interactions into a single, fixed self-interaction that repeats identically at each step.“ (§6.6)

**(b) Frühe Festlegung nach Datenwechsel: teilweise (nur konzeptuell).** LeDoux führt eine „kritische Lernperiode“ je Feature ein und datiert sie sehr früh, testet sie aber **nicht** durch einen Wechsel:
> „the Stride model identifies the fundamental frequency F=101 within the first 3 epochs, and by epoch 30 the spectral structure of the eventual solution is already visible.“ (§3.4)
> „The fundamental frequency is identifiable by epoch 3 and crosses the significance threshold by epoch 14 (Section 5.1.2), placing the critical learning period squarely within the first few dozen epochs“ (§6.2)

Die Reihenfolgen sind über alle Epochen fest („The ordering is computed once and held fixed across all epochs“, §4.1.2); ein Wechsel der Reihenfolge oder Menge mitten im Training kommt nicht vor.

**(c) Teil-Resets: nicht gefunden.** Keine Resets einzelner Module. (§6.5 schlägt vor, den Reihenfolgekanal zur Lokalisierung zu nutzen, ohne Reset-Experiment.)

**Folge für unsere Formulierung.** Die Abgrenzung im Entwurf („Reihenfolge vs. Menge“) ist korrekt und lässt sich **schärfen**: Bei LeDoux legt unter Minibatch-SGD die Reihenfolge die Frequenz fest, und *zufällige* Teilmengen ändern sie nicht; K2 zeigt, dass unter Full-Batch *konstruierte* Teilmengen sie festlegen. Für K4 ist LeDoux' „critical learning period“ (Epoche 3–14) als nächstverwandte Datierung zu zitieren, mit dem Hinweis, dass dort kein Wechselexperiment gemacht wird. Wir sollten den Begriff „critical learning period“ nicht so verwenden, als sei er dort experimentell durch einen Wechsel belegt.

---

## 2. Marchetti, Kunin, Myers, Acosta, Miolane (2026), *Sequential Group Composition* (ICML 2026)

- **Link:** https://arxiv.org/abs/2602.03655 (v2; „Accepted at ICML 2026“)
- **Gelesen:** §1–§6 vollständig, Anhang A (Prosa), B (überflogen, Beweise), C (C.1 vollständig, C.2 überflogen), D (D.1–D.3 vollständig), E vollständig.

**(a) Mengenzusammensetzung → Irreps: nicht gefunden.** Die Reihenfolge der Irreps folgt der Fourier-Statistik des **Kodierungsvektors**; die Daten sind stets vollständig bzw. frisch und gleichverteilt gezogen:
> „networks do so by progressively decomposing the task into the irreducible representations of the group, learning these components in a greedy order based on the encoding vector“ (§1)
> „The network is trained to minimize the mean squared error loss over all sequences of length [k]“ (§3.2; Formelsymbol bei der Textumwandlung verloren)
> „The full dataset consists of all pairs […]“ (Anhang D.1, Schritt 4)
> „All models are trained online, sampling fresh sequences at each optimization step.“ (Anhang D.3)
> Grenzen: „finite groups, orbit-based encodings, polynomial activations, mean-squared loss, full-batch training, and vanishing initialization.“ (§6)

Keine Stelle mit nicht-uniformen Paarverteilungen oder Teilmengen gefunden (Suchbegriffe subset, uniform, training set, sampled, mask).

**(b) Persistenz nach Datenwechsel: nicht gefunden.** Nur Befund, dass Neuronen nach dem Einrasten auf eine Irrep ausgerichtet bleiben (Anhang C.1, Annahme 4.2), ohne Datenwechsel.

**(c) Teil-Resets: nicht gefunden.**

**Folge.** Die Formulierung im Entwurf (Kodierung bei uniformen Daten vs. Paarmenge) ist durch den Volltext gedeckt. **Korrektur für [[paper/related_work]]:** Die Aussage „bei One-hot-Kodierung sind alle Irreps gleichauf“ ist zu grob. Anhang D.2 zeigt für D₃ mit *mean-centered one-hot*-Kodierung einen **Dimensionsbias** (1-dim. Vorzeichen-Irrep vor 2-dim. Rotations-Irrep, wachsend mit der Sequenzlänge k):
> „the time between learning the one-dimensional sign irrep (brown) and the two-dimensional rotation irrep (blue) increases as the sequence length gets larger“ (Anhang D.2)

Richtig ist: Gleichstand nur zwischen Irreps gleicher Dimension. Für D₅₉ (K2) ist das relevant, weil wir zwischen 2-dim. Irreps steuern. Anhang E bestätigt die Einordnung von He et al. 2026a („Their analysis only considers a single phase, i.e., the first learned frequency (the ‘winning lottery ticket’)“).

---

## 3a. He, Wang, Chen, Yang (2026a), *On the Mechanism and Dynamics of Modular Addition*

- **Link:** https://arxiv.org/abs/2602.16849 (v1, 2026-02-18)
- **Gelesen:** §1–§7 vollständig, Anhang A (vollständig), B und C (überflogen, Beweise), D (vollständig).

**(a) Mengenzusammensetzung → Frequenz: nicht gefunden.** Die Theorie läuft auf der vollen Datenmenge, und die Frequenzwahl wird der Initialisierung zugeschrieben:
> „The final, dominant frequency learned by each neuron is entirely determined by a small subset of Fourier components in its initial parameters. […] A frequency's success is determined by its initial conditions, primarily two key factors: its initial magnitudes and its initial phase misalignment level.“ (§3.2)
> „[…] the loss is given by the cross-entropy (CE) loss in (2.2), evaluated over the full dataset“ (§5.2)
> Grokking-Experiment: „we randomly partition the entire dataset […], using a training fraction of 0.75“ (§3.3)

Einzige Stelle zur Zusammensetzung: In der Memorierphase bevorzugt das Modell symmetrische Paare, deren Gegenstück ebenfalls im Training ist (§3.3, Abb. 10). Das betrifft die Memorierung, nicht die Frequenzwahl. Außerdem: Bei großer Breite ist dort **jede** Frequenz vertreten („every frequency is represented among the neurons“, Observation 3). Das Zweischicht-MLP mit vielen Neuronen ist also ein anderes Regime als unser Transformer mit wenigen Key-Frequenzen.

**(b) Persistenz nach Datenwechsel: nicht gefunden.** Die Lotterie-Logik (früher Vorsprung gewinnt) passt zu K4, aber ohne Wechselexperiment.

**(c) Teil-Resets: nicht gefunden** (Zweischicht-MLP, keine Attention).

## 3b. He, Wang, Zhang, Chen, Yang (2026b), *Neural Networks Provably Learn Spectral Representations for Group Composition*

- **Link:** https://arxiv.org/abs/2606.02993 (v2)
- **Gelesen:** §1–§6 vollständig; Anhänge A–F überflogen (Beweise nicht nachvollzogen; Anhang F nach Daten-/Split-Begriffen durchsucht, ohne Treffer).

**(a) nicht gefunden.**
> „We train on the complete composition table, comprising all pairs […]“ (§1)
> „we focus on full-data training over the complete composition table: the network observes every pair“ (§2)
> „We observe empirically that the selection of learned irreps is governed by the initialization geometry rather than the energy landscape.“ (§4.4)
> „while we focus on the population case, a rigorous analysis of the train-test split remains open, particularly about the delayed generalization phenomenon known as grokking.“ (§6)

Der letzte Satz benennt die Lücke, die K2 empirisch füllt. §4.4 zeigt außerdem: Unter Zufalls-Init werden **höherdimensionale** Irreps häufiger gelernt.

**(b), (c): nicht gefunden.**

**Folge (3a/3b).** Die Formulierung „He et al. schreiben den Wettbewerb der Initialisierung zu, bei vollen Daten“ ist durch beide Volltexte gedeckt. Man kann 2606.02993 §6 wörtlich als offene Frage zitieren, an die K2 anschließt.

---

## 4. Lyle, Sokar, Pascanu, György (2025), *What Can Grokking Teach Us About Learning Under Nonstationarity?*

- **Link:** https://arxiv.org/abs/2507.20057 (v1, 2025-07-26)
- **Gelesen:** §1–§7 vollständig, Anhang A (A.1 Transformer, A.2 Warm-Starting), Anhang B (B.1–B.5), theoretischer Anhang überflogen.

**(a) nicht gefunden.** Zufälliger Split: „To generate a train-test split, we randomly extract a fraction of the set of all pairs“ (§4.1). Keine Frequenzanalyse.

**(b) Persistenz nach Datenwechsel: teilweise.** Rahmen und Begriff (Primacy Bias) passen, der Datenwechsel wird aber **nicht an modularer Arithmetik** untersucht, sondern als Warm-Start auf CIFAR-10 (10/50/100 % der Daten, §5.1). Für modulare Arithmetik betonen die Autoren selbst, dass die Aufgabe stationär ist:
> „An important difference between the typical setting for grokking and the continual learning settings which we will next investigate is that the modular arithmetic problem is stationary […] It is plausible that the process by which features are learned depends crucially in some way on changes which our approach makes during the earliest phase of training. Figure 3 addresses this concern. […] We observe that even after several hundred thousand optimizer steps, it is still possible to induce grokking via ELR re-warming.“ (§4.2)
> „The sensitivity of neural networks to early training data has been identified in the literature under a variety of names, for example critical periods […]. We use the term primacy bias in this work to refer to all such phenomena.“ (§1, Fußnote)

Keine Messung, *welche* Features/Frequenzen nach einem Wechsel bleiben.

**(c) Teil-Resets: nicht gefunden.** Es gibt Lernraten je Schicht (Vision-CNNs, §5.2), Resets nur als RL-Vergleich (§6) und in Anhang B.1 einen Zusammenhang zwischen Rang der Attention-Ausgaben und Grokking, aber keine Resets von Attention oder MLP.

**Folge.** Die Einstufung „teilweise, deutlich“ für K4 in [[paper/related_work]] ist eher **zu streng**. Genauer: gleiche Aufgabenfamilie und gleiche Leitfrage, aber dort kein Datenwechsel bei modularer Arithmetik und keine Frequenzmessung. Die ELR-Erklärung bleibt eine Pflicht-Konkurrenzerklärung: §4.2 zeigt, dass sich Merkmalslernen durch ELR-Re-Warming auch spät noch auslösen lässt. Das legt nahe, dass unsere Festlegung nach 25–50 Schritten vom Lernratenregime abhängen könnte (nicht getestet).

---

## 5. Vorwärtszitate und Suchtreffer

### 5.1 Dong (2026), *The Kinetics of Training* — relevant für (c)

- **Link:** https://arxiv.org/abs/2607.27281 (v1, 2026-07-29; Lei Dong; 40 Seiten). Gefunden als Vorwärtszitat von Lyle et al. 2025.
- **Gelesen:** §7 („loss of plasticity“) und §7.1 vollständig, Abstract, Überschriften; Anhang A.7 per Schlüsselwortsuche.
- **(a) nicht gefunden** (Sprachmodelle; das Mischungsverhältnis der Daten steuert, *ob/wann* eine Fähigkeit entsteht, nicht Frequenzen).
- **(b) teilweise (anderes System):** Wird zuerst auf Basisdaten trainiert („aging“), dann auf die Zielfähigkeit gewechselt, wächst die Verzögerung mit der Wartezeit bis zu einem Horizont, nach dem die Fähigkeit nicht mehr entsteht. Mechanismus: Attention-Köpfe legen sich auf die Basisdaten fest („heads commit to the base data“).
- **(c) Teil-Resets: teilweise, deutlich, mit entgegengesetztem Muster.**
> „We locate the damage (heads commit to the base data) and isolate the cure: re-initializing only the query-key slices restores learnability (6/6) while the value slices do nothing (0/6).“ (Abstract)
> „From one aged substrate, re-initializing the QK slices recovers formation 4.3× (6/6 formed), MLP does little, and re-initializing the OV slices is worse than no reset at all (1.76× slower)“ (§7.1 bzw. Anhang A.7; Faktor 1,76 aus Anhang A.7)
- **Folge für K4d/K4e:** „Attention-Reset stellt Plastizität deutlich stärker her als MLP-Reset“ ist für Transformer **allgemein schon gezeigt** (Pythia bis 1,4B und ein Gated-Attention-Spielmodell). Unser Unterschied: Grokking/Frequenzwahl, 1-Schicht-Modell, Persistenz einer *alten* Wahl statt Erlernbarkeit einer *neuen* Fähigkeit. Bei uns wirkt der **Wertepfad (W_V, W_O) stärker als Q/K**, bei Dong ist es umgekehrt (QK hilft, OV schadet). Diesen Kontrast muss das Paper ausdrücklich diskutieren. K4d darf nicht als erster Nachweis von Attention- vor MLP-Reset formuliert werden.

### 5.2 Khanh (2026), *Cross-Trajectory Chimera Interventions* — relevant für (b), (c)

- **Link:** https://arxiv.org/abs/2607.06628 (v1, 2026-07-07; Truong Xuan Khanh). Gefunden als Vorwärtszitat von Nanda et al. 2023.
- **Gelesen:** Volltext (§1–§11, Anhang A).
- **Setup sehr nah an unserem:** „a one-layer transformer […] trained full-batch with AdamW“ (§3); „circuit identity“ = normiertes Leistungsspektrum der Token-Embedding-Zeilen nach Nanda et al., bei Multiplikation im diskreten Logarithmus (§3).
- **(a) nicht gefunden** (Eingriff in den Gewichtsraum, nicht in die Daten).
- **(b) teilweise:** Die Frequenz-„Identität“ eines Laufs vor dem Grokking lässt sich durch Einpflanzen der Gewichtsrichtung eines anderen Laufs überschreiben, schwellenartig und abhängig von der Norm:
> „Direction carries a transferable, donor-specific circuit identity: implanting a donor's direction at the recipient's norm drives the run to the donor's circuit in 40/40 cases“ (Abstract)
> „a chimera near convergence (low norm) is already committed“ (§9)

Kein Datenwechsel und keine Datierung in Schritten ab Trainingsbeginn.
- **(c) teilweise:** Beim Tausch der Richtung nur einzelner Schichtgruppen ziehen Attention, MLP und Unembedding **jeweils einzeln** in Richtung Spender, nicht additiv. Die Autoren werten das selbst nur als Hinweis („suggestive rather than established, given three pairs per task“, §7/Anhang A). Das ist ein Transplantat, kein Reset.
- **Folge:** Muss als methodisch nächstverwandte Arbeit zu K4 zitiert werden (gleiches Maß, gleiches Regime). K4 ist dazu das Datenwechsel-Analogon mit gemessener Festlegungszeit. Ihr Befund „auch das MLP trägt die Identität“ steht in leichter Spannung zu unserem „MLP-Reset wirkt schwach“. Das ist zu diskutieren, wobei Reset und Transplantat verschiedene Eingriffe sind.

### 5.3 Weitere geprüfte Treffer (kein Beleg für a/b/c)

- **Tian (2025), *Provable Scaling Laws of Feature Emergence from Learning Dynamics of Grokking*,** https://arxiv.org/abs/2509.21519 (v5). Gelesen: §4.5, §5.2, §8 vollständig, Rest überflogen. **(a) teilweise (nur konzeptuell):** „different data distribution leads to different landscapes, which gives either generalization or memorization local maxima“ (§4.5). Theorem 4 gilt aber für **uniform zufällig** gezogene Teilmengen („If we select data sample […] uniformly at random […] the empirical energy function keeps local maxima for […] irreps“), und Theorem 5 für den degenerierten Fall einer einzigen Zielklasse (Memorierung). Keine Steuerung, *welche* Irreps. Theorem 7 („Top-down Modulation“): Sind einige Irreps gelernt, hat die Energie nur noch Maxima auf den fehlenden. Das ist ein möglicher theoretischer Rahmen für K4, dort aber nicht mit Datenwechsel geprüft. Zitierwürdig als Theorie, in der die Datenverteilung die Landschaft formt.
- **Jia (2026), *Beyond Embedding Transfer*,** https://arxiv.org/abs/2609.18078. Warm-Start-Transfer zwischen Operatoren in modularer Arithmetik; Komponenten E, U und B (B = Attention **und** MLP zusammen). Keine Frequenzanalyse, Attention und MLP nicht getrennt. (b) nur konzeptuell, (c) nicht gefunden.
- **Lin (2026), *Canalization Before Generalization*,** https://arxiv.org/abs/2608.25813. Kurze Weight-Decay-Pulse; die „Lösungsauswahl“ wird vor dem sichtbaren Grokking festgelegt. Kein Datenwechsel; Frequenzen werden nicht als Identität gemessen. Konzeptuell nah an K4 (frühe Kanalisierung).
- **Singh, Belilovsky, Aljundi (2025), *When Data Falls Short*,** https://arxiv.org/abs/2511.04760. Continual-Setting p1 → p2 mit **anderem Modulus**, Knowledge Distillation. Keine Frequenzen, kein Reset.
- **Nur Abstract [A]:** Li & Sreedhar 2026, *Natural Ungrokking* (https://arxiv.org/abs/2606.26050; eine Korpusstatistik entscheidet, welche Regeln ein Sprachmodell behält; konzeptuell „Daten wählen, was bleibt“). Howe 2026, *What Makes a Representational Prior Work?* (https://arxiv.org/abs/2607.12735; ein Prior wirkt nur in einem frühen Fenster, ohne Frequenzwahl). Cullen et al. 2026, *A Basin-Selection Perspective on Grokking via SLT* (https://arxiv.org/abs/2603.01192).

### 5.4 Ergebnis der Suche nach Vorwegnahmen

Unter den geprüften Vorwärtszitaten (Nanda 2023: 991 Titel gefiltert; LeDoux: 1; He 2026a: 6; Marchetti: 7; He 2026b: 2; Lyle 2025: 9) und in den arXiv-API-/Web-Suchen fand sich **keine Arbeit, die die Frequenz- oder Irrep-Wahl über die Zusammensetzung der Trainingspaare steuert** und keine, die die Frequenzwahl vor und nach einem kontrollierten **Datenwechsel** misst. Semantic-Scholar-Suche und Google Scholar waren nicht verfügbar, daher bleibt die Suche unvollständig.

---

## 6. Übersicht

| Arbeit | (a) Menge → Frequenz | (b) Festlegung nach Datenwechsel | (c) Attention- vs. MLP-Reset |
|---|---|---|---|
| LeDoux 2026 (2603.25047) | nicht gefunden (nur Reihenfolge; zufällige Teilmengen ändern F nicht) | teilweise (kritische Periode Epoche 3–14, ohne Wechsel) | nicht gefunden |
| Marchetti et al. 2026 (2602.03655) | nicht gefunden (Kodierung, volle/online-Daten) | nicht gefunden | nicht gefunden |
| He et al. 2026a (2602.16849) | nicht gefunden (Init entscheidet, volle Daten) | nicht gefunden | nicht gefunden |
| He et al. 2026b (2606.02993) | nicht gefunden (volle Tabelle; Split „remains open“) | nicht gefunden | nicht gefunden |
| Lyle et al. 2025 (2507.20057) | nicht gefunden | teilweise (Primacy, Warm-Start nur CIFAR; mod. Arithmetik stationär) | nicht gefunden |
| **Dong 2026 (2607.27281)** | nicht gefunden | teilweise (LM, Aging → Horizont) | **teilweise, deutlich** (QK-Reset hilft, MLP wenig, OV schadet; LM-Setting) |
| **Khanh 2026 (2607.06628)** | nicht gefunden | teilweise (Gewichts-Transplantat überschreibt Frequenz-Identität; Norm-Schwelle) | teilweise (Attention, MLP, Unembedding tragen je Identität; Transplantat) |
| Tian 2025 (2509.21519) | teilweise, konzeptuell (Datenverteilung formt Landschaft; nur uniforme Teilmengen) | nicht gefunden | nicht gefunden |
| Jia 2026 (2609.18078) | nicht gefunden | konzeptuell (Warm-Start-Transfer) | nicht gefunden (Attention+MLP gemeinsam) |

## 7. Konsequenzen für die Neuheitsformulierung (Vorschlag)

1. **K2 bleibt**, mit der Formel „nach unserer Suche nicht gefunden (vorläufig)“. Keine der gelesenen Arbeiten steuert über konstruierte Paarmengen. Zwei neue Stützen für die Abgrenzung: LeDoux §4.2.3/§5.3 (zufällige Teilmengen ändern die Frequenz unter Stride-Ordnung nicht) und He et al. 2026b §6 (der Train-Test-Split wird als offene Frage benannt).
2. **Marchetti-Einordnung präzisieren:** Mit One-hot-Kodierung besteht Gleichstand nur zwischen Irreps gleicher Dimension; es gibt einen Dimensionsbias (Anhang D.2). [[paper/related_work]] §3 entsprechend korrigieren.
3. **K4 bleibt**, aber zusätzlich zitieren: Khanh 2026 (gleiches Regime und Maß, Überschreiben der Frequenz-Identität per Gewichtstransplantat; K4 als Datenwechsel-Analogon mit Zeitangabe in Schritten) und LeDoux §3.4 (kritische Periode ohne Wechseltest). Die Einstufung von Lyle et al. 2025 auf „teilweise“ absenken (kein Datenwechsel bei modularer Arithmetik). Die ELR-Konkurrenzerklärung bleibt Pflicht.
4. **K4d/K4e umformulieren:** Nicht behaupten oder nahelegen, dass „Attention-Reset > MLP-Reset für Plastizität“ neu ist. Dong 2026 zeigt das für Transformer bereits (mit QK als wirksamem Teil). Neu ist höchstens: in der Grokking-Frequenzwahl, für die Persistenz einer alten Wahl, und **mit dem Wertepfad statt QK als wirksamerem Teil**. Das ist ein expliziter Kontrast zu Dong 2026 und muss mit dem Hinweis „Reset-Empfindlichkeit, kein Speicherort“ diskutiert werden. Die Spannung zu Khanh 2026 (MLP trägt ebenfalls Identitätssignal) nennen.
5. **Noch offen (Mensch):** Figuren und Formeln der Arbeiten (hier nicht gelesen), vollständige Vorwärtszitate über Google Scholar, Anhang A.7 von Dong 2026 im PDF gegenprüfen (Faktor 1,76 und MLP-Wert standen in der Textumwandlung ohne Zahl bzw. nur teilweise).

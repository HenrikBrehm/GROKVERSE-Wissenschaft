---
tags: [lab/neu]
---
# Neue Richtungen: Kandidaten mit Neuheitsprüfung

„Neu“ heißt hier immer: **nach unserer Suche vom angegebenen Datum nicht gefunden**. Das ist eine
vorläufige Einordnung, keine Garantie. Zurück zu [[LAB]] · [[BACKLOG]].

Tags: #neu/kandidat = keine direkte Vorarbeit gefunden · #neu/bekannt = Frage schon beantwortet.

---

Quellenprüfung: Die Links stammen aus einer Agentensuche. Selbst per WebFetch geprüft (2026-09-25) sind
2602.16849 (Titel, Autoren, Aussage „winner determined by its initial spectral magnitude and phase
alignment“, nur zweischichtige Netze) und 2607.05104 (siehe N3).

---

## N1: Frequenzverbot während des Trainings (kausaler Test des Timings) #neu/kandidat

- **Frage:** Verzögert das Herausprojizieren der früh entstehenden Embedding-Frequenzen ab t0 den
  Grokking-Übergang stärker als ein Verbot zufälliger Frequenzen?
- **Versuche:** [[experiments/EXP-001-freq-ban/README|EXP-001]], [[experiments/EXP-002-destined-ban/README|EXP-002]]
- **Suche 2026-09-25** (Agent, WebSearch/WebFetch). Suchbegriffe: „grokking modular addition ablate
  Fourier frequencies during training embedding projection causal“, „intervention during training
  remove Fourier component embedding grokking delayed modular arithmetic“, „grokking ‚frequency
  ablation‘ during training causal necessity early Fourier features random frequency control“.
- **Nächstverwandt:**
  - Nanda et al. 2023, Progress measures (https://arxiv.org/abs/2301.05217): Ablationen nur
    post hoc.
  - *Circuit Synchronization Precedes Generalization* 2026 (https://arxiv.org/abs/2606.12966):
    Eingriff über eine Gabelung der Weight Decay, ausdrücklich ohne Eingriff im Frequenzraum.
  - *Structure-Specific Representational Priors Causally Control the Grokking Delay* 2026
    (https://arxiv.org/abs/2607.04333): Prior auf Repräsentationsebene, keine einzelnen
    Frequenzen.
  - Khanh et al. 2026, First-Passage Prediction (https://arxiv.org/abs/2605.18845): Eingriff über
    Norm und Weight Decay.
- **Einordnung:** nicht gefunden. **Wichtige Konfundierung** (Codex-Review 2026-09-25): Ein
  Top-Verbot entfernt mehr Energie als ein Zufallsverbot. Dafür gibt es seit Nachtrag b die
  sekundäre Energiekontrolle `shrink_matched`.

## N2: Frequenz-Lotterie bei gemeinsamem Embedding. Init-Spektrum → netzweite Frequenzwahl #neu/kandidat

- **Frage:** Sagt das zufällige Init-Spektrum eines **gemeinsamen** Embeddings (`W_E`) voraus,
  welche Frequenzen das ganze Netz am Ende nutzt? Lässt sich das per Init-Tausch steuern? Wie
  unterscheidet sich das von Architekturen ohne gemeinsames Embedding (Lotterie pro Neuron)?
- **Versuche:** [[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]] (Befund positiv, p < 1e-5,
  seed-spezifisch; bei m2h nur pro Neuron) · [[experiments/EXP-010-init-swap/README|EXP-010]]
  (kausaler Init-Tausch, läuft seit Sitzung 4) · [[experiments/EXP-011-init-magswap/README|EXP-011]]
  (nur die Normen tauschen: trägt der Betrag oder die Richtung des Koeffizientenblocks?, vorbereitet)
- **Nachsuche 2026-09-26 (Sitzung 4, zu EXP-010/011).** Suchbegriffe: „grokking modular addition
  initialization embedding Fourier frequency magnitude versus phase which frequencies win intervention“,
  „arXiv 2026 transformer modular arithmetic key frequencies determined by initialization embedding swap
  experiment“. He et al. 2026 per WebFetch erneut geprüft: nur **beobachtend** (Betrag und Fehlausrichtung
  bei Init vs. Gewinner), keine gezielten Tausch- oder Skalierungseingriffe, nur 2-Schicht-MLPs pro Neuron.
  Weitere Treffer ohne Init-Eingriff ins Spektrum: *Mechanistic Insights into Grokking from the Embedding
  Layer* (https://arxiv.org/abs/2505.15624, Lernraten und Sampling für Embeddings), *The Discrete-Log Clock*
  (https://arxiv.org/abs/2606.17399), *Let Me Grok for You* (https://arxiv.org/pdf/2504.13292, Embedding-Transfer).
  **Einordnung:** Ein kausaler, verteilungserhaltender Init-Tausch im gemeinsamen Transformer-Embedding und
  die Trennung Betrag vs. Richtung wurden nach dieser Suche nicht gefunden. Vorläufig, keine Garantie.
- **Suche 2026-09-25.** Suchbegriffe: „grokking which Fourier frequencies selected initialization
  lottery modular addition“, „grokking modular addition frequency selection random seed determined
  initialization key frequencies per seed“, „modular addition transformer predict key frequencies
  from early training gradient spectrum commitment“, „Morwani Feature emergence via margin
  maximization“.
- **Nächstverwandt:**
  - **He, Wang, Chen, Yang 2026**, *On the Mechanism and Dynamics of Modular Addition: Fourier
    Features, Lottery Ticket, and Grokking* (https://arxiv.org/abs/2602.16849). Zeigt eine
    Lotterie pro Neuron: Es gewinnt die Frequenz mit der größten Init-Amplitude und der
    kleinsten Phasenabweichung. Untersucht sind 2-Schicht-MLPs, vor allem mit One-hot-Eingabe.
  - Morwani et al. 2024 (https://arxiv.org/abs/2311.07568): Im Max-Margin-Regime werden alle
    Frequenzen genutzt.
  - Nanda et al. 2023: Die Key-Frequenzen sind dünn besetzt und seed-abhängig.
- **Einordnung:** **teilweise bekannt.** Die Lotterie pro Neuron ist bekannt, und unser m2h-Befund
  repliziert sie. Nicht gefunden haben wir: die Vorhersage der netzweiten Menge aus dem
  Init-Spektrum eines gemeinsamen Embeddings (Transformer und MLP mit W_E), den Kontrast zwischen
  gemeinsamem Embedding und Lotterie pro Neuron, eine gemessene Lock-in-Zeit relativ zum Grokking
  und die verteilungserhaltende Steuerung per Koeffiziententausch. Wird etwas davon berichtet,
  dann nur als Erweiterung von He et al. 2026.

## N3: Fourier-Konzentration als Frühvorhersage pro Seed #neu/bekannt (teilweise)

- **Versuche:** [[experiments/EXP-003-early-prediction/SUMMARY|EXP-003]] und 003b/c, dazu 003d
  (vorbereitet)
- **Suche 2026-09-25.** Suchbegriffe: „predict grokking time early training Fourier sparsity
  embedding seeds“, „accelerate grokking Fourier regularizer embedding sparsity modular
  arithmetic“, „Grokfast gradient spectrum low-pass filter grokking acceleration“.
- **Nächstverwandt:**
  - FSD in 2606.12966 (Fourier-Maß über MLP-Neuronen, läuft dem Grokking voraus)
  - 2607.04333 (Konzentration des Embeddings bewegt sich vor der Generalisierung)
  - Howe 2026 (https://arxiv.org/abs/2609.19000): Vorhersage pro Seed, aber für Induction Heads
  - **Risiko:** Laut einem Such-Snippet soll 2607.05104 (https://arxiv.org/abs/2607.05104)
    zeigen, dass die Fourier-Konzentration bei kleinen Hidden-Größen kaum mit der
    Generalisierung korreliert. **Nicht bestätigt**, per WebFetch am 2026-09-25 geprüft. Das Paper heißt
    Ootani, *Grokking Is Conditional and Fragile* (12K-Parameter-Transformer). Im Abstract steht
    nichts zur Fourier-Konzentration. Es betont aber, dass Grokking von der **Thread-Zahl bzw.
    CPU/GPU** abhängt. Das ist relevant für unsere Abweichung von 4 statt 1 Thread.
- **Einordnung:** Vorläufer-Maße sind bekannt. Eine kalibrierte Regression pro Seed auf
  frühe Embedding-Konzentration haben wir nicht gefunden. Ein Regularisierer, der direkt die
  Fourier-Sparsität des Embeddings belohnt, war ebenfalls nicht zu finden, siehe N5.

## N4: Wählt man die Frequenzmenge vor, hängt dann das Timing davon ab, welche k es sind? #neu/kandidat (schwache Motivation)

- **Suche 2026-09-25:** nicht gefunden. Nächstverwandt sind GrokTransfer
  (https://arxiv.org/abs/2504.13292) und 2511.23443.
- **Starke Nullhypothese:** Für prime p ist jedes k ≠ 0 unter a ↦ ua äquivalent, und die Init ist
  iid. Im Erwartungswert sind also alle k symmetrisch. Unterschiede kann es nur pro Realisierung
  geben. Deshalb ist diese Richtung **zurückgestellt**. EXP-010 misst Δgen als Nebenprodukt.

## N5: Fourier-Sparsitäts-Regularisierer für das Embedding (Idee, ungeprüft) #neu/kandidat

- **Idee:** Ein Strafterm auf die Entropie des W_E-Leistungsspektrums. Der Test wäre kausal:
  Beschleunigt eine erzwungene Konzentration das Grokking, dann ist F6 (EXP-003) nicht nur
  ein Begleitsymptom.
- **Suche:** Nur in der Suche zu N3 mit abgedeckt, noch keine eigene. Vor einem Versuch
  gezielt suchen.

## N3: Der Trainingssplit wählt die Frequenzen mit (Masken-Spektrum) #neu/kandidat

- **Frage:** Bestimmt die zufällige Auswahl der Trainingspaare (nicht nur die Init), welche Fourier-Frequenzen ein
  Transformer für modulare Addition lernt? Lässt sich die Wahl aus dem Split allein vorhersagen, bevor Gewichte existieren?
- **Versuche:** [[experiments/EXP-014-split-vs-init/README|EXP-014]] (Kreuzdesign; Gradient-Vorschau: Spektrum des ersten
  Gradienten folgt dem Split, ρ 0.34 vs. −0.01) · [[experiments/EXP-015-mask-spectrum/README|EXP-015]] (Masken-Spektrum
  M0; Exploration Seeds 0–9: r̄ 0.307, p < 1e-5; Bestätigung offen)
- **Suche 2026-09-26.** Suchbegriffe: „grokking modular addition which key frequencies learned determined by training data
  subset split Fourier spectrum of training set“, „modular arithmetic neural network frequency selection "training set" mask
  Fourier sparsity random subset predicts learned frequencies“, „grokking transformer frequencies depend on random
  train/test split not initialization seed data-dependent frequency selection“.
- **Nächstverwandt:** He et al. 2026 (https://arxiv.org/abs/2602.16849): Init entscheidet (pro Neuron), Split nicht
  betrachtet. *Where Grokking Happens* (https://arxiv.org/html/2609.17571): stellt fest, dass der Seed Init **und** Split
  zugleich variiert, trennt beides aber nicht. Nanda et al. 2023 (https://arxiv.org/abs/2301.05217): seed-abhängige
  Schlüsselfrequenzen, ohne Ursache.
- **Einordnung:** Eine Zuordnung der Frequenzwahl zum Split und ein Vorhersager nur aus der Maske wurden nach dieser
  Suche **nicht gefunden**. Vorläufig, keine Garantie. Vor einem Anspruch: Bestätigung an Seeds 10–19 (EXP-015 Phase 2,
  EXP-014) und eine gründlichere Suche (OpenReview, Google Scholar).
- **Nachsuche 2026-09-26 (~03:35 Berlin).** Suchbegriffe: „openreview grokking "training set" choice influences learned
  Fourier features modular addition data subset determines representation“, „"modular addition" "train split" OR "data
  split" seed separate initialization seed frequencies learned grokking ablation“, „Mallinar Beaglehole grokking modular
  arithmetic average gradient outer product recursive feature machine“. Neu geprüft: **Mallinar et al. 2025, Emergence in
  non-neural models (RFM/AGOP)** (https://arxiv.org/abs/2407.20199): Kernel-Maschine ohne Zufalls-Init lernt
  blockzirkulante Merkmale; welche Frequenzen und warum, wird laut WebFetch **nicht** analysiert. Mehrere Arbeiten halten
  den Datensplit über Seeds fest (dann kann der Split-Effekt gar nicht auftauchen). **Einordnung unverändert:** nicht
  gefunden, vorläufig.
- **Stand 2026-09-26 04:53:** EXP-015 an frischen Seeds 10–17 **bestätigt** (Assoziation: r̄ 0.277, fremde Masken 0.499, exaktes p 2.5e-5; gegen funktionale Schlüsselfrequenzen p 3.6e-6); EXP-012 bestätigt (erster Gradient > Init). Achtung: Split und Init desselben Seeds sind gleich geseedet, also ist das noch kein Kausalnachweis. Kausale Tests EXP-016 (läuft) und EXP-014 stehen aus.
- **Idee (N3b):** In RFM gibt es keine zufällige Init; eine Frequenzauswahl dort müsste vollständig aus dem Split kommen.
  M0 sollte sie dann vorhersagen. Billiger Zusatztest außerhalb der Netze.

## N6: Spektral konzentrierte Trainingsmengen beschleunigen das Grokking? #neu/kandidat

- **Frage:** Generalisiert ein Transformer für modulare Addition auf einer festen, gleichverteilten Testmenge früher,
  wenn die Trainingspaare so gewählt sind, dass ihr Masken-Spektrum auf wenige Frequenzen konzentriert ist (bei
  gleicher Größe, gleicher Gewichtsverteilung und gleicher Abdeckung pro Antidiagonale)?
- **Versuch:** [[experiments/EXP-018-split-speed/README|EXP-018]] (vorbereitet). Anlass: EXP-016, gen 500–1100 statt
  3525–11200, aber mit Komplement-Testmenge und ohne passende Kontrolle.
- **Suche 2026-09-26 (Sitzung 5).** Suchbegriffe: „grokking modular addition training data selection accelerates
  generalization Fourier structured training set“, „grokking data pruning curriculum which training examples speed up
  grokking modular arithmetic arXiv“, „"grokking" non-uniform training distribution pairs importance sampling modular
  addition faster generalization 2025 2026“, „data selection controls learned features modular arithmetic training set
  composition determines Fourier frequencies“.
- **Nächstverwandt:**
  - **Kunin et al. 2025, Alternating Gradient Flows** (https://arxiv.org/abs/2506.06489), per WebFetch geprüft: Bei
    quadratischen 2-Schicht-Netzen auf modularer Addition werden Fourier-Merkmale „in decreasing order of |x̂[ξ]|“
    gelernt, x̂ = DFT des **Eingabe-Encodings**, trainiert auf **allen** p² Paaren. Das ist das nächste Gegenstück:
    Dort wählt das Encoding-Spektrum die Frequenzreihenfolge, bei uns (EXP-015/016) das Spektrum der **Trainingsmaske**.
    Ein Split-Einfluss wird dort nicht betrachtet. Theorie-Anschluss: Die AGF-Nutzenfunktion mit maskiertem Verlust
    sollte M0 enthalten (noch nicht hergeleitet).
  - *Grokking Explained: A Statistical Phenomenon* (https://arxiv.org/abs/2502.01774), per WebFetch: Grokking durch
    Verteilungsverschiebung zwischen Training und Test, erzeugt über unausgewogenes Sampling von Unterkategorien.
    Relevant als Konfundierung (deshalb EXP-018 mit fester Testmenge und gleichen Gewichten in D), aber keine
    spektrale Datenauswahl.
  - *Let Me Grok for You* (https://arxiv.org/pdf/2504.13292): Beschleunigung über Embedding-Transfer, nicht über
    Datenauswahl. Grokfast / Spektral-Ausgleich: Eingriff in Gradienten, nicht in Daten.
- **Einordnung:** Beschleunigung des Grokkings durch eine **spektral gewählte Trainingsmenge** bei festgehaltener
  Größe und Gewichtsverteilung wurde nach dieser Suche **nicht gefunden**. Vorläufig, keine Garantie; Google Scholar
  und OpenReview noch nicht gezielt durchsucht.
- **Nachsuche 2026-09-26 (Sitzung 5, ~06:07) zu N3 und N6.** Suchbegriffe: „openreview grokking modular addition
  "train/test split" seed determines key frequencies separate data seed model seed“, „"modular addition" learned
  frequencies depend on training subset "which frequencies" data distribution Fourier neural network 2026“,
  „designing training set to control which features a network learns algorithmic task frequency steering data
  curation grokking“. Per WebFetch geprüft:
  - **Zhou, Zhang, Xu 2024**, *A rationale from frequency perspective for grokking in training neural network*
    (https://arxiv.org/abs/2405.17479): **nächstverwandt zu N6.** Ungleichmäßig bzw. unzureichend gezogene
    Trainingsmengen erzeugen „spurious“ Frequenzanteile (NUDFT über den Eingaberaum, Frequency Principle), die das
    Netz zuerst lernt; sie konstruieren solche Mengen gezielt und **lösen damit Grokking aus**. Aufgaben: 1-D-Regression
    sin(6x), Parität, MNIST; **keine modulare Addition, keine Z_p-Fourier-Frequenzen im Embedding**. Ihr Bild sagt für
    EXP-018 das **Gegenteil** voraus: Das Spektrum von E passt nicht zur gleichverteilten Testmenge, also eher
    Verzögerung. EXP-018 trennt beide Vorhersagen.
  - **Amarine007/grokking-dynamics** (GitHub-Repo, kein begutachtetes Paper; https://github.com/Amarine007/grokking-dynamics),
    Nachbau von Nanda et al.: **fester** 30/70-Split, 10 Seeds nur mit verschiedener Init → kein Seed-Paar wählt dieselbe
    Frequenzmenge; die Init gibt nur einen „small, significant head start (p = 0.016)“; ~3/4 der Frequenzen stehen nach
    462 Schritten fest. **Folgerung für N3:** Der Split kann nicht die einzige Ursache sein (bei festem Split
    variiert K trotzdem). Das passt zu EXP-012 (Init trägt bei) und macht EXP-014 (Kreuzdesign) wichtig. Split-Variation
    wird dort nicht untersucht.
  - Kunin et al. 2025 (AGF), siehe N6.
  **Einordnung N3 unverändert vorläufig:** Eine Zuordnung der Frequenzwahl zum Datensplit und eine Steuerung durch
  konstruierte Splits bei modularer Addition wurden nicht gefunden. Die Idee „die Trainingsstichprobe erzeugt
  Frequenzen, die zuerst gelernt werden“ ist aber in anderer Form (F-Principle, Eingaberaum) **bekannt** (Zhou et al.
  2024). Ein Bericht müsste N3 als Übertragung auf Z_p-Fourier-Merkmale und als kausale Steuerung einordnen, nicht als
  neue Grundidee. #neu/bekannt (teilweise)

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

## N8: Kommutationssymmetrie des Splits und Frequenzwahl #neu/kandidat (schwach)

- **Befund (Rechnung, Sitzung 5; korrigiert 07:28):** M0c − M0 ist ein Kommutations-**Symmetrie**-Term des Splits (maximal = M0 bei symmetrischen Splits, ≈ 0 im Mittel bei Zufallssplits); vorher fälschlich „hängt nur an der Asymmetrie“ (Herleitung in
  [[experiments/EXP-019-coherent-mask/README|EXP-019]]). Die gemessenen Interferenzen im ersten Gradienten folgen diesem
  Term (18/18 Seeds).
- **Suche 2026-09-26** („grokking modular addition commutative symmetric training set include both (a,b) and (b,a) effect
  on generalization transformer“): Bekannt ist der Einfluss der Kommutationssymmetrie auf das Grokking selbst
  (*Controlling Grokking with Nonlinearity and Data Symmetry*, https://arxiv.org/abs/2411.05353; Datenaugmentierung mit
  vertauschten Paaren beschleunigt, KAN-Arbeit bei ScienceDirect). Ein Zusammenhang mit der **Frequenzwahl** über den
  Kreuzterm wurde nicht gefunden (vorläufig).
- **Einordnung:** Mechanismusdetail, niedrige Priorität. Mögliche billige Prüfung: symmetrisierter Split (gleiche
  ungeordnete Paare, beide Reihenfolgen) gegen asymmetrischen, Frequenzwahl und gen vergleichen. Nicht vorbereitet.

## N9: Wie viele Frequenzen? Ein-Frequenz-Lösung per Datenauswahl #neu/kandidat

- **Frage:** Lässt sich über einen spektral auf **eine** Frequenz konzentrierten Split eine Ein-Frequenz-Lösung
  erzwingen, und generalisiert sie (Robustheitsargument von He et al. 2026)?
- **Versuch:** [[experiments/EXP-022-single-frequency/README|EXP-022]] (vorbereitet).
- **Suche 2026-09-26:** „force neural network to learn single Fourier frequency modular arithmetic minimal circuit fewer
  frequencies generalization data intervention“, „modular addition network number of key frequencies why multiple
  frequencies single frequency solution sufficient margin robustness grokking“. Nächstverwandt: He et al. 2026
  (https://arxiv.org/abs/2602.16849, Mehrheitsabstimmung über Frequenzen und Phasen); Nanda et al. 2023 (3–8 Frequenzen).
  Ein Dateneingriff zur Zahl der Frequenzen wurde nicht gefunden (vorläufig).

## N10: Positions-Interferenz im Embedding-Gradienten über den geteilten Wertepfad #neu/kandidat

- **Befund (Sitzung 5, post hoc bzw. in silico, siehe [[BEFUND-split-mechanismus]]):** Im ersten W_E-Gradienten eines
  1-Schicht-Transformers interferieren die Beiträge der beiden Operanden frequenzweise nach dem Kreuzterm der Trainingsmaske
  (18/18 Seeds); die Ursache ist der geteilte Wertepfad der Attention (eigene Wertematrix für Position 1 → Interferenz weg);
  in der MLP mit getrennten W_in-Hälften fehlt sie, dort ist M0 die bessere Statistik. Kausaltest für die finale Wahl:
  [[experiments/EXP-023-split-value/README|EXP-023]] (vorbereitet).
- **Suche 2026-09-26:** „transformer shared token embedding gradient interference between input positions attention value
  path modular arithmetic training data mask spectrum“, „"modular addition" transformer vs MLP number of frequencies
  explanation attention commutativity embedding gradient initial“. Nächstverwandt: Beobachtung, dass MLPs viel mehr
  Frequenzen lernen als Transformer (z. B. *Interpreting Modular Addition in MLPs*,
  https://www.lesswrong.com/posts/cbDEjnRheYn38Dpc5/interpreting-modular-addition-in-mlps; die Studie selbst, RESULTS §16),
  ohne Mechanismus; *Context Staircase* (https://arxiv.org/pdf/2608.30315) zu Embedding-Dynamik bei kleiner Init mit
  positionsspezifischen Signaturen, andere Aufgabe. Der konkrete Mechanismus wurde **nicht gefunden** (vorläufig).
- **Grenze:** Bisher nur der erste Gradient bei Init und eine Konfiguration (p = 113, 30 %-Split).
- **Stand 2026-09-26 08:06 (Sitzung 5):** EXP-016 abgeschlossen, *steuerbar* (10/10 Seeds, Δ̄ +7.7, p ≈ 0.001). Kausaler
  Beleg, dass die Datenauswahl die Frequenzwahl eines Transformers für modulare Addition vorgibt; Einordnung siehe oben
  (Grundidee in anderer Form bekannt, Zhou et al. 2024; Z_p-Umsetzung und Steuerung nicht gefunden, vorläufig).

## N11: Architektur bestimmt, *welche* Harmonische des Split-Spektrums gelernt wird (k gegen k/2) #neu/kandidat

- **Rechnung (Sitzung 6, 2026-09-26):** AGF-Nutzen (Kunin et al. 2025) des Zwei-Hot-Netzes mit quadratischer Aktivation
  unter **maskiertem** Verlust: U = ‖P g‖, g_c = Σ_a M(a, c−a)(u_a + v_{c−a})². Das Quadrat erzeugt 2k-Oszillationen entlang
  der Antidiagonalen, also greift der Nutzen einer Frequenz k das Masken-Spektrum bei **2k** ab. Numerisch an 20 EXP-016-
  Splits: Top-5 des Nutzens enthalten 3.25/5 halbe Ziele fold(57·f), 0.2/5 Ziele (Zufall 0.45). Der Transformer lernt
  dagegen die Ziele selbst (EXP-016). Vorhersage: gleiche Daten, andere Architektur → andere, aber *vorhersagbare*
  Frequenzen (F/2 statt F). Test: [[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]].
- **Suche 2026-09-26 (Sitzung 6):** „quadratic activation network modular addition learns half frequency training subset
  mask Fourier 2k alternating gradient flows“, „"modular addition" architecture dependence which frequencies learned
  transformer vs quadratic MLP same training data frequency doubling“, „grokking modular addition "training set"
  subsample Fourier spectrum of training mask predicts learned frequencies two-layer network theory“.
  Nächstverwandt: Kunin et al. 2025 (https://arxiv.org/abs/2506.06489, volle Daten, Reihenfolge nach |x̂|);
  He et al. 2026 (https://arxiv.org/abs/2602.16849, Wettbewerb der Frequenzen je Neuron nach Init-Betrag und Phase, volle
  Daten); *Modular addition without black-boxes* (https://arxiv.org/abs/2412.03773, Frequenzverdopplung in der MLP als
  numerische Integration, anderer Zusammenhang). Ein Zusammenhang Split-Spektrum bei 2k ↔ Frequenz k und die
  Architekturabhängigkeit dieser Zuordnung wurden **nicht gefunden** (vorläufig; Google Scholar/OpenReview nicht gezielt).
- **Bezug:** Die in EXP-016 beobachteten Fehlgriffe des Transformers sind 2k der Ziele (Oberwellen), also die
  *entgegengesetzte* Richtung. Ob beides eine gemeinsame Ursache hat (Quadrat-artige Terme im Transformer), ist offen.
- **Nachsuche 08:57 (Sitzung 6):** „openreview modular arithmetic partial training data which Fourier frequencies
  activation function quadratic vs ReLU different frequencies learned“. Laut Suchzusammenfassung (nicht per WebFetch
  geprüft, Quelle wohl https://arxiv.org/abs/2602.16849 oder https://arxiv.org/abs/2505.18266): Eine mit ReLU trainierte
  Lösung stützt sich auf die **geraden** Anteile der Aktivierung (|x|, x² austauschbar). Das spräche dafür, dass auch das
  ReLU-Netz am Ende H statt F wählt, entgegen der ReLU-Nutzenrechnung am Start (F über den linearen Anteil).
  EXP-024 Arm R trennt beide Bilder. Ein Split-Einfluss wird dort nicht betrachtet; Einordnung N11 unverändert vorläufig.
- **Nachprüfung 09:01 (Sitzung 7, WebFetch Volltext https://arxiv.org/html/2602.16849):** He et al. 2026 schreiben wörtlich:
  „A model trained with ReLU is robust to changes of activation function at inference time. This is because learning a
  good solution only relies on the activation's dominant even-order components“ und „the output of a ReLU neural network
  is fundamentally determined by the ½|x| term“ (ReLU(x) = ½(x + |x|)); Tabelle 1: Tausch ReLU → |x|, x², x⁴ zur
  Inferenzzeit ohne Genauigkeitsverlust. Theorie nur für x² und **volle Daten**; Grokking-Teil mit Zufallssplit 0.75,
  ohne Frage, wie der Split die Frequenzen bestimmt. McCracken et al. (https://arxiv.org/abs/2505.18266): Abstract
  nennt weder Paritätsargument noch Splits (Quelle der Suchzusammenfassung war also He et al.).
  **Folge für EXP-024 Arm R:** Zwei Bilder sagen Gegensätzliches voraus: Nutzen am Start (linearer Anteil) → F; gerade
  Anteile tragen die Endlösung → H. Arm R ist damit ein echter Unterscheidungstest zwischen Anfangsauswahl und
  Endlösung. Einordnung N11 unverändert vorläufig (Split-Abhängigkeit weiter nicht gefunden).
- **Ergebnis EXP-024 (Sitzung 7, 09:43):** Richtung in beiden Armen wie vorhergesagt. x²: H angereichert (1.1/5 gegen F
  0.2, p = 0.002), aber *richtungsgleich, n. s.* nach der Größenregel; das breite x²-Netz nutzt fast alle Frequenzen
  (Morwani Thm 7), der Split neigt nur (+15 % Leistung auf H). ReLU: F 4.8/5 ab Schritt 50, *bestätigt*, aber die Netze
  memorieren (Test 6 %). Stand der Idee: **teilweise gestützt**; die Architekturabhängigkeit der Richtung ist da, als
  „Auswahl“ nur bei memorierenden ReLU-Netzen deutlich. Weiter: EXP-026 (Zeitpunkt), EXP-027 (Breite).

## N12: Paritäts-Umschlagpunkt als Uhr: Bei welcher Merkmalsamplitude fällt die Frequenzwahl? #neu/kandidat

- **Rechnung (Sitzung 7, 09:03):** Im exakten AGF-Nutzen unter maskiertem Verlust greift der ungerade Anteil der Aktivierung
  die Maske bei k ab (x: 5.0/5 Ziele F), der gerade bei 2k (|x|: 2.2/5 halbe Ziele H). Für σ_α = αx + x² zählt nur
  α/r (r = Merkmalsamplitude); der Nutzen schlägt bei α/r ≈ 1 um (`EXP-024/utility_parity.py`, `utility_parity.json`).
- **Idee:** Da r im Training wächst, verrät der Umschlagpunkt α* trainierter σ_α-Netze, bei welcher Amplitude und damit
  wann die Wahl fällt. Test: [[experiments/EXP-026-parity-crossover/README|EXP-026]].
- **Suche 2026-09-26 09:05 (Sitzung 7):** „activation function odd even part determines which Fourier frequency learned
  two-layer network small initialization feature amplitude …“, „arXiv grokking modular addition activation "alpha x + x^2"
  OR "linear plus quadratic" activation family frequency selection training subset“. Nächstverwandt: He et al. 2026
  (https://arxiv.org/abs/2602.16849, gerade Anteile tragen die ReLU-Endlösung, volle Daten, x²-Theorie); Salah & Yevick
  2024 (https://arxiv.org/abs/2411.05353, Nichtlinearität steuert Grokking, ohne Frequenzwahl oder Split); Kunin et al.
  2025 (AGF). Paritätszerlegung als Brücke Split-Spektrum (k vs 2k) ↔ gelernte Frequenz und der Umschlagpunkt als
  Zeitmesser: **nicht gefunden** (vorläufig; Google Scholar/OpenReview nicht gezielt).
- **EXP-026 (Sitzung 7, 10:30):** Nach Codex zum Umschaltversuch umgebaut (die α-Stufen-Uhr war nicht haltbar). Ergebnis:
  schon 50 Schritte mit 3x + x² legen die F-Neigung des danach reinen x²-Netzes fest (5/5, Plateau bis 2500); formal
  *Anker ok, Trend n. s.*, weil der Rangtest nicht zur Stufenform passte. Feinere Auflösung: [[experiments/EXP-032-early-lockin/README|EXP-032]].
  Die ursprüngliche Idee (Umschlagpunkt als Amplitudenuhr) ist **verworfen**, nicht getestet.
- **Suche 10:48 (Sitzung 7) zur frühen Festlegung:** „early training critical period first steps determine learned features
  grokking modular arithmetic activation function switch during training“. Nächstverwandt: Achille et al. 2019, *Critical
  Learning Periods* (https://arxiv.org/abs/1711.08856, frühe Defizite wirken bleibend); Frankle et al. 2020, *The Early Phase
  of Neural Network Training* (https://arxiv.org/abs/2002.10365). Dass wenige Dutzend Schritte mit einem ungeraden
  Aktivierungsanteil festlegen, welche Fourier-Frequenzen ein danach rein quadratisches Netz nutzt: **nicht gefunden**
  (vorläufig). Die allgemeine Aussage „frühe Phase legt fest“ ist bekannt.
- **EXP-032 (11:09):** vorab festgelegt, *Festlegung in ≤ 20 Schritten*, t½ = 5 Schritte (ρ 0.91, p = 1e-4). Die frühe
  Neigung wird bis zum Ende etwa verdreifacht. Stand N12: **gestützt** in der Form „wenige frühe Schritte mit ungeradem
  Aktivierungsanteil legen die Frequenzneigung fest“ (ein Modell, AdamW, 5 Splits).

- **Einwand (Sitzung 8, 12:03):** Die Zahl „5 Schritte“ ist an AdamW gebunden: Adams erster Schritt ist ein Vorzeichen-Schritt der
  Größe lr (Abuduweili & Liu 2024, https://arxiv.org/abs/2412.02153); in EXP-032 ist r am Umschaltschritt über alle Splits
  identisch. Kritische Perioden gibt es auch in linearen Netzen ohne Optimierer-Details (Kleinman, Achille & Soatto 2023,
  https://arxiv.org/abs/2308.12221). Ob die Festlegung selbst den Weg braucht: [[experiments/EXP-033-optimizer-lockin/README|EXP-033]].

- **EXP-033 (Sitzung 8, 13:18):** GD in der σ_3-Phase bis zur Amplitude von 10 AdamW-Schritten gibt eine bleibende F-Neigung in
  10/10 Splits, etwas stärker als AdamW (R 1.26). Die lineare Modentheorie (Singulärvektoren von Xᵀ(Y − 1/P)) sagte die
  stärkere GD-Neigung am Umschaltschritt vorher (10/10). N12 damit in der Form „frühe Festlegung braucht in Phase 1 kein
  Adam“ gestützt; Erhalt ohne Adam offen ([[experiments/EXP-034-phase2-optimizer/README|EXP-034]]).

## N13: Memorisierung prägt das Masken-Spektrum ein, Generalisierung verdrängt Teile durch 2k-Oberwellen #neu/kandidat

- **Beobachtung (Sitzung 7, post hoc, EXP-016):** Bei Schritt 250 (Memorisierungsphase) sind die W_E-Top-5 in 20/20
  Transformerläufen genau die Ziele des konstruierten Splits; bis zum Ende fällt die Überlappung auf 3.9, ersetzt durch
  2k-Oberwellen. Parallel: memorierende ReLU-Zwei-Hot-Netze (EXP-024 R) zeigen F ab Schritt 50. Deutung (Spekulation):
  Die frühe Wahl ist ein Abdruck der Trainingsmenge (ungerader/linearer Anteil), die Generalisierung bringt über gerade
  Anteile 2k-Komponenten. Bestätigung vorab festgelegt: [[experiments/EXP-028-memo-imprint/README|EXP-028]].
- **Suche 09:47:** „grokking modular addition embedding Fourier frequencies already present during memorization phase before
  generalization which frequencies training set“. Nächstverwandt: Nanda et al. 2023 (Schaltkreis entsteht nach der
  Memorisierung, vor dem Test-Sprung; https://www.alignmentforum.org/posts/N6WM6hs7RQMKDhYjB/), He et al. 2026
  (Frequenzwahl je Neuron nach Init, https://arxiv.org/abs/2602.16849), https://arxiv.org/pdf/2607.05104 (kleine Modelle,
  Einbettungs-Konzentration sagt Generalisierung nicht voraus; nicht im Detail gelesen). Dass die Memorisierungsphase das
  Spektrum der *Trainingsmaske* vollständig einprägt und die Generalisierung Teile davon durch 2k-Oberwellen ersetzt:
  **nicht gefunden** (vorläufig).
- **Zufallssplits (Sitzung 7):** explorativ an Seeds 0–9 ρ(W_E, M0) Init −0.02 → Memorisierung 0.46 → nach Grokking 0.19;
  vorab festgelegte Bestätigung an 10–19 ([[experiments/EXP-029-memo-imprint-random/README|EXP-029]]): Einprägung 10/10
  (ρ 0.42), Verblassen bis gen + 25 nur 8/10 → *teilweise*. Die frühere EXP-015-Aussage „M0 sagt K voraus“ ist damit
  wahrscheinlich ein Rest dieser Einprägung, der die Generalisierung teilweise überlebt.
- **Korrektur nach Codex-Angriff (09:57, `EXP-029/codex_conclusion_review_2026-09-26.txt`), übernommen:** Belegt ist nur:
  W_E ist vor der Generalisierung **spezifisch** mit der eigenen Trainingsmaske ausgerichtet (eigene 0.42 / 0.47 gegen
  fremde 0.02 / −0.02, je 10/10). **Nicht belegt:** dass die Generalisierung den Abdruck löscht (das Maximum liegt in
  allen Seeds vor der Generalisierung, teils um den Memorisierungsbeginn; eher allmähliches Abklingen, Fenster und
  Endpunkt sind ungleich aggregiert) und dass „M0 → K“ ein Rest ist (dafür fehlt ein Überlebens-/Mediationstest →
  [[experiments/EXP-030-imprint-residue/README|EXP-030]]). Die beiden Sätze oben („Generalisierung verdrängt“,
  „wahrscheinlich ein Rest“) gelten bis dahin als Hypothesen, nicht als Befunde.
- **EXP-030 (09:58):** Mediation vorab festgelegt: M0 → K ρ 0.24, gegeben W_E bei Schritt 250 nur 0.04 (10/10, p = 0.001)
  → *Rest gestützt*: Die Maskenwirkung auf K läuft über den frühen Abdruck. Offen bleibt nur der Abbau-Teil von N13.

## N14: Kritische Periode der Frequenzwahl im Transformer: Schrittzahl oder Lernratenplan? #neu/kandidat

- **Beobachtung (Sitzung 8, EXP-020 Seed 30, beschreibend):** Datenwechsel F → G nach t Schritten, danach 2000 G-Schritte: Die
  Frequenzwahl folgt ab t ∈ (25, 50] dauerhaft F; ab t = 150 ist K identisch mit „nur F“. Frage: Verschiebt ein Warmup diese
  Periode? → [[experiments/EXP-035-warmup-lockin/README|EXP-035]].
- **Suche 2026-09-26 13:48:** „grokking modular addition critical period data distribution shift early training frequencies fixed
  switch training set“, „learning rate warmup delays critical period feature commitment early training“. Nächstverwandt:
  Achille et al. 2019 (https://arxiv.org/abs/1711.08856) und Kleinman et al. 2023 (https://arxiv.org/abs/2308.12221), kritische
  Perioden allgemein; Kosson, Messmer & Jaggi 2024 (https://arxiv.org/abs/2410.23922): Warmup wirkt, weil es die anfangs zu großen
  (winkelmäßigen) Updates von AdamW begrenzt, passt zur Vermutung hinter EXP-035; „Mechanistic Insights into Grokking from the Embedding Layer“ (Autoren nicht geprüft)
  https://arxiv.org/abs/2505.15624 (Embedding-Dynamik beim Grokking, keine Frequenzwahl, kein Datenwechsel). Ein
  Datenwechsel-Eingriff, der die *Identität* der gelernten Fourier-Frequenzen als Marker einer kritischen Periode benutzt, und
  dessen Verschiebung durch Warmup: **nicht gefunden** (vorläufig; Google Scholar/OpenReview nicht gezielt).


## N15: Widersprüchliche frühe Daten geben die Frequenzwahl an die Initialisierung zurück #neu/kandidat

Beobachtung (EXP-020 Nachtrag d, Seeds 30–32, Exploration): Wechselt der Split vor der Festlegung (t ≤ 50), enthält das Endnetz
Frequenzen außerhalb F ∪ G ∪ 2k ∪ K_nurF ∪ K_nurG, mit kleinen Init-Rängen (Median 8 von 56). Kausaltest:
[[experiments/EXP-036-init-conflict/README|EXP-036]] (neue Init, gleicher Split), Vorhersage an frischen Seeds: EXP-020 Nachtrag d.
**Literatur (Suche 2026-09-26 ~15:00 Berlin, WebSearch „modular addition grokking data distribution shift early training
initialization frequencies conflicting training sets“, „critical learning period data switch … grokking plasticity primacy“):**
- He, Wang, Chen, Yang 2026, https://arxiv.org/abs/2602.16849: Zweischicht-Netz, Frequenzen konkurrieren je Neuron, Gewinner
  durch Init-Betrag und Phasenausrichtung („Lottery Ticket“). → Dass die Init Frequenzen auswählt, ist **bekannt**.
- Lyle, Sokar, Pascanu, György 2025, https://arxiv.org/abs/2507.20057: Primacy Bias bei nichtstationären Daten, Verbindung zu
  Grokking, Abhilfe durch höhere effektive Lernrate; laut Abstract keine Frequenzmessung nach Datenwechsel. Relevant auch für
  EXP-020/N14 (kritische Periode).
- https://arxiv.org/abs/2510.09687 (kritische Lernperioden; laut Abstract: Plastizitätsverlust nach Defizit-Daten, Abhilfe
  durch zyklischen Lernratenplan; keine modulare Arithmetik, keine Fourier-Merkmale, kein Schritt-Timing).
- Zusatzsuche (2026-09-26 ~15:16, „grokking modular addition change training set mid-training which Fourier frequencies
  persist critical period steps“): nur allgemeine Grokking-/Fourier-Arbeiten (Nanda et al. 2023, He et al. 2026, AGF
  arXiv 2506.06489), nichts zu Datenwechsel mit Frequenzmessung.
**Stand 2026-09-26 (EXP-020 Nachtrag d, frische Seeds 33/34):** Init-Deutung **nicht bestätigt** (P-d1 1/2, P-d2 verfehlt, Rang 34).
Fremde Frequenzen bei frühem Wechsel: 4/5 Seeds, Ursprung offen. Direktere Tests: EXP-036 (Init-Wechsel), EXP-037 (Wechselspiel).
**Stand nach EXP-037:** Konfliktfrequenzen je Seed reproduzierbar und funktional; neue Konkurrenzhypothese „gemeinsame frühe
Unterstützung durch beide Datensätze“ (EXP-036 Nachtrag b, P36b).
Nicht gefunden (vorläufig, nur Abstracts): dass **widersprüchliche Splits vor der Festlegung** die Wahl zur Init zurückgeben,
also ein Zusammenspiel Split-Signal ↔ Init-Lotterie, messbar über den Wechselzeitpunkt. Einordnung: Kandidat, Teil bekannt.

## N16: Wo sitzt die Festlegung der Frequenzwahl? Teil-Rücksetzen nach der kritischen Periode #neu/kandidat

Idee (Sitzung 9): Nach der Festlegung (EXP-020, t = 150) nur W_E bzw. nur den Rest auf die Init zurücksetzen und dann auf
dem Konkurrenz-Split G weitertrainieren. Zeigt, ob die Wahl im Embedding oder in den nachgelagerten Gewichten gespeichert ist.
Versuch: [[experiments/EXP-038-where-lockin/README|EXP-038]].
**Literatur (Suche 2026-09-26 16:25 Berlin, „reset embedding layer vs reinitialize other layers localize learned features grokking
modular arithmetic where are Fourier features stored“):** arXiv 2609.18078 (Komponenten-Transfer zwischen Operationen,
Beschleunigung vs. Stabilität, laut Abstract keine Frequenzmessung), arXiv 2505.15624 (Rolle des Embeddings beim Grokking,
seltene Tokens, kein Rücksetzen), He et al. 2026 (Init-Lotterie). Teil-Resets sind aus RL bekannt (Primacy Bias, Resets der
letzten Schichten); nicht gefunden (vorläufig): Lokalisierung der Frequenzwahl durch Teil-Rücksetzen nach einem Datenwechsel.

## N17: Festlegung der Frequenzwahl auf einer „Lernraten-Uhr“ (aufsummierte Lernrate statt Schrittzahl) #neu/kandidat

- **Beobachtung (Sitzung 10, beschreibend, ein Seed):** EXP-035 Seed 30 mit Warmup: Festlegung in (100, 150], vorab aus
  Λ(n) = n(n+1)/400 ∈ (25, 50] erwartet (ohne Warmup (25, 50] in 5/5 Seeds, EXP-020). Frage: Hängt der Zeitpunkt allgemein an
  Λ = Σ lr (unabhängig von der Form des Plans)? Test mit gleichmäßiger Skalierung: [[experiments/EXP-039-lr-clock/README|EXP-039]].
- **Suche 2026-09-26 17:44:** siehe EXP-039-README. Nächstverwandt He et al. 2026 (https://arxiv.org/abs/2602.16849,
  Frequenz-Lotterie über Init-Spektrum und Phasenausrichtung, auch relevant für N15/EXP-036), Tan et al. 2026
  (https://arxiv.org/abs/2606.05863, zwei Uhren im Grokking), Achille et al. 2019. **Nicht gefunden** (vorläufig).
- **Nachtrag zu N15 (Sitzung 10):** He et al. 2026 beschreiben (laut Abstract) im zweischichtigen Netz, dass Init-Betrag und
  Phasenausrichtung den Frequenzwettbewerb entscheiden. Das stützt die Init-Deutung von N15 als plausible Vorannahme; EXP-036
  prüft sie im Transformer unter Datenkonflikt, was dort nicht behandelt wird.

## N18: Festlegung als Amplitudenschwelle: Datensignal gegen Init-Amplitude #neu/kandidat

- **Idee (Sitzung 10, aus gespeicherten EXP-035-Strecken, grob):** Die Frequenzwahl bleibt offen, solange das datengetriebene
  Signal in W_E unter der Init-Amplitude der Konkurrenzfrequenzen liegt, und fällt, wenn es sie einholt. Unter Adam wächst die
  Strecke ∝ Σ lr, das erklärte die Λ-Uhr (N17) und verbände sie mit N15 (Init entscheidet bei Konflikt) und mit der
  Frequenz-Lotterie von He et al. 2026 (https://arxiv.org/abs/2602.16849). Test: [[experiments/EXP-040-we-init-scale/README|EXP-040]]
  (Init-Skala s verschiebt das Λ-Fenster um den Faktor s), zusammen mit [[experiments/EXP-039-lr-clock/README|EXP-039]].
- **Suche 2026-09-26 18:02 (WebSearch/WebFetch):** „initialization scale determines which features are learned early training
  signal exceeds initialization noise feature selection timing Adam“, „grokking initialization scale embedding Fourier frequency
  selection lottery initial magnitude modular addition“. He et al. 2026 (https://arxiv.org/abs/2602.16849, OpenReview
  https://openreview.net/forum?id=Qc4RLl7t3S): Lotterie **innerhalb jedes Neurons** eines Zweischichtnetzes, Gewinner nach
  Init-Betrag und Phasenfehlstellung, Theorie im Gradientenfluss bei kleiner Init; **kein Zeitpunkt abgeleitet**, keine
  Abhängigkeit von Lernrate oder Init-Skala quantifiziert, keine Split- oder Datenwechsel-Abhängigkeit (laut Volltext-Auszug).
  „No More Adam“ (Autoren nicht geprüft) (https://arxiv.org/abs/2412.11768): Gradienten-SNR bei der Init, andere Frage. Ergebnis:
  **nicht gefunden** (vorläufig). Weiter nachholen: „initialization scale feature selection
  timing“, „signal-to-init ratio critical period“, „lazy to rich transition init scale grokking“ (Kumar et al. 2023,
  https://arxiv.org/abs/2310.06110, verbindet Init-Skala mit dem Grokking-Zeitpunkt, nicht mit der Frequenzwahl).

## N19: Frequenzen „programmieren“ durch einen kurzen Vorlauf auf einer anderen Trainingsmenge #neu/kandidat

- **Idee (Sitzung 10):** Wenn die Wahl nach Λ ≈ 50 festliegt (EXP-020), sollte ein 150-Schritte-Vorlauf auf einem konstruierten
  Split die Frequenzen eines danach normal (Zufallssplit) trainierten Netzes festlegen; offen ist, ob ein spektral schwacher Split
  genauso fest prägt. Test: [[experiments/EXP-041-imprint/README|EXP-041]].
- **Suche 2026-09-26 18:05:** siehe EXP-041-README. Nächstverwandt **LeDoux 2026** (https://arxiv.org/abs/2603.25047):
  Minibatch-Reihenfolge bestimmt die Grundfrequenz (feste Trainingsmenge, kein Wechsel, keine Festlegungszeit). **Nicht gefunden**
  in der hier gestellten Form (vorläufig). LeDoux ist auch für N3/N14/N17 die nächstverwandte Arbeit und dort nachzutragen.

## N20: Datengepflanzte Frequenzen als Prüfstand mit bekannter Wahrheit für Interpretierbarkeitsmethoden #neu/kandidat

- **Idee (Sitzung 10, ungeprüft):** EXP-016 (konstruierter Split gibt die Frequenzen vor, 10/10) und ggf. EXP-041 (Vorlauf prägt
  sie) erlauben Netze, deren Fourier-Frequenzen **vor dem Training festgelegt** sind, und zwar nur über die Daten, bei sonst
  gewöhnlichem Training (kein Hilfsverlust, keine kompilierten Gewichte). Das ergäbe einen Prüfstand mit bekannter Wahrheit:
  Findet eine Methode (automatische Fourier-Suche, SAE-Merkmale, Schaltkreis-Entdeckung) genau die gepflanzten Frequenzen?
  Fehlerraten lassen sich zählen, weil die Wahrheit bekannt ist.
- **Suche 2026-09-26 18:16:** „interpretability benchmark models with known ground truth circuits trained naturally InterpBench
  Tracr planted features“. Nächstverwandt: InterpBench (Gupta et al. 2024, https://arxiv.org/abs/2407.14494): 17 halbsynthetische
  Transformer, per Strict-IIT an Tracr-Schaltkreise angeglichen (Hilfsverlust); TracrBench (https://arxiv.org/abs/2409.13714).
  Unterschied: dort wird die Struktur über einen Trainingsverlust erzwungen, hier nur über die Trainingsmenge. **Nicht gefunden**
  in dieser Form (vorläufig). Grenze: Nur die Frequenz-*Identität* ist gepflanzt, nicht der ganze Schaltkreis; die 2k-Oberwellen
  (EXP-021/028) sind ein bekannter Störfaktor, den ein solcher Prüfstand mitliefern müsste.
- **Nächster Schritt (klein):** an vorhandenen EXP-016-Läufen prüfen, ob eine Standard-Fourier-Analyse der Studie (Top-5 von W_E)
  und eine Neuronen-Analyse (dominante Frequenz je MLP-Neuron) die gepflanzten Frequenzen gleich gut finden. Erst danach entscheiden.

**Nachtrag zu N14/N17 (Sitzung 10):** Nächstverwandte Arbeit ist auch dort LeDoux 2026 (https://arxiv.org/abs/2603.25047,
Minibatch-Reihenfolge bestimmt die Grundfrequenz; keine Festlegungszeit, kein Wechsel, keine Lernratenabhängigkeit).

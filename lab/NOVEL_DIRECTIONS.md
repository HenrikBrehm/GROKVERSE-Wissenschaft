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

- **Nachtrag Sitzung 30 (19:12):** Post-hoc-Beobachtung an EXP-047: 20/20 konstruierte gegen 0/20 gemischte Arme (gleiche Token-Häufigkeiten, gleiche Init) generalisieren innerhalb von 2000 Schritten, Testmengen sind Komplemente. EXP-018 auf die GPU gestellt (Nachtrag c), rechnet in der Nacht 27./28. Nachsuche (1 Anfrage, s. JOURNAL Sitzung 30): nichts Einschränkendes. Nachsuche mit 21 Anfragen: [[paper/lit_grokking_speed_2026-09-27]]. Teilweise bekannt: Datenauswahl über Token-Häufigkeiten beschleunigt (AlQuabeh et al. 2025). Konzentration des Paarspektrums nicht gefunden (vorläufig). #neu/bekannt (teilweise)
- **Nachtrag Sitzung 31 (19:36, gemessen; post hoc, keine neue Suche):** Dosis-Wirkung an gespeicherten Läufen mit gleicher Init, Testmenge und Größe: ε 8 / 2 / 1 → Generalisierung nach 425–450 / 700–900 / nicht bis 2000 Schritte, strenge Ordnung in 4/4 Seeds (`EXP-042/posthoc_speed_dose.py`). Innerhalb von ε = 2 (P1) nur zwischen den Seeds ein Zusammenhang, nicht gepaart innerhalb der Init (`lab/confirm/speed_posthoc_share_within.py`). Vorschlag: Dosis-Trend als Hypothese in [[confirm/R5_REGISTRATION_DRAFT|R5]].

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
- **Ergebnis (Sitzung 21, 2026-09-27, Pilot n = 5):** *redundant* 5/5. W_E allein oder der Rest allein genügt, und der Rest schreibt die F-Wahl sogar in ein auf die Init zurückgesetztes W_E zurück ([[experiments/EXP-038-where-lockin/README|EXP-038]]). Die Frage „wo sitzt sie“ hat damit die Antwort „nicht an einem Ort“. Schärfere Folgefrage: Welcher Teil des Rests genügt, und gilt das schon bei t = 25?
- **Nachsuche 2026-09-27 04:52 (WebSearch, „reinitialize embedding layer relearn same features downstream layers restore representation grokking modular addition Fourier frequencies“):** nächstverwandt weiter arXiv 2505.15624 (Embedding als Auslöser des Grokkings), arXiv 2507.11645 (Embeddings/Dropout auf dem Weg zum Grokking), He et al. 2026 (https://arxiv.org/abs/2602.16849, Frequenz-Lotterie). Kein Rücksetz-Versuch nach Datenwechsel gefunden → weiterhin *nicht gefunden (vorläufig)*.

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
- **Nachtrag Suche 2026-09-27 (Sitzung 24, WebSearch):** „Adam optimizer sign-like updates feature amplitude grows linearly competition early features persist after distribution shift primacy bias theory“.
  Nächstverwandt: Primacy Bias (Nikishin et al. 2022, https://ar5iv.labs.arxiv.org/html/2205.07802), frühe Trainingsphase prägt die Anpassung an Verteilungswechsel (https://arxiv.org/pdf/2403.15210),
  Adam als vorzeichenartiges Verfahren (https://arxiv.org/pdf/2507.06464), Grokking unter Nichtstationarität (Lyle et al. 2025, https://arxiv.org/html/2507.20057). **Weiter nicht gefunden (vorläufig):**
  eine quantitative Festlegungszeit, die aus „Adam-Wachstum ∝ Λ gegen Init-Amplitude der Konkurrenz“ folgt. EXP-040 ist der vorab festgelegte Test; EXP-075 prüft, ob die Festlegung ohne Attention auftritt.

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

## N21: Diskrete Endzustände der Frequenzwahl je Seed (Attraktor-Katalog) #neu/kandidat

- **Beobachtung (Sitzung 10, post hoc, 58 Läufe, Seeds 30–34):** Verschiedene Eingriffe (Datenwechsel zu verschiedenen Zeiten,
  Warmup, Wechselspiel) enden je Seed in wenigen, teils exakt gleichen Top-5-Mengen; exakte Übereinstimmung auch zwischen Eingriffen
  bei ähnlichem Λ. Frage: Ist die Menge der erreichbaren Endzustände je (Init, Splitpaar) klein und durch Λ beim Wechsel
  parametrisiert? Erster Test: EXP-035 Nachtrag c (P35d, Seed 32). Literatur: noch nicht gezielt gesucht.
- **Suche 2026-09-26 18:21:** „modular addition transformer learned frequency set discrete solutions basin of attraction training
  perturbation same seed converges same Fourier frequencies“. Gefunden: Frequenzen variieren über Seeds und Optimierer (z. B.
  https://arxiv.org/abs/2606.17399, Discrete-Log Clock; He et al. 2026). Eine Untersuchung, ob **bei fester Init und festen Daten**
  verschiedene Trainingseingriffe in wenige, exakt wiederkehrende Frequenzmengen münden: **nicht gefunden** (vorläufig).
- **Nachtrag (18:26, nach Codex):** Überschrift und Deutung sind zu stark. Belegt ist nur eine **unkalibrierte Top-5-Kollision**: zwei
  exakte Übereinstimmungen von Mischzuständen über verschiedene Eingriffe, post hoc gesucht, ohne Zufallsvergleich; die Verdichtung
  entsteht größtenteils durch die Plateaus „nur F“/„nur G“. „Wenige diskrete Zustände“ und „Attraktor“ sind **nicht** gezeigt.
  Nötig wären: Plateaus ausschließen, Vergleiche vorab festlegen, seed-spezifische Zufalls-Null mit Mehrfachkorrektur, kontinuierliche
  Spektren oder Verhalten statt Top-5, Störungs-/Neustart-Tests. Bis dahin: Kandidat mit niedriger Priorität.

## N22: Festlegung als Wettlauf „Vorsprung gegen Split-Neigung“ (H42) #neu/kandidat

- **Überlegung (Sitzung 10, 18:27, ohne neue Daten):** Jede Frequenzmenge löst dieselbe Aufgabe (a + b mod p); F und G sind nur
  verschiedene Stichproben derselben Tabelle. Der Split *neigt* die Wahl (EXP-015/016), er erzwingt sie nicht. Nach dem Wechsel kann
  das Netz G mit den schon angelegten F-Frequenzen lernen; die G-Neigung verstärkt dann eher die vorhandenen als neue Frequenzen.
  **H42:** Festgelegt ist die Wahl, sobald der Amplitudenvorsprung der F-Frequenzen größer ist als der Vorteil, den die G-Neigung den
  G-Frequenzen pro Schritt verschafft. Folgerungen: (a) stärker konzentriertes G (größeres eps in `make_splits.py`) → spätere
  Festlegung; stärker konzentriertes F → frühere; (b) für EXP-041 P41b (schwacher Split R als Vorlauf, starker E danach) eher
  *überschrieben* oder *gemischt* als *geprägt*; (c) verträglich mit H40 (Vorsprung wird relativ zur Init-Amplitude gemessen).
- **Skizze eines Tests (nicht festgelegt):** EXP-020-Protokoll mit G-Splits eps ∈ {1, 2, 4} bei festem F (eps 2), Gitter wie EXP-020,
  Seeds 30–32; Vorhersage H42: hi(eps = 4) > hi(eps = 2) > hi(eps = 1). Konkurrenz (reine Λ-Uhr): gleiches Intervall.
- **Literatur (Suche 2026-09-26 18:26):** Kunin et al. 2025, Alternating Gradient Flows (https://arxiv.org/abs/2506.06489, NeurIPS 2025):
  Bei kleiner Init lernen (quadratische) Zweischichtnetze Fourier-Merkmale nacheinander in absteigender Koeffizientengröße, ein
  aktiviertes Merkmal bleibt. Einordnung (Spekulation): Nach dem Wechsel erklären die schon aktiven F-Merkmale den G-Rest weitgehend
  (gleiche Aufgabe), sodass kein G-spezifisches Merkmal mehr genug Nutzen hat, um zu aktivieren; das wäre H42 in AGF-Sprache.
  Datenwechsel und Split-Neigung behandelt AGF laut Abstract nicht. H42 in dieser Form: nicht gefunden (vorläufig).

**Nachsuche zu N14 (Kernbefund EXP-020, Sitzung 10, 18:40):** „grokking critical period modular arithmetic early training data swap
which features irreversible first steps transformer 2026“, „openreview grokking representation fixed early training switch dataset
mid-training Fourier frequencies persist“. Neu gesehen: „Where Grokking Happens: Distributed Utility and Fourier Recoding Without a
Module Switch“ (https://arxiv.org/abs/2609.17571, Sept. 2026; laut Abstract *wo* im Netz das Grokking stattfindet, kein Datenwechsel,
keine Festlegungszeit); „Circuit Synchronization Precedes Generalization“ (https://arxiv.org/abs/2606.12966, nicht geprüft);
„First-Passage Prediction of Grokking Delay under AdamW“ (https://arxiv.org/abs/2605.18845, Grokking-*Zeitpunkt*, nicht die
Frequenzwahl; nicht geprüft). Ergebnis: Die EXP-020-Frage (kausale Festlegungszeit der Frequenzwahl per Datenwechsel) bleibt
**nicht gefunden** (vorläufig; Google Scholar weiterhin nicht direkt durchsucht).

**Google Scholar (erstmals direkt, 18:49):** Abfrage „grokking modular addition "data switch" OR "switching the training set" frequencies
early training“. Einziger gemeldeter Treffer: Liu, Paquette & Sous 2026, „Spectral Lens“ (https://arxiv.org/abs/2605.05683). Im
HTML-Volltext geprüft: modulare Arithmetik nur als statisches Spielzeugmodell, **kein** Datenwechsel mitten im Training und keine
Festlegungszeit (die Zusammenfassung des Abruf-Werkzeugs hatte „data switch“ fälschlich als Inhalt angegeben). Einordnung von N14
unverändert: nicht gefunden (vorläufig).

**Nachtrag zu N14/N22 (18:51):** Nach der Festlegung (Wechsel bei 150) wachsen unter G-Daten die F-Frequenzen wie unter F weiter,
die G-Ziele schrumpfen (5/5 Seeds, beschreibend). Einschränkung: F/G teilen ≈ 73 % der Paare; die Festlegung ist bisher nur gegen
einen Teilwechsel (≈ 27 %) gezeigt; EXP-041 (≈ 63 % Wechsel) ist der härtere Test.

**Auffälligkeit zu N22 (18:54, post hoc, beschreibend):** Nach der Festlegung liegen die G-Zielfrequenzen unter G-Training fast immer
**niedriger** als unter fortgesetztem F-Training (t = 150: 39/40; t = 400: 33/40; t = 1000: 25/35; EXP-037 C_F100: 24/24). Die
naheliegende Erklärung (schnelleres F-Wachstum) hält nicht (F höher nur in 13/40 bei t = 400). Ungeklärt; Kandidat für eine
eigene Frage, falls es sich in EXP-041/042 wiederholt.

- **Erklärungskandidat (18:55, Spekulation, ungeprüft):** „Adam-Verdrängung“: Der Verlustsprung beim Wechsel (Seed 30: 0.04 → 1.65,
  Seed 31: 0.02 → 1.23; binnen ≈ 20 Schritten abgebaut) erzeugt große Gradienten in F-Richtung. Adams zweites Moment je W_E-Eintrag
  steigt (die Einträge mischen alle Frequenzen), der normierte Schritt für die kleinen G-Anteile sinkt, der entkoppelte Weight Decay
  bleibt gleich: G schrumpft schneller. Vorhersage: unter SGD ohne Momente keine zusätzliche Unterdrückung; ein kleinerer Verlustsprung
  (späterer Wechsel) gibt schwächere Unterdrückung (passt qualitativ zu 39/40 → 33/40 → 25/35). Test wäre ein EXP-020-Wechsel mit SGD in
  der G-Phase. Korrektur: `--opt2 gd` gibt es nur im EXP-033-Trainer (`train_opt.py`, anderes Modell), nicht in `freq_ban.py`;
  für den Transformer müsste die Option erst gebaut werden. Nicht festgelegt.

- **Suche zur „Adam-Verdrängung“ (18:56) #neu/bekannt (als allgemeiner Mechanismus):** „Adam second moment large gradient suppresses
  small features weight decay forgetting after distribution shift loss spike“. Der allgemeine Effekt ist beschrieben: Ein großer
  Gradient bleibt über viele Schritte im zweiten Moment und dämpft die normalen Updates („Second-Moment Memory in Coordinatewise Adam“,
  https://arxiv.org/abs/2608.15824; ähnlich „Adaptive Preconditioners Trigger Loss Spikes in Adam“, https://arxiv.org/abs/2506.04805).
  Unsere Erklärung der G-Unterdrückung wäre eine Anwendung dieses bekannten Effekts; neu wäre höchstens die Beobachtung selbst
  (Frequenzwahl nach Datenwechsel). Erklärung weiterhin ungeprüft.

## N23: Datensteuerung der Charaktere bei Gruppenoperationen (Multiplikation mod p über den diskreten Logarithmus) #neu/kandidat

*Sitzung 11, 2026-09-26.* Frage: Lässt sich bei Multiplikation mod p, die das Netz in der Log-Basis (Charaktere von Z_{p−1}) löst,
die Wahl der Charaktere durch einen in Log-Koordinaten konstruierten Trainingssplit vorgeben, wie bei Addition (EXP-016)? Wenn ja,
wirkt der Hebel über die Gruppenstruktur der Aufgabe, nicht über die Zahlendarstellung. Test: [[experiments/EXP-043-generalize-steering/README|EXP-043]].
**Suche (2026-09-26):** WebSearch „grokking modular multiplication discrete logarithm Fourier features training data selection controls
learned frequencies“ und „arXiv 2026 grokking which frequencies learned depend on training set subset modular arithmetic group“.
Nächstverwandt: „The Discrete-Log Clock: How a Transformer Learns Modular Multiplication“ (https://arxiv.org/abs/2606.17399; im
Volltext per Abrufwerkzeug geprüft: 30 % Daten ohne Nullpaare, Mechanismus in 80 % der Seeds, Schlüsselfrequenzen je Seed
verschieden, **keine** Untersuchung, was die Wahl bestimmt, kein Dateneingriff); Chughtai et al. 2023 (Gruppendarstellungen,
universell); He et al. 2026 (https://arxiv.org/abs/2602.16849, Init-Lotterie, Addition). *Einordnung:* nach unserer Suche nicht
gefunden (vorläufig; Abruf-Zusammenfassung, Volltext nicht selbst vollständig gelesen).

## N24: Datensteuerung der Irreps in nicht-abelschen Gruppen (Diedergruppe D₅₉) #neu/kandidat

*Sitzung 12, 2026-09-26.* Frage: Gibt die Auswahl der Trainingspaare auch bei einer **nicht-abelschen** Gruppenverknüpfung vor, welche
(mehrdimensionalen) Irreps das Netz lernt? Anlass: Multiplikation und andere Moduli sind für dieses Modell nach Token-Umbenennung
zyklisch (Sitzung 11, Zyklus 5), also kein neuer Aufgabentyp. Nicht-abelsches Analogon des Masken-Spektrums: Leistung
2·‖Σ_t N(t) ρ_k(t)‖²_F der Paar-Indikatoren je Ausgabe. Test: [[experiments/EXP-046-dihedral-steering/README|EXP-046]].
**Suche (2026-09-26, 19:40 Berlin):** WebSearch „grokking group composition which irreducible representations learned training data
distribution arXiv“, „toy model of universality Chughtai group composition irreps learned seeds dihedral S5“, „"non-abelian" group
multiplication neural network training set sampling biases which representation is learned grokking dihedral“, dazu Abstract-Abruf
von https://arxiv.org/abs/2606.02993 (He et al. 2026: Auswahl durch Init, keine Datenmanipulation laut Abstract) und
https://arxiv.org/abs/2602.03655 (Marchetti et al. 2026: Reihenfolge nach Fourier-Statistik der *Eingabekodierung*). Chughtai et al.
2023 (https://arxiv.org/abs/2302.03025): welche Irreps gelernt werden, variiert, Ursache offen. *Einordnung:* nach unserer Suche nicht
gefunden (vorläufig; nur Abstracts geprüft). Folgekandidat bei positivem Ergebnis: S₅ (Irreps sehr verschiedener Dimension 1–6).

## N25: Datensteuerung der Frequenzen bei nicht-modularer Addition #neu/kandidat

*Sitzung 13, 2026-09-26.* Frage: Erzeugt ein konstruierter Split auch bei gewöhnlicher Addition a + b (keine Gruppe auf den Token,
bekannte Lösung: Zahlengerade, Liu et al. 2022, https://arxiv.org/abs/2205.10343) die vorgegebenen Fourier-Frequenzen in W_E?
Test: [[experiments/EXP-048-intadd-steering/README|EXP-048]] (Log-Leistungskontrast Δ_pow, an EXP-016 kalibriert: 8.4, 10/10).
Zusatzidee: Wenn ja, konkurrieren Zahlengerade und aufgezwungene Uhr; das R²-Maß zeigt, ob der Split die Gerade verdrängt.
**Suche (2026-09-26, 20:04–20:06 Berlin):** siehe EXP-048-README (drei Suchanfragen; Liu et al. 2022, Zhou et al. 2024
https://arxiv.org/abs/2406.03445, Chen et al. 2026 https://arxiv.org/abs/2607.07066). *Einordnung:* nach unserer Suche nicht gefunden
(vorläufig; nur Abstracts/Suchtreffer).

*Nachtrag zu N24/K2 (Sitzung 13, 2026-09-26 20:18 Berlin):* He et al. 2026 (https://arxiv.org/abs/2606.02993) per Abruf der HTML-Fassung
geprüft (Zusammenfassung des Abrufwerkzeugs, nicht selbst vollständig gelesen): §2 „the network observes every pair (g₁, g₂) ∈ G×G“,
also **nur vollständige Trainingsmengen**; welche Irreps gelernt werden, bestimmt dort die zufällige Init (abelsch: gleichverteilt über die
nicht-trivialen Irreps, §5.1). Eine Steuerung über unvollständige oder verzerrte Trainingsmengen behandelt die Arbeit nicht. Einordnung von
K2/N24 unverändert: nach unserer Suche nicht gefunden (vorläufig).

## N26: Phasen-Dissoziation M0 gegen M0c (Sitzung 13, 20:27) #neu/kandidat

Frage: Wählt der Transformer seine Frequenzen nach dem kohärenten Masken-Spektrum M0c (Theorie erster Ordnung, gemeinsamer Pfad beider Positionen) oder nach M0? Splits mit gegenphasigem Kreuzterm heben die Ziele in M0 (Rang 2) und lassen sie in M0c auf Zufallsniveau (Rang 25 von 56) – bei gleichen Token-Häufigkeiten. Vorhersage: Der Transformer folgt anti-Splits nicht, ein MLP mit getrennten W_in-Hälften schon (doppelte Dissoziation). Test: [[experiments/EXP-050-phase-dissociation/README|EXP-050]] (Transformer-Teil). Suche und Einordnung: siehe EXP-050-README (nach unserer Suche vom 2026-09-26 nicht gefunden, vorläufig).

*Literatur zu Paket B / K4 (Sitzung 13, 2026-09-26 21:01 Berlin):* Suche „grokking switch training data mid-training learned Fourier features persist critical period modular arithmetic“. Nächstverwandt: *What Can Grokking Teach Us About Learning Under Nonstationarity?* (https://arxiv.org/abs/2507.20057): Netze müssen gelernte Repräsentationen bei Datenänderung überschreiben, eine höhere effektive Lernrate stellt Merkmalslernen wieder her (laut Zusammenfassung; Autoren/Volltext nicht geprüft). Berührt EXP-039 (Lernraten-Uhr) direkt; eine gezielte Steuerung *welcher* Frequenzen über die Trainingsmenge und deren Persistenz nach einem kontrollierten Wechsel wird dort laut Zusammenfassung nicht untersucht. Einordnung von B: vorläufig nicht gefunden; Volltext vor jeder Kernaussage lesen.

*Volltext-Nachtrag (21:03, per Abrufwerkzeug, Zusammenfassung des HTML):* arXiv 2507.20057 ist Lyle, Sokar, Pascanu, György (Google DeepMind). Transformer mit einem Attention-Block auf modularer Addition (x+y mod 117, 20 % Training, 1 Mio. Schritte). Befund: Eine hohe **effektive Lernrate** (Lernrate relativ zur Parameternorm) löst Merkmalslernen aus und erlaubt, frühe Merkmale zu ersetzen; Grokking lässt sich auch nach Hunderttausenden Schritten durch ELR-Wiedererwärmung auslösen (§4.2); Gewichtsprojektion auf konstante Norm beschleunigt die Generalisierung (§4.1). **Keine** Frequenzanalyse, **keine** Zusammensetzung der Trainingsmenge. *Folgerung für uns:* Die ELR ist eine benannte Konkurrenzerklärung für die frühe Festlegung (K4/Paket B): Festlegung wäre dann ein Effekt sinkender ELR, nicht der Datenauswahl. EXP-039 (Lernratenskala) und EXP-040 (W_E-Init-Skala) trennen genau das (18c: zulässig, weil sie zwischen Modellen entscheiden). Einordnung von „Split steuert *welche* Frequenzen, und diese Wahl bleibt nach einem Wechsel“: weiterhin nach unserer Suche nicht gefunden (vorläufig).


## N27: Eine Masken-Theorie erster Ordnung für jede Aufgabe mit Token-Einbettung, vorab eingefroren geprüft (Sitzung 14) #neu/kandidat

Frage: Das Masken-Spektrum M0 (erwartete Frequenzleistung des ersten W_E-Gradienten, nur aus der Trainingsmenge) braucht keine
Gruppe: N_L(t, c) = [(t, ·) ∈ Train mit Ausgabe c] genügt. Sagt es das frühe W_E-Spektrum auch bei anderem Modulus, zusammengesetzter
Gruppe (mul 113 = Z₁₁₂), nicht-abelscher Gruppe (D₅₉, Irreps statt Frequenzen) und nicht-modularer Addition voraus? Umsetzung:
[[experiments/EXP-052-oos-mask-prediction/README|EXP-052]], alle 40 Vorhersagen vor den Läufen per Commit eingefroren, Holm über vier Fälle,
Sekundär M0c gegen M0 gegen Häufigkeiten gegen Init. Literatur (Suche 2026-09-26): eNTK-Merkmalsidentifikation (arXiv 2510.00468, nur
nachträglich), He et al. 2026 (arXiv 2602.16849, 2606.02993: Init-Lotterie bei vollständigen Trainingsmengen). Eine Vorhersage aus der
Zusammensetzung der Trainingsmenge über Aufgabentypen hinweg nicht gefunden; vorläufig, nur Abstracts/Zusammenfassungen.

## N28: Die Trainingsteilmenge aus den Gewichten erkennen, über eine geschlossene Formel (Sitzung 14) #neu/kandidat

Umkehrung von K1: Wenn M0 (nur aus der Trainingsmenge) das W_E-Spektrum vorhersagt, kann man umgekehrt unter Kandidaten-Teilmengen die
tatsächlich benutzte aus den Gewichten wiedererkennen, ohne Detektor-Training und ohne Zugriff auf Ausgaben. Erster Test ohne eigene Läufe:
EXP-052 Nachtrag d (Top-1-Identifikation unter 10 Kandidaten je Fall). Suche 2026-09-26 („identify which training subset was used from model
weights spectral fingerprint dataset inference provenance“): Arbeiten zu Modell-Abstammung über Spektren der Gewichte (z. B.
https://arxiv.org/abs/2608.07786, https://arxiv.org/abs/2511.06390) erkennen das *Basismodell*, nicht die Trainingsteilmenge; „Dataset
Inference“ arbeitet über das Verhalten. Vorläufig nicht gefunden; Spielzeug-Rahmen (algorithmische Aufgaben), Übertrag offen.

*Literatur zu K4 / Paket B (Sitzung 14, 2026-09-26):* Suche „early training commitment features persist after training data distribution
switch small transformer 2026 critical period representation lock-in“. Nächstverwandt: *Critical Windows of Complexity Control: When
Transformers Decide to Reason or Memorize* (https://arxiv.org/abs/2605.04396): ein scharfes Zeitfenster (≈ 25 % des Trainings), in dem
Weight Decay über „Schlussfolgern oder Memorieren“ entscheidet; Lage hängt von der Init-Skala ab; laut Abstract **nicht** bei modularer
Arithmetik und ohne Frequenzen oder Datenzusammensetzung. Unser K4 (Festlegung der Frequenzwahl nach 25–50 Schritten, über die Daten)
bleibt damit vorläufig ungefunden; die Init-Skalen-Abhängigkeit dort passt zur Frage von EXP-040 (W_E-Init-Skala).
*Nachtrag N28 (Sitzung 14):* Simulierte Kapazität bei ρ ≈ 0.45: Top-1 unter 1000 Kandidaten ≈ 0.47 (Zufall 0.001), also grob 9–10 Bit
über die Teilmenge aus 56 Spektralwerten. Falls EXP-052 ρ in dieser Höhe zeigt, wäre ein eigener Versuch mit vielen Kandidaten (und
Schritten nach dem Grokking, wo ρ sinkt) der nächste Schritt; Datenschutz-Lesart (Mitgliedschaft aus Gewichten) nur als Spielzeug-Analogie.

## N29: Frequenzsteuerung über Loss-Gewichte statt über die Auswahl der Paare (Sitzung 14, 22:02) #neu/kandidat

Frage: Die Theorie erster Ordnung sagt, dass nur das *gewichtete* Masken-Spektrum M0_w zählt (Gradient = Σ w(a, b) · …). Dann müsste man die
Frequenzwahl auch steuern können, **ohne Paare zu entfernen**: gleiche zufällige Trainingsmenge, aber Loss-Gewichte w = q(a, b) aus der
EXP-016-Konstruktion. Offline (reine Rechnung, 10 Zielmengen, add 113, ε = 2): Zielanteil in M0 bei Auswahl (EXP-016) 0.193, bei Gewichten auf
einem zufälligen 30-%-Split 0.179, bei Gewichten auf **allen** Paaren 0.986 (die volle Maske ist selbst flach, es bleibt nur das Gewichtsmuster;
gleichverteilt 0.089). **Nutzen:** (1) trennt „welche Paare fehlen“ (samt Komplement-Testmenge) von „wie stark wird gewichtet“, also ein
direkter Test des Mechanismus hinter K2; (2) eine Steuerung, die keine Daten weglässt. **Vorhersage erster Ordnung:** Gewichte auf dem
zufälligen Split steuern etwa so stark wie die Auswahl (Δ_pow ähnlich EXP-016). Gegenhypothese: Die Steuerung hängt am Fehlen von Paaren
(Memorisierungsdruck), dann steuern Gewichte deutlich schwächer. Braucht eine Option `--pair-weights` im gemeinsamen Trainer (Review nach 18c)
und gehört zu Paket A (Mechanismus von P1). Suche 2026-09-26 („per-example loss weighting controls which Fourier features learned modular
addition grokking sample weights“): nur Arbeiten zu Init-Lotterie und Weight Decay (He et al. 2026, https://arxiv.org/abs/2602.16849);
Gewichtssteuerung der Frequenzen nicht gefunden (vorläufig).
*Selbstprüfung N29 (Sitzung 14, reine Rechnung):* Auch die gewichteten Token-Häufigkeiten tragen die Ziele: Zielanteil im Häufigkeitsspektrum
bei Auswahl 0.166, bei Gewichten auf zufälligem Split 0.173, bei Gewichten auf allen Paaren **0.987** (gleichverteilt 0.089); die Gewichte der
Ausgabeklassen bleiben fast gleich (CV 0.004). Die Vollvariante trennt also Paarstruktur und Häufigkeiten nicht. Für einen Mechanismus-Test
braucht N29 dieselbe Kontrolle wie [[experiments/EXP-047-marginal-control/README|EXP-047]] (Gewichte so umverteilen, dass die gewichteten
a/b-Häufigkeiten gleich bleiben, die Paarstruktur aber zerstört ist). Erst nach dem EXP-047-Ergebnis festlegen.
*Literatur zu N27 (Sitzung 14):* Suche „first gradient step predicts learned features alignment early training data-dependent feature
selection theory“. Allgemeine Theorie, dass schon ein Gradientenschritt die erste Schicht auf das Signal der Daten ausrichtet: Ba et al. 2022,
*High-dimensional Asymptotics of Feature Learning: How One Gradient Step Improves the Representation* (https://arxiv.org/abs/2205.01445;
Lehrer-Schüler, Gauß-Eingaben, Rang-1-Spitze); Zwei-Schritt-Erweiterung (https://pith.science/paper/2605.17767). **Einordnung:** Die Idee
„erster Schritt bestimmt Merkmale“ ist bekannt (#neu/bekannt für den allgemeinen Satz). Nicht gefunden (vorläufig): eine geschlossene Formel
für Einbettungstabellen, die aus der *Zusammensetzung einer diskreten Trainingsmenge* die Frequenz-/Irrep-Rangfolge vorhersagt und über
Gruppen und eine nicht-modulare Aufgabe geprüft wird. Das bleibt der Kandidat von N27.

## N30: Integrationsfenster der Frequenzwahl: frühe Schritte addieren sich, spätere skalieren nur (Sitzung 15, 22:50) #neu/kandidat

- **Beobachtung (post hoc, EXP-020/037):** Die F/G-Mischung (π) steht ab Schritt ≤ 250 praktisch fest; ein Fenstermodell (jeder der ersten
  ≈ 50–100 Schritte zählt etwa gleich) gibt Wechsel- und Verschränkungsläufe wieder. Schwach belegt (Gegenprüfung: Konstante 0.5 fast so
  gut für EXP-037, alt5 ohne Trennschärfe).
- **Test, der trennen würde (nicht festgelegt):** Verschränkung mit G zuerst (G-Block, dann F) und ungleichen Blocklängen (z. B. 10 F / 30 G),
  wo Fenster-, Exponential- und Konstantmodell verschiedene π vorhersagen; dichte Spektren (alle 10 Schritte) in den ersten 250 Schritten,
  um „eingefroren“ von „proportional verstärkt“ zu trennen (Top-k-Identität und die übrigen Richtungen, nicht nur π).
- **Literatur (Suche 2026-09-26 22:48):** „The Order Is The Message“ (https://arxiv.org/abs/2603.25047), Critical Learning Periods
  (https://arxiv.org/abs/1711.08856). Ein additives Integrationsfenster für die Frequenzwahl: nicht gefunden (vorläufig).
- **Nachtrag Literatur (22:58):** „A Spectral Theory of Grokking: Weight Decay induces Feature Learning“ (https://arxiv.org/abs/2609.26679,
  laut Abstract): Nach der Memorisierung treibt Weight Decay einen Übergang von lazy zu rich; Fourier-Struktur im NTK wächst weiter, Zeitskala
  lr · wd. Passt zur späten gemeinsamen Verstärkung (π bleibt, Kontrast wächst), sagt aber nichts über Frequenzwahl oder Datenzusammensetzung.


## Nachsuche 2026-09-27 (Sitzung 17, bis 00:24 Berlin, gemessen) zu K2, K4, N29, N30

- **Wie:** Claude-Subagent, 16 WebSearch-Anfragen (u. a. „training data subset determines learned Fourier frequencies modular addition grokking“,
  „critical period early training feature selection grokking“, „data reweighting steers learned features modular addition“,
  „modular addition per-example loss weights induce chosen frequencies“, „openreview 2026 modular arithmetic training set composition controls
  learned frequencies“). Meist nur Abstracts. Ein OpenReview-Treffer (Gf7nZAfiaB) war hinter einer Browserprüfung, nicht geprüft.
  Drei Abstracts habe ich selbst nachgelesen (He et al. 2602.16849, LeDoux 2603.25047, Pracher et al. 2609.26679); die übrigen Angaben stammen vom Subagenten.
- **Ergebnis:** Keine der gesehenen Arbeiten beantwortet K2, K4, N29 oder N30. Einordnung bleibt „nach unserer Suche vom 2026-09-27 nicht gefunden, vorläufig“.
- **Nächstverwandte, mit Abgrenzung:**
  - He, Wang, Chen, Yang 2026, https://arxiv.org/abs/2602.16849 (selbst gelesen): Gewinnerfrequenz je Neuron durch „initial spectral magnitude and
    phase alignment“ bestimmt; Trainingssplit laut Abstract nicht behandelt. **K2 ist die Gegenposition zur reinen Init-Lotterie** und sollte in FINDINGS
    so benannt werden (EXP-012: erster Gradient schlägt Init; EXP-016: Split gibt die Frequenzen vor).
  - LeDoux 2026, https://arxiv.org/abs/2603.25047 (selbst gelesen): Die Grundfrequenz ist das „Fourier dual of the ordering structure“, gleich
    „regardless of initialization or training set composition“. Das ist **kein Widerspruch zu K2** (unsere Läufe sind Full-Batch, ohne Reihenfolge),
    aber eine Grenze: Unter einer strukturierten Reihenfolge könnte die Reihenfolge die Zusammensetzung überstimmen. → Kandidat N31.
  - Pracher et al. 2026, https://arxiv.org/abs/2609.26679 (selbst gelesen, schon unter N30 notiert).
  - He, Wang, Zhang, Chen, Yang 2026, https://arxiv.org/abs/2606.02993 (Gruppenkomposition, Init verteilt Neuronen auf Irreps; laut Subagent, nur verwandt, relevant für EXP-046).
  - Zhou, Zhang, Xu, CiCP 2026, https://www.global-sci.com/cicp/article/view/24634 (Journalfassung; ungleichmäßige Stichprobe erzeugt zuerst „unechte“ Frequenzen; laut Subagent).
  - Sivasankar 2026, https://arxiv.org/abs/2606.12966 (Frequenz-Synchronisation 500–3000 Schritte vor der Generalisierung; nichts zur Wahl; laut Subagent).
  - Ootani 2026, https://arxiv.org/abs/2607.05104 („Grokking Is Conditional and Fragile“: Abdeckung der Trainingsmenge entscheidet, *ob* gegrokt wird; laut Subagent).
  - Zu N29: nur allgemeine Importance-Weighting-Literatur (Übersicht https://arxiv.org/abs/2403.10175: Gewichtung wirkt früh, verblasst später; laut Subagent).
    Das wäre für N29 eine Vorhersage: Loss-Gewichte steuern nur, wenn sie in das frühe Fenster fallen (passt zu K4/N30).

## N31: Reihenfolge gegen Zusammensetzung: Wer bestimmt die Frequenzen, wenn beide etwas anderes vorgeben? (Sitzung 17, 00:24) #neu/kandidat

- **Frage:** LeDoux 2026 findet unter einer strukturierten Datenreihenfolge (Mini-Batches) eine Grundfrequenz, die unabhängig von der Zusammensetzung der
  Trainingsmenge ist. Wir finden unter Full-Batch, dass die Zusammensetzung die Frequenzen vorgibt (K2). Was passiert, wenn eine konstruierte
  Zusammensetzung (Ziele F) mit einer Reihenfolge kombiniert wird, deren Fourier-Dual eine andere Frequenz g ∉ F ist?
- **Konkurrenzmodelle:** (a) Reihenfolge dominiert (LeDoux), (b) Zusammensetzung dominiert (K2), (c) beide erscheinen (Mischung), (d) die Reihenfolge wirkt
  nur über ihre frühen Schritte (Fenster wie N30).
- **Stand:** Nur Idee. Braucht Mini-Batch-Training im Trainer (neue Option, Bauregel „Fingerprint nur bei Abweichung“). Gehört zu Paket A (Grenzen von K2),
  wird erst nach der Pilotnacht gegen die offene Frage in [[FINDINGS]] priorisiert. Vorher LeDoux im Volltext lesen (Reihenfolgekonstruktion, Batchgröße).
- **Volltext LeDoux gelesen (00:24, HTML-Fassung, per Zusammenfassung des Abrufwerkzeugs):** p = 9973, 2-Schicht-Transformer (d 256), AdamW wd 0.1, Batch 256,
  5000 Epochen, 300 000 Trainingspaare (0.3 %). Die Reihenfolge „Stride“ sortiert nach (a mod s, a) mit s = ⌊√p⌋ = 99; Grundfrequenz F = round(p/s) = 101.
  **Die Zusammensetzung wird dort nicht variiert** (alle Strategien mit denselben Trainings- und Testmengen), Full-Batch und ein Konflikt Reihenfolge ↔
  Zusammensetzung werden nicht getestet. Die Abstract-Formel „regardless of … training set composition“ ist also kein Befund gegen K2.
  N31 bleibt offen und wird dadurch schärfer: In unserem Aufbau (p = 113, Full-Batch-fähig) wäre der Stride s = 10 → Frequenz round(113/10) = 11;
  ein Konfliktarm nähme Ziele F ohne 11 und die Stride-Reihenfolge, Kontrollen Stride allein (Zufallssplit) und F allein (Zufallsreihenfolge, gleiche Batchgröße).
  Unterschiede zu LeDoux (Modulus, Datenanteil, Tiefe, Epochenzahl) vor jeder Deutung beachten.

## Nachprüfung 2026-09-27 (Sitzung 20, 01:31 Berlin, gemessen): Zhou, Zhang, Xu gegen K2

- **Frage:** Nimmt „A Rationale from a Frequency Perspective for Grokking“ (CiCP, Juni 2026, https://www.global-sci.com/cicp/article/view/24634) K2 vorweg?
  In der Nachsuche von Sitzung 17 stand dazu nur die Angabe des Subagenten.
- **Selbst geprüft (Seite der Zeitschrift, arXiv-Abstract und HTML-Volltext https://arxiv.org/html/2405.17479, per Zusammenfassung des Abrufwerkzeugs):**
  Die Zeitschriftenfassung ist die Arbeit, die in [[FINDINGS]] schon als Zhou et al. 2024 zitiert ist. Aufgaben: sin(6x) in 1D, dünne Parität (10,[10]) und MNIST.
  **Keine modulare Arithmetik, keine Gruppenoperation.** Eine unzureichende, ungleichmäßige Stichprobe erzeugt „unechte“ (aliasierte) Frequenzen. Das Netz lernt
  sie zuerst. Auf der Trainingsmenge bleiben sie durch Aliasing erhalten, auf der Testmenge sinkt ihre Amplitude, sobald die wahren Frequenzen gelernt sind.
- **Abgrenzung:** Dort hat die Zielfunktion einen festen Frequenzinhalt, und die Stichprobe erzeugt Artefakte *neben* der richtigen Lösung. Bei Addition mod p
  ist jede Frequenzmenge eine gleich richtige Lösung. K2 behauptet, dass die Zusammensetzung *unter gleichwertigen Lösungen auswählt* und die Wahl bleibt
  (EXP-016 misst bei festem Schritt 2000; alle 20 Läufe haben da schon generalisiert, gen 450–1100, Test ≈ 1.0). Das zeigt die Arbeit nicht. Ihr Befund „Stichprobe → Frequenzen, zuerst“ ist aber die nächste
  bekannte Vorarbeit. Beim Einordnen von K1/K2 muss sie ausdrücklich genannt werden (bisher nur als „verwandt, andere Aufgaben“).
- **Einordnung:** K2 bleibt „nach unserer Suche vom 2026-09-27 nicht gefunden, vorläufig“. Neuer Prüfpunkt für Paket A: Bleibt die gepflanzte Wahl auch
  **lange nach dem Grokking** erhalten (Zhou et al. sehen ein Abklingen auf der Testmenge)? *Post hoc an EXP-016 (Sitzung 20, 01:33 gemessen, nur gespeicherte Läufe, beschreibend):* nein, kein Abklingen. Der Anteil der eigenen Ziele an der W_E-Leistung steigt vom
  ersten Messpunkt ≥ gen bis Schritt 2000 (750–1500 Schritte danach) von 0.56 auf 0.82 (20/20 steigen, Δ 0.26 ± 0.07); Ziele des anderen Arms 0.016, Zufall 5/56 = 0.089.
  |Top-5 ∩ T| sinkt leicht (4.3 → 3.9, bekannte 2k-Oberwellen). Grenzen: F/G teilen die Init; nur bis 2000 Schritte. Länger: EXP-045 (MLP, bis 10 000).
  Skript und Zahlen: `lab/experiments/EXP-016-engineered-split/posthoc_postgen_persistence.py/.json`.
  *Kontrolle (Zyklus 2):* Zufallssplit-Läufe der Studie verdichten nach dem Grokking ebenfalls (+0.11 nach 750 Schritten, 10/10). Der Anstieg ist also allgemein.
  Belastbar ist nur „kein Abklingen“, eine Verstärkung durch den Split ist nicht gezeigt (`posthoc_postgen_control.py/.json`).

## Ergebnisse Sitzung 20 (2026-09-27, Pilotnacht auf der GPU) zu N23–N26

Alle Einordnungen bleiben „nach unserer Suche vom 2026-09-26/27 nicht gefunden, vorläufig“. Die Versuche sind Piloten mit 10 Seeds, keine Bestätigung.
- **N23 (Charaktere bei Multiplikation):** [[experiments/EXP-043-generalize-steering/README|EXP-043]] mul 113 *steuerbar* (10/10, p 0.001). Einschränkung: Multiplikation ≈ Z₁₁₂ + Null, also vor allem ein zusammengesetzter Modulus.
- **N24 (Irreps in D₅₉):** [[experiments/EXP-046-dihedral-steering/README|EXP-046]] *steuerbar* (Δ̄ 9.6, Top-3-Δ 6/6 in 10/10). Häufigkeits-Confound dort nicht getrennt.
- **N25 (nicht-modulare Addition):** [[experiments/EXP-048-intadd-steering/README|EXP-048]] *steuerbar* (Δ_pow 2.2 trendbereinigt, 10/10), vor jedem Lernen der Aufgabe (Test 0.23).
- **N26 (M0c gegen M0):** [[experiments/EXP-050-phase-dissociation/README|EXP-050]]: M0c selektiert **und** M0 trägt auch. Die Theorie erster Ordnung stimmt nur halb.
- **N27 (vorab eingefrorene Masken-Theorie):** [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]] trifft in 4/4 unberührten Fällen (Assoziation).
- Vor einer Veröffentlichung nötig: gezielte Nachsuche zu „training set composition selects among equivalent Fourier solutions“ (Stand der Suche: Sitzung 17 und 20), und die P1-Bestätigung.

## N28: Das Gedächtnis der ersten Trainingsschritte für die Frequenzwahl sitzt im Adam-Zustand #neu/bekannt (herabgestuft, EXP-059)

- **Beobachtung (Sitzung 21, 2026-09-27, Pilot [[experiments/EXP-057-optim-reset/README|EXP-057]], 10 bekannte Seeds):** Nach 25 Schritten auf Split A und 2000 auf einem paar-disjunkten
  Split B bleibt ohne Eingriff ein Drittel der A-Präferenz erhalten (P3 bestätigt: π 0.35, A-Ziele 20 % der W_E-Leistung). Wird beim Wechsel nur der AdamW-Zustand gelöscht, fällt π auf 0.11,
  und die A-Ziele liegen unter Zufall (7 %).
- **Frage:** Trägt m (Richtung) oder v (Skala je Koordinate) das Gedächtnis, oder nur die neu startende Bias-Korrektur? Wann geht das Gedächtnis vom Optimierer in die Gewichte über
  (t = 25 gegen 150, vgl. EXP-038)?
- **Alternative Erklärung (vor jedem Anspruch zu prüfen):** Nach dem Reset macht Adam einige vorzeichenartige Schritte von etwa lr je Koordinate. Die könnten die kleine Gewichtsspur
  der ersten 25 Schritte einfach überschreiben, ohne dass im Zustand ein „Gedächtnis“ steckt. Kontrollen: nur m zurücksetzen, nur v zurücksetzen, Schrittzähler beibehalten.
- **Suche 2026-09-27 06:22 (WebSearch, „Adam optimizer state moments carry memory of earlier training data after distribution shift reset optimizer state feature persistence“):**
  nächstverwandt Asadi et al. 2023, Optimizer-Reset in Deep RL (https://arxiv.org/abs/2306.17833); Kontinuierliches Lernen mit weitergeführtem zweitem Moment (https://arxiv.org/abs/2404.02754);
  Übersicht „Training Memory in Deep Neural Networks“ (https://arxiv.org/abs/2601.21624); SPAM, Momentum-Reset (https://arxiv.org/abs/2501.06842). **Nicht gefunden (vorläufig):**
  dass die Persistenz einer datengesteuerten Merkmalswahl (Fourier-Frequenzen) nach einem Datenwechsel im Adam-Zustand liegt.
- **Korrektur (Codex, eingearbeitet 06:31):** Die Deutung „das Gedächtnis sitzt im AdamW-Zustand“ ist **nicht identifiziert**. Ein voller Reset entfernt die A-bedingten Momente **und** startet die Bias-Korrektur neu. Die ersten Schritte danach sind ≈ lr·sign(g) je Koordinate und können die kleine 25-Schritt-Spur überschreiben. Gestützt ist nur: *Eine volle Neuinitialisierung des Optimierers beim Wechsel senkt die spätere A-Persistenz (π 0.30 → 0.11).* „Unter Zufall“ ist nicht signifikant (7.1 % ± 4.7 %, t = −1.2 gegen 8.9 %; selbst nachgerechnet). Das formale Urteil „teilweise“ bleibt als Etikett der Festlegung stehen, ist aber keine additive Zerlegung in Optimierer- und Gewichtsanteil. Nächste Kontrolle: nur m auf 0 setzen (v und Schrittzähler bleiben), dazu die frühen Update-Normen protokollieren; danach „alle Momente zurück, Schrittzähler bleibt“ und ein voller Reset mit angeglichener früher Update-Norm. N28 bleibt **Kandidat**, kein Befund.
- **Folgepilot EXP-058 (06:50):** Nur m löschen (Schrittzähler bleibt, frühe Schritte kleiner als normal) senkt π wie der volle Reset (0.12 gegen 0.11; normal 0.30). Das Überschreiben ist als Erklärung damit unwahrscheinlich. Das erste Moment trägt den größten Teil. Weiter **Kandidat**: Bestätigung an frischen Seeds, Richtungsanalyse, t = 50/150 stehen aus.
- **Herabgestuft nach EXP-059 (Sitzung 22, 07:22):** Das Löschen von m wirkt wie der Verlust von ≈ 6–10 A-Schritten (π_rom(35) = 0.36 ≥ π_normal(25) = 0.30, D = +0.059, 90-%-KI [0.02, 0.09]). Ein eigenes „Gedächtnis im Adam-Zustand“ ist nicht nötig; der Momentum-Schwanz setzt einfach die A-Exposition fort. Das ist Standardwissen über Heavy-Ball-Momentum und **kein Neuheitskandidat** mehr (#neu/bekannt für die Mechanismus-Deutung). Was bleibt, ist die Steilheit der Festlegung (π 0 → 1 zwischen t = 10 und 50) — die gehört zu K4/Programm B, nicht zu N28. Bestätigung der engen Aussage (H1 m-Reset senkt π, H2 Nichtunterlegenheit m@35 gegen normal@25): [[confirm/N28_REGISTRATION|N28]].

## N29: Zwei Regime nach einem frühen Datenwechsel: erst Koexistenz, dann Ausschluss neuer Merkmale #neu/kandidat

- **Beobachtung (Sitzung 22, [[experiments/EXP-062-rate-race/README|EXP-062]], Exploration, Seeds 400–409):** Wechsel nach t ≤ 30 Schritten: Die alten Frequenzen bleiben, die neuen werden fast normal gelernt (Koexistenz).
  Wechsel nach t = 50: Die neuen Frequenzen entstehen kaum (≈ 70× weniger Energie, Ausschluss). Der Übergang liegt weit vor Memorisierung und Generalisierung (Schritt ≈ 900).
  Der Gradient der neuen Daten baut die alte Struktur erster Ordnung sogar ab ([[experiments/EXP-061-grad-alignment/README|EXP-061]]); der Ausschluss entsteht also nicht durch Verstärkung über den neuen Gradienten.
- **Vorab festgelegte Vorhersage an frischen Seeds:** `lab/confirm/n28_regimes.py` (2bdfdaf), Auswertung nach dem N28-Block.
- **Suche 2026-09-27 07:52 (WebSearch):** „early training data switch features coexistence then exclusion new features not learned critical period feature competition modular arithmetic“;
  „warm-starting pretraining brief exposure prevents learning new features later loss of plasticity feature suppression timing“. Nächstverwandt: Achille et al. 2019, kritische Perioden
  (https://arxiv.org/abs/1711.08856); Frankle et al. 2020, frühe Trainingsphase (https://arxiv.org/abs/2002.10365); Shin et al. 2024, DASH, Plastizitätsverlust beim Warm-Start ab ≈ 50 % Vortrainingsgenauigkeit
  über Memorisierung (https://arxiv.org/abs/2410.23495); „On the Occurence of Critical Learning Periods“ (https://arxiv.org/abs/2510.09687). **Nicht gefunden (vorläufig):** ein Übergang von Koexistenz zu Ausschluss
  bestimmter, datengesteuerter Merkmale innerhalb der ersten ≈ 50 Schritte, vor jeder Memorisierung, mit exakter Zerlegung in erhaltene alte und fehlende neue Merkmalsenergie.
- **Nach N28 und Codex (Sitzung 22, 08:34):** Die Vorhersage ist an 30 frischen Seeds erfüllt (29/30, 30/30). Wortlaut enger: koexistenz- bzw. ausschlussartige *Spektralsignaturen* in W_E; funktionale Koexistenz bzw. funktionaler Ausschluss ist nicht geprüft. Nächster Schritt für einen Neuheitsanspruch: funktionaler Test (Ablation der alten bzw. neuen Frequenzen am Endmodell).
- **EXP-064 (Sitzung 22, 09:06, beschreibend, nicht auswertbar 7/10):** Funktional rechnet das Netz nach einem Wechsel bei t = 25 überwiegend mit den **neuen** Frequenzen, bei t = 50 nur mit den alten (10/10). Schärfere Kandidatenfrage: *Innerhalb von ≈ 25 Schritten kippt die funktionale Wahl von „umsteigen“ zu „festhalten“, während alte Spektralenergie in beiden Fällen bleibt.*


## N32: Die Attention hält nach ≈ 50 Schritten die frühe Frequenzwahl fest (Sitzung 23) #neu/kandidat

- **Beobachtung (Pilot [[experiments/EXP-067-exclusion-part/README|EXP-067]], 10 bekannte Seeds):** Setzt man beim Datenwechsel nach 50 Schritten nur W_Q, W_K, W_V, W_O auf ihre Init zurück, lernt das Netz die
  neuen Frequenzen und rechnet mit ihnen; ein MLP-Reset (doppelte Parameterzahl) oder W_U-Reset tun das nicht. Bestätigung [[confirm/N29b_REGISTRATION|N29b]] läuft.
- **Hypothese (ungeprüft):** Die Attention ist nach wenigen Schritten auf die Frequenzen der ersten Daten eingestellt (in diesem Modell ist die Attention periodisch in a und b, Nanda et al. 2023) und leitet
  neue Richtungen in W_E nicht weiter. Prüfbar: Entropie/Periodizität der Attention bei t = 50; Reset nur von W_Q/W_K (Muster) gegen W_V/W_O (Werte).
- **Suche 2026-09-27 (Sitzung 23, WebSearch):** „resetting attention layers restores plasticity transformer loss of plasticity which layer reset“, „grokking modular addition attention layer re-initialization new
  features data distribution shift early training“. Nächstverwandt: Plastizitätsverlust in Transformern geht mit einem Entropiekollaps der Attention einher (Lyle et al., https://clarelyle.com/posts/2025-09-06-plasticity-survey.html;
  Übersicht https://arxiv.org/pdf/2411.04832); Resets einzelner Schichten aus RL/kontinuierlichem Lernen (https://arxiv.org/html/2410.20098v3). Nanda et al. 2023 (https://arxiv.org/abs/2301.05217) zum Mechanismus.
  **Nicht gefunden (vorläufig):** dass ein Attention-Reset schon nach ≈ 50 Schritten den Ausschluss neuer Merkmale bei einem Datenwechsel aufhebt, während MLP- und Unembedding-Reset es nicht tun.
- **Nachtrag (Sitzung 23, EXP-069, Pilot):** Den Ausschluss trägt vor allem der Wertepfad (W_V, W_O; b 0.49), nicht das Muster (W_Q, W_K; b 3.17). Nach dem Wertepfad-Reset nutzt das Netz beide Mengen.


## N33: Teilweises Zurückspulen beim Datenwechsel lokalisiert die Zeitabhängigkeit der Festlegung #neu/kandidat

- **Frage:** Welcher Teil des Netzes trägt, dass eine Frequenzwahl nach 50 Schritten fest ist, nach 25 aber kaum? Werkzeug: beim Wechsel bei t einen Teil samt AdamW-Zustand auf seinen Stand bei R < t
  zurücksetzen, den Rest behalten, weitertrainieren. Versuch: [[experiments/EXP-073-part-rewind/README|EXP-073]] (vorbereitet, Sitzung 24).
- **Suche 2026-09-27 (Sitzung 24, WebSearch):** „rewind subset of layers to earlier checkpoint during training critical period localize which layers rewinding arxiv“, „layer-wise weight rewinding mixed checkpoint
  chimera network continual learning plasticity which layer retains early features arxiv“. Nächstverwandt: **Modul-Kritikalität** (Chatterji et al. 2019, https://arxiv.org/pdf/1912.00528): einzelne Module
  des *fertigen* Netzes auf frühere Epochen zurückspulen, ohne Weitertraining, um Generalisierung zu erklären → das Werkzeug „Modul zurückspulen“ ist **bekannt**. Gewichts-Rewinding beim Pruning
  (Frankle et al. 2020, https://arxiv.org/pdf/2002.10365; Renda et al. 2020, https://arxiv.org/abs/2003.02389); Kritische Perioden (https://arxiv.org/abs/2506.15954); Resets der letzten Schicht
  (https://arxiv.org/abs/2310.07996).
- **Nicht gefunden (vorläufig):** das Zurückspulen eines Teils *samt Optimiererzustand* zum Zeitpunkt eines Datenwechsels mit anschließendem Weitertraining, um zu messen, welcher Teil die
  Zeitabhängigkeit einer Festlegung trägt; dazu die Selbstprüfung „alles zurückspulen = früher wechseln“. Einordnung: neue Anwendung eines bekannten Werkzeugs, keine neue Methode.


## Literatur-Nachtrag zu K2 (Split-Steuerung der Frequenz-/Irrep-Wahl), Sitzung 24, 2026-09-27 #neu/kandidat

- **Suche (WebSearch/WebFetch):** „which irreducible representations are learned group composition neural network depends on training data distribution Chughtai toy model of universality follow-up dihedral“.
- **Nächstverwandt, neu gefunden:** Marchetti, Kunin, Myers, Acosta, Miolane, *Sequential Group Composition* (ICML 2026, https://arxiv.org/abs/2602.03655): Zwei-Schicht-Netze lernen die Aufgabe
  „eine Irrep nach der anderen, in einer Reihenfolge, die die Fourier-Statistik der **Kodierung** bestimmt“ (laut Abstract). Das verbindet Datenstatistik und Irrep-Wahl, aber über die Eingabekodierung,
  nicht über die Auswahl der Trainingspaare. He, Wang, Zhang, Chen, Yang (2026, https://arxiv.org/abs/2606.02993): Neuronen konvergieren zu je einer Irrep, *welche* wird nicht vorhergesagt,
  keine Split-Abhängigkeit (laut Abstract). Chughtai et al. 2023 (https://arxiv.org/abs/2302.03025): welche Irreps gelernt werden, ist je Netz „beliebig“.
- **Einordnung (vorläufig):** Dass Datenstatistik die Reihenfolge/Wahl der Irreps bestimmt, ist theoretisch für die Kodierung gezeigt (Marchetti et al.). **Nicht gefunden:** dass bei festen One-hot-Token
  allein die **Zusammensetzung der Trainingspaare** (Masken-Spektrum M0) steuert, welche Irreps gelernt werden, auch bei D₅₉ und über das Grokking hinaus (P1, EXP-072). Nächster Schritt: Volltext von
  Marchetti et al. prüfen, ob eine nicht-uniforme Paarverteilung dort als Spezialfall der „Kodierungsstatistik“ abgedeckt ist (dann wäre K2 eine Bestätigung ihrer Theorie in einem Transformer, nicht neu).
- **Volltext geprüft (gleiche Sitzung, WebFetch https://arxiv.org/html/2602.03655):** Training **gleichverteilt über alle Sequenzen** („1/2|G|^k ∑_{g∈G^k} …“), keine Teilmengen oder Splits; die
  Reihenfolge folgt der Operatornorm der Fourier-Koeffizienten des festen Kodierungsvektors x (bei One-hot, x = e₁, sind alle Irreps gleichauf); Gradientenfluss mit verschwindender Init, MSE, kein Adam,
  kein Weight Decay, kein Grokking; Gruppen C_p, D_n, C_n × C_n. **Ergebnis:** Eine nicht-uniforme Paarverteilung ist dort nicht abgedeckt. K2 bleibt nach unserer Suche nicht gefunden (vorläufig) und
  ist eine Ergänzung: Bei One-hot-Token, wo die Kodierung keine Irrep bevorzugt, bricht in unseren Versuchen die Zusammensetzung der Trainingspaare (M0) die Gleichheit. Offene Brückenfrage:
  Lässt sich M0 in ihrem AGF-Rahmen als effektive „Kodierungsstatistik“ schreiben (theoretische Arbeit, Programm C)?
- **Skizze (Sitzung 24, ungeprüft, keine Behauptung):** In AGF wird die nächste Irrep über ihren „Nutzen“ am Sattel gewählt, bei kleiner Init also über die Korrelation des ersten Gradienten mit dem
  Irrep-Unterraum. Unsere Herleitung erster Ordnung ([[BEFUND-split-mechanismus]], Sitzung 13) zeigt, dass die Leistung des ersten W_E-Gradienten je Frequenz bei One-hot-Token gerade M0c (Transformer)
  bzw. M0 (MLP) ist. Vermutung: Bei nicht-uniformer Paarverteilung tritt M0 (bzw. `dihedral.mask_power` für D_n) an die Stelle von ‖x̂[ρ]‖ in der Auswahlregel von Marchetti et al. Prüfbar ohne neue Läufe
  an einer kleinen Rechnung (AGF-Nutzen erster Stufe mit Paargewichten w(a, b) ausschreiben) und dann an gespeicherten Läufen (Rangfolge der zuerst wachsenden Irreps gegen M0; EXP-015, EXP-046).
- **Ergebnis (EXP-076, Sitzung 24, 13:38):** *keine Brücke* im einfachsten AGF-Modell (quadratisch, Ein-Frequenz-Ansatz): Der Nutzen erster Stufe sieht die konstruierten Ziele nicht (Treffer = Zufall),
  M0 trifft alle. Neue Kandidatenfrage **N34**: Hängt die Split-Steuerung an einer endlichen (zufälligen) Auslese bei der Init und verschwindet sie im AGF-Bereich sehr kleiner Init? (vorläufig, ungeprüft)

## N35: Frequenzsteuerung allein über die Häufigkeit eines Operanden (Sitzung 25) #neu/kandidat

- **Idee:** Nach der Theorie erster Ordnung fällt im ersten W_E-Gradienten nur die eigene Häufigkeit einer Zeile heraus; die Häufigkeit des *anderen* Operanden erzeugt Leistung p|ρ̂(k)|²
  bei den Frequenzen von ρ. Dann müsste ein Split, der nur die Häufigkeit des linken Operanden periodisch formt (keine Paarstruktur), die gelernten Frequenzen steuern.
- **Konkurrenz:** „nur Paarstruktur“ (Lesart nach EXP-047) gegen „erste Ordnung inkl. Fremd-Häufigkeiten“. Test: [[experiments/EXP-077-marginal-steering/README|EXP-077]] (Pilot, vorbereitet).
- **Suche 2026-09-27** (3 Suchbegriffe, im EXP-077-README): nicht gefunden (vorläufig).

## N36: Routing oder Inhalt: Welcher Attention-Pfad hält fest, hängt davon ab, was der Wechsel verlangt? (Sitzung 25) #neu/kandidat

- **Anlass:** Dong 2026 (arXiv 2607.27281): in Sprachmodellen stellt ein QK-Reset die Lernfähigkeit her, Value nicht; bei uns (K4e) wirkt der Wertepfad stärker als QK.
- **Vermutung (ungeprüft):** Beim Wechsel F→G bleibt die Aufgabe gleich (beide Operanden beachten), nur der *Inhalt* (Frequenzen) ändert sich → Festhalten im Wertepfad. Verlangt der Wechsel eine
  neue *Leitung* (andere Positionen beachten), sollte QK wichtiger werden.
- **Möglicher Test (Skizze, nicht festgelegt):** Wechsel zu einer Aufgabe mit anderem Aufmerksamkeitsbedarf (z. B. Ausgabe hängt nach dem Wechsel nur von einer Position ab oder von einer
  zusätzlichen Position), QK- gegen VO-Reset wie N29c. Erst nach EXP-074 (Reset-Muster bei anderen Aufgaben) entscheiden; Konkurrenzmodelle: „Wertepfad hält immer“ gegen „der benötigte Pfad hält“.
- **Suche 2026-09-27 15:00** („partial reset attention query key versus value output plasticity task switch routing content transformer reinitialization which weights“): Die Aufteilung
  QK = Leitung, OV = Inhalt ist Standard (Elhage et al. 2021, *A Mathematical Framework for Transformer Circuits*; Kanäle für Inhalt z. B. https://arxiv.org/abs/2606.20678). Eine Vorhersage,
  welcher Teil-Reset je nach Art des Datenwechsels die Plastizität herstellt, wurde nicht gefunden (vorläufig; eine Suche, nur Treffer).
- **Schärfung (Sitzung 26, 15:45, gemessen; reine Überlegung, ungeprüft):** Ein sauberer Gegensatz „Leitung gegen Inhalt“ lässt sich über die Symmetrie der Aufgabe bauen. Weil W_E für beide Operanden
  geteilt ist, hängt bei positionssymmetrischer Attention (gleiche Gewichte auf a und b in jedem Kopf) die Attention-Ausgabe nur von W_E[a] + W_E[b] ab (plus Konstanten aus W_pos); das Netz kann dann nur
  **symmetrische** Funktionen f(a, b) = f(b, a) berechnen. Daraus zwei Wechsel nach einer Vorphase auf a + b (gleiche Paare, nur neue Labels):
  - **Inhalt:** a + b → a² + b² (mod p): symmetrisch, braucht neue Einbettungsmerkmale (Frequenzen über x ↦ x²), aber keine neue Leitung. N36 sagt: VO-Reset hilft mehr als QK-Reset (wie K4e).
  - **Leitung:** a + b → a − b: antisymmetrisch, braucht positionsabhängige Verarbeitung (z. B. Köpfe, die getrennt a bzw. b beachten, mit eigenem OV). N36 sagt: QK-Reset hilft mehr als VO-Reset.
  - Konkurrenz „der Wertepfad hält immer“: VO-Reset hilft in beiden Fällen mehr. Maß: Lerngeschwindigkeit nach dem Wechsel (Verlustfläche über die ersten 1000 Schritte, Trainingsmenge) relativ
    zu „kein Reset“; Test der **Wechselwirkung** (Nutzen QK − Nutzen VO) zwischen den beiden Aufgaben.
  - **Vorbedingung, sonst ist der Gegensatz nicht sauber:** Haben die Köpfe nach a + b schon eine Positionsvorliebe (einige Köpfe vor allem auf a, andere auf b), dann braucht a − b keine neue
    Leitung, sondern nur ein neues Vorzeichen in einem OV. Erst im Fenster an gespeicherten N29-Modellen messen (`attention_pattern`, Anteil auf a gegen b je Kopf); nur bei annähernd symmetrischer
    Attention den Versuch festlegen. Braucht außerdem einen Aufgabenwechsel im Trainer (neue Labels, gleiche Paare): laboreigenes Skript, Prüfung Pflicht.

## N37: Liegt das Festlegungsfenster am Horizont von Adams zweitem Moment? (Sitzung 26) #neu/kandidat

- **Beobachtung (Rechnung, keine Läufe):** Der Umschlag der Festlegung liegt zwischen 25 und 50 Schritten (N29); der Horizont des zweiten Moments ist 1/(1 − β₂) = 50 Schritte (β₂ = 0.98 im Preset),
  die Bias-Korrektur-Masse 1 − β₂ᵗ ist 0.40 bei t = 25 und 0.64 bei t = 50. Zufall oder Ursache?
- **Konkurrenzmodelle:** *β₂-Schrittuhr* (festgelegt, sobald v̂ die Gradientengrößen der ersten Daten „kennt“; danach sind Schritte entlang neuer Richtungen relativ klein) gegen *Λ-Uhr*
  (Amplitudenrennen, H40). R3 ([[confirm/R3_REGISTRATION_DRAFT|R3]]) trennt Λ gegen Schritte, aber nicht β₂ gegen andere Schrittmechanismen.
- **Möglicher Test (Skizze, nicht festgelegt):** β₂ ∈ {0.95, 0.995} (Horizont 20 bzw. 200 Schritte) bei sonst gleichem N29-Protokoll; die β₂-Uhr sagt eine Verschiebung des Fensters proportional zum
  Horizont voraus, die Λ-Uhr keine. Braucht eine Trainer-Option `--beta2` (Codex-Pflicht). Erst nach R3 entscheiden: Bestätigt R3 die Λ-Uhr, ist N37 in dieser Form unwahrscheinlich.
- **Suche 15:38** (WebSearch: „Adam beta2 horizon critical period early training feature lock-in data switch second moment bias correction first steps determine features“): Treffer zu kritischen
  Perioden allgemein (https://arxiv.org/abs/2506.15954), zur Stabilität von Adam in Abhängigkeit von β₂ und zu Konvergenzbedingungen (https://arxiv.org/abs/2603.02092), LeDoux 2026; **keine Arbeit,
  die ein Festlegungsfenster an den β₂-Horizont bindet** (eine Suche, nur Treffer; vorläufig).

- **Zu N36, Korrektur (15:53, gemessen, nach einer Prüfung):** Die N36-Schärfung (Sitzung 26) ist in einem Punkt falsch: Austauschsymmetrische Attention erzwingt keine symmetrischen Funktionen; über die OV-Positionsmarke W_O W_V (W_pos[0] − W_pos[1]) (und W_pos) kann Antisymmetrie auch ohne QK-Änderung entstehen. a − b verlangt also Positionsinformation, nicht zwingend neue QK-Leitung. EXP-080 zurückgestellt; EXP-079 misst jetzt die Kanäle (QK-Versatz, OV-Marke, Logit-Antisymmetrie) als Grundlage eines neuen Designs.

## N38: Der Momentum-Schwanz von Adam sagt die Größe von K4b voraus (Sitzung 27) #neu/kandidat

- **Rechnung (post hoc, nur numpy, kein Training; `lab/experiments/EXP-059-momentum-exposure/inflight_adam.py`):** Beim Wechsel steckt in Adams erstem Moment noch eine Verschiebung entlang der alten Richtung von
  ≈ β₁/(1 − β₁) Update-Äquivalenten. Im Skalarmodell (β = 0.9/0.98, Bias-Korrektur, danach kein Gradient entlang der alten Richtung) sind es bei t = 25–35 **6.5–10.8** Schritte, je nachdem, wie stark
  neue Gradienten das zweite Moment derselben Koordinate füllen (≈ 8.7–8.9 bei gleich großen Gradienten). Das Löschen von m entfernt genau diesen Schwanz; der Aufbau von m in neuer Richtung ist mit und ohne Löschen gleich.
- **Vergleich mit gemessenen Daten (bekannte Seeds, Pilot):** EXP-059 `delta_shift` (Verschiebung der π-Kurve durch das Löschen von m, in Schritten): **8.1 / 9.6 / 6.5** bei t = 25 / 30 / 35
  (Kurve dort alle 5 Schritte gemessen). Bei t = 40 / 50 nur **3.8 / 2.4** (linear über 35 → 50 interpoliert; *korrigiert kurz nach der Eintragung:* ich hatte das zuerst als Interpolationsartefakt einer sättigenden Kurve abgetan, aber die mittlere Steigung ist 30 → 35 und 35 → 50 praktisch gleich, 0.034 bzw. 0.033 je Schritt, also keine erkennbare Sättigung). *Zweite Korrektur (gemessen 16:09–16:10):* Auch das ist nicht entscheidbar. π = 1 ist der Endpunkt „rein erster Split“, also eine natürliche Obergrenze, die das Mittel bei t = 50 erreicht (1.05); zwischen 35 und 50 ist π_normal nicht gemessen, die Sehnensteigung schließt eine Sättigung ab ≈ 45 nicht aus. Gepaart je Seed: Abfall durch m-Löschen bei t = 50 **0.077 [0.031, 0.118]**, gegenüber 0.295, falls die lokale Steigung der Sehnensteigung entspräche. **Stand: N38 passt bei t = 25–35 (Verschiebung je Seed-Mittel 8.4 / 11.1 / 5.7 mit lokaler Steigung aus den 5-Schritt-Nachbarn, stark verrauscht); bei 40–50 unentscheidbar ohne feinere π_normal-Kurve (t = 40, 45).** Das wäre ein billiger Zusatz in einem späteren Piloten (π_normal bei 40/45 und m-Löschen bei 45).
  N28 (bestätigt): π 0.340 → 0.189 durch Löschen, m@35 = 0.410 → grob 6–7 Schritte, im selben Bereich.
- **Deutung:** Bei t = 25–35 ist die Größe von K4b aus der Adam-Arithmetik ohne freien Parameter vorhersagbar (bei 40–50 nicht, s. o.); die Lesart „Momentum = fortgesetzte Exposition“ (EXP-059) wird damit quantitativ, nicht nur qualitativ gestützt.
  Post hoc, an bekannten Seeds, ein Skalarmodell (Koordinaten ≠ Fourier-Richtungen, Gradient vor dem Wechsel nicht konstant).
- **Möglicher Test (Skizze, nicht festgelegt):** β₁ ∈ {0.8, 0.9, 0.95} (Schwanz ≈ 4 / 9 / 19 Schritte) bei sonst gleichem N28-Protokoll: normal gegen m-Löschen bei t = 25. Vorhersage: Die Verschiebung skaliert
  mit β₁/(1 − β₁). Lässt sich mit N37 (β₂) in einem „Optimierer-Uhr“-Piloten verbinden; braucht Trainer-Optionen `--beta1/--beta2` (Codex-Pflicht). Erst nach R3. → Entwurf [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (Sitzung 27, mit Vorhersagen aller drei Uhren).
- **Suche vor 16:07, gemessen** (WebSearch: „Adam momentum reset at task switch residual momentum effective steps 1/(1-beta1) feature persistence continual learning“; „momentum optimizer state carried over distribution shift grokking early training features persist data switch Adam first moment“): Dass Momentum ≈ 1/(1 − β₁) Schritte nachwirkt, ist Lehrbuchwissen. **Nächstverwandt:** *Stored in Optimizer State, Valued by Later Training* (arXiv 2608.20442, nur Such-Snippet gelesen): Nach dem Entfernen von Quelldaten wirkt Adams erstes Moment als verzögerter Träger weiter („delayed-release carrier“), über Optimierer und Architekturen. Das ist qualitativ unsere K4b-Lesart; **#neu/bekannt** für die qualitative Aussage. Offen bleibt nur die parameterfreie Größenvorhersage (Schwanz in Schritten gegen gemessene π-Verschiebung). Außerdem Khanh 2026 (2607.06628): Identitätsübertragung hängt an den Gewichten, nicht am mitgeführten Optimiererzustand. *Nachtrag Sitzung 27 (Volltext):* Sweeney 2026 (arXiv 2606.29554) beschreibt das erste Moment als Gedächtnis mit festem Takt, das Reihenfolge-Effekte erster Ordnung trägt → Mechanismus bekannt, nur die Größenvorhersage in einer Festlegungsgröße nicht gefunden. Zu prüfen im Volltext: [[paper/related_work]].

- **Zu N37, Korrektur (Sitzung 27, 16:25, gemessen, nach einer Designprüfung):** Die Begründung „festgelegt, sobald v̂ die Gradientengrößen kennt“ trägt nicht: Bias-korrigiertes v̂ ist ab Schritt 1 unverzerrt, die Füllmasse 1 − β₂ᵗ ist kein Uhrwerk (Skalarmodell: gleicher Vorlauf für jedes β₂).
  N37 ist damit nur noch eine **Skalierungshypothese ohne Mechanismus**. Test mit großen vorhergesagten Abständen bei festem t: [[experiments/EXP-081-optimizer-clock/README|EXP-081]] Nachtrag a, Teil B.


## N39: Das Spektrum der Trainingspaare ordnet auch die Frequenzen innerhalb der Zielmenge (Sitzung 28) #neu/kandidat

- **Beobachtung (Exploration, gesehene P1-Seeds):** Welches der fünf vorgegebenen Ziele bei Schritt 2000 am schwächsten ist, folgt der zufälligen Schwankung des Masken-Spektrums des Splits (ρ 0.21–0.44 bei add 113, mul 113, add 97, D₅₉), deutlich mehr als der Init-Energie (0.08–0.15); bereinigt um k und Init unverändert (add 113: 0.433). Feinere Form: Nach einem Wechsel bei t = 50 behalten die alten Ziele ihre Rangfolge (N29, ρ 0.58).
- **Registriert:** [[confirm/C1_REGISTRATION|C1]] (an R1), [[confirm/C2_REGISTRATION|C2]] (an R2), beide vor jedem Lauf.
- **Suche 2026-09-27 (WebSearch):** „grokking training pairs subset Fourier spectrum predicts which frequencies learned modular addition non-uniform data distribution“; „"training set" composition which Fourier frequencies grokking transformer data spectrum versus initialization lottery 2026“. Nächstverwandt: He et al. 2026a (arXiv 2602.16849: bei vollen Daten entscheidet Init-Betrag/Phase den Wettbewerb je Neuron), Marchetti et al. 2026 (arXiv 2602.03655: Irrep-Reihenfolge aus der Kodierungsstatistik bei gleichverteilten Daten), Zhou et al. 2024 (arXiv 2405.17479: Frequenzsicht auf Trainings- und Gesamtmenge). Die Aussage „bei konstruierten Splits ordnet das realisierte Paarspektrum die Zielfrequenzen stärker als die Init“ wurde **nach unserer Suche nicht gefunden** (vorläufig; Erweiterung von K2, kein eigener Anspruch vor C1).
- *Ergänzt Sitzung 28, später:* Verallgemeinerung (Piloten): 4× Breite 0.30, Integer-Addition 0.29–0.36, MLP 0.60 (Init jeweils ≈ 0) → [[confirm/C3_REGISTRATION|C3]]. Zeitverlauf: Im Transformer überdauert die Ordnung das Grokking (add 113 0.54 → 0.42 bei 4000, add 97 → 0.24 bei 8000, mul 113 → 0.13, D₅₉ ≈ 0.5 bis 20 000), im MLP verblasst sie (0.17 bei 10 000). Die architekturspezifische Herleitung (MLP folgt M0) trägt die Ordnung **nicht** (MLP: M0c 0.60 > M0 0.46).
- *Zyklus 15:* Im MLP ist M0c ab Schritt 1000 vorn (0.64 / 0.48), bei Schritt 250 gleichauf (0.67 / 0.62); eine frühe M0-Führung (erster Gradient) wäre nur in den ersten < 250 Schritten sichtbar. Offen, braucht dichte frühe Spektren.


## N40: Verrät ein gegroktes Embedding, welchen von mehreren gleich gebauten Splits es gesehen hat? (Sitzung 28) #neu/kandidat

- **Test (Exploration, P1 add 113, 100 Arme, `lab/confirm/P1_posthoc_split_id.py`):** echter Split gegen 9 Attrappen mit denselben Zielen und ε, aber anderen Zufallsphasen/-schlüsseln. Über die Rangfolge der 5 Ziele: Top-1 aus 10 in 0.20 (Zufall 0.10), paarweise 0.74 (Zufall 0.50). Zweites Maß (nach dem ersten Ergebnis, vor seiner Rechnung festgelegt), Log-Energie der 51 Nicht-Ziel-Frequenzen: Top-1 0.22, paarweise 0.63.
- **Einordnung:** schwache, aber über dem Zufall liegende Spur des konkreten Splits in den Gewichten. Konzeptionell gehört das zur bekannten Datensatz- und Mitgliedschafts-Inferenz aus Gewichten. Suche 2026-09-27 (WebSearch: „identify training subset from trained weights Fourier features modular arithmetic dataset inference grokking“): nichts Spezifisches zu Grokking/Fourier-Splits gefunden; nächstverwandt nur Arbeiten zum Auslesen der Fourier-Struktur aus Gewichten (z. B. arXiv 2603.23784, 2510.00468). **Nicht weiter verfolgt:** Die Spur ist schwach und beantwortet keine offene Frage in FINDINGS; höchstens als Randbemerkung zu N39.
- *Zyklus 19 (Sitzung 28):* Momentum-Reset beim Wechsel senkt den Anteil der alten Ziele (t = 25–35: −0.15 bis −0.23), nicht ihre Rangerhaltung (≈ 0) → das Momentum trägt die Menge, W_E beim Wechsel die Ordnung (Exploration, `EXP059_posthoc_rom_order.py`). Passt zu N38.

## N41: Gegen welche Init-Amplitude läuft das Rennen? Nur den Hintergrund skalieren (Sitzung 29, vor 18:10) #neu/kandidat

- **Anlass:** Vorprüfung an EXP-039 ([[LESART-nacht-2026-09-28]] Punkt 11): Die Wahl fällt, wenn die Zielverschiebung ≈ 1/3–2/3 der *Median*-Init-Amplitude erreicht. EXP-040 skaliert alle Frequenzen zugleich und kann darum nicht trennen, **welche** Init-Amplitude die Schwelle setzt: (a) der Hintergrund aller Nicht-Ziel-Frequenzen („Rauschen“) oder (b) die Init-Amplitude der späteren Konkurrenten (G-Ziele).
- **Idee (erst nach EXP-040 *H40-Muster gestützt*, sonst verwerfen):** Nur die Init-Komponenten der ≈ 46 Frequenzen, die weder F- noch G-Ziel sind, mit s_bg ∈ {0.5, 2} skalieren; F- und G-Ziele unverändert. Vorhersagen: (a) Fenster verschiebt sich ∝ s_bg; (b) und reine Λ-/Schrittuhr: keine Verschiebung. Das Skalieren nur der G-Ziele wäre dagegen konfundiert (größere G-Init begünstigt G nach dem Wechsel unter jedem Modell).
- **Suche 2026-09-27 (WebSearch):** „frequency-selective initialization scaling background Fourier components competition feature selection lock-in data switch neural network“: nächstverwandt He et al. 2026a (2602.16849, Init-Lotterie je Neuron über Betrag und Phase) und 2606.02993 (Irrep-Wettbewerb, Gewinner über die Init); beide ohne Datenwechsel und ohne frequenzselektive Init-Eingriffe. Nach unserer Suche nicht gefunden (vorläufig).
- **Kosten:** Trainer-Option analog zu `--we-init-scale` (Nicht-Gleichanteil, Fourier-Projektion der Zahlenzeilen), sonst EXP-040-Protokoll; nicht vor dem EXP-040-Ergebnis bauen (YAGNI).

## N42: Nutzung jenseits der Energie über einen energieerhaltenden Phaseneingriff? (Sitzung 30, 18:58, gemessen) #neu/verworfen

- **Anlass:** Gutachter-Einwand O2 zum [[paper/draft]]: K2-Funktion folgt der Energie. [[experiments/EXP-068-matched-sensitivity/README|EXP-068]] zeigt, dass Ablationen (gleiche Schrittnorm, gleiche entfernte Energie) Nutzung und Energie grundsätzlich nicht trennen, weil sie nur die Dosisgeometrie vertauschen. EXP-068 schlug als sauberen Eingriff vor: Energie konstant halten und nur die Richtung (Phase) der Frequenzkomponenten ändern.
- **Idee:** Den 2-dim. Fourier-Koeffizientenblock jeder Frequenz k ∈ S in W_E um einen Winkel θ drehen (gleicher Winkel über alle d Dimensionen = Verschiebung der k-Komponente entlang der Tokenachse). Die Energie je k bleibt exakt gleich. Eine vom Netz genutzte Frequenz sollte zerbrechen (die nachgeschalteten Gewichte erwarten die alte Phase), eine bloß vorhandene nicht.
- **Störgrößen, schon jetzt sichtbar:** (1) ‖ΔX_k‖² = 2(1 − cos θ)·E_k, also ist auch dieser Eingriff proportional zur Energie. Ein fairer Vergleich braucht gleiche ‖ΔX‖ zwischen Mengen, und bei energiearmen Kontrollmengen ist die erreichbare Norm begrenzt (höchstens 2·√E bei θ = π). (2) Möglicher Ausweg ohne Vergleich zwischen Mengen: *innerhalb* derselben Menge Drehung gegen Skalierung gleicher Norm vergleichen (Quotient der Schäden). Dafür fehlt noch eine Vorhersage, was ein „nur vorhandener“ Anteil hier täte. Ohne sie ist der Quotient nicht deutbar.
- **Stand:** nur Idee, keine Suche, kein Code. Erst weiterverfolgen, wenn sich für (2) eine Nullvorhersage herleiten lässt (z. B. linearisiert: Schaden ≈ ‖J·ΔX‖² mit J aus dem gespeicherten Modell, getrennt für Dreh- und Skalierungsrichtung). Sonst verwerfen.
- **Nachtrag (18:58, gemessen), Überschlag ohne Rechner: verworfen in dieser Form.** Modell einer genutzten Frequenz: Embedding-Komponente cos(ωt)·a + sin(ωt)·b, das Netz bildet den Logit-Beitrag cos(ω(a + b − c)). Eine Drehung um θ verschiebt die Phase beider Operanden, der Beitrag der richtigen Klasse fällt von 1 auf cos 2θ, Schaden 2 sin²θ. Eine Skalierung gleicher Norm (c = 2 sin(θ/2)) wirkt quadratisch (Produkt zweier Embeddings), Schaden 1 − (1 − c)² ≈ 2θ für kleine θ. Folgen: (a) Bei kleiner Dosis schadet die Skalierung stärker (erste gegen zweite Ordnung), bei θ = π/2 die Drehung. Der Quotient hängt also von der Dosis ab, nicht von der Nutzung. (b) Eine Drehung um festes θ ist wie die volle Ablation eine *relative* Dosis: Sie misst den Beitrag einer Frequenz, und der ist bei energiereichen Frequenzen natürlicherweise größer. „Nutzung jenseits der Energie“ ist ohne eine Definition von Nutzung pro Energieeinheit (z. B. Beitrag / E_k, gegen ein Modell, das Energie ohne Ausrichtung auf die nachgeschalteten Gewichte trägt) nicht wohlgestellt. **Entscheidung:** keine Registrierung; Paper-Formulierung unverändert („folgt der Energie“). Eine sinnvolle Neufassung wäre eine Ausrichtungsfrage: Sind die Leser-Gewichte (W_Q/K/V, W_in) auf die gelernten Phasen ausgerichtet? Das wäre eine Wiederaufnahme von EXP-070/071 und bleibt vorerst nicht verfolgt.

## N43: Wechselkosten mit Spitze im Festlegungsfenster: Ein Datenwechsel bei t ≈ 25 verzögert das Grokking, bei t ≥ 50 nicht (Sitzung 32, 20:44, gemessen) #neu/kandidat

- **Beobachtung (post hoc, Exploration):** N28 (30 Seeds, GPU): Wechsel A→B bzw. B→A bei 25 Schritten generalisiert pro Seed in 28/30 später als der Lauf nur auf dem Ziel-Split (≈ ×1.4); bei 50 Schritten in 24/30 **früher** (≈ ×0.77); @25 gegen @50 27/30 (≈ ×1.9). Repliziert an P3 (Seeds 1050–1079, Hypothese vorher festgelegt): 28/30, ≈ ×1.45. Adam-Momenten-Reset verringert die Kosten nur leicht. EXP-020 (CPU, 5 Seeds): @10/@25/@50 langsam, @150/@400 schnell. [[JOURNAL]] Sitzung 32, Zyklen 5–6; Skripte `lab/confirm/speed_switch_cost_*_s32.py`.
- **Hypothese:** Die Verzögerung ist maximal, wenn der Wechsel die halb aufgebaute alte Frequenzmenge trifft (K4c-Umschlag zwischen 25 und 50). Das Maximum der Kostenkurve über t wäre dann eine funktionale Messung der Festlegungszeit.
- **Suche 2026-09-27 (Sitzung 32), Suchbegriffe:** „timing of training data distribution switch non-monotonic cost critical period early training feature commitment grokking delay“, „"critical learning periods" deep networks data switch early epochs interference then recovery small transformer algorithmic task 2025 2026“, „grokking curriculum short pretraining prefix structured data accelerates generalization modular arithmetic“, „arXiv 2026 grokking faster warm start embedding Fourier features transfer grokking speed up data switch“, „grokking training set order of data subsets first phase determines speed modular addition early training data composition critical period“. Nächstverwandt: Achille et al. 2019 (kritische Perioden: frühe *Defizite* schaden dauerhaft, monoton in der Dauer; https://arxiv.org/abs/1711.08856); Kleinman/Achille et al. und 2506.15954 (Identifikation kritischer Perioden); GrokTransfer 2504.13292 und 2609.18078 (Warmstart beschleunigt Grokking); Howe 2026, 2607.04333 (strukturierte Repräsentationspriors steuern die Grokking-Verzögerung, über eine Zusatz-Loss, nicht über Datenwechsel); 2606.12966 (Zeitpunkt der Regularisierung relativ zur Schaltkreisbildung). **Nicht gefunden:** eine nicht-monotone Zeitkostenkurve eines Datenwechsels mit Maximum am Festlegungszeitpunkt der Merkmale. Vorläufig, ohne Zitationsverfolgung.
- **Nächster Schritt:** Bestätigung mit frischen Seeds und feinem Raster (t ∈ {0, 10, 20, 25, 30, 35, 40, 50, 75, 150}), Registrierung vor jedem Lauf.
- **Nachtrag (Sitzung 32, 21:04 gemessen, post hoc):** Die Kosten wachsen mit dem Anteil ω gemeinsamer Paare. EXP-056: C(ω 0.4) > C(ω 0) in 8/10 Seeds (p = 0.055, vorab festgelegt), Mediane 0.71/1.07/1.04 für ω 0/0.2/0.4. P3 gepaart 24/30 (gesehen). Folgefrage: Verschiebt eine höhere Überlappung das Kostenfenster zu späteren t (EXP-020 mit ≈ 73 % Überlappung: auch @50 langsam)? Erst nach R6.
- **Nachtrag (Sitzung 32, 21:12 gemessen, post hoc, vorab festgelegt):** Feine Kurve an den Seeds 400–409 (EXP-059 + EXP-056): C(t) = 0.27/0.38/0.53/0.57/0.55/0.33/−0.67 bei t = 10/15/20/25/30/35/50. Spitze bei 25, Vorzeichenwechsel zwischen 35 und 50, wo π von 0.56 auf 1.05 steigt. Schon t = 10 kostet (π ≈ 0.01).
- **Nachtrag (Sitzung 32, 21:14 gemessen, post hoc):** N29 @25 gegen @50: 20/20 Seeds langsamer (≈ ×2). Resets bei 50 verzögern in der Reihenfolge der Persistenzsenkung (N29b Attention > MLP 15/20; N29c VO > QK 19/20). Ob „aufgehobene Festlegung“ oder „zerstörte Funktion“ dahintersteckt, ist offen. Trennender Test: gleicher Reset bei t = 0 / 150.
- **Nachtrag (21:16, post hoc, beschreibend):** Resets senken den Sofortverlust auf dem neuen Split; VO am stärksten (0/20 Seeds über QK) und doch am langsamsten. Unmittelbarer Schaden erklärt die Reset-Kosten nicht.
- **Nachtrag (21:22, Einordnung):** Dass *späte* Wechsel (t ≥ 50 bzw. 150) das Grokking beschleunigen, ist erwartbar und im Kern bekannt: Es gibt insgesamt mehr verschiedene Trainingspaare, und mehr Daten bzw. Augmentierung beschleunigen Grokking (Power et al. 2022, https://arxiv.org/abs/2201.02177; Augmentierung ≈ 2×, https://arxiv.org/html/2412.10898; Suche „grokking adding more training data mid-training accelerates generalization …“, 2026-09-27). Als Kandidat für Neues bleibt nur die **Verzögerung** im Festlegungsfenster und ihr Verschwinden bei π ≈ 1. #neu/bekannt (teilweise)
- **Nachtrag (21:23, post hoc, vorab festgelegt):** Zerlegung in N28: Bei t = 25 liegen 90 % der Verzögerung (+283 von +315 Schritten) in der Lücke zwischen Memorisation und Generalisierung, nur +32 in der Memorisation. Bei t = 50 ist die Memorisation langsamer (+92), die Lücke aber kürzer (−237). Der Konflikt betrifft also die Generalisierung.
- **Nachtrag (21:33, Skeptiker-Prüfung):** Die ernsteste Alternative lautet: Jede frühe Datenänderung kostet Zeit, ein Frequenzkonflikt ist nicht nötig. Kontrolle vorbereitet: [[experiments/EXP-086-same-spectrum-switch/README|EXP-086]] (A→A2 mit gleichen Zielfrequenzen). Adams Optimizer-Zustand trägt etwa die Hälfte der Kosten bei 25 (EXP-058: 0.57 → 0.25–0.28), das zweite Moment nichts zusätzlich.
- **Nachtrag (21:35, post hoc):** Warum ein Wechsel nach der Festlegung beschleunigt: Der neue Split wird über die festen Merkmale gefittet. Beim Erreichen von 99 % Train liegt die Testgenauigkeit nach einem Wechsel bei 50 bei 0.42, bei „nur Ziel“ am selben Schritt bei 0.16 (30/30). Bei 25 gibt es keinen Unterschied.
- **Korrektur (21:38, Quellenprüfung):** Der Optimizer-Anteil liegt bei einem Viertel (N28) bis der Hälfte (EXP-058), nicht pauschal bei der Hälfte. Der VO-Reset senkt den Sofortverlust stärker als QK, aber nicht am stärksten von allen Resets.
- **Nachtrag (Sitzung 33, vor 22:36 gemessen, reine Rechnung auf Split-Dateien):** Jeder Wechsel zwischen *disjunkten* Splits aus einem gemeinsamen Pool enthält einen Gegenterm. In erster Ordnung zeigt der W_E-Gradient des neuen Splits bei den alten Zielen gegen den alten (N28 cos −0.53, P3 −0.54, je 30/30; Projektion ≈ −0.38 des alten Eigenschubs; `lab/confirm/switch_alignment_s33.py`). Auch A2 aus EXP-086 („gleiche Frequenzen“) zeigt so gegen A (−0.52), ebenso zwei disjunkte Zufallssplits gegeneinander (−0.42). Mit der Überlappung ω verschwindet der Gegenterm (−0.53/−0.28/−0.04 bei ω 0/0.2/0.4), die Kosten stiegen aber eher (EXP-056). Ein Modell „Kosten = Umkehr halb aufgebauter Richtungen“ passt deshalb schlecht (post hoc, n. s.). **Bedingte Folgeidee, erst nach EXP-086 und nur, wenn D ≈ 0:** ein Kontrollwechsel A → A3 *ohne* Mengen- und ohne Richtungskonflikt, mit ≥ 60 % der A-Paare behalten und dem Rest aus dem Komplement mit A's eigenen Wellenphasen (vorher prüfen: cos(A, A3) bei F > 0, gleicher F-Anteil). Kostet auch das Zeit, ist N43 eine reine Neuheitsaussage über Daten und keine Frequenzaussage. Kein Code (YAGNI).
- **Zweite Suche (Sitzung 33, 5 Anfragen, Details in [[paper/related_work]] Nachtrag Sitzung 33):** nichts Einschränkendes gefunden. Neu als Kontext: 2604.13082 (Decoder-Engpass, Encoder-Transplantat beschleunigt) und 2208.04832 (kritische Periode im RL). Ein Titel „Critical Learning Periods in Grokking“ aus dem AI-Scientist-Umfeld (2606.15497) betrifft laut Snippet Lernratenfenster; für die menschliche Prüfung vermerkt.
- **Nachtrag (Sitzung 34, 23:00 gemessen, post hoc, vorab festgelegt):** Modell „Aufräumen“ (die alten Ziele müssen vor der Generalisierung durch Weight Decay abgebaut werden) **widerlegt**: mehr alte Zielenergie bei t + 250 geht *nicht* mit mehr Verzögerung einher (ρ −0.16 N28, −0.23 P3), der alte Anteil sinkt vor der Generalisierung nicht, zensierte Läufe tragen weniger alte Energie. Ein Konzentrationsdefizit-Modell wurde wegen eines gemeinsamen Terms in Vorhersage und Beobachtung (eigener Designfehler) nicht registriert. [[JOURNAL]] Sitzung 34, Zyklus 2.
- **Nachtrag (Sitzung 37, 02:46 gemessen): EXP-086 → Frequenzkonflikt (Pilot).** Wechsel bei 25 zu gleichen Zielfrequenzen (A2): C −0.26 log2 (4/10); zu anderen Zielen (B): +0.57; D = +0.82, 9/10, p = 0.011. Zufallssplit → Zufallssplit: −0.80 (0/10). Die Skeptiker-Alternative „jede frühe Datenänderung kostet“ ist an diesen Seeds widerlegt; die Kosten hängen an der Zielmenge, nicht an der Gegenrichtung erster Ordnung (A2 und B gleich stark gegen A). Bekannte Seeds, n = 10: eine Bestätigung an frischen Seeds wäre nötig, bevor es eine Kernaussage wird.
- **Suche (Sitzung 37, 2026-09-28, 2 WebSearch-Anfragen: „grokking data switch early training delay feature conflict warm-starting modular arithmetic Fourier frequencies“; „early training data distribution shift delays grokking same features vs different features critical period switch cost“):** Nächstverwandt ist der Primacy-Bias im nichtstationären Lernen, bei dem frühe Daten das spätere Generalisieren behindern (Lyle et al. 2025, [arXiv 2507.20057](https://arxiv.org/abs/2507.20057), schon zitiert), dazu frühe Trainingsphasen und OOD-Anpassung ([arXiv 2403.15210](https://arxiv.org/abs/2403.15210)) und Grokking unter der kritischen Datenmenge mit Destillation zwischen Verteilungen ([arXiv 2511.04760](https://arxiv.org/abs/2511.04760)). Nicht gefunden: die Trennung „früher Wechsel zu anderen Zielmerkmalen kostet, zu gleichen Zielmerkmalen mit neuen Paaren nicht (beschleunigt eher)“. Einordnung vorläufig **#neu/kandidat** (nach unserer Suche vom 2026-09-28 nicht gefunden; Pilot an bekannten Seeds).
- **Nachtrag (Sitzung 37, 04:42 gemessen, post hoc an R6, Exploration):** Auch über Seeds innerhalb eines t hängen die Kosten an π, mit Vorzeichenwechsel: ρ(π, C) = +0.39 bei t = 20 (p 0.035), −0.41 bei 40 (0.026), −0.56 bei 50 (0.0014). Nur t = 50 übersteht Bonferroni über 7 t. Das passt zum umgekehrten U („halb aufgebaut kostet, fest gebaut hilft“). `lab/confirm/R6_posthoc_pi_cost_s37.json`.

- **N6, Nachtrag (Sitzung 32, 22:08, gemessen):** EXP-018 (vorab registriert, Kontrollarm prospektiv): *beschleunigt*, E ≈ 6.5× schneller als D (gleiche Gewichtsverteilung je Antidiagonale), 10/10. EXP-084 (frische Seeds): Vorhersage vor dem Lauf getroffen, die Zeit sättigt mit dem Masken-Zielanteil (M_share). Neuheit weiter „nach unserer Suche nicht gefunden“ (vorläufig).

## N44: Zielmenge als geheimer Schlüssel: Herkunftsnachweis eines Trainingssplits allein über die Paarauswahl (Sitzung 34, vor 23:03, gemessen) #neu/bekannt

- **Idee:** Ein Datenhalter wählt geheim 5 Zielfrequenzen und veröffentlicht nur einen danach konstruierten Split (keine veränderten Eingaben, nur die *Auswahl* der Paare). Ein darauf trainiertes Modell trüge die Ziele messbar in W_E (K2, P1: großes Δ_pow), die Prüfung wäre ein Test gegen zufällige 5er-Mengen. Anders als N40 (welcher von mehreren gleich gebauten Splits, schwach) ist hier die Zielmenge der Schlüssel.
- **Einordnung:** Das Konzept ist bekannt als „radioaktive Daten“ (Sablayrolles et al., ICML 2020, https://arxiv.org/abs/2002.00937: unmerklich veränderte Bilder markieren jedes darauf trainierte Modell, Nachweis mit p-Wert). Der Unterschied, nur Teilmengenauswahl statt veränderter Eingaben, ist eine Anwendung von K2 und beantwortet keine offene Frage in [[FINDINGS]]. Suche 2026-09-27: nur diese Arbeit geprüft (WebSearch „Radioactive data: tracing through training Sablayrolles 2020 arXiv“), keine Suche nach Teilmengen-Varianten.
- **Entscheidung:** nicht verfolgt (Regel 15: Verallgemeinerung und Bestätigung haben Vorrang). Höchstens ein Satz in der Diskussion des Papers, falls der Nutzer das wünscht.

## N45: Gerade Oberwellen in W_E als Transformer-Merkmal? (Sitzung 35, 23:33 gemessen, vor jeder Rechnung festgelegt) #neu/kandidat

- **Anlass:** Die Nicht-Ziel-Glieder der W_E-Top-5 unter konstruierten Splits waren explorativ gerade Oberwellen fold(2k) der Ziele (EXP-016, 14/14; Bestätigung [[experiments/EXP-021-harmonic-misses/README|EXP-021]] wird um 01:30 gerechnet). He et al. 2026a (2602.16849, laut Blog der Autoren, Abschnitt 4.6) beschreiben im zweischichtigen ReLU-Netz nur **ungerade** Oberwellen in den Eingangsgewichten ([[paper/related_work]], Nachtrag Sitzung 35).
- **Frage:** Tritt der 2k-Überschuss auch im MLP mit gemeinsamer Einbettung auf, oder nur im Transformer?
- **Daten (Exploration, gesehene Seeds, keine Bestätigung):** Transformer P1 add 113 (Seeds 1000–1049, F/G, 100 Läufe, GPU) und MLP [[experiments/EXP-045-mlp-steering/README|EXP-045]] (Seeds 90–99, F/G, 20 Läufe, GPU). Top-5 und Steuerung beider Blöcke sind gelesen; welche Nicht-Ziel-Glieder Oberwellen sind, wurde nach unserer JOURNAL-Suche nie gezählt.
- **Zählung:** exakt wie EXP-021 (Top-5 bei 2000, Poisson-Binomial-Null), für n = 2 (primär) und n = 3 (sekundär, beschreibend). Skript `lab/confirm/N45_even_harmonics_s35.py`.
- **Lesart (vorab):** (i) Transformer 2k p < 0.01 **und** MLP 2k p ≥ 0.05 → „gerade Oberwellen in W_E nur im Transformer“ (Exploration; passt zu He et al. für das MLP); (ii) beide p < 0.01 → kein Transformer-Merkmal; (iii) Transformer nicht p < 0.01 → widerspricht der EXP-016-Exploration, EXP-021 abwarten; MLP mit < 8 Nicht-Ziel-Gliedern → nicht auswertbar; MLP 0.01 ≤ p < 0.05 → unklar. **Vorhersage:** (i).
- **Grenzen:** Das MLP ist kein One-hot-Netz wie bei He et al. (gemeinsame Einbettung, dann W_in); F und G teilen die Init; die Null behandelt Frequenzen als unabhängig. Keine Neuheitssuche über die zwei Anfragen hinaus.
- **Ergebnis (Sitzung 36, 01:31):** *nicht auswertbar* nach der vorab festgelegten Regel. Transformer P1: 99/107 Nicht-Ziel-Glieder gerade Oberwellen (erwartet 9.3 %, p = 8e-92), ungerade 3k 9/107 (p = 0.67). MLP EXP-045: **0 Nicht-Ziel-Glieder in 20 Läufen** (Top-5 = Ziele). Die MLP-Seite braucht ein Maß ohne Top-5-Schnitt (Energieanteil auf fold(2k)); das wäre ein neuer Versuch, kein Nachtrag. `lab/confirm/N45_even_harmonics_s35.json`, [[JOURNAL]] Sitzung 36.


## N46: Mengen- oder Phasenkonflikt? Die Wechselkosten gegen die Gegenrichtung erster Ordnung bei gleicher Zielmenge (Sitzung 37, 04:38 gemessen, vor jeder Rechnung) #neu/kandidat

Zurück: N43 · [[confirm/R8_REGISTRATION_DRAFT|R8]] (bestätigt: nur ein Wechsel der Zielmenge kostet) · [[FINDINGS]] größte offene Frage.
- **Offener Rest von R8:** A2 hat dieselben Zielfrequenzen, aber neue, teilweise umgekehrte Wellenphasen (cos −0.52 zu A bei F). Trotzdem kostet A→A2 nichts. Das spricht schon gegen einen *reinen* Phasenkonflikt, schließt ihn aber nicht aus, weil nur eine Phasenlage geprüft ist.
- **Idee:** Bei gleicher Zielmenge F und gleicher Stärke die Ausrichtung von A2 zu A in erster Ordnung (cos bei F) gezielt variieren, z. B. −0.5 / 0 / +0.3. Positive Ausrichtung verlangt Überlappung mit A (ω > 0) oder eine Auswahl nach der Phase von A. Dieselbe Konstruktion gibt es für B (andere Ziele). Vorhersage des Mengenmodells: C_AA2 ≈ 0 bei jeder Ausrichtung, C_AB > 0 bei jeder. Vorhersage des Phasenmodells: C_AA2 steigt mit negativer Ausrichtung.
- **Kosten:** Splits reine numpy-Rechnung; 2000-Schritt-Läufe, ≈ 7 je Seed. Zuerst ein Pilot mit 10 bekannten Seeds.
- **Priorität:** niedrig bis mittel. Erst nach den eingefrorenen Blöcken (R5, R3, P4, R2, R4, R7). Neuheit nicht geprüft (baut auf N43 auf; dortige Suchen vom 2026-09-27/28).

## N47: Läuft die Split-Beschleunigung (R5) ganz über das frühe W_E-Zielsignal? Mediationstest durch Einpflanzen (Sitzung 38, 05:25 gemessen, vor jeder Rechnung) #neu/kandidat

- **Anlass:** R5 (bestätigt): E2 groks ×6.5 früher als R; der W_E-Zielanteil bei 250 ist nach Armen geordnet und sagt die Zeit auch *innerhalb* der E-Arme vorher (post hoc ρ −0.64 bis −0.79, `R5_posthoc_share_speed_s38.py`). Offen: Ursache oder Fortschrittsmarker?
- **Bekannt (Suche 2026-09-28, WebSearch „accelerating grokking embedding transfer Fourier initialization modular addition“, „grokking training data selection speed mediated by early embedding structure causal“):** Eingepflanzte Struktur beschleunigt Grokking: GrokTransfer, Einbettungen eines schwächeren Modells als Init ([arXiv 2504.13292](https://arxiv.org/abs/2504.13292), ICLR 2025, [OpenReview](https://openreview.net/pdf?id=4rEI2JdHH6)); Howe 2026, *Structure-Specific Representational Priors Causally Control the Grokking Delay* ([arXiv 2607.04333](https://arxiv.org/abs/2607.04333), Abstract gelesen): kontrastiver Zusatzverlust mit wahrer Struktur beschleunigt dosisabhängig, falsche kohärente Struktur nicht, zufällige verhindert; Datenzusammensetzung wird dort nach dem Abstract nicht variiert. Dazu [arXiv 2609.18078](https://arxiv.org/html/2609.18078) (Komponentenrollen beim Grokking-Transfer; nicht gelesen). **„Frühe Einbettungsstruktur beschleunigt“ ist also bekannt.**
- **Geschärfte Frage (nach unserer Suche nicht gefunden, vorläufig):** Erklärt das frühe Zielsignal die *Daten*-Beschleunigung vollständig? Arme bei gleicher Init und Testmenge: R (Zufallssplit), R+P (Zufallssplit, W_E bei t = 0 so auf die 5 Ziele von E vorgeladen, dass der Zielanteil bei 250 dem von E2 entspricht, ≈ 0.30), E2, E2+P. Vorhersagen: volle Mediation → b(R+P) ≈ b(E2); fortlaufender Datengradient nötig → b(R+P) deutlich > b(E2), und/oder E2+P schneller als E2. Nebenfrage: Steuert das eingepflanzte Signal auf R die Endfrequenzen (K2 ohne Datensteuerung)?
- **Grenzen vorab:** Die Einpflanzung verändert Norm und Phasen; Amplitude muss an der Norm abgeglichen werden (vgl. EXP-040 Init-Skala, N41). Anteil bei 250 ist nach dem Eingriff kein unabhängiges Maß mehr (Kalibrierung, keine Messung).
- **Budget:** Pilot 10 Seeds × 4 Arme × ≤ 8000 Schritte GPU ≈ 30 min. **Priorität:** mittel, nach den eingefrorenen Blöcken; zielt auf FINDINGS Programm C (mechanistische Vorhersage) und macht R5 im Paper mechanistisch einordenbar. Braucht eine Option in `freq_ban.py` (Trainer-Änderung → Tests, Regel 18c). Entwurf: [[experiments/EXP-087-planted-signal-mediation/README|EXP-087]].

*Stand Sitzung 39 (2026-09-28):* Pilot [[experiments/EXP-087-planted-signal-mediation/README|EXP-087]] *unklar* (registriert): Einpflanzen allein beschleunigt einen Zufallssplit ×11 (10/10) und ist schneller als E2 (Kalibrierung überschoss). Der frühe Zielanteil ordnet die Zeit über alle Arme; Folgeversuch [[experiments/EXP-088-common-dose-curve/README|EXP-088]] (gemeinsame Dosiskurve, Äquivalenztest) registriert. Neuheit bleibt eng: bekannt ist, dass ausgerichtete Einbettungen beschleunigen (Howe 2026, GrokTransfer); nach unserer Suche nicht gefunden ist nur die quantitative Gleichwertigkeit von datengetriebenem und eingepflanztem Frühsignal. Vor einem Anspruch neu suchen. #neu/kandidat

*Stand Sitzung 39, später:* [[experiments/EXP-088-common-dose-curve/README|EXP-088]] (20 frische Einheiten) *unklar* (registriert): Eingriffs- und Datenarme liegen nahe an einer gemeinsamen Dosiskurve (Residuum −0.39 log2 [−0.55, −0.24], 17/20; Eingriff ≈ ×1.3 wirksamer je Anteilseinheit). Der frühe W_E-Zielanteil erklärt den Großteil der Split-Beschleunigung; ein zusätzlicher Datenbeitrag ist nicht zu sehen. Offene Schärfung: Hängt der Eingriffsvorteil davon ab, dass das Signal schon bei Schritt 0 da ist (Einpflanzen bei t = 0 gegen t = 50)?

## N48

**Frage (Sitzung 40, 2026-09-28):** Tickt die frühe Festlegung der Frequenzwahl in aufsummierter Lernrate Λ, sobald Adams β₁-Verzögerung ebenfalls in Λ gemessen wird? Macht eine kürzere Momentum-Verzögerung die frühe Bewegung frequenzselektiver? #neu/kandidat
**Stand:** Piloten [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]] (Mischuhr gestützt), [[experiments/EXP-090-beta-window-lambda/README|EXP-090]] (H-β gestützt: mit β′ = 1 − c(1 − β) verschwindet der Schrittanteil, Rest +0.002 ± 0.024), [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (N38 gestützt, N37 verworfen; längeres β₁-Fenster → weniger Festlegung beim Wechsel, post hoc).
**Suche 2026-09-28:** Die β-Umskalierung ist bekannt (Malladi et al. 2022, arXiv 2205.10287, SDE-Skalierungsregeln für Adam; **Korrektur Sitzung 41:** dort gilt η ∝ √κ und 1 − β ∝ κ, also 1 − β ∝ η², nicht ∝ η; unsere Regel 1 − β ∝ η ist die deterministische ODE-Angleichung, vgl. Barakat & Bianchi, arXiv 1810.02263); ihre Folge für die persistente frühe Merkmalswahl beim Grokking nicht gefunden. Also *vorläufig neu* nur als Befund, nicht als Regel.
**Nächster Schritt:** Bestätigung mit eingefrorenem Manifest (frische Seeds, zweite c-Stufe, z. B. c = 2 mit β′ 0.8/0.96 und c = 0.5), dann Mechanismus: Warum wirkt eine kürzere Verzögerung selektiver? (Idee: Momentum als Tiefpass mischt frühe, noch unspezifische Gradientenrichtungen länger nach.)
**Stand Sitzung 41:** R9 bestätigt (K5). Post hoc an R9: kürzere Verzögerung → frühe Bewegung *zielgenauer* (log f +0.128 gegen log N +0.089), mehr Zeit → vor allem *größer*; Zuwächse werden zielgenauer (0.21 → 0.46, 72/72) → Tiefpass-Lesart gestützt (Voraussetzung). [[experiments/EXP-092-momentum-lag-clock/README|EXP-092]]: Lag-Uhr sagt ungesehene Zellen voraus (MAE 0.029), versagt bei c = 4 (wenige große Schritte, unselektiv) → [[experiments/EXP-093-lag-clock-range/README|EXP-093]] (Gültigkeitsbereich). Kandidat für den Fehlschlag: fast vorzeichenartige erste Adam-Schritte. **EXP-093:** Lag-Uhr verfehlt ab c = 2 zunehmend (bis −0.25 bei c = 8); bei festem Λ schwächere, unselektivere Festlegung mit größeren Schritten; Lag + c/2 (Euler) erklärt nur einen Teil. Nächste Frage: Zielgenauigkeit ∝ Zahl der Gradientenauswertungen? Trennender Versuch braucht Trainer-Option (Unterschritte bei gleichem Adam-Zustand). Neu nach Suche vom 28.09. höchstens die Anwendung; Prinzip bekannt (Sweeney 2026, Barakat & Bianchi).

**Stand Sitzung 42:** [[experiments/EXP-095-gradient-feedback/README|EXP-095]] trennt „frische Gradienten entlang des Wegs (Rückkopplung)“ von „grober Adam-Schritt“: 24 normale Adam-Schritte, Gradient nur alle k Schritte neu (g4/g8/g24), gegen c8b. **Suche 2026-09-28 (Sitzung 42)**, Begriffe: „stale gradient early training feature selection grokking“, „frozen initial gradient Adam first-order early dynamics feature learning“, „delayed stale gradients asynchronous SGD feature learning implicit bias“. Nächstverwandt: eingefrorene Gradienten als Erste-Ordnung-Näherung (Geiger et al., arXiv 1906.08034, „frozen kernel dynamics“); „frozen Adam“ mit festem Präkonditionierer (Cohen et al., arXiv 2207.14484, Stabilität, nicht Merkmalswahl); exponentiell beschleunigtes Wachstum der Gewinnerfrequenz bei modularer Addition (arXiv 2602.16849, Lotterie-Bild, Rückkopplung implizit); Staleness bei asynchronem SGD (Dutta et al. 2018, arXiv 2003.10579; arXiv 2605.02043) mit Konvergenz-, nicht Merkmalsfolgen. Nicht gefunden: gezielter Eingriff in die Zahl der Gradientenauswertungen vor einem Datenwechsel, um die Persistenz einer frühen Merkmalswahl zu messen. *Vorläufig neu* (nur „nach unserer Suche nicht gefunden“).

**Stand Sitzung 43:** Post hoc (EXP-095 Nachtrag b): g24 ist Vorzeichenabstieg (Adam mit festem g₀ → lr · sign(g₀)); Binarisierung erklärt ≈ 56 % der Selektivitätslücke. Die Frage schärft sich zu: *Braucht die frühe Festlegung frische Gradienten auch ohne Vorzeichen-Quantisierung?* → [[experiments/EXP-097-sign-vs-staleness/README|EXP-097]] (2 × 2, Adam-Zustand im Schatten). **Suche 2026-09-28 (Sitzung 43, Agent; Semantic Scholar 429, Google Scholar nicht erreicht):** Begriffe u. a. „stale gradient feature learning implicit bias“, „gradient reuse multiple optimizer steps“, „delayed gradient descent implicit regularization“, „one gradient step feature learning“, „number of gradient evaluations vs number of steps“, „rich-get-richer feature learning“, „grokking optimizer momentum early“. Neu verwandt: Dandi et al. (arXiv 2305.18270, ein großer Schritt lernt eine Richtung, weitere Richtungen brauchen weitere Schritte), Ba et al. 2022 (arXiv 2205.01445), Kumar et al. 2023 (arXiv 2310.06110), Mitliagkas et al. 2016 (arXiv 1605.09774, Staleness ≈ implizites Momentum, Konvergenz). Weiter nicht gefunden: Eingriff in die Zahl frischer Auswertungen bei fester Schrittzahl mit Messung der Merkmalswahl. *Vorläufig neu.*

## N49

**Frage (Sitzung 43, 2026-09-28):** Adam normiert elementweise in der Token-Basis von W_E. Bei einem wenig veränderlichen Gradienten ist das fast ein Vorzeichenschritt, und die Vorzeichenbildung entlang der Token-Achse streut Energie auf Nicht-Ziel-Frequenzen (Arkussinus-Gesetz, EXP-095 Nachtrag b/c: ≈ 56 % der Zielanteil-Lücke von g24; Vorhersage „grob“ getroffen). **Hypothese:** Parametrisiert man W_E in Fourier-Koordinaten (W_E = B·C, B die feste orthonormale DFT-Basis, Adam auf C), wirkt die Vorzeichenbildung je Frequenz. Dann sollte die frühe Bewegung frequenzselektiver sein, die Festlegung früher, und der g24-Nachteil kleiner. Das Modell bleibt funktional gleich, nur die Optimierer-Geometrie ändert sich (Rotation). #neu/kandidat
**Suche 2026-09-28 (Sitzung 43, WebSearch):** „sign descent Adam spectral leakage Fourier features arcsine law harmonics“, „signSGD implicit bias frequency spectrum features sign quantization gradient Adam modular arithmetic Fourier“. Nächstverwandt: Adams Rotationsabhängigkeit (arXiv 2510.23804, *How do simple rotations affect the implicit bias of Adam?*, Snippet: SignGD-Grenzen hängen von der Rotation ab); Balles & Hennig 2018 (Adam = Vorzeichen × Varianzfaktor). Nicht gefunden: Optimierer-Basis (Token gegen Fourier) als Stellgröße für die Merkmalswahl beim Grokking. *Vorläufig neu*, Suche schmal (nur zwei Anfragen).
**Nächster Schritt:** erst nach EXP-097 (Q1 „Quantisierung erklärt“ würde N49 stützen). Kleinster Test: Trainer-Option `--we-fourier-param` (Gleichwertigkeit am Init prüfen: gleiche Logits), Pilot n24/g24 in beiden Parametrisierungen, 16 Seeds.
**Stand Sitzung 43 (später):** Post hoc an R9 (JOURNAL Zyklus 12): Bei lr × 0.25 geht die höhere Festlegung mit Standard-β mit viel geringerer Vorzeichen-Quantisierung einher (q 0.25 gegen 0.55, 36/36), bei lr × 2 nicht. Stützt N49 als Richtung, ohne Test. *Korrektur nach Nachrechnung:* Messgröße f, nicht π; Kovariation, keine Mediation; der Befund bei lr × 2 ist toleranzabhängig (bei ±5 % ebenfalls gegenläufig, 36/36).
**Suche 2 zu N49 (2026-09-28, Sitzung 43, WebSearch, nur Snippets [S]):** „Adam versus SGD grokking modular addition Fourier features optimizer basis dependence“, „Adam not rotation invariant coordinate basis feature learning embedding Fourier basis reparameterization“. Verwandt: Slingshot-Studie (arXiv 2206.04817: Grokking mit Adam/AdamW, nicht mit SGD+Momentum), „Grokking at the edge of numerical stability“ (arXiv 2501.04697), *Understanding Adam Requires Better Rotation Dependent Assumptions* (OpenReview, id 4wC4NdkiWg: Adams Empfindlichkeit für globale Koordinatenwechsel), *Fourier Preconditioning for Neural Feature Learning* (arXiv 2607.02199: Basisrotation als Vorkonditionierung, anderes Ziel, H-Score), Muon beim Grokking (arXiv 2607.20512). Weiter nicht gefunden: W_E in Fourier-Koordinaten unter Adam als Eingriff in die Merkmalswahl beim Grokking. Vorläufig neu; die OpenReview-Arbeit vor jedem Anspruch im Volltext lesen.
**Zwei konkurrierende Vorhersagen für N49 (Sitzung 43, vor jedem Code):** (V1, Streuung) In der Token-Basis streut Adams Vorzeichenbildung Energie von den Ziel- auf Nicht-Ziel-Frequenzen (Arkussinus). In Fourier-Koordinaten entfällt diese Streuung, die frühe Bewegung wird selektiver, die Festlegung früher und stärker, und der g24-Nachteil schrumpft. (V2, Angleichung) In Fourier-Koordinaten gleicht Adam die Schrittgrößen der Frequenzen an (m̂/√v̂ ≈ Vorzeichen je Frequenzkoeffizient). Frequenzen mit großem Gradienten, also die vom Split bevorzugten Ziele, wachsen dann nicht mehr schneller als die anderen. Die Datensteuerung K2 und die frühe Selektivität würden schwächer. V1 und V2 sagen für den Zielanteil f der frühen Bewegung entgegengesetzte Vorzeichen voraus (Fourier-Adam minus Token-Adam: V1 > 0, V2 < 0). Das macht den Versuch trennend. Messgrößen: f beim Wechsel, π, und K2 (Δ_pow bei 2000) unter beiden Parametrisierungen, gleiche Seeds, gleiche Init (W_E identisch, nur die Optimierer-Koordinaten verschieden). Umsetzung (Skizze): W_E[:p] aus dem Optimierer nehmen, dafür C = Bᵀ·W_E[:p] als Parameter; Gradient g_C = Bᵀ·g_W, AdamW-Schritt auf C, dann W_E[:p] = B·C (entkoppelter Weight Decay ist rotationsinvariant). Zuerst prüfen: am Init gleiche Logits, erster Schritt in C-Koordinaten ist ein Vorzeichenschritt.

## N50: Braucht die Split-Steuerung (K2) einen Auswahldruck im Lerner? (Sitzung 44, 2026-09-28, 20:40 gemessen, vor jeder Rechnung) #neu/kandidat

**Frage:** Die Transformer konzentrieren ihre W_E-Energie auf ≈ 5 Frequenzen; die Datenauswahl entscheidet, welche. Ist diese Steuerung eine Eigenschaft der Daten allein (dann auch in einem Lerner ohne Sparsamkeitsdruck sichtbar) oder braucht sie einen Druck, der zwischen Frequenzen entscheiden muss (Weight Decay, begrenzte Breite)? **Vorhandene Hinweise (gesehene Daten, post hoc, keine Tests):** In R1 wächst Δ_pow mit dem Weight Decay (0.3 → 4.30, 3 → 10.74), aber ebenso mit der Lernrate (5e-4 → 5.81, 2e-3 → 9.37) und dem Trainingsanteil (0.2 → 4.80, 0.5 → 9.11). Das ist mit „mehr Trainingsfortschritt bei Schritt 2000“ ebenso vereinbar (Pracher et al. 2026: Grokking-Zeitskala vom Produkt lr·wd bestimmt, Generalisierungszeit ∝ 1/(lr·wd)), also kein Beleg für einen Auswahldruck. **Entscheidender Test ohne diese Verwechslung:** [[experiments/EXP-101-rfm-k2/README|EXP-101]] (Gauß-RFM: kein Weight Decay, keine Breitengrenze; Erwartung dort vorab notiert). Zweiter Test (später, nur wenn EXP-101 „negativ“ oder „unklar“): Δ_pow bei gleichem Fortschritt statt gleicher Schrittzahl vergleichen (z. B. am Schritt der Generalisierung) über wd 0.3/1/3 an den vorhandenen R1-Läufen (post hoc, dann eigene Bestätigung).
**Suche 2026-09-28 (Sitzung 44, WebSearch, Snippets [S] + ein Abstract [A]):** „weight decay number of Fourier frequencies sparsity grokking modular addition key frequencies regularization“, „recursive feature machine AGOP modular arithmetic Fourier spectrum few frequencies sparse circulant eigenvalues“. Nächstverwandt: Nanda et al. 2023 (arXiv 2301.05217; Weight Decay räumt auf, wenige Schlüsselfrequenzen) [S]; He et al. 2026 (arXiv 2602.16849; Fourier-Merkmale, Lotterie) [S]; Pracher et al. 2026 (arXiv 2609.26679, „A Spectral Theory of Grokking: Weight Decay induces Feature Learning“; Zeitskala ∝ lr·wd; laut Zusammenfassung nichts zu Frequenzzahl oder Datenzusammensetzung) [A]; Mallinar et al. 2025 (arXiv 2407.20199; RFM lernt blockzirkulante Merkmale; laut Zusammenfassung keine Aussage zur Frequenzzahl) [S]. Die konkrete Frage (steuert die Datenauswahl die Frequenzwahl nur zusammen mit einem Sparsamkeitsdruck?) wurde nicht gefunden; vorläufig, nicht „neu“.

## N51: Zwei Uhren? Frühe Festlegung in Σ lr, spätere Verstärkung der Steuerung in Σ lr·wd (Sitzung 44, 2026-09-28, 20:45 gemessen, Hypothese aus gesehenen Daten) #neu/kandidat

**Beobachtungen (alle gesehen, post hoc):** (1) K5/R9: Die Festlegung in den ersten 25–50 Schritten tickt in Σ lr, wenn Adams Fenster ebenfalls in Σ lr gemessen werden (Weight Decay dort immer 1). (2) R1 post hoc (Sitzung 44, JOURNAL Zyklus 4, unabhängig nachgerechnet): Die Größe von Δ_pow bis Schritt 2000 folgt in den lr/wd-Zellen ab τ ≥ 250 der Zeit Σ lr·wd (±4–7 %), nicht den Schritten und nicht Σ lr allein (0.264). (3) R2: Bei wd 0.3 hielt die alte Wahl nach 50 Schritten trotzdem (0.83, 30/30). Mit einer Festlegungsuhr in Σ lr·wd wäre bei wd 0.3 nach 50 Schritten erst τ = 15 vergangen, zu früh für eine Festlegung; mit Σ lr ist es wie beim Preset. Das spricht für Σ lr als frühe Uhr (die Wechselseite bei 25 ist wegen fehlender Generalisierung nicht lesbar). **Hypothese:** Zwei Phasen mit zwei Uhren: die frühe Auswahl/Festlegung ist Adams lr-große Bewegung (bei t ≤ 50 hat der Weight Decay erst ≈ 5 % geschrumpft: e^(−lr·wd·t)), die spätere Verstärkung der gewählten Frequenzen ist die AdamW-Zeitskala 1/(lr·wd). **Test (vorbereitet):** [[experiments/EXP-103-early-steering-curve/README|EXP-103]] Teil B (gleiches lr·wd, lr ×2 bzw. ×0.5): frühe Punkte getrennt nach lr, späte zusammen. Ein sauberer Festlegungstest bräuchte R9-artige Wechsel bei wd 0.5/2 mit gleichem Σ lr.
**Suche 2026-09-28 (Sitzung 44, WebSearch, Snippets [S]):** „AdamW effective timescale learning rate times weight decay early training feature selection two timescales lr*wd“. Bekannt: AdamW als EMA mit Zeitskala 1/(η·λ) (Wang & Aitchison 2024/2025, arXiv 2405.13698) [S]; Weight Decay wirkt vor allem früh auf die Dynamik (Golatkar, Achille, Soatto 2019, arXiv 1905.13277) [S]; Grokking-Zeit ∝ lr·wd (Pracher et al. 2026, arXiv 2609.26679) [A]. Dass die lr·wd-Zeit bekannt ist, ist klar; die Trennung „Wahl in Σ lr, Verstärkung in Σ lr·wd“ für die datengesteuerte Frequenzwahl wurde nicht gefunden. Vorläufig.
**Gegenhinweis zu N51 (Sitzung 44, aus denselben Zahlen):** Bei t = 250 hat die Zelle wd 0.3 dieselbe Σ lr wie das Preset, liegt aber mit Δ_pow 2.80 unter dem Preset (3.22). Eine reine Σ lr-Uhr gilt dort also schon nicht mehr (Weight Decay hat bis 250 Schritte ≈ 7 % geschrumpft: e^(−0.075)). Die Zwei-Uhren-Hypothese kann höchstens für die ersten ≈ 25–50 Schritte gelten, in denen die Festlegung gemessen wurde. EXP-103 Teil B misst ab t = 250 und trennt das deshalb nur grob. Ein direkter Test bräuchte Δ_pow-Spektren bei 10–50 Schritten in den gekreuzten Zellen (einfach über `--spectra-at` ergänzbar, vor dem Lauf).

## N52: Wann schlägt die Reihenfolge die Menge? Epochenlänge n/B gegen das Festlegungsfenster (Sitzung 44, 2026-09-28, 21:01 gemessen) #neu/kandidat

**Hypothese:** Die datengesteuerte Frequenzwahl fällt in einem kurzen Fenster (≈ 25–50 Schritte, K4/K5). Eine feste Reihenfolge kann nur dann eine andere Frequenz durchsetzen, wenn das Fenster kürzer ist als eine Epoche (n/B Schritte); sonst summieren sich die Batches im Fenster zur Menge. **Vorhersage erster Ordnung (vor dem Piloten gerechnet, EXP-100, JOURNAL Zyklus 9):** B = 256 (15 Schritte je Epoche): ausgewaschen; B = 64 (60 Schritte): kann wirken (an der Schwelle). **Test:** L0-Machbarkeit (B = 256) und die Ausweichregel (B = 64); später eine Batchgrößen-Reihe bei fester Menge als Regime-Kurve (Reihenfolgewirkung gegen n/B). **Suche 21:01 (WebSearch, Snippets [S]):** „data ordering effect depends on epoch length relative to early critical period feature selection minibatch order grokking frequency“. Nächstverwandt: LeDoux 2026 (arXiv 2603.25047, „The Order Is The Message“) [S; Methode in Sitzung 43 im Volltext gelesen]: bei hoher Datendichte generalisieren alle Reihenfolgen schnell, bei 0.3 % isoliert sich der Reihenfolge-Kanal; die Deutung dort ist „Inhalt reicht bei hoher Dichte“. Eine Schwelle über das Verhältnis Epochenlänge zu Festlegungsfenster (und damit eine Vorhersage über die Batchgröße bei fester Datenmenge) wurde nicht gefunden. Vorläufig.

**N52, Nachtrag nach Nachrechnung:** B = 64 bei L = 50 ist eine Messerschneide (Überschuss fällt von 0.147 bei L = 25 auf exakt 0 bei L = 60 = eine Epoche). Die Regime-Aussage ist daher qualitativ: Reihenfolge-Überschuss nur innerhalb der ersten Epoche; ob er wirkt, hängt am Verhältnis von Epochenlänge zum Festlegungsfenster. Empirisch entscheidet die L0-Machbarkeit (B = 256 und 64).

**N52, Abgleich mit LeDoux 2026 (Sitzung 44, 21:08; HTML über ein zusammenfassendes Werkzeug, Zahlen zitiert):** Batch 256 in allen Versuchen (§4.1.2). p = 9973, 0.3 % Daten (≈ 300 000 Paare, also ≈ 1170 Schritte je Epoche): Stride 99.5 % Testgenauigkeit nach 487 Epochen, Zufall 0.30 % nach 5000 Epochen (§5.1.1). p = 97, 26.5 % Daten (≈ 2490 Paare, ≈ 10 Schritte je Epoche): alle nicht-adversariellen Reihenfolgen generalisieren, feste Reihenfolgen ≈ 20 % schneller als i.i.d. (§4.1.1). Deutung dort: „The ordering channel's practical importance thus scales inversely with content signal adequacy“ (§6.4). **Passt zu N52:** kurze Epoche (≈ 10 Schritte) → Reihenfolge nur mäßig; lange Epoche (≈ 1170) → Reihenfolge entscheidet. Unsere Formulierung ist eine andere, prüfbare Variable (n/B gegen das Festlegungsfenster, bei fester Datenmenge über die Batchgröße veränderbar); LeDoux verändert Datendichte und p gemeinsam. Gemessen wird dort Generalisierung, bei uns die Frequenzwahl.

**N51, Nachtrag (Sitzung 44, post hoc):** Die späte Uhr hat eine einfache Beschreibung: Nach Schritt 250 kommen ≈ 85 % des Δ_pow-Wachstums vom Abbau der Ziele des anderen Splits (log-Leistung −0.0012 je Schritt, ≈ 61 % der reinen Weight-Decay-Rate −0.002), ≈ 15 % vom Zuwachs der eigenen Ziele (`lab/confirm/P1_posthoc_decomp_s44.py`). Das ist Nandas „cleanup“ auf der lr·wd-Uhr, keine neue Mechanik; neu wäre höchstens die Trennung der beiden Uhren für die datengesteuerte Wahl.

**N51, Korrektur (Sitzung 44, nach Nachrechnung):** Nicht „85 % vom Abbau der fremden Ziele“, sondern: eigene Ziele halten sich, alle nicht eigenen Frequenzen zerfallen ähnlich schnell (≈ 0.5–0.75 der reinen Weight-Decay-Rate); die fremden Ziele nur wenig schneller als der Rest. Ob die späte Uhr lr·wd ist, entscheidet EXP-103 Teil B.

## N53: Steuer-Splits mit exakt flachen Häufigkeiten von a, b und c (Sitzung 45, 2026-09-28, 22:00 Berlin gemessen; reine Rechnung, kein Lauf) #neu/kandidat

**Anlass:** In einem Sprachmodell (Leiter Stufe 1 mit gebundenen Embeddings bzw. Verlust auf allen Positionen, Stufe 2) können die Token-Häufigkeiten der Zahlen die Ziele direkt in W_E prägen, ohne Rechnen. Die P1/EXP-016-Splits tragen die Ziele auch in ihren Randhäufigkeiten (count(b) 0.225, count(a) 0.165; `pba_spectrum_s44.py`). EXP-047 hat das nur für a/b und nur im Klassifikationsmodell kontrolliert.
**Konstruktion:** S(λ, D) = {(a, b): a − λb mod p ∈ D}, λ ∉ {0, −1}. Jedes a, jedes b und jedes c = a + b hat genau |D| Partner. Entlang einer Antidiagonale ist die Maske der Indikator von D nach a ↦ (1 + λ)a − λc, also M0(k) ∝ |D̂(k/(1 + λ))|². D = die 34 größten Werte einer Kosinussumme auf T/(1 + λ).
**Ergebnis** (`lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_split_s45.py`, 5 Zielmengen × λ ∈ {1, 2, 5}): |S| = 3842, alle drei Randhäufigkeiten exakt 34; Zielanteil von M0 0.660–0.722 (P1-Splits 0.17–0.19); die Top-5 von M0 sind in 14/15 Fällen genau die Ziele. Vorab-Lesart: **„brauchbar“**, und zwar viel stärker als die bisherigen Splits.
**Risiko (nach der Rechnung erkannt):** S ist unter allen p Verschiebungen (a, b) → (a + λs, b + s) invariant. Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316) berichten, dass RFM auf Aufteilungen, die unter einer nicht-trivialen Untergruppe invariant sind, nicht generalisiert. Ob ihr Invarianzbegriff diese Verschiebungen umfasst und ob ein Transformer daran scheitert, ist offen. **Symmetriebrechung durch Mischung** zweier Familien (λ₁, λ₂; je |D| = 17; `flat_marginal_mix_s45.py`): nur noch die Identität als Verschiebungssymmetrie, Zielanteil 0.46–0.59, aber die c-Häufigkeiten schwanken 18–34 (Überlappungen) → Vorab-Lesart **nicht erfüllt** (±20 %). Eine flache und zugleich symmetriefreie Variante fehlt noch.
**Nächster Schritt (nachrangig nach L0, GPU-Füllarbeit, Exploration):** 2 Seeds F/G mit S(1, D) in `freq_ban.py` (8000 Schritte): generalisiert der Transformer, und wie groß ist Δ_pow? Generalisiert er nicht, ist das ein Befund zur Symmetrie-Aussage von Tomàs Bernal et al. im Transformer; dann die gemischte Variante mit ausgeglichenen c-Häufigkeiten suchen. Erst danach als Kontrolle in EXP-102/Stufe 2 einsetzen.
**Neuheitsprüfung (Sitzung 45):** WebSearch „grokking modular addition structured train split "a - b" lines difference set Fourier frequencies training data symmetry“: nur bekannte Arbeiten (Nanda et al. 2023, 2602.16849, 2603.05228, 2503.22059), keine Split-Konstruktion dieser Art. Nach unserer Suche vom 28.09.2026 nicht gefunden; Linien-/Differenzmengen sind aber eine naheliegende Standardkonstruktion, die Einordnung ist vorläufig.

**N53, Nachtrag (Sitzung 45, 22:02 gemessen; `flat_marginal_swap_s45.py`, Lesarten vorab):** Tauschzug auf S(1, D): (a₁,b₁), (a₂,b₂), (a₃,b₃) raus, (a₁,b₂), (a₂,b₃), (a₃,b₁) rein, mit b₃ = a₁ + b₁ − a₂, b₂ = a₃ + b₁ − a₂. Das erhält die Häufigkeiten von a, b und c exakt (im Skript nach jedem Abschnitt geprüft). **Ergebnis** (3 Zielmengen): Nach 10 Zügen (30 von 3842 Paaren) ist keine Verschiebungssymmetrie mehr übrig (nur die Identität), Zielanteil 0.641/0.655/0.729 (vorher 0.654/0.669/0.743), Top-5 = Ziele. Mit mehr Zügen sinkt der Anteil stetig: 50 → 0.59–0.67, 200 → 0.44–0.51, 500 → 0.27–0.30, Top-5 bleiben die Ziele. Vorab-Lesart: **„flach und symmetriefrei, brauchbar“**. Die Zugzahl ist ein Stellrad für die Steuerstärke bei exakt flachen Häufigkeiten, also auch ein Split in P1-Stärke (≈ 0.18) ohne Häufigkeitssignal (Zugzahl dafür noch nicht bestimmt, > 500). **Grenze:** Nur die exakte Invarianz ist gebrochen; näherungsweise (> 99 % der Paare) bleibt sie bei wenigen Zügen erhalten. Andere Symmetrien (Vertauschen von a und b, Skalierungen) nicht geprüft. Der 2-Seed-GPU-Test nach L0 sollte deshalb drei Zugzahlen nehmen (0, 10, 500): Scheitern bei 0 und Gelingen bei 10 wäre ein Befund zur exakten Invarianz, Scheitern bei 10 und Gelingen bei 500 einer zur näherungsweisen.

## N54 (Sitzung 46, 29.09.): Zählt die frühe Festlegung in Epochen statt in Schritten? #neu/kandidat

Anlass: [[experiments/EXP-100-set-vs-order/README|EXP-100]] Wechselläufe (8 Seeds): Full-Batch repliziert das Fenster 25–50 Schritte (π 0.38 → 0.87), unter i.i.d.-Minibatch B = 256 ist nach 25 und 50 Schritten nichts festgelegt (π ≈ 0, auch bei gleichem Horizont, post hoc). 50 Full-Batch-Schritte sind 50 Epochen, 50 Schritte bei B = 256 nur 3.3. Vorhersage: bei B = 256 erscheint das Fenster bei ≈ 375–750 Schritten (25–50 Epochen); Alternative: Adam-Fenster in Schritten + Gradientenrauschen (dann eher bei einem festen Vielfachen der Schritte, nicht proportional zu N/B). Test: [[experiments/EXP-107-lockin-epochs/README|EXP-107]]. Literatur noch nicht geprüft (Suche nötig: „critical period data epochs vs steps minibatch lock-in“, Kleinman/Achille/Soatto zu kritischen Perioden).
*Stand 03:00 (EXP-107):* weder Schritt- noch Epochen-Uhr; unter B = 256 t½ ≈ 133 Schritte (Full-Batch ≈ 30). Verfeinerte Hypothese N54b (post hoc): Uhr ∝ √(N/B) (Rauschen/Wurzelregel); Test = B-Reihe mit vorab festgelegter Vorhersage. Literatursuche steht noch aus.
*Stand 03:19 (EXP-108, vorab festgelegt):* „Wurzel-Uhr gestützt“, α = 0.54 [0.52, 0.56] (B 1024 t½ ≈ 62 wie vorhergesagt 60–67; B 64 ≈ 290 gegen 240–266). Nächster Schritt: Literatur (Rauschskala, Wurzelregel für Adam, Malladi et al. 2022; kritische Perioden und Batchgröße) und eine Registrierung mit frischen Seeds + zweiter Lernrate.
*Literatur (erste Suche, 29.09. ≈ 03:21 Berlin; Suchbegriffe: „critical period early training commitment scales with batch size square root Adam noise scale feature selection lock-in steps“):* Gefunden nur allgemeine Batchgrößen-/Lernraten-Skalierung: Wurzelregel für Adam (Gradientenrauschvarianz ∝ η²/B; Malladi et al. 2022; Blog/Arbeiten zur kritischen Batchgröße, z. B. arXiv 2505.23971, arXiv 2601.05034; Noisy-Quadratic-Model, Zhang et al. 2019, arXiv 1907.04164). Keine Arbeit gefunden, die den **Zeitpunkt einer frühen Merkmalsfestlegung** gegen die Batchgröße misst. Einordnung: Die √-Skalierung ist als Rausch-Skalierung bekannt und plausibel; neu wäre höchstens die Messung an der Festlegung der Frequenzwahl (nach dieser einen Suche nicht gefunden, vorläufig). Weitere Suche (OpenReview, Scholar; kritische Perioden Achille et al. 2019, Kleinman et al. 2024) steht aus.
*Stand Sitzung 47 (29.09., 03:50):* EXP-108 stützte N54b (α = 0.54 [0.52, 0.56], nachgerechnet). **Literatursuche 29.09.** (Agent; Begriffe: Malladi SDE scaling rules Adam; critical learning periods batch size; grokking batch size minibatch; linear mode connectivity batch size; break-even point; surge phenomenon sign noise √B; u. a.): keine Arbeit gefunden, die eine frühe Festlegungszeit ∝ (N/B)^0.5 bei fester Lernrate misst → vorläufig „nicht gefunden“ (nicht „neu“). Nächstverwandt: [Malladi et al. 2022](https://arxiv.org/abs/2205.10287) (Adam-SDE, Wurzelregel), [Li et al. 2024](https://arxiv.org/abs/2405.14578) (Sign-Modell: Drift ∝ √B), [Granziol et al. 2022](https://arxiv.org/abs/2006.09092), [Jastrzebski et al. 2020](https://arxiv.org/abs/2002.09572), [Frankle et al. 2020](https://arxiv.org/abs/1912.05671), [Achille et al. 2019](https://arxiv.org/abs/1711.08856). Daraus abgeleitet (eigene Ableitung): Modell (i) feste Driftstrecke → t½ ∝ 1/(lr·√B); (ii) Drift schlägt Diffusion → t½ ∝ 1/B. Pilot [[experiments/EXP-109-lockin-lr-pilot/README|EXP-109]]: doppelte lr halbiert t½ bei B 1024, bei B 64 nur ×0.75 → Mischung. Bestätigung [[confirm/N54B_REGISTRATION_DRAFT|N54b]] eingefroren (624c2213), läuft.
*Stand Sitzung 47 (05:46):* N54b **bestätigt** (H1 α(1e-3) 0.583 [0.560, 0.606]; H2 Δα +0.139 [0.098, 0.178]; nachgerechnet). Modellvergleich (vorab festgelegt): Drift + ≈ 2 Epochen passt am besten. **Neu (EXP-110, 2 Seeds):** bei B 64 ist t½ in lr nicht monoton (lr 4e-3 später als 1e-3 und 2e-3) → Kandidat N54c „Minimum der Festlegungszeit in der Lernrate bei kleinem Batch“; vor einer Registrierung Literatur zu „optimal learning rate vs batch size surge“ (Li et al. 2024 beschreiben einen Anstieg-und-Abfall der optimalen lr mit B — prüfen, ob das dasselbe Phänomen ist).
*Korrektur Sitzung 47 (05:51):* Die Nicht-Monotonie bei B 64 hat sich in EXP-111 (Seeds 3702–3703) nicht bestätigt (lr 4e-3 dort etwas schneller als 2e-3); Kandidat N54c zurückgestellt.


## N55 (Sitzung 48, 29.09., 07:47 Berlin gemessen): Operanden-Verlust als Grokking-Bremse und Steuerungsdämpfer #neu/kandidat

**Beobachtung (Exploration, [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]], [[experiments/EXP-112-lm-ladder-minibatch/README|EXP-112]]):** Next-Token-Verlust auf der Position, die den zweiten Operanden b vorhersagt, verzögert Grokking bei add 113 (30 % Daten) von ≈ 750 auf 9 000–46 000 Full-Batch-Schritte und lässt die Datensteuerung nach dem Grokking bei ≈ 55 % (nachgerechnet; Störfaktor Trainingslänge offen). Ohne das b-Ziel hält die Steuerung im Full-Batch, unter Minibatch im vollen LM-Format ist sie kleiner.
**Hypothese (Mechanismus, ungeprüft):** b ist aus a nicht vorhersagbar, lässt sich aber für die Trainingspaare auswendig lernen (Verlust ≈ log 113 → log 34 bei 30 % Daten). Dieser Gedächtnisdruck verschwindet mit dem Grokking nicht und konkurriert dauerhaft mit Weight Decay und mit dem Fourier-Schaltkreis.
**Prüfbar:** Dosis (Gewicht des b-Verlusts 0 … 1) gegen Grokking-Zeit und Δ_pow; Datenanteil (bei 100 % Daten ist b nicht memorierbar → Vorhersage: keine Bremse); Curriculum Antwort → Full-Sequence (Blogbeitrag unten: Algorithmus bleibt erhalten).
**Suche (29.09., WebSearch):** „grokking modular addition next-token loss on all tokens operands delays generalization“; „"grokking" "loss on all positions" OR "full sequence loss" OR "only on the answer token" modular arithmetic“. Nächstverwandt: LessWrong-Beitrag „Training a Transformer to Compose One Step Per Layer“ (D3-Komposition: Full-Sequence-Verlust → Nachschlagetabelle, Antwort-Verlust → Algorithmus; keine Zeitmessung), Power et al. 2022 (Verlust nur auf der Antwort). Keine Messung der Verzögerung oder der Wirkung auf die Frequenzsteuerung gefunden → vorläufig „nicht gefunden“, nicht „neu“.

## N56: Beschleunigt eine konstruierte Faktenauswahl das Lernen eines von Grund auf trainierten Sprachmodells? (Sitzung 52, 17:42 gemessen) #neu/kandidat

- **Frage:** R5 (konstruierte Splits groken ≈ ×6.5 früher) im kleinen LM: Lernen die Rechenfakten aus F/G früher als aus einem gleich großen Zufallssplit? Test: [[experiments/EXP-119-lm-speed-r5/README|EXP-119]] (vorab festgelegt, eingereiht).
- **Suche (2026-09-29, WebSearch, 2 Abfragen, Wortlaut im EXP-119-README):** nächstverwandt Zhou et al. 2024 (Fourier-Merkmale, von Grund auf nur niedrige Frequenzen), Datenaugmentation/Transfer beschleunigen Grokking in Spielzeugaufgaben (arXiv 2405.16658, GrokTransfer 2504.13292), Howe 2026b. Die Frage selbst nach unserer Suche nicht gefunden (vorläufig).
- **Vorwissen:** Stufe 1 (Textformat, kleines Modell): R 0/10 bzw. 2/10 generalisiert gegen F/G 40/40; im LM keine Grokking-Lücke (post hoc, 9 Läufe), ein Vorteil müsste also den Lernbeginn verschieben.
- **Stand Sitzung 54:** EXP-119 „constructed faster“ (q ≥ 3.15 / ≥ 2.61). Die Annahme „im LM keine Grokking-Lücke“ war falsch: Der Zufallssplit memorisiert gleich früh und bleibt dann auf einem Plateau ≈ 0.3, das post hoc vollständig aus Kommutativität besteht (N57).

## N57: Besteht das Plateau vor dem Grokking aus Kommutativität? (Sitzung 54, 23:42) #neu/kandidat

- **Beobachtung:** Im LM (EXP-119, Zufallssplit) sind nach der Memorisation genau die ungesehenen Fakten richtig, deren Tauschpaar trainiert wurde (0.99 gegen 0.03), [[experiments/EXP-119-lm-speed-r5/README|EXP-119 Nachtrag 1]].
- **Frage:** Gilt das auch im Spielzeugmodell auf dem Grokking-Plateau (Zufallssplit, Schritte zwischen Memorisation und Generalisierung)? Wenn ja: Die Test-Genauigkeit vor dem Grokking ist kein „Rauschen um 0.3“, sondern eine exakt vorhersagbare Symmetrie-Generalisierung; der eigentliche Sprung betrifft nur Fakten ohne Tauschpartner. Folgefragen: Wann setzt die Kommutativität ein (vor oder nach der Memorisation)? Steuern konstruierte Splits den Sprung bei den übrigen Fakten?
- **Billigster Test:** `freq_ban.py` Standardaufbau mit Zufallssplit, 2–3 Seeds, Test-Genauigkeit getrennt nach Tauschpaar im Training an Zwischenständen (braucht Zwischen-Checkpoints oder eine Auswertung im Trainer → Trainer-Hash-Sperre beachten; ggf. `repro/train.py` erweitern). Lesart vorab festlegen.
- **Suche (2026-09-29, 1 Abfrage, Wortlaut in [[paper/related_work]] Nachsuche S54):** Kommutativität als bekannte Memorisations-Abkürzung (wird im Datendesign ausgeschlossen); eine Messung „Plateau = Kommutativität“ nach dieser Suche nicht gefunden (vorläufig; gezielter suchen, z. B. „symmetric pairs“ in Power et al. 2022, Nanda et al. 2023, Liu et al. 2022).
- **Erster Blick (23:43, beschreibend, ohne Vorab-Lesart, gespeicherte R4-Läufe Seeds 2600–2603, 8 Läufe):** Im Spielzeugmodell liegt die Test-Genauigkeit auf Zufallssplits vor dem Grokking bei 0.01–0.2 (Schritte 250–4000) und steigt allmählich; ein reines Kommutativitäts-Plateau läge bei ≈ 0.3 (Anteil zurückgehaltener Paare mit Tauschpartner im Training). Also **kein** voll ausgebildetes Kommutativitäts-Plateau im Spielzeugmodell; ob ein Teil der frühen Test-Genauigkeit Kommutativität ist, bleibt offen (braucht Zwischenmodelle). Der Unterschied LM ↔ Spielzeugmodell ist selbst eine Frage (Architektur? Verlust? Text?).
- **Korrektur/Ergebnis (30.09., 00:02): [[experiments/EXP-122-toy-commutativity/README|EXP-122]] „Kommutativität zuerst“ (4/4 Läufe, vorab festgelegt):** Auch im Spielzeugmodell trägt die Kommutativität die Test-Genauigkeit vor dem Grokking (50 % des Weges: 0.35–0.67 auf Paaren mit Tauschpartner gegen ≤ 0.03 sonst). Der „erste Blick“ oben war ein Fehlschluss aus der Gesamtkurve.
- **Suche 30.09. (00:04):** siehe [[paper/related_work]] „Nachsuche Sitzung 54 … Kommutativität vor dem Grokking“: Rolle der Kommutativität und kommutative Augmentation bekannt (2411.05353, 2405.16658); die Plateau-Messung nicht gefunden (vorläufig, Volltexte offen).
- **Nachtrag 1 (00:08):** Konstruierte Splits (P2d, 4 Läufe): Kommutativität liegt auch vorn, aber die übrigen Paare generalisieren schon früh mit („teilweise“). Arbeitsbild: zwei Stufen (Kommutativität → übrige Paare); die Datenauswahl verkürzt vor allem die zweite. **Nachfolger (vorzumerken, sauber festlegen):** gleiche Init-Seeds für Zufalls- und konstruierte Splits, ≥ 10 Seeds, dichte Zwischenstände (z. B. jede 5 % des Weges), Maße acc_swap/acc_other und Beginn jeder Stufe relativ zur Memorisation; Vorhersage: Zufallssplit-Stufe 2 beginnt erst nahe am Grokking, konstruierte Splits früh.
- **Sitzung 55 (30.09., 01:00): Literatur geschärft, Nachfolger festgelegt.** **He, Wang, Chen, Yang 2026** (https://arxiv.org/abs/2602.16849, §3.3, HTML selbst geprüft) zeigen das Muster „Tauschpartner der Trainingsdaten richtig, Rest nicht“ bei zufälligem Split und drei Stufen – aber in einem Netz mit Eingabe h_x + h_y, in dem die Kommutativität eingebaut ist. Die Beobachtung an sich ist damit **#neu/bekannt** für symmetrische Netze; offen (nach unserer Suche vom 30.09. nicht gefunden) bleiben: die Kommutativität als *gelernte* erste Stufe im Transformer, die Verkürzung der zweiten Stufe durch die Paarauswahl, das LM-Plateau. Volltexte 2411.05353 (§3.5) und 2405.16658 (§4.2) geprüft: nur Entfernen/Hinzufügen von Tauschpaaren, keine Aufteilung nach Tauschpaar. Nachfolger: [[experiments/EXP-123-commutativity-stages/README|EXP-123]] (20 R5-Einheiten × R/E2_0/D_0, vorab, läuft).
- **Ergebnis EXP-123 (02:47):** Kommutativität als gelernte erste Stufe vor dem Grokking im Transformer: 18/18 R5-Einheiten (vorab, Holm 7.6·10⁻⁶). Die Hypothese „Datenauswahl verkürzt vor allem Stufe 2“ ist nicht gestützt (d 0.041 unter 0.05); post hoc verkürzt sie Stufe 1 stärker (×11.1) als Stufe 2 (×4.6). Status: #neu/kandidat für „gelernte Stufe im Transformer“ (He et al. 2026a zeigt das Muster mit eingebauter Kommutativität). Offene Frage: Warum steigt die Kommutativität auf konstruierten Splits so viel früher? (Die Zählkontrolle D verhält sich wie R.)
- **Zyklus 15 (02:54, post hoc):** In E2 hängt t_swap so eng an der frühen W_E-Zielenergie (ρ −0.80) wie t_gen (−0.79). Trennender Folgeversuch (vorgemerkt): Zielfrequenzen in den ersten Schritten unterdrücken (freq_ban-Bann) und messen, ob die Kommutativitätsstufe dann später kommt (→ Kommutativität über Fourier-Struktur) oder nicht (→ eigener Lernpfad).
- **Zyklus 20 (03:11, beschreibend):** Kommutativität setzt um die Memorisation ein (t_mem 150 in allen Armen); bei E2 bei t_mem schon 0.22 (11/20 Einheiten ≥ 0.1 vorher), bei R 0.05 und ≥ 0.1 erst nach ≈ 800 Schritten.
- **Sitzung 57 (06:26 gemessen, post hoc, nur Split-Metadaten, kein Lauf):** Liegt der ≈ ×11 frühere Kommutativitäts-Schritt der konstruierten Splits (EXP-123) an mehr trainierten Tauschpartnern? **Nein:** In den 20 R5-Einheiten ist der Tauschanteil (Anteil der Trainingspaare, deren Spiegel ebenfalls im Training liegt) R 0.303 / E2_0 0.305 / D_0 0.303 und der Test-Tauschanteil (Testpaare mit trainiertem Spiegel) R 0.300 / E2_0 0.299 / D_0 0.300 (Spannweiten je 0.27–0.32; aus `lab/confirm/r5_splits/r5_u*.json`, Feld `match`). Gleich viele Nachschlage-Gelegenheiten, trotzdem lernen E die Regel viel früher und D nicht. Das schließt „mehr Spiegelpaare“ als Erklärung aus und passt zur Kopplung von t_swap an die frühe W_E-Zielenergie (ρ −0.80, Zyklus 15 S55). **Spekulation (ungeprüft):** Konstruierte Splits erreichen die Vertauschung über früh gebildete, in a und b symmetrische Fourier-Merkmale (cos(ω(a+b)) ist symmetrisch), nicht über gelerntes Nachschlagen der Spiegel; der vorgemerkte Bann-Versuch (EXP-124) würde das trennen, ruht aber nach Regel 20a.
- **Sitzung 57, Zyklus 6 (06:29, post hoc, vorab-Lesart „gleicher Weg“):** Bei t_swap haben alle Arme dieselbe W_E-Top-5-Konzentration (Median R 0.31, D_0 0.32, E2_0 0.29; Init 0.10; bei t_gen ≈ 0.5–0.58; mit dem Schnappschuss nach t_swap 0.33/0.33/0.38). Die Vertauschungsstufe liegt also überall an derselben Stelle des Konzentrationswegs; konstruierte Splits kommen ≈ 13× früher dorthin. Kovariation, kein Kausalnachweis (`lab/experiments/EXP-123-commutativity-stages/posthoc_route_s57.json`).

## N58: Setzt sich die Faktenauswahl beim Nachtrainieren gegen vortrainierte Zahlmerkmale durch? (Sitzung 58, 30.09., 09:03 Berlin) #neu/kandidat

- **Frage:** Ein vortrainiertes LM (Pythia-160M) trägt in den Zahl-Einbettungen schon Frequenzen (1–5 und 11/23/45 ≈ Dezimalperioden 10/5/2.5; `EXP-127/pretrained_spectrum.json`). Bestimmt beim Nachtrainieren auf mod-113-Fakten die Auswahl der Fakten, welche Frequenzen hinzukommen und genutzt werden – und gewinnt sie auch, wenn die Ziele mit den vortrainierten Spitzen konkurrieren? Pilot: [[experiments/EXP-127-pretrained-lm/README|EXP-127]].
- **Suche (30.09.2026; WebSearch):** „fine-tuning pretrained language model modular addition Fourier features number token embeddings training data selection frequencies“; „arXiv 2026 pretrained LLM fine-tuned modular arithmetic which Fourier frequencies emerge data composition Pythia“; „fine-tuning GPT-2 OR Pythia modular addition Fourier embeddings grokking pretrained initialization frequencies selected“.
- **Nächstverwandt:** Zhou, Fu, Sharan, Jia 2024 ([arXiv 2406.03445](https://arxiv.org/abs/2406.03445)): feinjustiertes GPT-2-XL rechnet Addition mit Fourier-Merkmalen, die aus dem Vortraining stammen; von Grund auf nur tiefe Frequenzen; vortrainierte Einbettungen „retten“ ein Zufallsmodell – Auswahl der Trainingsbeispiele nicht variiert. Zhou et al. 2025 FoNE ([2502.09741](https://arxiv.org/abs/2502.09741)): Pythia lernt die Frequenzen schrittweise im Vortraining. „Let Me Grok for You“ ([2504.13292](https://arxiv.org/pdf/2504.13292)): GPT-Einbettungen als Start für modulare Addition (Tempo, nicht Frequenzwahl). Fu et al. 2026 ([2604.20817](https://arxiv.org/pdf/2604.20817)): Daten/Tokenizer bestimmen Zahlenmerkmale beim Vortraining. Gomezjurado Gonzalez 2026 ([2604.13082](https://arxiv.org/abs/2604.13082)): Grokking-Verzögerung bei Collatz, von Grund auf; ein Pythia-160M-Nachtraining auf Collatz erwähnt, ohne Frequenzmessung (nur Suchzusammenfassung gelesen).
- **Einordnung (vorläufig):** Dass vortrainierte Modelle Fourier-Zahlmerkmale haben und beim Nachtrainieren nutzen, ist bekannt. Dass die *Auswahl der Nachtrainingsfakten* vorschreibt, welche Frequenzen in den Zahl-Einbettungen hinzukommen, haben wir nach unserer Suche vom 30.09.2026 nicht gefunden. Nicht „neu“ behaupten; erst Pilot, dann ggf. Bestätigung.
- **Volltext-Nachtrag (09:30, Commit-Zeit, arXiv-HTML 2406.03445 über ein Zusammenfassungswerkzeug gelesen):** Zhou et al. finden in Zahl-Einbettungen vortrainierter Modelle Ausreißer mit Perioden 2, 2.5, 5 und 10; „Fourier features are learned during pre-training“, von Grund auf trainierte Modelle haben sie nicht. Andere Formate (umgekehrte polnische Notation) und Multiplikation zeigten *dieselben* Perioden; eine Variation der ausgewählten Trainingsbeispiele mit dem Ziel anderer Frequenzen gibt es dort nicht. Unsere Basismessung über 0–112 passt (11/23/45 ≈ Perioden 10.3/4.9/2.5); Periode 2 ist bei 113 Zahlen kein eigener Frequenzbehälter (k = 56.5; k = 56 nur 0.026–0.03). Einordnung von N58 unverändert (vorläufig „nicht gefunden“).
- **Nachtrag Sitzung 59 (11:26, Exploration, 2 Seeds, nur Schritt 0):** Erster Gradient der Zahl-Eingabezeilen (Antwortverlust, Trainingsreihenfolge): Mit 16 Fakten je Sequenz trägt er die Maskenfrequenzen weder im vortrainierten Pythia (Δ_pow ≈ 0) noch in einem zufällig gestarteten LM (≈ 0). Mit **einem** Fakt je Sequenz trägt er sie im zufällig gestarteten LM klar (Δ_pow 1.21/1.31, Top 5 = genau die eigenen Ziele), im vortrainierten Pythia weiterhin nicht (−0.13/−0.01, tiefe Frequenzen). → Zwei getrennte Hemmnisse der Rechnung erster Ordnung: Mehrfakten-Kontext (bei Init) und vortrainierte Zahlstruktur. Details [[JOURNAL]] Sitzung 59, Zyklen 2–3; S58-Messung war durch sortierte Faktenreihenfolge verfälscht.

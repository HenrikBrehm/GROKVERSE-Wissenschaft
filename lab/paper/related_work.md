---
id: related-work
status: entwurf
datum: 2026-09-27
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# Verwandte Arbeiten (Entwurf für den Preprint)

**Zweck und Status.** Dieses Dokument ist die **Grundlage für eine menschliche Prüfung**, kein fertiger Abschnitt des Papers und kein Urteil über Neuheit.
Es wurde von einem KI-Agenten am 2026-09-27 zusammengestellt. Alle Neuheitsaussagen sind vorläufig und lauten höchstens: „nach unserer Suche nicht gefunden (vorläufig)“.
Einordnungen, die nur auf Such-Snippets beruhen, sind als **nur Snippet** markiert. Vor der Einreichung müssen die mit ⚠ markierten Arbeiten im Volltext gelesen werden.

**Unsere Aussagen (Kurzform, Geltungsbereich: 1-Schicht-Transformer „arch25k“, AdamW lr 1e-3, wd 1, Full-Batch, 30 % Trainingsanteil, One-hot-Token):**
- **K2:** Konstruierte Splits (welche Paare (a, b) im Training sind) steuern kausal, welche Frequenzen bzw. (D₅₉) Irreps W_E lernt; vorhergesagt vom Masken-Spektrum M0; add 113, mul 113, add 97, D₅₉, je 50 frische Seeds.
- **K2-Funktion:** Gleich große W_E-Störungen entlang der gesteuerten Frequenzen senken den Logit-Abstand stärker als entlang von Kontrollfrequenzen (add 113, mul 113, add 97; D₅₉ offen). Grenze: Funktion folgt Energie.
- **K4/K4b/K4c:** Schon ≈ 25–50 Schritte auf einem ersten Split legen die Frequenzwahl gegen einen paar-disjunkten zweiten Split über Tausende Schritte fest; Wechsel nach 50 Schritten → Endmodell nutzt die alten, nach 25 → die neuen Frequenzen; gelöschtes Adam-Momentum wirkt wie weniger Vorschritte.
- **K4d/K4e:** Reset der Attention (besonders Wertepfad W_V, W_O; Gewichte + AdamW-Zustand) beim Wechsel hebt die Persistenz weitgehend auf; MLP-Reset wirkt deutlich schwächer.

**Legende Prüfstatus:**
- **[A]** Abstract in dieser Sitzung per WebFetch der arXiv-Seite gelesen.
- **[L]** Volltext bzw. HTML früher im Labor per Abrufwerkzeug geprüft (Nachweis in [[NOVEL_DIRECTIONS]]); in dieser Sitzung nur Abstract/Snippet erneut gesehen.
- **[K]** Klassische, weithin bekannte Arbeit; bibliografische Angaben per Suchergebnis bestätigt, Inhalt aus Abstract/Snippet und Fachwissen, Volltext nicht erneut gelesen.
- **[S]** nur Snippet (Suchzusammenfassung); Inhalt nicht selbst verifiziert.

---

## 1. Suchprotokoll

**Datum:** 2026-09-27 (eine Sitzung). **Werkzeuge:** WebSearch (allgemeine Websuche; Treffer aus arXiv, OpenReview, PMLR/NeurIPS/ICLR-Proceedings, Semantic Scholar, ML Anthology, ResearchGate) und WebFetch (arXiv-Abstractseiten).
**Einschränkung:** Google Scholar und die Semantic-Scholar-API wurden **nicht direkt** abgefragt (kein Zugriff über die Werkzeuge); Semantic Scholar und OpenReview nur als Trefferseiten der Websuche bzw. über „openreview“ im Suchstring.
Frühere Suchen des Labors (2026-09-26/27, mehr als 40 Suchstrings) sind in [[NOVEL_DIRECTIONS]] und [[FINDINGS_DETAILS]] protokolliert und wurden hier als Ausgangspunkt übernommen, nicht wiederholt.

**Suchstrings dieser Sitzung (wörtlich):**
1. `grokking modular arithmetic training set composition determines which Fourier frequencies learned`
2. `grokking switch training data distribution early training features persist modular addition`
3. `arXiv 2026 group composition irreps learned depend on training data distribution non-uniform`
4. `critical learning periods transformer attention reset plasticity arXiv`
5. `warm-starting neural network training generalization gap Ash Adams 2020 shrink and perturb`
6. `"modular addition" training pairs subset spectrum which frequencies neural network learns data-dependent frequency selection`
7. `Hermann Lampinen "What shapes feature representations" datasets architectures training`
8. `Frankle linear mode connectivity lottery ticket hypothesis stability early in training`
9. `"Fortuitous forgetting" Zhou later-layer reinitialization relearning`
10. `active forgetting pretraining reset embedding layer periodically language plasticity Chen 2023`
11. `Mohamadi "Why do you grok" theoretical analysis grokking modular addition kernel regime`
12. `Morwani "Feature emergence via margin maximization" modular addition Fourier`
13. `Stander "Grokking group multiplication with cosets" 2024`
14. `Kleinman Achille Soatto critical learning periods emerge even in deep linear networks`
15. `Dohare loss of plasticity in deep continual learning Nature 2024 continual backpropagation`
16. `continual learning modular arithmetic sequential tasks grokking retained Fourier features transfer new modulus`
17. `"The Order Is The Message" LeDoux 2026 data ordering`
18. `curriculum data order determines which features learned toy transformer interpretability 2025 2026 arXiv`
19. `"One Period to Rule Them All" critical learning periods deep networks 2025`
20. `Frankle Schwab Morcos "The Early Phase of Neural Network Training" 2020`
21. `grokking "data selection" OR "training subset" controls learned representation modular arithmetic Fourier key frequencies intervention 2026`
22. `openreview grokking dihedral group irreducible representations training data which irreps learned`
23. `grokking pretraining on one split then fine-tune different split modular addition representation lock-in`
24. `Zhou Zhang Xu "frequency perspective" grokking arXiv 2405.17479`
25. `Rahaman "On the spectral bias of neural networks" 2019 ICML`
26. `Zhong Liu Tegmark Andreas "The Clock and the Pizza" two stories mechanistic explanation`
27. `Salah Yevick "Controlling Grokking with Nonlinearity and Data Symmetry"`
28. `Lampinen 2024 "Learned feature representations are biased by complexity, learning order, position"`
29. `Zhang Bengio Singer "Are all layers created equal" re-initialization robustness critical layers`
30. `Nikishin 2022 "The Primacy Bias in Deep Reinforcement Learning" resets last layers`
31. `resetting attention layers restores plasticity transformer distribution shift which layer stores early features reset value output projection`
32. `Asadi "Resetting the Optimizer in Deep RL" Adam moment reset`
33. `non-uniform sampling of input pairs modular arithmetic network learns frequencies aligned with sampling pattern Fourier transform of training mask`
34. `Kunin "Alternating Gradient Flows" feature learning two-layer networks NeurIPS 2025 authors modular addition order frequencies`
35. `Tian "Composing Global Optimizers" reasoning tasks algebraic structure grokking 2024`
36. `openreview.net grokking "training distribution" Fourier "frequencies" steer OR control OR select "embedding" modular 2026`
37. `"loss of plasticity" transformer attention entropy collapse Lyle 2025 "disentangling the causes of plasticity loss"`

**Per WebFetch gelesene Abstracts (arXiv):** 2602.03655, 2606.02993, 2602.16849, 2609.17571, 2607.05104, 2507.20057, 2510.09687, 2605.04396, 2609.26679, 2603.25047, 2606.17399, 2606.12966, 2608.04451.

**Ergebnis der gezielten Suchen nach Vorwegnahmen (Strings 1, 2, 3, 6, 16, 21, 22, 23, 33, 36):** Kein Treffer, der die Zusammensetzung der Trainingspaare als Steuergröße für die Frequenz-/Irrep-Wahl untersucht, und kein Treffer, der die Frequenzwahl vor und nach einem kontrollierten Datenwechsel misst. Ein Snippet zu String 33 behauptete, bei nicht-uniformer Stichprobe „löse sich der Fourier-Bias unter einer Schwelle auf“; die Quelle war ein Medium-Blogbeitrag, kein begutachtetes Paper (**nur Snippet**, nicht zitierfähig).

---

## 2. Grokking und Fourier-Schaltkreise bei modularer Arithmetik

**Power, Burda, Edwards, Babuschkin, Misra (2022).** *Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets.* arXiv:2201.02177. https://arxiv.org/abs/2201.02177 [K]
- Zeigt: Das Phänomen Grokking auf algorithmischen Datensätzen, Abhängigkeit vom Trainingsanteil und Weight Decay.
- Abgrenzung: Keine Frequenzanalyse, keine Steuerung, welche Lösung gelernt wird.
- Schränkt Neuheit ein: **nein** (Hintergrund).

**Nanda, Chan, Lieberum, Smith, Steinhardt (2023).** *Progress Measures for Grokking via Mechanistic Interpretability.* ICLR 2023. https://arxiv.org/abs/2301.05217 [L]
- Zeigt: Der 1-Schicht-Transformer löst Addition mod 113 mit wenigen „Key-Frequenzen“ (Einbettung → Attention/MLP → Logits); die Key-Frequenzen unterscheiden sich zwischen Seeds; Ablationen auf Frequenzen (restricted/excluded loss).
- Abgrenzung: Unsere Architektur und unser Messmaß (W_E-Spektrum, Frequenz-Ablation) folgen dieser Arbeit. Sie fragt nicht, *was* die Key-Frequenzen bestimmt, und variiert den Split nicht getrennt von der Init.
- Schränkt Neuheit ein: **nein** für K2/K4; **teilweise** für K2-Funktion (Frequenz-Ablationen als Funktionsnachweis sind dort eingeführt; unsere gleich-normierten Störungen sind eine Variante).

**Zhong, Liu, Tegmark, Andreas (2023).** *The Clock and the Pizza: Two Stories in Mechanistic Explanation of Neural Networks.* NeurIPS 2023 (Oral). https://arxiv.org/abs/2306.17844 [S]
- Zeigt: Bei **fester Trainingsmenge** führen kleine Änderungen von Hyperparametern (Attention-Stärke, Breite) und Init zu qualitativ verschiedenen Algorithmen (Clock, Pizza, Mischformen).
- Abgrenzung: Variiert Architektur/Init, nicht die Trainingsmenge; betrifft den Algorithmustyp, nicht welche Frequenzen.
- Schränkt Neuheit ein: **nein**, aber wichtig als Hinweis, dass „was gelernt wird“ auch von Hyperparametern abhängt (unser Geltungsbereich ist eine Architektur).

**Gromov (2023).** *Grokking Modular Arithmetic.* arXiv:2301.02679. https://arxiv.org/abs/2301.02679 [K]
- Zeigt: Analytische Lösung (Zweischicht-MLP, quadratische Aktivierung) aus periodischen Gewichten; viele Frequenzmengen sind gleich gute Lösungen.
- Abgrenzung: Stützt unsere Prämisse „jede Frequenzmenge ist eine gleich richtige Lösung“; keine Datensteuerung.
- Schränkt Neuheit ein: **nein**.

**Morwani, Edelman, Oncescu, Zhao, Kakade (2024).** *Feature Emergence via Margin Maximization: Case Studies in Algebraic Tasks.* ICLR 2024. https://arxiv.org/abs/2311.07568 [K/S]
- Zeigt: Max-Margin-Lösungen für modulare Addition, Paritäten und endliche Gruppen verwenden Fourier-Features bzw. Irreps; im Max-Margin-Limit werden (laut Laborsuche) alle Frequenzen genutzt.
- Abgrenzung: Asymptotische Aussage über die volle Datenmenge; sagt nicht, welche Teilmenge bei endlichem Training und Teil-Split gewählt wird.
- Schränkt Neuheit ein: **nein** (eher Spannung: im Max-Margin-Limit wäre die Split-Prägung transient; zu diskutieren).

**Mohamadi, Li, Wu, Sutherland (2024).** *Why Do You Grok? A Theoretical Analysis of Grokking Modular Addition.* ICML 2024. https://arxiv.org/abs/2407.12332 [S]
- Zeigt: Im frühen Kernel-Regime braucht jedes permutationsäquivariante Modell einen konstanten Anteil aller Paare; erst das Verlassen des Kernel-Regimes erlaubt Generalisierung mit wenigen Daten.
- Abgrenzung: Keine Aussage, welche Frequenzen gewählt werden. Relevant für K4: Die Festlegung nach 25–50 Schritten liegt womöglich im Kernel-/frühen Regime.
- Schränkt Neuheit ein: **nein**.

**Kumar, Bordelon, Gershman, Pehlevan (2024).** *Grokking as the Transition from Lazy to Rich Training Dynamics.* ICLR 2024. https://arxiv.org/abs/2310.06110 [K]
- Zeigt: Grokking als Übergang von lazy zu rich; Init-Skala steuert den Zeitpunkt.
- Abgrenzung: Zeitpunkt des Grokkings, nicht Frequenzwahl oder Datenwechsel.
- Schränkt Neuheit ein: **nein**.

**Liu, Kitouni, Nolte, Michaud, Tegmark, Williams (2022).** *Towards Understanding Grokking: An Effective Theory of Representation Learning.* NeurIPS 2022. https://arxiv.org/abs/2205.10343 — sowie **Liu, Michaud, Tegmark (2023).** *Omnigrok.* ICLR 2023. https://arxiv.org/abs/2210.01117 [K]
- Zeigen: Repräsentationslernen und Datenanteil/Gewichtsnorm als Erklärung des Grokkings.
- Schränkt Neuheit ein: **nein** (Hintergrund).

**Varma, Shah, Kenton, Kramár, Kumar (2023).** *Explaining Grokking through Circuit Efficiency.* arXiv:2309.02390. https://arxiv.org/abs/2309.02390 [K]
- Zeigt: Konkurrenz von memorierenden und generalisierenden Schaltkreisen unter Weight Decay.
- Schränkt Neuheit ein: **nein**.

**Lyu, Jin, Li, Du, Lee, Hu (2024).** *Dichotomy of Early and Late Phase Implicit Biases Can Provably Induce Grokking.* ICLR 2024. https://arxiv.org/abs/2311.18817 [K]
- Zeigt: Frühe (kernel-artige) und späte (Margin-)Implizitbiase erzeugen Grokking.
- Abgrenzung: Relevant als Rahmen, warum früh geprägte Strukturen später noch umgeschrieben werden *könnten*; K4 zeigt, dass es bei uns nicht passiert.
- Schränkt Neuheit ein: **nein**.

**Mallinar, Beaglehole, Zhu, Radhakrishnan, Pandit, Belkin (2025).** *Emergence in Non-Neural Models: Grokking Modular Arithmetic via Average Gradient Outer Product.* ICML 2025. https://arxiv.org/abs/2407.20199 [L]
- Zeigt: Recursive Feature Machines (ohne Zufalls-Init) groken und lernen block-zirkulante (Fourier-)Features.
- Abgrenzung: Interessant für K2: Ohne Zufalls-Init muss die Wahl der Features aus den Daten kommen; die Arbeit analysiert aber nicht, welche Frequenzen der Split festlegt.
- Schränkt Neuheit ein: **nein** (⚠ Volltext prüfen, ob dort Frequenzen je Split berichtet werden).

**Tian (2024).** *Composing Global Optimizers to Reasoning Tasks via Algebraic Objects in Neural Nets.* arXiv:2410.01779. https://arxiv.org/abs/2410.01779 [S]
- Zeigt: Algebraische Struktur der globalen Optima für quadratische Zweischichtnetze auf abelschen Gruppen; Lösungen aus Teillösungen zusammengesetzt.
- Schränkt Neuheit ein: **nein**.

**He, Wang, Chen, Yang (2026).** *On the Mechanism and Dynamics of Modular Addition: Fourier Features, Lottery Ticket, and Grokking.* arXiv:2602.16849 (OpenReview https://openreview.net/forum?id=Qc4RLl7t3S). https://arxiv.org/abs/2602.16849 [A, L] ⚠
- Zeigt: In Zweischichtnetzen konkurrieren Frequenzen **innerhalb jedes Neurons**; der Gewinner ist durch den **anfänglichen spektralen Betrag und die Phasen-Fehlausrichtung** bestimmt (Lotterie); Mehrheitsabstimmung über Neuronen; Grokking in drei Stufen.
- Abgrenzung: Volle Trainingsmengen bzw. Init als Quelle der Wahl; die Zusammensetzung der Trainingspaare wird laut Labor-Volltextprüfung nicht als Steuergröße betrachtet.
- Schränkt Neuheit ein: **teilweise** — der *Mechanismus „Wettbewerb der Frequenzen mit anfänglichem Vorsprung“* ist dort gezeigt; K2 verschiebt die Quelle des Vorsprungs von der Init auf die Daten. K4 (Festlegung) ist mit ihrer Lotterie-Logik vereinbar und muss als deren Datenanalog diskutiert werden.

**Zhou, Zhang, Xu (2024; Zeitschriftenfassung CiCP 2026).** *A Rationale from Frequency Perspective for Grokking in Training Neural Network.* arXiv:2405.17479; https://www.global-sci.com/cicp/article/view/24634. https://arxiv.org/abs/2405.17479 [L] ⚠
- Zeigt: Bei unzureichender, ungleichmäßiger Stichprobe lernt das Netz zuerst „unechte“ (aliasierte) Frequenzen; Aufgaben sin(6x), dünne Parität, MNIST.
- Abgrenzung: Keine modulare Arithmetik; die Zielfunktion hat dort einen festen Frequenzinhalt, die Stichprobe erzeugt Artefakte *neben* der richtigen Lösung, die auf der Testmenge wieder abklingen. K2: Die Stichprobe wählt *zwischen gleich richtigen* Lösungen, und die Wahl bleibt über das Grokking hinaus.
- Schränkt Neuheit ein: **teilweise** — „die Stichprobe bestimmt, welche Frequenzen zuerst gelernt werden“ ist dort in anderer Form gezeigt. Muss im Paper ausdrücklich als nächste Vorarbeit genannt werden.

**LeDoux (2026).** *The Order Is The Message.* arXiv:2603.25047. https://arxiv.org/abs/2603.25047 [A] ⚠
- Zeigt: Die **Reihenfolge** der Trainingsbeispiele ist ein Informationskanal; bei modularer Arithmetik (p = 9973, 0,3 % der Paare) konstruiert das generalisierende Modell eine Fourier-Darstellung, deren **Grundfrequenz das Fourier-Duale der Ordnungsstruktur** ist.
- Abgrenzung: Steuert über die Reihenfolge bei fester Menge (Full-Batch schließt diesen Kanal bei uns aus); wir steuern über die Menge selbst bei Full-Batch. Kein Datenwechsel, keine Persistenzmessung, keine nicht-abelsche Gruppe.
- Schränkt Neuheit ein: **teilweise, deutlich** — die allgemeine Aussage „eine Dateneigenschaft legt fest, welche Frequenz das Modell lernt, und das lässt sich konstruieren“ ist dort für modulare Arithmetik gezeigt. K2 ist dazu die Variante „Mengenzusammensetzung statt Reihenfolge“, mit Vorhersage (M0), vier Aufgaben und D₅₉.

**Salah, Yevick (2024).** *Controlling Grokking with Nonlinearity and Data Symmetry.* arXiv:2411.05353. https://arxiv.org/abs/2411.05353 [S]
- Zeigt: Aktivierungsprofil, Tiefe und Breite steuern das Grokking bei modularer Arithmetik; Datensymmetrie/Augmentierung.
- Abgrenzung: Steuert *ob/wann* gegrokt wird, nicht welche Frequenzen.
- Schränkt Neuheit ein: **nein**.

**Sivasankar (2026).** *Circuit Synchronization Precedes Generalization: A Causal Precursor to Grokking.* arXiv:2606.12966. https://arxiv.org/abs/2606.12966 [A]
- Zeigt: Ein Frequenz-Synchronisationsmaß läuft dem Grokking 500–3000 Schritte voraus; Zeitversatz ∝ 1/λ; auch S₅.
- Schränkt Neuheit ein: **nein** (Zeitpunkt, nicht Wahl).

**Ootani (2026).** *Grokking Is Conditional and Fragile: A Fully-Tractable, Multi-Seed Study at 12K Parameters.* arXiv:2607.05104. https://arxiv.org/abs/2607.05104 [A]
- Zeigt: Grokking als Multi-Seed-Rate; gesteuert durch die **Abdeckung** der Trainingsmenge; numerische Empfindlichkeit (Threads, CPU/GPU).
- Abgrenzung: Keine Frequenzanalyse. Methodisch relevant (Multi-Seed-Raten, fixierte Numerik; stützt unser Seed-Design).
- Schränkt Neuheit ein: **nein**.

**Yang (2026).** *Where Grokking Happens: Distributed Utility and Fourier Recoding Without a Module Switch.* arXiv:2609.17571. https://arxiv.org/abs/2609.17571 [A]
- Zeigt: Grokking als spektrales Umkodieren eines verteilten Schaltkreises; prospektive Attention-Voreinstellung in Block 0; MLP vermittelt mehr als andere Pfade.
- Abgrenzung: Kein Datenwechsel, keine Resets. Laut früherer Laborsuche wird dort bemerkt, dass der Seed Init und Split gemeinsam variiert, ohne beides zu trennen (⚠ im Volltext bestätigen).
- Schränkt Neuheit ein: **nein**; relevant als Kontext für K4d (Rolle der Attention).

**Pracher, de Jong, Lieshaus, Jeffares, Rulands (2026).** *A Spectral Theory of Grokking: Weight Decay Induces Feature Learning.* arXiv:2609.26679. https://arxiv.org/abs/2609.26679 [A]
- Zeigt: NTK-Spektraltheorie; Generalisierungszeit ∝ 1/(lr·wd); aufgabenausgerichtete Fourier-Struktur entsteht im NTK nach dem Sättigen der Trainingsgenauigkeit.
- Abgrenzung: Welche Fourier-Komponenten *zuerst* aufgelöst werden, hängt dort an NTK-Eigenwerten; bei Teil-Splits könnte das M0 berühren (⚠ Volltext prüfen, ob Teilmengen analysiert werden).
- Schränkt Neuheit ein: **nein** nach Abstract; **offen** bis Volltext.

**Nguyen (2026).** *The Discrete-Log Clock: How a Transformer Learns Modular Multiplication.* Mechanistic Interpretability Workshop, ICML 2026. arXiv:2606.17399. https://arxiv.org/abs/2606.17399 [A]
- Zeigt: Bei Multiplikation mod p ist die passende Basis die multiplikative Charaktertransformation; dort nur ≈ 4 Key-Frequenzen.
- Abgrenzung: Methodische Grundlage für unsere mul-113-Analyse; keine Untersuchung, was die Wahl bestimmt.
- Schränkt Neuheit ein: **nein**.

---

## 3. Gruppenkomposition, Irreps und Theorie der Feature-Reihenfolge

**Chughtai, Chan, Nanda (2023).** *A Toy Model of Universality: Reverse Engineering How Networks Learn Group Operations.* ICML 2023. https://arxiv.org/abs/2302.03025 [L]
- Zeigt: Netze lernen Gruppenkomposition über Irreps (C_n, S_n, D_n); welche Irreps gelernt werden, variiert zwischen Läufen und ist „beliebig“; Ursache offen.
- Abgrenzung: Genau die offene Frage, die K2 für D₅₉ adressiert (Datenseite).
- Schränkt Neuheit ein: **nein**.

**Stander, Yu, Fan, Biderman (2024).** *Grokking Group Multiplication with Cosets.* ICML 2024. https://arxiv.org/abs/2312.06581 [S]
- Zeigt: MLPs auf S₅/S₆ zerlegen die Gruppenarithmetik über Nebenklassen/Untergruppen.
- Schränkt Neuheit ein: **nein**.

**He, Wang, Zhang, Chen, Yang (2026).** *Neural Networks Provably Learn Spectral Representations for Group Composition.* arXiv:2606.02993. https://arxiv.org/abs/2606.02993 [A, L] ⚠
- Zeigt: Riemannscher Gradientenaufstieg auf einem darstellungstheoretischen Energiefunktional; Neuronen konvergieren fast sicher zu je einer Irrep; bei abelschen Gruppen verteilt die **Zufalls-Init** gleichmäßig auf die nicht-trivialen Irreps.
- Abgrenzung: Laut Labor-HTML-Prüfung sieht das Netz alle Paare (g₁, g₂) ∈ G × G; keine Teil- oder verzerrten Mengen.
- Schränkt Neuheit ein: **teilweise** — Theorie der Irrep-Auswahl existiert, aber mit Init als Quelle bei vollständigen Daten.

**Marchetti, Kunin, Myers, Acosta, Miolane (2026).** *Sequential Group Composition: A Window into the Mechanics of Deep Learning.* ICML 2026. arXiv:2602.03655. https://arxiv.org/abs/2602.03655 [A, L] ⚠
- Zeigt: Netze lernen Gruppenkomposition Irrep für Irrep; die Reihenfolge folgt der Fourier-Statistik der **Eingabekodierung**; Gruppen C_p, D_n, C_n × C_n; Breiten-/Tiefenskalierung.
- Abgrenzung: Laut Labor-Volltextprüfung Training gleichverteilt über alle Sequenzen; bei One-hot-Kodierung sind alle Irreps gleichauf. K2 bricht genau diese Gleichheit über die Paarzusammensetzung. MSE, Gradientenfluss, kleine Init, kein Adam/WD.
- Schränkt Neuheit ein: **teilweise, deutlich** — „Datenstatistik bestimmt die Irrep-Reihenfolge, auch für D_n“ ist theoretisch gezeigt; K2 ist dazu die Paarverteilungs-Variante im Transformer. Eine formale Brücke M0 ↔ ihre Auswahlregel fand das Labor im einfachsten AGF-Modell *nicht* (EXP-076); das muss im Paper offen benannt werden.

**Kunin, Marchetti, Chen, Karkada, Simon, DeWeese, Ganguli, Miolane (2025).** *Alternating Gradient Flows: A Theory of Feature Learning in Two-layer Neural Networks.* NeurIPS 2025. https://arxiv.org/abs/2506.06489 [L, S]
- Zeigt: Saddle-to-saddle-Dynamik bei kleiner Init: dormante Neuronen aktivieren nacheinander über einen Nutzen; bei modularer Addition werden Fourier-Features in absteigender Koeffizientengröße gelernt.
- Abgrenzung: Volle Daten; Reihenfolge durch Datenkoeffizienten, nicht durch Teilmengen. EXP-076: der Nutzen erster Stufe sieht unsere konstruierten Ziele nicht.
- Schränkt Neuheit ein: **teilweise** (Rahmen, in dem „Daten bestimmen die Reihenfolge der Features“ bereits formalisiert ist).

**Saxe, McClelland, Ganguli (2014).** *Exact Solutions to the Nonlinear Dynamics of Learning in Deep Linear Neural Networks.* ICLR 2014. https://arxiv.org/abs/1312.6120 — und **Jacot, Ged, Şimşek, Hongler, Gabriel (2021).** *Saddle-to-Saddle Dynamics in Deep Linear Networks.* arXiv:2106.15933. https://arxiv.org/abs/2106.15933 [K]
- Zeigen: Moden werden in der Reihenfolge ihrer Singulärwerte der Eingabe-Ausgabe-Korrelation gelernt (stufenweise).
- Abgrenzung: Allgemeines Prinzip „Datenstatistik → Lernreihenfolge“; bei uns ist die Frage, welche von gleichwertigen Lösungen *endgültig* bleibt.
- Schränkt Neuheit ein: **teilweise** (konzeptuell; M0 ist in diesem Sinn eine Korrelationsstatistik der Trainingsmenge).

---

## 4. Frequency Principle und Spectral Bias

**Rahaman, Baratin, Arpit, Draxler, Lin, Hamprecht, Bengio, Courville (2019).** *On the Spectral Bias of Neural Networks.* ICML 2019. https://arxiv.org/abs/1806.08734 [K]
- Zeigt: Netze lernen niedrige Frequenzen (im Eingaberaum) zuerst.
- Abgrenzung: Frequenzen im kontinuierlichen Eingaberaum; bei One-hot-Token auf Z_p gibt es keine natürliche „niedrig/hoch“-Ordnung, und unsere Ziele sind beliebig wählbar.
- Schränkt Neuheit ein: **nein**.

**Xu, Zhang, Luo, Xiao, Ma (2019/2020).** *Frequency Principle: Fourier Analysis Sheds Light on Deep Neural Networks.* CiCP 2020; arXiv:1901.06523. https://arxiv.org/abs/1901.06523 [K]
- Zeigt: F-Principle (niedrige Frequenzen zuerst).
- Schränkt Neuheit ein: **nein** (Hintergrund zu Zhou et al. 2024).

---

## 5. Datenzusammensetzung, Reihenfolge und Curriculum als Former gelernter Features

**Hermann, Lampinen (2020).** *What Shapes Feature Representations? Exploring Datasets, Architectures, and Training.* NeurIPS 2020. https://arxiv.org/abs/2006.12433 [S]
- Zeigt: In synthetischen Daten mit kontrollierter Relevanz einzelner Features repräsentiert das Modell bei redundanten Features bevorzugt eines; die Präferenz spiegelt, was im **untrainierten** Modell am besten linear dekodierbar ist; leichte Features unterdrücken schwere.
- Abgrenzung: Allgemein, keine Frequenzen, keine Gruppenstruktur; aber sehr nahe am Grundgedanken „unter gleichwertigen Lösungen entscheiden Daten/Init“.
- Schränkt Neuheit ein: **teilweise** (konzeptuell; K2 ist eine präzise, vorhersagbare Instanz davon).

**Lampinen, Chan, Hermann (2024).** *Learned Feature Representations Are Biased by Complexity, Learning Order, Position, and More.* TMLR 2024. https://arxiv.org/abs/2405.05847 [S]
- Zeigt: Repräsentationen sind systematisch zugunsten von Features verzerrt, die einfacher sind oder **früher gelernt** wurden.
- Abgrenzung: Allgemein, keine Frequenzen; „früher gelernt → stärker repräsentiert“ berührt K4.
- Schränkt Neuheit ein: **teilweise** (konzeptuell für K4).

**Chan, Santoro, Lampinen, Wang, Singh, Richemond, McClelland, Hill (2022).** *Data Distributional Properties Drive Emergent In-Context Learning in Transformers.* NeurIPS 2022. https://arxiv.org/abs/2205.05055 [K]
- Zeigt: Eigenschaften der Trainingsverteilung (Burstiness, Zipf) bestimmen, welcher Mechanismus (In-Context vs. In-Weights) entsteht.
- Abgrenzung: Anderer Mechanismus, anderes Modell; zeigt das Prinzip „Datenverteilung wählt Mechanismus“.
- Schränkt Neuheit ein: **nein** (Kontext).

(LeDoux 2026 und Zhou et al. 2024 gehören inhaltlich auch hierher, siehe Abschnitt 2.)

---

## 6. Kritische Lernperioden und frühe Trainingsphase

**Achille, Rovere, Soatto (2019).** *Critical Learning Periods in Deep Networks.* ICLR 2019. https://arxiv.org/abs/1711.08856 [K] ⚠
- Zeigt: Frühe, vorübergehende Defizite (z. B. verschwommene Bilder) schädigen dauerhaft; nach der kritischen Phase lassen sich gelernte Verbindungen kaum umschreiben; Fisher-Information steigt früh und fällt dann.
- Abgrenzung: Defizit vs. vollwertige Daten; Bildaufgaben; keine Frequenz-/Lösungswahl unter gleichwertigen Lösungen; Zeitskala Epochen.
- Schränkt Neuheit ein: **teilweise, deutlich** für K4 — das Phänomen „frühe Daten prägen dauerhaft“ ist hier etabliert. K4 ist eine Instanz mit messbarer Frequenz-Signatur und sehr kurzer Zeitskala.

**Kleinman, Achille, Soatto (2024).** *Critical Learning Periods Emerge Even in Deep Linear Networks.* ICLR 2024. https://arxiv.org/abs/2308.12221 [S]
- Zeigt: Kritische Perioden entstehen bereits in tiefen linearen Netzen; abhängig von Tiefe und Datenstruktur, auch in Multi-Task-Wettbewerb.
- Abgrenzung: Minimalmodell; Wettbewerb zwischen Quellen ähnelt dem Frequenzwettbewerb in K4 konzeptuell.
- Schränkt Neuheit ein: **teilweise** (Mechanismusklasse; ⚠ Volltext auf „Wettbewerb gleichwertiger Pfade“ prüfen).

**Kleinman, Achille, Soatto (2023).** *Critical Learning Periods for Multisensory Integration in Deep Networks.* CVPR 2023. https://arxiv.org/abs/2210.04643 [S]
- Zeigt: Frühe Defizite einer Modalität bestimmen dauerhaft, welche Quellen integriert werden.
- Schränkt Neuheit ein: **teilweise** (konzeptuell für K4).

**Frankle, Schwab, Morcos (2020).** *The Early Phase of Neural Network Training.* ICLR 2020. https://arxiv.org/abs/2002.10365 [K]
- Zeigt: Wesentliche Veränderungen passieren in den ersten Iterationen; Gewichte sind nach wenigen hundert Iterationen stark strukturiert, Re-Init mit Vorzeichen reicht nicht.
- Abgrenzung: Allgemein; kein Datenwechsel mit Frequenzmessung.
- Schränkt Neuheit ein: **teilweise** (die Idee „wenige frühe Schritte legen viel fest“).

**Frankle, Dziugaite, Roy, Carbin (2020).** *Linear Mode Connectivity and the Lottery Ticket Hypothesis.* ICML 2020. https://arxiv.org/abs/1912.05671 [S]
- Zeigt: Netze werden früh (≈ 3 % des Trainings bei ResNet-20) stabil gegen SGD-Rauschen; danach liegt das Ergebnis in einem linear verbundenen Becken.
- Abgrenzung: Stabilität gegen Batch-Reihenfolge bei gleichen Daten, nicht gegen einen paar-disjunkten Datenwechsel. Ein direktes Analogon zu K4 (Stabilität der Frequenzwahl gegen *andere Daten*).
- Schränkt Neuheit ein: **teilweise** (methodisch und konzeptuell naheliegender Vergleich; sollte zitiert werden).

**Frankle, Carbin (2019).** *The Lottery Ticket Hypothesis.* ICLR 2019. https://arxiv.org/abs/1803.03635 [K]
- Schränkt Neuheit ein: **nein** (Begriffsherkunft für „Lotterie“ bei He et al.).

**Pawlak (2025).** *On the Occurence of Critical Learning Periods in Neural Networks.* arXiv:2510.09687. https://arxiv.org/abs/2510.09687 [A]
- Zeigt: Kritische Perioden und Warm-Start-Verlust lassen sich durch zyklische Lernratenpläne vermeiden.
- Abgrenzung: Konkurrenzerklärung für K4 (Lernrate/Plastizität statt Datenprägung); keine Frequenzen.
- Schränkt Neuheit ein: **nein**, aber als Alternativerklärung zu diskutieren.

**Ali (2026).** *Critical Windows of Complexity Control: When Transformers Decide to Reason or Memorize.* arXiv:2605.04396. https://arxiv.org/abs/2605.04396 [A]
- Zeigt: Weight Decay nur in einem 25-%-Fenster reicht; Verschieben um 100 Schritte kippt zwischen Memorieren und Schließen; laut Abstract **nicht** bei Grokking modularer Arithmetik beobachtet.
- Abgrenzung: Fenster für Regularisierung, nicht für Daten; der ausdrückliche Negativbefund für modulare Arithmetik ist ein interessanter Kontrast zu K4.
- Schränkt Neuheit ein: **nein**.

**(Autoren nicht geprüft) (2025).** *One Period to Rule Them All: Identifying Critical Learning Periods in Deep Networks.* arXiv:2506.15954. https://arxiv.org/abs/2506.15954 [S]
- Zeigt: Verfahren, kritische Perioden zu lokalisieren, um teure Trainingsrezepte danach abzuschalten.
- Schränkt Neuheit ein: **nein**.

---

## 7. Plastizitätsverlust, Primacy Bias, Warm-Start und Resets

**Lyle, Sokar, Pascanu, György (2025).** *What Can Grokking Teach Us About Learning Under Nonstationarity?* arXiv:2507.20057. https://arxiv.org/abs/2507.20057 [A, L] ⚠
- Zeigt: Primacy Bias bei nichtstationären Daten; dieselben Feature-Learning-Dynamiken wie beim Grokking erlauben das Überschreiben alter Features; eine höhere **effektive Lernrate** (Parameter- zu Update-Norm) stellt das her; Experimente u. a. an modularer Addition mit einem Attention-Block.
- Abgrenzung: Keine Frequenzanalyse, keine konstruierte Trainingsmengen-Zusammensetzung, keine Messung, *welche* Frequenzen nach einem Wechsel bleiben.
- Schränkt Neuheit ein: **teilweise, deutlich** für K4 — gleiche Aufgabenfamilie, gleiche Frage (Überschreiben früher Features nach Datenwechsel). Die ELR ist eine benannte Konkurrenzerklärung für die Festlegung, die im Paper adressiert werden muss.

**Nikishin, Schwarzer, D'Oro, Bacon, Courville (2022).** *The Primacy Bias in Deep Reinforcement Learning.* ICML 2022. https://arxiv.org/abs/2205.07802 [S]
- Zeigt: Agenten überanpassen an frühe Erfahrungen; periodisches Zurücksetzen der **letzten Schichten** behebt es.
- Abgrenzung: RL, keine Frequenzen; Teil-Resets als Abhilfe sind hier etabliert.
- Schränkt Neuheit ein: **teilweise** für K4 (Phänomen) und K4d (Methode „Teil-Reset hebt Primacy auf“).

**Ash, Adams (2020).** *On Warm-Starting Neural Network Training.* NeurIPS 2020. https://arxiv.org/abs/1910.08475 [S]
- Zeigt: Warm-Start auf einem Teil der Daten schadet der Generalisierung dauerhaft; Shrink-and-Perturb hilft.
- Abgrenzung: Wachsende Datenmengen, Bildaufgaben; misst Genauigkeit, nicht welche Lösung bleibt.
- Schränkt Neuheit ein: **teilweise** für K4 (Warm-Start-Persistenz allgemein bekannt).

**Lyle, Zheng, Nikishin, Avila Pires, Pascanu, Dabney (2023).** *Understanding Plasticity in Neural Networks.* ICML 2023. https://arxiv.org/abs/2303.01486 [S]
- Zeigt: Plastizitätsverlust hängt mit der Krümmung/Geometrie des Verlustes zusammen; Layer-Norm hilft.
- Schränkt Neuheit ein: **nein**.

**Lyle, Zheng, Khetarpal, van Hasselt, Pascanu, Martens, Dabney (2025).** *Disentangling the Causes of Plasticity Loss in Neural Networks.* CoLLAs 2025 (PMLR 274). https://arxiv.org/abs/2402.18762 [S]
- Zeigt: Plastizitätsverlust zerfällt in mehrere unabhängige Mechanismen; Layer-Norm + Weight Decay robust.
- Schränkt Neuheit ein: **nein**.

**Dohare, Hernandez-Garcia, Lan, Rahman, Mahmood, Sutton (2024).** *Loss of Plasticity in Deep Continual Learning.* Nature 632, 768–774. https://www.nature.com/articles/s41586-024-07711-7 [S]
- Zeigt: Plastizitätsverlust ist breit verbreitet; Continual Backprop (Re-Init wenig genutzter Einheiten) behebt ihn.
- Schränkt Neuheit ein: **nein** (Kontext).

**Asadi, Fakoor, Sabach (2023).** *Resetting the Optimizer in Deep RL: An Empirical Study.* NeurIPS 2023. https://arxiv.org/abs/2306.17833 [S]
- Zeigt: Zurücksetzen der Adam-Momente bei neuer Zielfunktion verbessert Deep RL deutlich.
- Abgrenzung: Relevant für K4b (gelöschtes Momentum) und K4d (wir setzen Gewichte **und** AdamW-Zustand zurück); keine Frequenzen.
- Schränkt Neuheit ein: **teilweise** für K4b (dass der Optimiererzustand Vergangenheit trägt, ist bekannt).

**Zhou, Vani, Larochelle, Courville (2022).** *Fortuitous Forgetting in Connectionist Networks.* ICLR 2022. https://arxiv.org/abs/2202.00155 [S]
- Zeigt: Forget-and-Relearn; Re-Init später Schichten entfernt gezielt unerwünschte Information.
- Abgrenzung: Schicht-selektive Resets als Werkzeug; nicht Attention-Teilpfade, keine Frequenzen.
- Schränkt Neuheit ein: **teilweise** für K4d (Methodenklasse).

**Chen, Marchisio, Raileanu, Adelani, Stenetorp, Riedel, Artetxe (2023).** *Improving Language Plasticity via Pretraining with Active Forgetting.* NeurIPS 2023. https://arxiv.org/abs/2307.01163 [S]
- Zeigt: Periodisches Zurücksetzen der **Embedding-Schicht** macht den Transformer-Körper anpassungsfähiger an neue Embeddings.
- Abgrenzung: Hier sitzt die Anpassungsfähigkeit im Körper, das Embedding ist austauschbar; K4d zeigt umgekehrt, dass der Attention-Körper die alte Frequenzwahl festhält. Passt konzeptuell zusammen.
- Schränkt Neuheit ein: **nein** (aber gut zu zitieren).

**Zhang, Bengio, Singer (2022).** *Are All Layers Created Equal?* JMLR 23. https://arxiv.org/abs/1902.01996 [S]
- Zeigt: Schichten sind „robust“ oder „kritisch“ gegenüber Re-Init nach dem Training.
- Abgrenzung: Methodischer Vorläufer der Reset-Empfindlichkeit; nach dem Training, nicht beim Datenwechsel.
- Schränkt Neuheit ein: **teilweise** für K4d (Methode), **nein** für den Befund.

**Chatterji, Neyshabur, Sedghi (2020).** *The Intriguing Role of Module Criticality in the Generalization of Deep Networks.* ICLR 2020. https://arxiv.org/abs/1912.00528 [L]
- Zeigt: Modul-Kritikalität (Rückspulen einzelner Module zur Init) sagt Generalisierung voraus.
- Schränkt Neuheit ein: **teilweise** für K4d (Methode).

---

## 8. Übersichtstabelle

| Arbeit | zeigt | Abgrenzung | schränkt Neuheit ein? |
|---|---|---|---|
| Nanda et al. 2023 (ICLR) | Key-Frequenzen im 1-Schicht-Transformer, seed-abhängig; Frequenz-Ablationen | Fragt nicht, was die Wahl bestimmt | nein (K2/K4); teilweise (K2-Funktion, Methode) |
| Zhong et al. 2023 (NeurIPS) | Hyperparameter/Init wählen Algorithmus bei fester Trainingsmenge | Variiert nicht die Menge | nein |
| Gromov 2023 | Analytische Fourier-Lösung, viele Frequenzmengen gleichwertig | Keine Datensteuerung | nein |
| Morwani et al. 2024 (ICLR) | Max-Margin → Fourier/Irreps | Asymptotisch, volle Daten | nein |
| Mohamadi et al. 2024 (ICML) | Kernel-Regime braucht konstanten Datenanteil | Keine Frequenzwahl | nein |
| Kumar et al. 2024 (ICLR) | Lazy→rich erklärt Grokking | Zeitpunkt, nicht Wahl | nein |
| Liu et al. 2022/2023; Varma et al. 2023; Lyu et al. 2024 | Grokking-Theorien | Keine Frequenzwahl | nein |
| Mallinar et al. 2025 (ICML) | RFM groken ohne Zufalls-Init | Frequenzen je Split nicht analysiert | nein (⚠ Volltext) |
| Tian 2024 | Algebraische Struktur der Optima | Keine Datensteuerung | nein |
| **He et al. 2026a (2602.16849)** | Frequenz-Lotterie je Neuron nach Init-Betrag/Phase | Init statt Daten, volle Daten | **teilweise** (K2, K4) |
| **Zhou et al. 2024/2026 (CiCP)** | Ungleichmäßige Stichprobe → zuerst aliasierte Frequenzen | Keine mod. Arithmetik; Artefakte klingen ab | **teilweise** (K2) |
| **LeDoux 2026** | Reihenfolge → Grundfrequenz der Fourier-Lösung | Reihenfolge statt Menge; kein Wechsel | **teilweise, deutlich** (K2) |
| Salah & Yevick 2024 | Nichtlinearität steuert Grokking | ob/wann, nicht welche Frequenz | nein |
| Sivasankar 2026 | Frequenz-Synchronisation vor Grokking | Zeitpunkt | nein |
| Ootani 2026 | Grokking-Rate durch Abdeckung gesteuert | Keine Frequenzen | nein |
| Yang 2026 | Grokking als spektrales Umkodieren; Attention-Bias Block 0 | Kein Wechsel, keine Resets | nein |
| Pracher et al. 2026 | NTK-Spektraltheorie, Zeit ∝ 1/(lr·wd) | Teilmengen? (⚠) | nein (vorläufig) |
| Nguyen 2026 (ICML-WS) | Charakterbasis für mul mod p | Keine Wahlursache | nein |
| Chughtai et al. 2023 (ICML) | Irreps gelernt, Wahl „beliebig“ | Ursache offen | nein |
| Stander et al. 2024 (ICML) | Nebenklassen-Schaltkreise S₅/S₆ | Keine Wahlursache | nein |
| **He et al. 2026b (2606.02993)** | Theorie Irrep-Auswahl, Init verteilt gleichmäßig | Volle Daten G×G | **teilweise** (K2) |
| **Marchetti et al. 2026 (ICML)** | Irrep-Reihenfolge nach Fourier-Statistik der Kodierung, auch D_n | Uniforme Daten; One-hot → Gleichstand | **teilweise, deutlich** (K2) |
| **Kunin et al. 2025 (NeurIPS)** | AGF: Features in Reihenfolge der Datenkoeffizienten | Volle Daten; keine Brücke zu M0 (EXP-076) | **teilweise** (K2) |
| Saxe et al. 2014; Jacot et al. 2021 | Stufenweises Lernen nach Datenstatistik | Lineare Netze | teilweise (konzeptuell, K2) |
| Rahaman et al. 2019; Xu et al. 2019 | Spectral Bias / F-Principle | Kontinuierlicher Eingaberaum | nein |
| **Hermann & Lampinen 2020 (NeurIPS)** | Daten/Init wählen unter redundanten Features | Allgemein, keine Frequenzen | **teilweise** (K2, konzeptuell) |
| Lampinen et al. 2024 (TMLR) | Früher gelernte Features stärker repräsentiert | Allgemein | teilweise (K4, konzeptuell) |
| Chan et al. 2022 (NeurIPS) | Datenverteilung wählt Mechanismus (ICL) | Anderes System | nein |
| **Achille et al. 2019 (ICLR)** | Kritische Lernperioden | Defizite, Bilder, Epochen | **teilweise, deutlich** (K4) |
| Kleinman et al. 2023 (CVPR), 2024 (ICLR) | Kritische Perioden, auch in linearen Netzen, Quellenwettbewerb | Keine Frequenzen | teilweise (K4) |
| Frankle et al. 2020 (ICLR, early phase) | Frühe Iterationen legen viel fest | Kein Datenwechsel | teilweise (K4) |
| Frankle et al. 2020 (ICML, LMC) | Früh stabil gegen SGD-Rauschen | Gleiche Daten, keine Frequenzen | teilweise (K4) |
| Pawlak 2025 | Zyklische LR verhindert kritische Perioden | Keine Frequenzen | nein (Alternativerklärung) |
| Ali 2026 | Kritisches Fenster für Weight Decay; nicht bei mod. Arithmetik | Regularisierung, nicht Daten | nein |
| **Lyle et al. 2025 (2507.20057)** | Grokking ↔ Überschreiben früher Features; ELR stellt es her | Keine Frequenzen, keine konstruierten Splits | **teilweise, deutlich** (K4) |
| **Nikishin et al. 2022 (ICML)** | Primacy Bias; Reset letzter Schichten | RL | **teilweise** (K4, K4d) |
| Ash & Adams 2020 (NeurIPS) | Warm-Start schadet dauerhaft | Genauigkeit, nicht Lösungswahl | teilweise (K4) |
| Lyle et al. 2023 (ICML); 2025 (CoLLAs); Dohare et al. 2024 (Nature) | Ursachen und Abhilfen des Plastizitätsverlusts | Keine Frequenzen | nein |
| Asadi et al. 2023 (NeurIPS) | Optimizer-Reset hilft | RL | teilweise (K4b) |
| Zhou et al. 2022 (ICLR) | Later-layer forgetting | Keine Attention-Teilpfade | teilweise (K4d, Methode) |
| Chen et al. 2023 (NeurIPS) | Embedding-Resets → plastischer Körper | Umgekehrte Fragestellung | nein |
| Zhang et al. 2022 (JMLR); Chatterji et al. 2020 (ICLR) | Schicht-/Modul-Kritikalität über Resets | Nach Training, nicht beim Wechsel | teilweise (K4d, Methode) |

---

## 9. Einschätzung für die menschliche Prüfung

**Hinweis:** Die folgende Einschätzung ist ein Vorschlag eines KI-Agenten und **Grundlage für eine menschliche Prüfung**. Sie ersetzt weder das Lesen der mit ⚠ markierten Volltexte noch eine Suche in Google Scholar/Semantic Scholar mit Zitationsverfolgung (Vorwärtszitate von He et al. 2026a, Marchetti et al. 2026, LeDoux 2026, Lyle et al. 2025), die hier nicht möglich war.

### K2 (Split steuert Frequenz-/Irrep-Wahl)
- **Nächstverwandt:** LeDoux 2026 (Reihenfolge → Frequenz, modulare Arithmetik); Marchetti et al. 2026 (Datenstatistik der Kodierung → Irrep-Reihenfolge, auch D_n); He et al. 2026a/b (Init entscheidet den Frequenz-/Irrep-Wettbewerb bei vollen Daten); Zhou et al. 2024 (Stichprobe → zuerst gelernte Frequenzen); Kunin et al. 2025 (AGF); Hermann & Lampinen 2020 (Daten wählen unter redundanten Features).
- **Was bekannt ist:** Dass Dateneigenschaften mitbestimmen, welche Features/Frequenzen gelernt werden, ist in mehreren Formen gezeigt, am nächsten für modulare Arithmetik über die Reihenfolge (LeDoux) und theoretisch für Gruppen über die Kodierungsstatistik (Marchetti et al.).
- **Restaussage (vorläufig):** Nach unserer Suche nicht gefunden (vorläufig): eine **kausale, vorab vorhergesagte (M0) Steuerung der Frequenz- bzw. Irrep-Wahl allein über die Zusammensetzung der Trainingspaare** bei One-hot-Token und Full-Batch, bestätigt an vier Aufgaben einschließlich einer nicht-abelschen Gruppe (D₅₉) mit je 50 frischen Seeds.
- **Formulierungsvorschlag:** K2 als „Mengen-Analogon“ zu LeDoux und als empirische Ergänzung zu Marchetti et al./He et al. rahmen, nicht als neues Prinzip. Das Fehlen einer AGF-Brücke (EXP-076) offen nennen.

### K2-Funktion (Störungen entlang gesteuerter Frequenzen schaden mehr)
- **Nächstverwandt:** Nanda et al. 2023 (Frequenz-Ablationen, restricted/excluded loss); He et al. 2026a (Mehrheitsabstimmung, Beitrag einzelner Frequenzen); Zhang et al. 2022 und Chatterji et al. 2020 (Störungs-/Reset-Empfindlichkeit als Funktionsmaß).
- **Einschätzung:** Die Methode ist eine Variante bekannter Ablationen, und der Befund ist durch die eigene Grenze („Funktion folgt Energie“) eng. **Kaum eigenständiger Neuheitsbeitrag**; als Validierung von K2 darstellen (die gesteuerte Energie ist funktional genutzt), nicht als separate Aussage.

### K4 / K4b / K4c (Festlegung nach 25–50 Schritten gegen einen paar-disjunkten Wechsel)
- **Nächstverwandt:** Achille et al. 2019 und Kleinman et al. 2023/2024 (kritische Perioden); Lyle et al. 2025 (Grokking und Überschreiben früher Features, gleiche Aufgabenfamilie, ELR als Erklärung); Nikishin et al. 2022 (Primacy Bias); Ash & Adams 2020 (Warm-Start); Frankle et al. 2020 (frühe Phase, frühe Stabilität); Lampinen et al. 2024 (Lernreihenfolge); Asadi et al. 2023 (Optimiererzustand, für K4b); He et al. 2026a (Lotterie-Logik: früher Vorsprung gewinnt).
- **Was bekannt ist:** Das Phänomen „frühe Daten prägen dauerhaft“ (kritische Perioden, Primacy, Warm-Start) ist gut etabliert, auch bereits an Grokking/modularer Addition diskutiert (Lyle et al. 2025).
- **Restaussage (vorläufig):** Nach unserer Suche nicht gefunden (vorläufig): eine **Messung der Festlegungszeit der Frequenzwahl** (≈ 25–50 Schritte) gegen einen paar-disjunkten Datenwechsel, mit Ablationskontrast, der zwischen 25 und 50 Schritten kippt (K4c), und der Äquivalenz „gelöschtes Adam-Momentum ≈ weniger Vorschritte“ (K4b).
- **Pflichtdiskussion:** ELR-Erklärung von Lyle et al. 2025 und LR-Erklärung von Pawlak 2025 als Konkurrenzmodelle; Einschränkung auf add 113 und eine Architektur. Das Wort „kritische Periode“ nur als Analogie verwenden.

### K4d / K4e (Attention-, besonders Wertepfad-Reset hebt Persistenz auf)
- **Nächstverwandt:** Nikishin et al. 2022 (Teil-Resets gegen Primacy); Zhou et al. 2022 (schicht-selektives Vergessen); Zhang et al. 2022, Chatterji et al. 2020 (Reset-Kritikalität von Modulen); Asadi et al. 2023 (Optimizer-Reset); Chen et al. 2023 (Embedding-Resets, komplementär); Yang 2026 und Nanda et al. 2023 (Rolle der Attention im Modulo-Schaltkreis).
- **Was bekannt ist:** Teil-Resets als Werkzeug gegen Primacy/Plastizitätsverlust und Reset-Empfindlichkeit als Lokalisierungsmethode sind etabliert.
- **Restaussage (vorläufig):** Nach unserer Suche nicht gefunden (vorläufig): dass im 1-Schicht-Modulo-Transformer die **Persistenz einer daten-geprägten Frequenzwahl** vor allem am Reset der Attention, stärker am Wertepfad (W_V, W_O) als am Musterpfad (W_Q, W_K), und deutlich weniger am MLP hängt.
- **Pflichtformulierung:** Reset-Empfindlichkeit, **kein** Speicherort (Gewichte und AdamW-Zustand gemeinsam zurückgesetzt); nur add 113.

### Offene Prüfpunkte für den Menschen (Priorität)
1. ⚠ LeDoux 2026 Volltext: Gibt es Experimente mit veränderter *Menge* (nicht nur Reihenfolge) oder Full-Batch?
2. ⚠ Marchetti et al. 2026 und He et al. 2026b: Anhänge auf nicht-uniforme Paarverteilungen prüfen (Laborprüfung beruhte auf Zusammenfassungen des Abrufwerkzeugs).
3. ⚠ Lyle et al. 2025 Volltext: Messen sie *welche* Features nach einem Datenwechsel bleiben (irgendeine Frequenzanalyse)?
4. ⚠ Achille et al. 2019 / Kleinman et al. 2024: Gibt es dort Wettbewerb gleichwertiger Lösungen und Zeitskalen in Schritten?
5. Vorwärtszitate (Google Scholar/Semantic Scholar) von He et al. 2026a, Marchetti et al. 2026, LeDoux 2026, Lyle et al. 2025 und Nanda et al. 2023 für Arbeiten nach Juli 2026.
6. ⚠ Pracher et al. 2026 und Mallinar et al. 2025: Werden Teilmengen/Splits und die resultierenden Frequenzen analysiert?

## Nachtrag Sitzung 25 (2026-09-27): Volltextprüfung der engsten Arbeiten

Details, Zitate und Abschnittsangaben: [[paper/fulltext_check_2026-09-27]] (Hintergrund-Agent, arXiv-HTML-Volltexte inkl. Anhänge; Formeln und Abbildungen nicht gesehen).
Von mir selbst am Abstract geprüft: Dong 2607.27281 und Khanh 2607.06628. Die Einschätzungen in der Tabelle oben bleiben als Stand von Sitzung 24 stehen; **gültig ist diese Ergänzung**:

| Arbeit | Neu/geändert | Wirkung auf unseren Anspruch |
|---|---|---|
| **Dong 2026 (2607.27281)**, *The Kinetics of Training* | neu: in Sprachmodellen (Pythia bis 1.4B) stellt ein Re-Init nur der Query-Key-Anteile die Lernfähigkeit nach „Alterung“ her (6/6), Value-Anteile nichts (0/6) | **schränkt K4d ein** („Attention-Reset > MLP-Reset“ in Transformern bekannt); K4e hat die **umgekehrte** Reihenfolge (Wertepfad > QK) → als Gegensatz diskutieren. (Der Agent schrieb „Value schlechter als kein Reset“; der Abstract sagt „do nothing“, das gilt.) |
| **Khanh 2026 (2607.06628)**, *Cross-Trajectory Chimera Interventions* | neu: gleiche Modellklasse, Frequenzidentität über Gewichtsrichtung übertragbar | **teilweise** für K4 (Eingriff im Gewichtsraum statt Datenwechsel); muss zitiert werden; Spannung zu unserem schwachen MLP-Reset laut Agent (nicht selbst geprüft) |
| Tian 2025 (2509.21519) | neu: Datenverteilung formt die Energielandschaft, nur gleichverteilte Zufallsteilmengen | nur konzeptionell für K2 |
| LeDoux 2026 | Volltext: zufällige Teilmengen ändern die Frequenz **nicht** (§4.2.3, §5.3); kritische Periode nur vermutet (§3.4, §6.2) | K2 unberührt (schärft den Kontrast); K4 teilweise (Vermutung ohne Wechselversuch) |
| Marchetti et al. 2026 | Korrektur: bei One-hot gleichauf nur innerhalb derselben Dimension; niedrigdimensionale Irreps zuerst (App. D.2) | K2 unberührt; relevant für die Deutung von D₅₉ |
| Lyle et al. 2025 | Warmstart nur auf CIFAR, modulare Arithmetik als stationär behandelt, keine Frequenzanalyse | für K4 von „teilweise, deutlich“ auf **„teilweise“**; ELR bleibt Pflicht-Alternative |
| He et al. 2026b (2606.02993) | §6: „analysis of the train-test split remains open“ | stützt die Lücke, die K2 füllt (zitierbar) |

Fazit (vorläufig, Grundlage für die menschliche Prüfung): K2 weiter „nach unserer Suche nicht gefunden“; K4 bleibt, mit Khanh und LeDoux §3.4 zitiert; K4d/K4e neu formuliert und direkt gegen Dong gestellt.

*Ergänzung (14:57, von mir per WebFetch am HTML-Volltext geprüft):* Khanh 2026 (2607.06628), §3: 1-Schicht-Transformer, d = 128, Full-Batch-AdamW lr 1e-3, wd 1.0, β = (0.9, 0.98),
50 % Split, Addition und Multiplikation mod 59; §7/App. A: Richtungstausch von Attention, MLP oder Unembedding allein verschiebt die Identität jeweils (Autoren: „suggestive“, drei Paare je Aufgabe).

## Nachtrag Sitzung 26 (2026-09-27, 15:10 bis vor 15:22 Berlin, gemessen): Vorwärtszitate über die Semantic-Scholar-API

**Korrektur der Einschränkung oben:** Die Semantic-Scholar-Graph-API ist über WebFetch erreichbar (`api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations`). Die Lücke „keine Vorwärtszitate“
ist damit für Semantic Scholar teilweise geschlossen; Google Scholar bleibt ungeprüft.
**Vorgehen:** Ein Claude-Hilfsagent (nur lesend) hat die zitierenden Arbeiten von 9 Ausgangsarbeiten gesichtet: Nanda et al. 2023 (≈ 280 Zitate ab 2026-03-01, alle Titel), Marchetti et al. 2026 (7, alle),
LeDoux 2026 (1), Lyle et al. 2025 (9), Chughtai et al. 2023 (≈ 28 ab 2026-03), He et al. 2026a (6), He et al. 2026b (2), Dong 2026 und Khanh 2026 (je 0, **vermutlich Indexierungsverzug**, danach
HTTP 429; nachholen). Kandidaten nach Titel, dann Abstract, die zwei engsten im HTML-Volltext. Prüfgrad wie oben: [A] Abstract, [L] Volltext (HTML, über das Zusammenfassungswerkzeug), [T] nur Titel.
**Selbst nachgeprüft (Hauptagent):** die Abstracts von 2604.00316 und 2609.18078 und die Aufbau-Angaben von 2609.18078 im HTML-Volltext.

**Ergebnis:** Keine der gesichteten Arbeiten schränkt K2, K2-Funktion, K4–K4c oder K4d/e ein. Neu zitierwürdig:

- **Tomàs Bernal, Mallinar, Belkin (2026).** *Breaking Data Symmetry is Needed For Generalization in Feature Learning Kernels.* arXiv:2604.00316. https://arxiv.org/abs/2604.00316 [A, L]
  Recursive Feature Machines (Kernel, **kein neuronales Netz**) auf modularer Arithmetik: Generalisierung „occurs only when a certain symmetry in the training set is broken“; die gelernten
  Merkmalsmatrizen kodieren Elemente der Invarianzgruppe. *Abgrenzung:* Die Struktur der Trainingsmenge entscheidet dort, **ob** generalisiert wird, nicht **welche** Frequenzen gelernt werden; keine
  Transformer, kein Datenwechsel. **Engster Vorläufer zu K2 auf der Kernel-Seite; Pflichtzitat, schränkt K2 nicht ein.**
- **Jia (2026).** *Beyond Embedding Transfer: Component Roles in Grokking Transfer and Stability.* arXiv:2609.18078. https://arxiv.org/abs/2609.18078 [A, L]
  Gleiche Modellfamilie (1-Schicht-Transformer mit Pre-LayerNorm, AdamW lr 1e-3, wd 1): Warmstart-Übertragung zwischen modularen Aufgaben, Übertragen/Einfrieren von W_E, W_U und inneren Blöcken.
  Q, K, V sind **eine fusionierte Matrix** (Volltext: „single fused linear layer … qkv.weight“); keine Resets beim Datenwechsel, keine Frequenzanalyse. *Abgrenzung zu K4d/e:* Komponentenrollen ja,
  aber weder Reset noch Trennung Wertepfad/QK. Zitieren.
- **Howe (2026a).** *What Makes a Representational Prior Work? Feature Families, Label-Free Invariances, and Critical Windows in Grokking.* arXiv:2607.12735 [A]. Ein Hilfsverlust nur in den ersten
  2000 Epochen bringt fast den ganzen Nutzen („critical window“). Fenster in Tausenden Epochen, Eingriff über den Verlust, nicht die Daten. Zitieren bei K4 (kritische Fenster).
- **Howe (2026b).** *Structure-Specific Representational Priors Causally Control the Grokking Delay.* arXiv:2607.04333 [A]. Optional.
- **Li, Sreedhar (2026).** *Natural Ungrokking: Asymmetric Control of Which Rules Survive Pretraining.* arXiv:2606.26050 [A]. Kleine Sprachmodelle: der Korpus entscheidet, welche Regeln bleiben;
  Wiederzuführen der Daten stellt eine verdrängte Regel nicht wieder her. Analogie zu K2 (Daten wählen Merkmale) und K4 (Unumkehrbarkeit), anderes Setting. Zitieren.
- **Swaroop (2026).** *Latent Algorithmic Structure Precedes Grokking.* arXiv:2603.23784 [A]. Frequenzen und Phasen schon während der Memorisation kodiert (ReLU-MLPs). Stützender Kontext zu K4.
- **Hidajat, Stoll, An (2026).** *Grokking as Structural Inference: Transformers Need Bayesian Lottery Tickets.* arXiv:2605.15787 [A]. Theorie: Aufmerksamkeitszuteilung als Engpass. Optional zu K4d.
- **Sweeney (2026).** *Optimizer Memory Makes Shuffle Order a First-Order Source of Fine-Tuning Noise.* arXiv:2606.29554 [A]. AdamW-Gedächtnis macht die Datenreihenfolge zu einem Effekt erster
  Ordnung (Fine-Tuning). Optional zu K4b (Optimiererzustand trägt Datengeschichte).

Nach Abstract als nicht einschlägig eingestuft (keine Paar-Steuerung, keine frühe Festlegung gegen einen Datenwechsel, keine Wertepfad/QK-Resets), u. a.: 2609.15047, 2609.27593, 2606.23044, 2607.07066,
2605.08119 („spectral lock-in“ meint dort Eigenlücken im Update-Spektrum), 2608.25813, 2605.17704, 2605.24057, 2607.29503, 2609.12259, 2607.10116, 2603.07323, 2609.20166.
**Offen für die menschliche Prüfung:** Zitate aus 2604.00316 und 2609.18078 vor der Übernahme ins Paper am PDF gegenprüfen (das Werkzeug fasst zusammen); Vorwärtszitate von Dong und Khanh nachholen;
Google Scholar.
*Nachtrag (15:32, gemessen):* Zweiter Versuch für Dong/Khanh: Semantic Scholar weiter HTTP 429; Websuche nach Titeln und die Pith-Seite von 2607.06628 zeigen keine zitierenden Arbeiten (Pith: keine „cited by“-Liste im Abruf). Bleibt offen für eine spätere Sitzung.

*Korrektur (15:42, gemessen; Volltext von 2604.00316 selbst per WebFetch gelesen, Aussagen über das Zusammenfassungswerkzeug, am PDF gegenzuprüfen):* Die Einordnung oben („entscheidet, **ob** generalisiert wird, nicht welche Frequenzen“) war zu schwach. Tomàs Bernal et al. bauen neben Zufallssplits **absichtlich H-invariante Splits** (Test = Fixpunkte einer Spiegelung s, z. B. die Paare (a, a)) und zeigen, dass RFM dann nur die Untergruppe H = {id, s·r^k} lernt und genau die Punkte in Orbit_H(X_tr) richtig klassifiziert („perfect match (100% precision, 100% recall)“ zwischen Vorhersage und Ergebnis). Die Struktur der Trainingsmenge bestimmt dort also, **welche Gruppenstruktur** die gelernten Merkmale kodieren. Keine Fourier-/Charakteranalyse, keine neuronalen Netze; Moduln 29, 32, 53, 61, C₅ × C₁₁. **Neue Einordnung: schränkt K2 teilweise ein** (konzeptioneller Vorläufer: Trainingsmengen-Struktur wählt die gelernte Merkmalsstruktur, für Kernel und über Symmetrie-Untergruppen). K2 bleibt nach unserer Suche nicht gefunden in der engeren Form: Auswahl vorgegebener Fourier-Frequenzen/Irreps in Transformern über das Paarmasken-Spektrum, bei Splits ohne Symmetrie-Invarianz, an frischen Seeds bestätigt. Im Paper als Pflichtzitat mit dieser Abgrenzung.

*Volltextprüfung (15:43, gemessen, WebFetch HTML):* Li & Sreedhar 2026 (2606.26050): 4-Schicht-Decoder (11.5 M Parameter), Muon/AdamW, Pronomen- und a/an-Regeln; Eingriff: Belege einer Regel im Korpus in Gegenbelege umkehren. Zeigt, **ob** eine Regel überlebt („support frequency decides a rule's fate“), nicht die Wahl zwischen gleich richtigen Lösungen; keine Fourier-Analyse, keine Resets von Komponenten. Einordnung bleibt: zitieren, schränkt nicht ein.
*Volltextprüfung (15:43, gemessen):* Swaroop 2026 (2603.23784): MLP mit einer verborgenen Schicht (256, Two-hot), add 97, AdamW lr 1e-3, wd 1, fester 30/70-Split; Struktur schon bei Erreichen von 99 % Trainingsgenauigkeit kodiert, **ohne Zeitangabe in Schritten, ohne Datenwechsel, ohne Datensteuerung**. Einordnung bleibt: stützender Kontext zu K4, schränkt nicht ein.
*Volltextprüfung (15:44, gemessen):* Howe 2026a (2607.12735): **gleiche Modellklasse und Einstellung wie wir** (1-Schicht-Transformer ohne LayerNorm, add 97, 30-%-Split, Vollbatch-AdamW lr 1e-3, wd 1). Das kritische Fenster betrifft einen Hilfsverlust (SupCon nur in Epochen 0–2000: 10/10 generalisieren, 2.7× schneller), keinen Datenwechsel; keine Analyse, welche Frequenzen gelernt oder festgelegt werden. Einordnung: zitieren (gleiches Setting, Fenster in Tausenden Schritten für einen Verlust), schränkt K4 nicht ein.

*Nachsuche (15:47, gemessen; WebSearch „choice of training pairs determines which Fourier frequencies transformer learns modular arithmetic 2026“, „openreview 2026 grokking training data controls learned representation frequency modular addition subset structure“):* Neu nur **Fu, Zhou, Belkin, Sharan, Jia (2026), *Convergent Evolution: How Different Language Models Learn Similar Number Representations*, arXiv:2604.20817 (COLM 2026) [A]**: Sprachmodelle lernen periodische Zahldarstellungen (Perioden 2, 5, 10); Daten, Architektur, Optimierer und Tokenizer entscheiden, *ob* trennbare Merkmale entstehen. Keine gezielte Auswahl von Trainingspaaren, um bestimmte Frequenzen zu steuern → zitieren als Kontext (Daten formen Fourier-Merkmale in Sprachmodellen), schränkt K2 nicht ein. Übrige Treffer bekannt.
*Nachtrag (15:48):* Semantic Scholar liefert für Dong 2026 (2607.27281) eine **leere** Zitatliste (gültige Antwort, keine Sperre); Khanh erneut HTTP 429. Leere Liste heißt bei einer Arbeit von Ende Juli vermutlich Indexierungsverzug, nicht „nie zitiert“.
*Nachtrag (15:56):* Auch für Khanh 2026 (2607.06628) liefert Semantic Scholar eine leere Zitatliste (gültige Antwort). Damit sind alle 9 Ausgangsarbeiten gesichtet; leer bei Dong und Khanh = vermutlich Indexierungsverzug (beide Juli 2026). In einer späteren Woche erneut prüfen.

## Nachtrag Sitzung 27 (2026-09-27, vor 16:07 Berlin, gemessen)

- **Xu 2026, *Stored in Optimizer State, Valued by Later Training: A Causal Account of Subliminal Trait Transfer*** (arXiv 2608.20442, eingereicht 2026-08-20; [A] Abstract-Seite per WebFetch). Zustandschirurgie zeigt Adams
  erstes Moment als kausalen Träger eines Quellsignals, das nach dem Entfernen der Quelldaten weiterwirkt (Effekte über 8–16 Updates). Keine Grokking-/Fourier-Analyse, kein früher Datenwechsel, keine Größenvorhersage über β₁.
  *Einordnung:* schränkt die **qualitative** Lesart von K4b ein (erstes Moment trägt die frühe Exposition über den Wechsel), nicht K4/K4c. Zitieren bei K4b. Unsere parameterfreie Größenabschätzung
  (Momentum-Schwanz ≈ 6.5–10.8 Update-Äquivalente gegen gemessene π-Verschiebung 6.5–9.6 Schritte, EXP-059, post hoc; [[NOVEL_DIRECTIONS]] N38) ist dort nicht enthalten.
  Suchbegriffe: siehe N38.
- **Salah, Yevick 2024** (arXiv 2411.05353, v1 2024-11-08) **am Volltext geprüft (PDF → pdftotext, 16:16)**, bisher [S]. Zweischichtiges MLP mit quadratischer Aktivation, verkettete One-hot-Eingaben, Adam mit Weight Decay, P = 53, TRAIN_FRAC 0.5. §3.5 „Data Dependence“: Die Trainingsmenge wird
  gezielt eingeschränkt („One symmetry in the dataset is associated with the commutation relation … and can be removed by considering only the values of a + b with a ≥ b“; zusätzlich Ausschluss der Paare mit a − b = 1, 2, 5, 8). Gemessen wird nur, **ob** und wie gut
  generalisiert wird (z. B. Testgenauigkeit 0.85 bzw. kein Grokking ohne TRAIN_FRAC 0.8), **nicht, welche Frequenzen** gelernt werden. *Einordnung:* schränkt K2 **nicht** ein; zitieren als früheres Beispiel gezielter Trainingsmengen-Wahl bei modularer Addition (Wirkung auf das Ob, nicht auf das Welche).
- **Volltextprüfung dreier [A]-Einträge (Agent, HTML-Volltext; Kernzitate von mir in den Rohtexten nachgeprüft, 16:19):**
  - **Sweeney 2026** (arXiv 2606.29554v1, 2026-06-28), LoRA-Fine-Tuning 1B-Sprachmodelle: Weil der Optimiererzustand „auf dem Schritt-Takt“ läuft, wird der Reihenfolge-Effekt O(η) statt O(η²); wörtlich (§2): „fixed-clock first-moment memory alone suffices to make the first-order impulse weights position-dependent“;
    §3: „At K=16, s=100, β1=0.9, the endpoint impulse weight falls from 0.815 to 0.100 across the window.“ Verwandte Arbeiten: Reihenfolge-Sensitivität „amplified by momentum and collapsing when the optimizer state is reset (Sevetlidis and Pavlidis, 2026)“.
    *Einordnung:* **teilweise** für K4b/N38 (Mechanismus „erstes Moment als Gedächtnis mit festem Takt“ ist beschrieben und zu zitieren); keine Frequenzen, keine Festlegung, keine Schrittzahl β₁/(1 − β₁). K2/K4 nicht eingeschränkt.
  - **Pracher, de Jong, Lieshaus, Jeffares, Rulands 2026** (arXiv 2609.26679v1): Residual-NTK-Theorie, Grokking-Zeit ∝ (ηλ)⁻¹; Full-Batch-SGD ohne Momentum, MSE; eine frühe NTK-Intervention beschleunigt Grokking. Schränkt K2/K4 **nicht** ein (keine Split-Steuerung, kein Wechsel).
  - **Yang 2026** (arXiv 2609.17571v1; arXiv-Seite nennt 2026-07-29, vom Agenten so übernommen): 2-Block-Transformer, **exakt unser Optimierer** (Full-Batch AdamW, lr 1e-3, β 0.9/0.98, wd 1.0; §3.1, von mir im Rohtext bestätigt), zufälliger Split; „Frequenzauswahl“ = Auswahl durch den Analytiker. Schränkt **nicht** ein; zitieren als Setting-Nachbar.
  - **Noch zu prüfen:** Sevetlidis & Pavlidis 2026 (arXiv 2601.16563), Reihenfolge-Sensitivität und Optimiererzustand, für K4b/N38.
- **Sevetlidis, Pavlidis 2026**, *Process-Tensor Tomography of SGD: Measuring Non-Markovian Memory via Back-Flow of Distinguishability* (arXiv 2601.16563, 2026-01-23; [A] Abstract per WebFetch, 16:19). Modellunabhängiges Maß für Trainingsgedächtnis; es wächst mit höherem Momentum,
  größerer Batch-Überlappung und mehr Mikroschritten und **bricht zusammen, wenn der Optimiererzustand zurückgesetzt wird**. Keine Frequenzen, kein Grokking, keine Festlegungszeit. *Einordnung:* stützt die qualitative K4b-Lesart als bekannt (mit Xu 2026, Sweeney 2026); schränkt K4/K4c nicht ein. Volltext nicht gelesen.
- **arXiv-Durchsicht der neuesten Grokking-Arbeiten (16:44, gemessen; arXiv-API `search_query=all:grokking`, sortiert nach Einreichung, 40 neueste, bis 2026-09-24; nur Titel/Abstracts [A]):** neu gegenüber dieser Datei u. a.
  2609.25634 (Replica-Overlap-Probe, registriert, Ergebnis „unbestimmt“), 2609.10657 (Skalierung der Grokking-Zeit T ∝ H^−0.27 D^−2.04 η^−0.50 λ^−0.64, zweischichtige MLPs; **Kontext für R1**: Lernrate und Weight Decay verschieben den Zeitpunkt stark),
  2609.19363 (Stiefel-Attention, W_Q/W_K auf der Stiefel-Mannigfaltigkeit, Weight Decay wirkt dort nicht; Kontext zu K4d/e, nicht einschränkend), 2608.07436 (Muon-Transformer verlieren die Generalisierung nach dem Grokking bei (a + b) mod 113, **auch eine AdamW-Referenz in 4/5 Seeds**;
  Kontext: unsere Persistenzmaße liegen bei 2000–4000 Schritten nach dem Wechsel, spätes Verhalten nicht geprüft), 2608.14803, 2608.28184, 2608.01833 (Dynamik/Mechanismen, nicht einschlägig).
  **Keine** steuert die Frequenzwahl über die Trainingsmenge oder misst eine Festlegung nach einem Datenwechsel → K2/K4 unverändert „nach unserer Suche nicht gefunden“.


### Nachtrag Sitzung 28 (2026-09-27): Einordnung der Feinordnung (C1)

Explorativ ordnet das Paarspektrum des Splits auch die Frequenzen **innerhalb** der Zielmenge, stärker als die Init-Energie ([[NOVEL_DIRECTIONS]] N39; Registrierung [[confirm/C1_REGISTRATION|C1]]). Abgrenzung: He et al. 2026a (2602.16849) finden bei vollen Daten die Init (Betrag/Phase) als Entscheider je Neuron; bei unseren konstruierten Splits ist der Init-Beitrag zur Rangfolge klein (ρ 0.08–0.15 gegen 0.21–0.44). Das widerspricht He et al. nicht (andere Datenlage), grenzt aber ab: Zu zitieren als „Daten gegen Init“. Suche vom 2026-09-27 ohne einschränkenden Treffer (Suchbegriffe in N39).

### Nachtrag Sitzung 29 (2026-09-27, vor 18:10 Berlin, gemessen): Init-Skala und Festlegungszeit (für EXP-040)

Suchbegriffe (WebSearch, 2026-09-27): „initialization scale critical period feature commitment time grokking embedding Adam“; „arXiv 2026 grokking data switch early training commitment Fourier features initialization scale“; „"initialization scale" feature learning time Adam linear versus exponential growth small initialization rich regime timescale“; „initialization scale shifts critical period timing neural network data switch first task persists steps“; „Adam sign-like updates linear feature growth small initialization time to escape scales with initialization magnitude“.
- **Khanh, Viet, Trung, Duc 2026**, *The Weight Norm Sets the Grokking Timescale: A Causal Delay Law* (arXiv 2606.13753, 2026-06-11; [A] Abstract per WebFetch). Eingriff: Gewichtsnorm auf Vielfache ρ eines kritischen Werts geklemmt; Grokking-Verzögerung ∝ exp(α ρ), α ≈ 7.5 über vier Moduli; Norm wirkt ≈ 19× stärker als die Lernrate (≈ 2×); LayerNorm hebt die Abhängigkeit auf. Keine Frequenzwahl, keine Festlegung nach Datenwechsel. *Einordnung:* schränkt K2/K4 nicht ein; **Kontext für EXP-040**: Eine größere W_E-Init (s = 2) kann das Grokking von „nur F“ verzögern (dort schon als Ausfallgrund „Zelle unklar“ geregelt); Beleg neben Kumar et al. 2023. Klemmen der Gesamtnorm ≠ unsere Skalierung nur des Nicht-Gleichanteils von W_E.
- **Das, Beneventano, Dey, McKinley, Poggio 2026**, *Do Deep Networks Forget Initialization? A Forgetting-Time View of Practical Inductive Bias* (arXiv 2605.29152, 2026-05-27; [A]). „Initialisierungsgedächtnis“: SGD mit kleiner Lernrate behält die Abhängigkeit von der Init-Skala, Adam-Familie löscht sie weitgehend (ResNet-9). Keine Aufgabe mit Frequenzen, kein Datenwechsel. *Einordnung:* Kontext zu H40 (unter Adam wirkt die Init-Skala vor allem früh); schränkt nichts ein.
- Nichts gefunden, das prüft, ob die Init-Skala das **Festlegungsfenster gegen einen Datenwechsel** verschiebt (H40). He et al. 2026a (2602.16849, schon zitiert) behandeln die Init-Lotterie ohne Datenwechsel. EXP-040 bleibt „nach unserer Suche nicht gefunden“ (vorläufig).

### Nachtrag Sitzung 29 (2026-09-27, vor 18:10 Berlin, gemessen): erste direkte Google-Scholar-Abfrage (Lücke aus Sitzung 24)

## Nachtrag Sitzung 30 (2026-09-27, 18:37 Berlin gemessen): Zufallssplit gegen Init (für [[confirm/R4_REGISTRATION_DRAFT|R4]])

Suchbegriffe (WebSearch, 2026-09-27): `grokking modular addition which Fourier frequencies learned depends on initialization or training split random seed`; `arXiv 2026 grokking "training set" subset determines key frequencies seed dependence modular arithmetic transformer`.
- **He et al. 2026a** (arXiv 2602.16849, schon zitiert): Init entscheidet den Frequenz-Wettbewerb (Lotterie); volle Daten, kein Split-Faktor. Bleibt die Vergleichsgröße zu H2 in R4.
- **Janati, El Maghraoui, Kanavalau, Belfatmi (2026).** *Post-Grokking Collapse at the Representation-Readout Interface in Muon-Trained Transformers.* arXiv 2608.07436. https://arxiv.org/abs/2608.07436 [A] (Abstract per WebFetch, Sitzung 30): Bei (a + b) mod 113 groken alle neun Muon-Konfigurationen und verlieren die Generalisierung später wieder; die AdamW-Referenz fällt in 4 von 5 Läufen unter die Schwelle. Für uns: Grenze „Persistenz nur 2000–4000 Schritte nach dem Wechsel gemessen“ (§6), schränkt K2/K4 nicht ein. (Die Arbeit war bisher nur als Nummer notiert; Autoren und Titel in Sitzung 30 nachgetragen.)
- **Ootani 2026** (arXiv 2607.05104, *Grokking Is Conditional and Fragile*, [A]+HTML gelesen): Mehr-Seed-Grokking-Raten; Testmenge mit festem Seed, Split nicht unabhängig von der Init variiert; misst die Konzentration des Spektrums, nicht die Identität der Frequenzen. Schränkt R4 nicht ein.
- Ergebnis: Kein Treffer, der Init- und Split-Seed für die **Identität** der gelernten Frequenzen gekreuzt trennt; nächstverwandt bleibt LeDoux 2026 (Zufalls-Teilmengen ändern die Frequenz unter Stride-Reihenfolge nicht). Einordnung: nach unserer Suche vom 2026-09-27 nicht gefunden (vorläufig, zwei Suchanfragen, keine Zitationsverfolgung).

## Nachtrag Sitzung 30 (19:18): Grokking-Tempo durch Datenauswahl

Suche (Agent, 21 Anfragen, 2026-09-27): [[paper/lit_grokking_speed_2026-09-27]]. Nächstverwandt und selbst am Abstract geprüft: **AlQuabeh et al. 2025**, *Mechanistic Insights into Grokking from the Embedding Layer*, arXiv 2505.15624 [A]: „frequency-aware sampling, which balances token updates by minimizing gradient variance“ beschleunigt das Grokking (Token-Häufigkeiten, Minibatch). Das schränkt die Aussage „die Datenauswahl ändert das Tempo“ ein. Unsere Beobachtung grenzt sich ab, weil sie über die Paarstruktur bei festgehaltenen Token-Häufigkeiten läuft (EXP-047). Die Autorenliste gab das Abrufwerkzeug verstümmelt wieder; sie muss am PDF geprüft werden. *Nachtrag Sitzung 32 (2026-09-27, 20:39 gemessen, arXiv-Abstractseite und arXiv-API):* Die Verstümmelung steckt in den arXiv-Metadaten selbst. Sie führen fünf Einträge: „H. V. AlquBoj“, Hilal AlQuabeh, Velibor Bojkovic, Munachiso Nwadike, Kentaro Inui. Der erste ist offenbar ein Einreichungsartefakt (eine Verschmelzung der Namen). Vorschlag zum Zitieren: AlQuabeh, Bojkovic, Nwadike, Inui (2025), v1 vom 21.05.2025. Die Entscheidung trifft ein Mensch am PDF. Der Abstract nennt ausdrücklich nur die Balance der **Token**-Updates („balances token updates by minimizing gradient variance“), keine Paarstruktur und keine Fourier-Frequenzen. Nach unserer Suche nicht gefunden: eine Beschleunigung durch Konzentration des Paarspektrums auf wenige Frequenzen (vorläufig, ohne Zitationsverfolgung).

## Nachtrag Sitzung 32 (2026-09-27, 21:10 Berlin, gemessen): Wechselkosten im Festlegungsfenster (N43, Exploration; Bestätigung R6 im Entwurf)

Suchbegriffe (5 Anfragen, 2026-09-27) in [[NOVEL_DIRECTIONS]] N43. Selbst am Abstract geprüft [A]:
- **Achille, Rovere, Soatto (2017/2019)**, *Critical Learning Periods in Deep Neural Networks*, arXiv 1711.08856 [A]: Ein vorübergehendes Reiz-*Defizit* schadet dauerhaft, abhängig von Beginn und Länge des Defizitfensters; Defizite ohne Einfluss auf niedrige Statistik (vertikales Spiegeln) wirken nicht nach. Die Fisher-Information steigt früh und fällt dann („Information Plasticity“). **Abgrenzung:** Dort gibt es Defizite und Endgenauigkeit, keinen Wechsel zwischen zwei gleich starken Trainingsmengen und keine Zeit bis zur Generalisierung; eine nicht-monotone Abhängigkeit vom Wechselzeitpunkt wird nicht berichtet. **Schränkt N43 ein:** teilweise, konzeptionell (frühe Phase entscheidet, kritische Perioden sind bekannt); die konkrete Beobachtung (Verzögerung maximal im Festlegungsfenster, keine bei vollendeter Festlegung) nicht.
- **Fukase et al. (2025)**, *One Period to Rule Them All*, arXiv 2506.15954 [A]: Kritische Perioden über Generalisierungsvorhersage finden, um teure Trainingsverfahren früh abzuschalten. **Abgrenzung:** kein Datenwechsel, kein Grokking. **Schränkt nicht ein.**
- **GrokTransfer** (arXiv 2504.13292) und **2609.18078** [S/A aus früheren Suchen]: Ein Warmstart aus einem anderen Modell beschleunigt Grokking. Kontext für den Befund „später Wechsel (≥ 150) beschleunigt“: dort Transfer zwischen Modellen, bei uns dasselbe Modell mit anderer Trainingsmenge. **Schränkt teilweise ein** (Beschleunigung durch Vortraining ist bekannt).
- **Howe (2026)**, arXiv 2607.04333 [A]: Strukturierte Repräsentationspriors (kontrastive Zusatz-Loss) steuern die Grokking-Verzögerung. **Abgrenzung:** kein Datenwechsel. **Schränkt nicht ein.**
Nach unserer Suche nicht gefunden (vorläufig, ohne Zitationsverfolgung): eine Zeitkostenkurve eines Datenwechsels, die im Fenster der Merkmalsfestlegung ihr Maximum hat und verschwindet, sobald die Wahl persistiert.
- **Theoretischer Rahmen, nur Kontext [S, Suchtreffer 2026-09-27, Sitzung 32]:** Saddle-to-Saddle-Dynamik (z. B. arXiv 2512.20607, *Saddle-to-Saddle Dynamics Explains A Simplicity Bias Across Neural Network Architectures*): Plateaus zwischen dem Lernen einzelner Merkmale, deren Länge vom Zustand beim Verlassen des Sattels abhängt. Mögliche Lesart für N43: Ein Wechsel mitten im Wachstum lässt teilweise gewachsene, zur neuen Aufgabe schlecht passende Merkmale zurück und verlängert das Plateau vor der Generalisierung. Das ist nicht geprüft, nicht aus der Arbeit abgeleitet und nur als Hypothese notiert.
- **Anterograde Interferenz, Kontext [S]:** Beim kontinuierlichen Lernen stören ähnliche Folgeaufgaben stärker (Menschen und Netze; Nature Human Behaviour 2025, https://www.nature.com/articles/s41562-025-02318-y). Das ist eine Parallele zum Befund, dass mehr gemeinsame Paare die Wechselkosten erhöhen (EXP-056/P3). Dort ging es um Aufgabenwechsel und Endleistung, nicht um die Zeit bis zur Generalisierung innerhalb einer Aufgabe. **Schränkt N43 nicht ein**, ist aber zu zitieren, falls N43 ins Paper geht.

## Nachtrag Sitzung 33 (2026-09-27, 22:44 Berlin, gemessen): zweite Suche zu N43 (Wechselkosten im Festlegungsfenster)

Suchbegriffe (WebSearch, 2026-09-27): „non-monotonic effect of pretraining duration on subsequent training speed switch timing "critical period" neural network generalization delay“; „grokking data distribution shift during training delays generalization timing of switch modular arithmetic 2025 2026 arXiv“; „"warm-starting" "time to generalize" or "convergence time" depends on amount of pretraining non-monotonic intermediate worst“; „"critical learning periods" citing grokking transformer "task switch" early training representation commitment delay 2026“; „"Critical Learning Periods in Grokking" temporal dynamics of algorithmic understanding“.
- **Park et al. (2022)**, *On the Importance of Critical Period in Multi-stage Reinforcement Learning*, arXiv 2208.04832 [A]: Eine formende Belohnung wirkt am besten nahe einer kritischen Periode. Es geht darum, was in der Periode gezeigt wird, nicht um eine Zeitkostenkurve eines Datenwechsels. **Schränkt nicht ein.**
- **Gomezjurado Gonzalez (2026)**, *The Long Delay to Arithmetic Generalization*, arXiv 2604.13082 [A]: Der Encoder ist früh organisiert, der Decoder ist der Engpass. Ein verpflanzter Encoder beschleunigt Grokking um das 2.75-Fache, ein verpflanzter Decoder schadet. Kontext zu „später Wechsel beschleunigt“ und zur Lücke nach der Memorisation (N43: 90 % der Verzögerung). Kein Datenwechsel. **Schränkt nicht ein**, lohnt sich aber als Zitat zur Plateau-Deutung.
- **„Critical Learning Periods in Grokking: Temporal Dynamics of Algorithmic Understanding“** [S]: Der Titel erscheint nur im Umfeld von *Towards End-to-End Automation of AI Research* (Yamada et al. 2026, arXiv 2606.15497), offenbar als vom System erzeugte Studie. Laut Snippet geht es um Lernraten-Erhöhungen in gleitenden 500-Schritt-Fenstern, nicht um Datenwechsel. Den Volltext habe ich nicht geprüft. **Für die menschliche Prüfung:** Anhang von 2606.15497 lesen, ob dort eine Zeitkostenkurve über den Eingriffszeitpunkt steht.
- Schon zitiert und erneut getroffen: 2510.09687 (Auftreten kritischer Perioden), 2507.20057 (Grokking und Nichtstationarität), 2605.04396 / 2606.12966 (kritische Fenster der Regularisierung).
**Stand:** Weiter nicht gefunden: eine nicht-monotone Zeitkostenkurve eines Datenwechsels mit Maximum im Festlegungsfenster der Merkmale. Das bleibt vorläufig, ohne systematische Zitationsverfolgung.

## Nachtrag Sitzung 34 (2026-09-27, vor 23:03 Berlin, gemessen)

- **Offener Vermerk aus Sitzung 33 geklärt:** arXiv 2606.15497 ist laut Abstract (WebFetch) *Yamada, Lange, Lu, Lu, Hu, Foerster, Ha, Clune: „Towards End-to-End Automation of AI Research“* (The AI Scientist) und behandelt kein Grokking. Der Titel „Critical Learning Periods in Grokking“ stammt wohl aus einem dort erzeugten Beispielmanuskript. Eine exakte Titelsuche (WebSearch „"Critical Learning Periods in Grokking"“, 2026-09-27) fand keine eigenständige Arbeit, nur bekannte Treffer (Lyle et al. 2025, 2507.20057, schon im Volltext geprüft; Achille et al. 2019). **Schränkt K4 nicht ein.** Für die menschliche Prüfung: kein Zitat nötig, außer das Beispielmanuskript soll erwähnt werden (Entscheidung beim Nutzer).
## Nachtrag Sitzung 35 (2026-09-27, bis 23:32 Berlin, gemessen): 2k-Oberwellen in W_E (Kontext für EXP-021, Paper §5.4(ii))

Suchbegriffe (WebSearch, 2026-09-27): „grokking modular addition second harmonic 2k frequency embedding Fourier features ReLU“, „modular arithmetic network learns frequencies k and 2k harmonics key frequencies interpretability arXiv“.
- **He, Wang, Chen, Yang (2026a), arXiv 2602.16849** (schon zitiert). Laut dem Blogbeitrag der Autoren (https://y-agent.github.io/posts/modular_addition_feature_learning/, Abschnitt 4.6 „Beyond Quadratic: ReLU Dynamics“, per WebFetch gelesen) gilt im **zweischichtigen ReLU-Netz mit One-hot-Eingabe**: In den Eingangsgewichten sickert Energie nur in **ungerade** Oberwellen (3k*, 5k*), in den Ausgangsgewichten in alle (2k*, 3k*); Stärke ≈ 1/n² der Grundfrequenz. Die WebFetch-Zusammenfassung der arXiv-HTML-Fassung v1 fand diese Aussage nicht wörtlich; in welcher Fassung bzw. welchem Abschnitt des Papers sie steht, ist für die menschliche Prüfung offen. [B: Blog, Paper-Stelle ungeprüft]
- **Abgrenzung zu uns:** Unsere Nicht-Ziel-Glieder der W_E-Top-5 unter konstruierten Splits sind **gerade** Oberwellen fold(2k) der Ziele (explorativ 14/14, EXP-016 Seeds 10–15; Bestätigung EXP-021 steht aus). In deren Modell (Eingangsgewichte ≈ Einbettung) würde man nur ungerade Oberwellen erwarten. Unser Modell ist aber ein Transformer: Attention und die gemeinsame Einbettung beider Positionen erlauben gerade Anteile (Vermutung, ungeprüft: z. B. über Produkte der Einbettungen in den Attention-Scores). **Schränkt nichts ein**; liefert eine prüfbare Unterscheidung (gerade Oberwellen in W_E als Transformer-Merkmal, im MLP-Piloten EXP-045 nachsehbar).
- Weitere Treffer ohne Bezug zu 2k in der Einbettung: 2402.09469 (Fourier-Schaltkreise, mehrere Eingaben), 2312.08550 (Harmonics of Learning, invariante Netze), 2603.25047 (schon zitiert: Harmonische durch Beispielreihenfolge).

## Nachtrag Sitzung 37 (2026-09-28, Berlin): Einordnung von R6/R8 (Wechselkosten nur bei anderer Zielmenge)

Suchen (WebSearch, 2026-09-28): „grokking data switch early training delay feature conflict warm-starting modular arithmetic Fourier frequencies“; „early training data distribution shift delays grokking same features vs different features critical period switch cost“; „critical learning periods deficit removed early training switch cost only when features differ“.
- **Achille, Rovere, Soatto (2019), arXiv 1711.08856** (schon zitiert, [K]): Defizite, die die niederstufige Statistik nicht ändern (z. B. vertikales Spiegeln), haben dort keine bleibende Wirkung, Unschärfe dagegen schon. **Das ist die nächste Parallele zu R8:** Ein früher Wechsel auf neue Paare mit *denselben* Zielfrequenzen kostet nichts, einer auf *andere* Zielfrequenzen schon. Abgrenzung: Die Autoren messen dauerhafte Endleistung nach einem Defizit, wir messen die Zeit bis zur Generalisierung nach einem Wechsel zwischen gleichwertigen Lösungen, bei gleicher Größe, Stärke und Aufgabe. **Schränkt die Neuheit von R8 teilweise ein** (das Prinzip „nur statistikverändernde frühe Änderungen wirken“ ist bekannt). Neu ist nach unserer Suche nur die kontrollierte Form: gleiche Zielmenge gegen andere Zielmenge bei gleicher Steuerstärke, als Zeitkosten beim Grokking.
- **2510.09687** (*On the Occurrence of Critical Learning Periods in Neural Networks*, schon gelesen, Abstract): Ein zyklischer Lernratenplan verhindert kritische Perioden. Für uns eine prüfbare Vorhersage: Hebt ein Lernraten-Neustart beim Wechsel die R6-Kosten auf? Nicht geplant; Bezug zu R3/EXP-081.
- **2506.15954** (*One Period to Rule Them All*, 2025): Die Autoren identifizieren kritische Perioden zur Trainingsverkürzung. Kein Bezug zu Lösungswahl oder Wechselkosten.
- **Lyle et al. 2025 (2507.20057, schon zitiert):** Der Primacy-Bias ist das allgemeine Phänomen, R6 eine gemessene Instanz davon mit Frequenz-Signatur.
- Für die menschliche Prüfung: Die Achille-Parallele sollte in §5b (Diskussion) des Entwurfs genannt werden, bevor R8 als neu dargestellt wird.

## Nachtrag Sitzung 38 (2026-09-28, 05:26 Berlin, gemessen): Einordnung von R5 (Beschleunigung durch konstruierte Splits)

Suchbegriffe (WebSearch): „accelerating grokking embedding transfer Fourier initialization modular addition“, „grokking training data selection speed mediated by early embedding structure causal“. Abstract von arXiv 2607.04333 selbst abgerufen.
- **Howe (2026)**, arXiv 2607.04333 [A]: Ein kontrastiver Zusatzverlust mit der *wahren* Struktur ((a + b) mod p) beschleunigt das Grokking eines 1-Schicht-Transformers dosisabhängig und bimodal über Seeds; eine kohärente, aber falsche Struktur ((a − b) mod p) lässt Grokking bestehen, eine zufällige verhindert es. Die Datenzusammensetzung wird nach dem Abstract nicht variiert. **Für R5:** Dass frühe, aufgabenrichtige Repräsentationsstruktur die Verzögerung kausal verkürzt, ist bekannt. R5 zeigt eine Beschleunigung allein über die *Paarauswahl* bei gleicher Größe, Init und Testmenge, gegen eine je Ausgabe exakt abgeglichene Kontrolle; der frühe W_E-Zielanteil ist bei uns nur beschreibend/korrelativ mit dem Tempo verbunden (post hoc innerhalb der E-Arme ρ −0.64 bis −0.79). **Schränkt ein:** eine Deutung „der Split wirkt über frühe Einbettungsstruktur“ wäre eine Anwendung dieses bekannten Mechanismus, kein neuer Mechanismus. Ob die Daten-Beschleunigung vollständig darüber läuft, ist offen ([[NOVEL_DIRECTIONS]] N47). Im Paper §3.9 zitieren.
- **GrokTransfer** (arXiv 2504.13292): Einbettungs-Warmstart aus einem schwächeren Modell beschleunigt Grokking (auch Transformer, modulare Addition). Gleiche Einordnung wie oben; bei uns kein Transfer, nur andere Trainingspaare.

## Nachtrag Sitzung 41 (2026-09-28, ≈ 13:40 Berlin): Einordnung von R9 / K5 (Adams Fenster und die Festlegungsuhr)

Suchen (WebFetch/WebSearch, 2026-09-28): Volltext Malladi et al. (HTML-Fassung, Definition 5.2); „Barakat Bianchi Adam ODE beta1 = 1 - a gamma step size vanishing continuous-time limit“; Volltext Barakat & Bianchi (PDF v4, Annahme 2.5).
- **Malladi, Lyu, Panigrahi & Arora (NeurIPS 2022), arXiv 2205.10287** [A]: SDE-Näherung für RMSprop/Adam; Quadratwurzel-Regel beim Vergrößern der Batch um κ: η′ = √κ·η, 1 − β₁′ = κ(1 − β₁), 1 − β₂′ = κ(1 − β₂), ε′ = ε/√κ (Definition 5.2, selbst gelesen). In Lernratenfaktor c ausgedrückt 1 − β ∝ c². **Nicht** unsere Regel (bis Sitzung 40 fälschlich als dieselbe bezeichnet; korrigiert).
- **Barakat & Bianchi (SIAM J. Optim. 2021), arXiv 1810.02263** [A]: kontinuierliche Adam-ODE; Annahme 2.5: a = lim (1 − α(γ))/γ und b = lim (1 − β(γ))/γ für Schrittweite γ → 0 existieren, also 1 − β ∝ γ (im Volltext geprüft). **Das ist unsere Regel 1 − β′ = c(1 − β)** (deterministischer Vollbatch-Grenzfall: gleiche Fenster in aufsummierter Lernrate). Bekannt ist also die Regel; nicht gefunden (nach dieser Suche) die Folge für die persistente frühe Merkmalswahl beim Grokking.
- **arXiv 2511.04622** (ODE approximation for Adam, 2025) [A, nur HTML überflogen]: betrachtet feste β bei fallender Schrittweite und grenzt sich ausdrücklich vom Regime „β → 1 so schnell wie γ → 0“ ab. Bestätigt, dass beide Grenzfälle in der Literatur getrennt behandelt werden.
- Für die menschliche Prüfung: K5 im Paper als „Folge einer bekannten Zeit-Umparametrisierung für eine neue Messgröße“ darstellen, nicht als neue Skalierungsregel.
- **Tissue, Wang, Wang (2024), arXiv 2408.11029** (*Scaling Law with Learning Rate Annealing*, NeurIPS 2025) [A, Abstract/Suchtreffer]: Verlustkurven von Sprachmodellen folgen L(s) = L₀ + A·S₁^(−α) − C·S₂ mit S₁ = Fläche unter der Lernratenkurve („forward area“, spiegelt die gesamte Parameterbewegung) und S₂ = Annealing-Fläche, in der ein Momentum-artiger Term vorkommt. **Unser Λ ist S₁.** Dass die aufsummierte Lernrate die natürliche Zeitachse des Trainings ist, ist also bekannt (dort für den Verlust, bei uns für die frühe Festlegung der Frequenzwahl).
- **Momentum als Gedächtnis-Zeitskala** [A, nur Suchtreffer, nicht gelesen]: neuere Arbeiten behandeln β₁/β₂ und Weight Decay als horizontabhängige Gedächtnisfenster und skalieren sie mit Batch oder Trainingsdauer (z. B. arXiv 2602.05298 *Logarithmic-time Schedules … with Momentum*; arXiv 2609.04577 *Optimizer Memory Schedules*; β₂ so gewählt, dass das zweite Moment über gleich viele Tokens mittelt). Das stützt die Lesart „Fenster in Schritten ist die falsche Einheit“, die R9 für die Festlegung zeigt.
- **Einordnung R9/K5 (für die menschliche Prüfung):** R9 ist eine **Anwendung bekannter Optimierungsprinzipien** (Zeit = aufsummierte Lernrate; Adams Fenster sind in Schritten fest und müssen für gleiche Dynamik mit der Lernrate mitskaliert werden, Barakat & Bianchi) auf eine neue Messgröße (Persistenz der frühen Frequenzwahl unter Datenwechsel). Neu nach unserer Suche vom 28.09. ist nur dieser Befund, nicht das Prinzip.

## Nachtrag Sitzung 41 (2026-09-28, ≈ 13:55 Berlin): Fourier-/Arithmetik-Mechanismen in Sprachmodellen und Datenkuratierung (Abgrenzung für die nächste Frage im [[paper/ONE_PAGER]])

Suchen (WebSearch/WebFetch, 2026-09-28): „Pre-trained Large Language Models Use Fourier Features to Compute Addition“; „Kantamneni Tegmark Language Models Use Trigonometry to Do Addition“; „Nikankin Arithmetic Without Algorithms“; „training data selected to induce a predicted internal mechanism Fourier features language model arithmetic designed training set mechanistic“. Nur Abstracts/Suchzusammenfassungen gelesen [A], außer wo vermerkt.
- **Zhou, Fu, Sharan, Jia (NeurIPS 2024), arXiv 2406.03445** [A]: Vortrainierte LLMs addieren mit Fourier-Merkmalen (MLP niedrige Frequenzen für die Größe, Attention hohe Frequenzen für modulare Anteile, Perioden 2/5/10 in den Token-Embeddings). Von Grund auf trainierte Modelle nutzen nur niedrige Frequenzen; vortrainierte Embeddings „retten“ das. **Nächste Vorarbeit für unsere offene Frage:** Dort ist die Quelle der Frequenzen das Vortraining bzw. die Embeddings, nicht eine gezielt zusammengestellte Trainingsmenge.
- **Kantamneni & Tegmark (2025), arXiv 2502.00873** [A]: Zahlen als verallgemeinerte Helix in GPT-J, Pythia-6.9B, Llama3.1-8B; Addition per „Clock“-Algorithmus, kausal belegt. Beschreibt, was große Modelle nutzen, nicht wie Daten es steuern.
- **Nikankin, Reusch, Mueller, Belinkov (2024), arXiv 2410.21272** [A]: Arithmetik in LLMs als „Bag of Heuristics“ (spärliche Neuronen mit einfachen Mustern). Gegenbild zu sauberen Fourier-Schaltkreisen: In großen Modellen ist nicht garantiert, dass eine vorhergesagte Fourier-Lösung entsteht.
- **Chen, Luo, Pan (2026), arXiv 2601.21996** (*Mechanistic Data Attribution*) [A, Abstract gelesen]: Influence-Funktionen führen interpretierbare Einheiten (Köpfe) auf Trainingsbeispiele zurück; Entfernen oder Hinzufügen weniger einflussreicher Beispiele verändert kausal das Entstehen dieser Köpfe, zufällige Eingriffe nicht. **Engste Arbeit zur Frage „Daten steuern einen Mechanismus“:** dort rückwärts (Attribution nach dem Training), nicht vorab aus einer Theorie berechnet. Schränkt einen Neuheitsanspruch „Datenauswahl verändert interne Mechanismen“ deutlich ein.
- **Datenkuratierung als Abgrenzung (bekannt, nur Einordnung):** Gunasekar et al. 2023, *Textbooks Are All You Need* (arXiv 2306.11644, Datenqualität für kleine Code-Modelle); Sorscher et al. 2022, *Beyond neural scaling laws: beating power law scaling via data pruning* (arXiv 2206.14486); Xie et al. 2023, *DoReMi* (arXiv 2305.10429, Datenmischung). Dass Datenauswahl beeinflusst, *was und wie schnell* Modelle lernen, ist etabliert.
- **Einordnung für die nächste Frage:** Bekannt: Datenauswahl wirkt auf Leistung und Tempo; LLMs nutzen Fourier-/Helix-Merkmale für Addition; Trainingsbeispiele lassen sich nachträglich Mechanismen zuordnen und gezielt verändern. **Nach unserer Suche vom 28.09. nicht gefunden (vorläufig):** Trainingsbeispiele *vorab aus einer Theorie* (Maskenspektrum/erster Gradient) so auswählen, dass ein Sprachmodell eine *vorhergesagte* interne Lösung (bestimmte Fourier-Frequenzen für Addition) lernt, und diese Vorhersage prüfen.

## Nachtrag Sitzung 41 (2026-09-28, ≈ 14:18 Berlin): Abgleich mit der Neuheitsprüfung des Nutzer-Assistenten ([[paper/outreach/NOVELTY_CHECK_2026-09-28]])
Die meisten genannten Arbeiten standen schon hier (Kleinman 2024, Frankle 2020, Lyle 2025, Jia 2026, Howe 2026a = 2607.12735, Sweeney 2026, Pracher 2026). Neu bzw. neu eingeordnet, jeweils selbst an der Quelle geprüft, wo vermerkt:
- **LeDoux 2026 (HTML selbst gelesen):** „F=101 emerged as the peak embedding frequency on every seed tested … despite each seed selecting a different random subset of 300,000 training pairs“ (p = 9973, 0.3 %, Batch 256, AdamW, strukturierte Reihenfolge). **Spannung zu R4** im Paper §3.14 diskutiert: dort setzt ein starkes Reihenfolgesignal die Frequenz, und die Maskenspektrum-Schwankung einer Zufallsteilmenge schrumpft etwa mit 1/√(Paarzahl) (≈ 9× kleiner als bei unseren 3831 Paaren).
- **He et al. 2026a** als konkurrierende Erklärung zu R4 in §3.14 genannt (Init und Split tragen beide bei; Split beschreibend mehr).
- **Kleinman, Achille, Soatto 2024 (Abstract selbst gelesen):** „pre-training on certain tasks can damage the transfer performance on new tasks, and show how this depends on the relationship between tasks“ → qualitative Parallele zu R8, im Paper §3.8 zitiert.
- **Sweeney 2026:** nimmt das *Prinzip* von R9 vorweg (Momente im Schritttakt statt τ = η·k); in §3.15 und im One-Pager als Vorarbeit genannt, R9 als Anwendung.
- **AlQuabeh et al. 2025, arXiv 2505.15624** [nur laut Neuheitsprüfung, nicht selbst gelesen]: gleichmäßiges Token-Sampling beschleunigt Grokking (Minibatch). Abgrenzung zu R5: unsere Kontrolle D hält die Anzahl der Paare je Ausgabe fest, der Vorsprung bleibt (×7.5); vor Übernahme ins Paper Abstract prüfen.

## Nachtrag Sitzung 43 (2026-09-28, ≈ 18:36 Berlin, gemessen): Einordnung von EXP-095 (frische Gradientenauswertungen) und der Vorzeichen-Einschränkung

Suche am 28.09. durch einen Recherche-Agenten (nur lesend; Websuche + arXiv-API; Semantic Scholar HTTP 429, Google Scholar nicht erreicht). Begriffe: „stale gradient feature learning implicit bias asynchronous SGD staleness“, „gradient reuse multiple optimizer steps lazy“, arXiv-API abs:"stale gradient" AND abs:feature (0 Treffer), „reusing gradients / gradient recycling“, „delayed gradient descent implicit regularization“, „one gradient step feature learning“, „multi-step vs giant step“, „number of gradient evaluations vs number of steps“, „early phase“, „silent alignment“, „rich-get-richer feature learning“, „saddle-to-saddle“, „AGF modular arithmetic“, „grokking optimizer momentum early Fourier“, „Grokfast“, „grokking lazy to rich“. Prüfgrad wie oben: [A] Abstract, [S] Snippet.

- **Dandi et al. (2023), arXiv 2305.18270 [S]:** Ein einzelner großer Gradientenschritt lernt in Zwei-Schicht-Netzen nur eine Richtung; weitere Richtungen brauchen weitere Schritte, die an schon gelernte anschließen. Nächste Analogie zu „Auswertungen, nicht Schrittweite“, aber in Lehrer-Modellen (Single/Multi-Index), nicht beim Grokking, und ohne feste Schrittzahl bei variierter Auswertungszahl. Schränkt EXP-095 nicht ein, ist aber zu zitieren.
- **Ba et al. (2022), arXiv 2205.01445 [A]:** Ein großer erster Schritt fügt einen Rang-1-Anteil hinzu, der nur mit dem linearen Teil des Ziels ausgerichtet ist. Kontrast zu unserer g24-Zelle (nur Anfangsgradient).
- **Mitliagkas et al. (2016), arXiv 1605.09774 [A]:** Staleness bei asynchronem SGD wirkt wie implizites Momentum; Konvergenz, nicht Merkmalswahl.
- **Barrett & Dherin (2020), arXiv 2009.11162 [A]; Smith et al. (2021), arXiv 2101.12176 [S]:** Implizite Regularisierung endlicher Schrittweiten (Rückwärtsfehleranalyse); Schrittweite, nicht Wiederverwendung veralteter Gradienten.
- **Atanasov, Bordelon, Pehlevan (2022), arXiv 2111.00034 [A]; Frankle, Schwab, Morcos (2020), arXiv 2002.10365 [A]; Pesme & Flammarion (2023), arXiv 2304.00488 [A]:** frühe Ausrichtung / frühe Phase / inkrementelles Lernen; stützen „frühe Festlegung“ allgemein, ohne Eingriff in die Frische der Gradienten.
- Schon zitiert und hier einschlägig: He et al. 2026a (2602.16849, zustandsabhängiges exponentielles Wachstum der Gewinnerfrequenz, Gradientenfluss), Kunin et al. 2025 (AGF), Kumar et al. 2024 (Lazy → Rich), Grokfast (2405.20233, verstärkt langsame Gradientenanteile in der späten Phase).

**Einordnung:** Dass frühe Merkmalswahl ein zustandsabhängiger, sich selbst verstärkender Prozess ist, den die Linearisierung an der Init nicht voll erfasst, ist **bekannt** (He et al., AGF, Dandi et al., Kumar et al.). **Nicht gefunden** (vorläufig): ein Eingriff, der bei fester Zahl von Optimiererschritten die Zahl frischer Gradientenauswertungen variiert und die Wirkung auf die persistente frühe Merkmalswahl misst (EXP-095, Bestätigung R10). **Einschränkung aus eigener Nachauswertung (Sitzung 43):** Mit eingefrorenem Gradienten macht Adam Vorzeichenschritte; das erklärt post hoc etwa die Hälfte der schwachen Selektivität im Arm „nur Anfangsgradient“. Die Sign-Descent-Deutung von Adam ist bekannt (Balles & Hennig 2018, ICML, arXiv 1705.07774, *Dissecting Adam: The Sign, Magnitude and Variance of Stochastic Gradients* [A], Abstract am 28.09. nachgeprüft: Richtung von Adam = Vorzeichen des Gradienten, Größe = Schätzung der relativen Varianz; bei festem Gradienten ist die Varianz 0, also reiner Vorzeichenschritt, wie bei uns gemessen). Für die menschliche Prüfung vorrangig: Dandi et al. im Volltext (ob dort Schrittzahl und Auswertungszahl getrennt werden).

## Nachtrag Sitzung 43 (2026-09-28, ≈ 19:20 Berlin): LeDoux 2026 im Volltext (HTML v1) für L0 (Regel 20b)

**LeDoux, J. (2026). *The Order Is The Message.* arXiv 2603.25047 (24.03.2026)** [L: HTML-Volltext per WebFetch, Methodenteil; Zitate aus der Zusammenfassung des Abrufs, vor dem Zitieren im Paper selbst gegenlesen].
- Aufgabe (a + b) mod p, **p = 9973**, 300 000 Trainingspaare (≈ 0.3 % der Paare), Test 1 000 000 Paare. Modell: 2-Schicht-Pre-LN-Transformer, d = 256, 4 Köpfe, FFN 2048, Eingaben per Embedding + Position, **mean-pooled**.
- Training: **Batch 256**, AdamW (wd 0.1, β 0.9/0.999), lr 1e-3 mit Cosine-Abfall über 5000 Epochen.
- Reihenfolgen bei identischen Daten: **Stride** (sortiert nach (a mod s, a), s = ⌊√p⌋ = 99; über Epochen fest), **Fixed-Random** (eine feste Permutation), **Random** (i.i.d.-Neumischung je Epoche), **Target** (nach (a + b) mod p sortiert). Ergebnis: Stride 99.5 % Test nach 487 Epochen, Fixed-Random nach 659, i.i.d. 0.30 % nach 5000, Target scheitert.
- „Regardless of initialization or training set composition“: Stride mit 6 Seeds, **jeder Seed zieht eine andere zufällige Teilmenge**; die Spitzenfrequenz F = 101 (Fourier-dual zur Stride-Struktur) tritt in allen auf.
- **Abgrenzung zu uns:** Dort variiert die Zusammensetzung nur als Zufallsteilmenge, bei uns ist sie spektral konstruiert (K2). Dort gibt es 0.3 % der Daten, Minibatch und eine feste Reihenfolge, bei uns 30 %, Full-Batch und keine Reihenfolge. Die Aussagen widersprechen sich also nicht direkt, aber die offene Frage ist genau L0: Was gewinnt, wenn eine konstruierte Menge und eine strukturierte Reihenfolge verschiedene Frequenzen bevorzugen? Und bleibt K2 unter i.i.d.-Minibatch bestehen? Übertrag der Stride-Konstruktion auf p = 113: s = ⌊√113⌋ = 10, duale Frequenz nahe p/s ≈ 11 (vor dem Pilot aus der Stride-Maske selbst berechnen, nicht annehmen).

## Nachtrag Sitzung 43 (2026-09-28, ≈ 20:05 Berlin): Tomàs Bernal, Mallinar, Belkin 2026 im HTML-Volltext (WebFetch, Zusammenfassung mit Zitaten)

- Konstruktion: symmetrische (H-invariante) Trainingsmengen, z. B. alle Fixpunkte (a, a) einer Spiegelung s in die Testmenge, der Rest ins Training. Dann ist h·X_tr = X_tr für H = {id, s}.
- Zitat: „RFM fails to generalize only when using train-test partitions that are invariant under the action of a non-singleton subgroup, H“. Die AGOP-Matrix zeigt dann nur die Streifen der Permutationsdarstellungen von srᵏ und der Identität. „breaking symmetry in the training data is needed to recover generalization“.
- Nicht untersucht: konstruierte, nicht-symmetrische Splits, die bestimmte Fourier-Frequenzen vorgeben; neuronale Netze (nur RFM mit Gauß-/quadratischem Kern); Aufgaben mod 29/53/61/32, C₅ × C₁₁.
- **Einordnung:** Unsere Lesart „symmetrische Splits wählen die kodierte Untergruppe“ stimmt im Kern, mit einer Einschränkung: Dort verhindern symmetrische Splits die Generalisierung. K2 ist dagegen eine graduelle Anreicherung vorgegebener Frequenzen in generalisierenden Netzen. Die Kurzfassung ist entsprechend angepasst. Für die menschliche Prüfung bleibt das PDF selbst zu lesen (die Zitate kamen über ein zusammenfassendes Werkzeug).

**Nachtrag Sitzung 44 (2026-09-28, 20:40):** Pracher, de Jong, Lieshaus, Jeffares, Rulands 2026, „A Spectral Theory of Grokking: Weight Decay induces Feature Learning“ (arXiv 2609.26679, eingereicht 22.09.2026) [A, über ein zusammenfassendes Werkzeug]: Weight Decay treibt den Übergang vom NTK-Regime zum Merkmalslernen; die Grokking-Zeitskala wird vom Produkt aus Lernrate und Weight Decay bestimmt (Generalisierungszeit ∝ 1/(lr·wd)); oberhalb eines kritischen Decays keine Generalisierung. Laut Zusammenfassung nichts zur Zahl der Frequenzen oder zur Datenzusammensetzung. **Bezug zu uns:** R1 misst Δ_pow bei fester Schrittzahl 2000; dass es mit lr und wd steigt, passt zu mehr Fortschritt bei größerem lr·wd und ist deshalb kein eigener Befund über Weight Decay (siehe [[NOVEL_DIRECTIONS]] N50). R5 (Beschleunigung durch die Datenauswahl) ist davon unabhängig. Vor Zitat im Volltext lesen.

**Nachtrag Sitzung 44 (20:47):** Wang & Aitchison, „How to set AdamW's weight decay as you scale model and dataset size“ (ICML 2025, arXiv 2405.13698) [A]: AdamW-Gewichte als exponentielles Mittel der jüngsten Updates; es gibt eine eineindeutige Zuordnung zwischen dessen Zeitskala und dem Weight Decay (die Formel 1/(lr·wd) laut Such-Snippet [S], nicht im Volltext geprüft). Bezug: Zeitmaß τ = t·lr·wd in der R1-Nachauswertung (draft §3.7, Abb. 12). Golatkar, Achille, Soatto 2019 (arXiv 1905.13277) [S]: Weight Decay wirkt vor allem auf die frühe Dynamik; Bezug zu N51 (zwei Uhren).

**Nachtrag Sitzung 44 (21:08), LeDoux 2026 Zahlen für L0/N52:** Batch 256 überall; p = 9973 bei 0.3 % (Epoche ≈ 1170 Schritte): Stride generalisiert (99.5 % nach 487 Epochen), Zufall nicht (0.30 % nach 5000); p = 97 bei 26.5 % (Epoche ≈ 10 Schritte): alle Reihenfolgen generalisieren, feste ≈ 20 % schneller; §6.4: Bedeutung der Reihenfolge „scales inversely with content signal adequacy“. Für das Paper: unser Regime (30 %, 15 Schritte je Epoche bei B = 256) liegt auf der Seite, auf der LeDoux selbst nur einen mäßigen Reihenfolgeeffekt fand.

**Nachtrag Sitzung 44 (21:29), Tomàs Bernal et al. 2026 Einstellungen:** RFM-Merkmale dort über Permutationsdarstellungen beschrieben, keine Frequenz-/Irrep-Zerlegung; meist 50 % Daten, L = 2.5, 60 Iterationen, Gauß- und quadratischer Kern. Für EXP-101 (Frequenzzerlegung der AGOP bei konstruierten Splits) nach unserer Suche nicht berichtet.

**Nachtrag Sitzung 44 (21:31), zwei Arbeiten für die Einordnung der Theorie erster Ordnung und von K4 (Suche: „"The Order Is The Message" LeDoux … follow-up 2026 …“, „grokking modular arithmetic minibatch versus full batch Fourier features … batch size 2026“, „"Fourier gap" initial gradient grokking large minibatch amplification“):**
- **Barak, Edelman, Goel, Kakade, Malach, Zhang (NeurIPS 2022), „Hidden Progress in Deep Learning: SGD Learns Parities Near the Computational Limit“, arXiv 2207.08799** [A]: „SGD gradually amplifies the sparse solution via a Fourier gap in the population gradient, making continual progress that is invisible to loss and error metrics.“ **Bezug:** Unsere Theorie erster Ordnung (§5) sagt, dass der erste W_E-Gradient das Maskenspektrum trägt und die Wahl früh fällt; das ist dieselbe Denkfigur (Information im Populationsgradienten wird verstärkt), bei uns aber mit einem vom Experimentator gesetzten Spektrum über die Datenauswahl. Als Vorläufer zitieren; schränkt K2 nicht ein.
- **Lin (2026), „Canalization Before Generalization: Grokking as a Dynamical Probe“, arXiv 2608.25813** (v2 4.9.2026) [A, nur Zusammenfassung]: Die Lösungsauswahl beim Grokking wird durch kurze Weight-Decay-Störungen sondiert; eine stabile Dosisordnung entsteht vor sichtbarer Generalisierung. **Bezug:** frühe Festlegung vor dem Grokking wie K4, aber über Weight-Decay-Störungen statt Datenwechsel und ohne Frequenzmessung (laut Zusammenfassung). Vor Zitat im Volltext prüfen, ob dort Frequenzen oder die Zeitskala der Festlegung gemessen werden.
Kein Folgepapier gefunden, das Datenmenge und Datenreihenfolge beim Grokking gegeneinander stellt (L0 bleibt nach dieser Suche offen).
- **Lin 2026, Volltext-Nachtrag (21:32, HTML über ein zusammenfassendes Werkzeug):** Aufgaben Paritäts-Abgleich, dünne Parität (MLP) und faktorisierte Addition mod 67 (Einbettungsmodell), AdamW. Nur der Weight Decay wird kurz gestört, die Daten bleiben gleich. „Kanalisierung“ = geordnete Dosis-Antwort der Generalisierungszeit auf die Störungen plus verschwindende Verlustbarrieren; die Ordnung entsteht ≈ 4000 Epochen vor sichtbarer Generalisierung (Aufgabe 1, t₀ ≈ 5000–5500, §2.3). Fourier-Anteile nur in Aufgabe 1 und erst nahe der Generalisierung (Anhang E). **Abgrenzung zu K4:** keine Datenwechsel, keine Messung, welche Frequenzen gewählt werden, keine Festlegung in den ersten 25–50 Schritten. Verwandt als „frühe Lösungsauswahl vor dem Grokking“, schränkt K4 nach dieser Lektüre nicht ein.

**Nachsuche Sitzung 44 (21:47), R5-Umfeld:** WebSearch „training data selection accelerates grokking modular arithmetic structured subset 2026 arXiv“. Neu gesichtet [A]: Song & Ye 2026 (arXiv 2605.09724, Grokking als Wettlauf von Memorier- und Generalisierungstempo, abhängig von der Modellkapazität; keine Datenauswahl, keine Frequenzen) und NeuralGrok (Zhou, Fan, Jaggi, Fu 2025, arXiv 2504.17243; Beschleunigung über eine gelernte Gradiententransformation, keine Datenauswahl). Beide schränken R5 nicht ein. Übrige Treffer (Howe 2026, 2605.15787, 2504.13292) bereits eingeordnet.

**Nachsuche Sitzung 45 (21:54, gemessen), L0-Umfeld (Minibatch/Reihenfolge):** WebSearch „grokking minibatch data order frequency selection modular arithmetic arXiv 2026“ und „training set composition determines Fourier features grokking transformer September 2026“. Neu gesichtet [S, nur Repository-README]: Hancock 2026, *The Effects of Online Batch Selection on Grokking* (https://github.com/PJHancock/Grokking, April 2026, kein arXiv-Link gefunden): Subtraktion mod 96, Decoder-Transformer; Online-Batch-Auswahl (uniform, RHO-Loss, DivBS, Bayes) ändert Zeitpunkt und Güte des Grokkings kaum, GrokFast beschleunigt stark. Frequenzwahl nach der README nicht berichtet. **Abgrenzung:** wählt Batches aus einer festen Trainingsmenge dynamisch nach Verlustkriterien, nicht die Menge selbst; misst Zeit, nicht welche Frequenzen. Schränkt K2/R5 nicht ein; für L0 als Beleg zitierbar, dass die Batch-Zusammensetzung *innerhalb* einer Menge die Grokking-Zeit dort kaum verschiebt (vor Zitat Volltext lesen). Außerdem [S]: arXiv 2605.20441 (Weight-Decay-Regime, Online-Diagnostik) – ohne Datenauswahl, nicht einschränkend. Übrige Treffer (LeDoux 2603.25047, 2609.26679, 2602.16849, 2607.05104, 2603.23784) bereits eingeordnet.

**Nachsuche Sitzung 45 (22:31, gemessen), von der simulierten Gutachter-Prüfung erwartete Zitate:** Zhu, Fu, Zhou, Lin 2024, *Critical Data Size of Language Models from a Grokking Perspective* (arXiv 2401.10463) [A]: Datenmenge als Schwelle zwischen schnellem Memorieren und langsamer Generalisierung, Größe steigt mit der Modellgröße; Datenmenge, nicht Zusammensetzung → für R5/L0 als Kontext zitieren, schränkt nicht ein. Singh, Belilovsky, Aljundi 2025, *When Data Falls Short: Grokking Below the Critical Threshold* (arXiv 2511.04760) [A, über ein zusammenfassendes Werkzeug]: Distillation aus einem gegrokkten Modell ermöglicht Grokking bei zu wenig Daten; keine Auswahl von Teilmengen, keine Frequenzanalyse → schränkt nicht ein; verwandt mit R5 (Beschleunigung) über einen anderen Hebel. Suchbegriff: „"Critical Data Size of Language Models from a Grokking Perspective" arXiv“.

**Nachsuche Sitzung 46 (29.09., ≈ 01:36 Berlin), Einordnung von EXP-100-Machbarkeit / EXP-106 (Suchbegriffe: „grokking small batch size weight decay fails to learn modular addition AdamW batch size effect“, „grokking data order curriculum fixed ordering minibatch Fourier frequency selection 2026 arXiv“):**
- **Liu et al. 2022** (Effective theory, arXiv 2205.10343) [S, nur Suchzusammenfassung]: Batch-Größe steuert das Rauschen; Grokking liegt im Phasendiagramm bei kleiner Decoder-Lernrate und kleiner Batch-Größe. Unser Befund „B = 16 mit wd 1 lernt in 30 000 Schritten nicht, mit wd 0.1 schon“ ist damit nicht im Widerspruch (anderes Modell, andere Achsen); dass die Kombination kleine Batches + starker Weight Decay zum Kollaps führen kann, passt zur Kollaps-Phase bei starkem Weight Decay in **Verma 2026** (arXiv 2605.20441, Abstract gelesen: Regime Memorisation / Grokking / Kollaps entlang des Weight Decay; keine Aussage zur Batch-Größe). Für das Paper: unsere B16-Beobachtung als Regimegrenze berichten, nicht als neu.
- **LeDoux 2026** (erneut, Abstract/Suchzusammenfassung): „the generalizing model reliably constructs a Fourier representation whose fundamental frequency is the Fourier dual of the ordering structure“ — **prüfbarer Gegensatz zu unserer B16-Sonde** (n = 3, gesehen): bei wd 0.1 / B = 16 lernt das Netz auch mit stride-Reihenfolge, die Energie auf O steigt, die stärkste Frequenz liegt aber in 0/3 Läufen in O. EXP-106 prüft das mit 8 Seeds; Unterschiede zu LeDoux: p = 113 statt 9973, 30 % statt 0.3 % Daten (die Menge trägt dort viel mehr Inhaltssignal, LeDoux §6.4 „scales inversely with content signal adequacy“).
- Keine Arbeit gefunden, die Menge und Reihenfolge mit gegenläufig gewählten Frequenzen direkt gegeneinander stellt (Stand dieser Suche; vorläufig).

## Nachtrag Sitzung 47 (2026-09-29, ≈ 04:15 Berlin): Festlegungsuhr unter Minibatch (N54b, EXP-108/109)

Suche durch einen Claude-Agenten am 2026-09-29 (WebSearch/WebFetch auf arXiv, OpenReview, Semantic-Scholar-Seiten; Google Scholar nicht erreicht, Semantic-Scholar-API nicht direkt abgefragt). Suchbegriffe u. a.: „Malladi SDEs and scaling rules for adaptive gradient algorithms square root“, „critical learning periods batch size early commitment square root scaling“, „grokking batch size modular arithmetic minibatch“, „Frankle linear mode connectivity instability onset batch size“, „Jastrzebski break-even point batch size learning rate“, „Granziol learning rates as a function of batch size random matrix Adam“, „Adam surge phenomenon sign noise sqrt(B)“, „critical period batch size onset Kleinman“. Prüfgrade vom Agenten angegeben, nicht von mir am Volltext nachvollzogen.

- **Li et al. (2024), *Surge Phenomenon in Optimal Learning Rate and Batch Size Scaling*, NeurIPS, https://arxiv.org/abs/2405.14578** [F laut Agent, HTML]: Sign-Modell E[sign(g_B)]ᵢ = erf(√(B/2)·μᵢ/σᵢ) ≈ √(2B/π)·μᵢ/σᵢ bei kleinem B → bei fester lr Drift je Schritt ∝ √B, Sättigung nahe Full-Batch. **Grundlage unserer Deutung** der Wurzel-Uhr (Ableitung von uns, nicht in der Arbeit).
- **Malladi, Lyu, Panigrahi, Arora (2022), NeurIPS, https://arxiv.org/abs/2205.10287** (schon oben, [A]; laut Agent [F] Abschnitte 4–5): Adam-SDE, ein Schritt = SDE-Zeit η², Rauschen ∝ η/√B; Wurzelregel. Behandelt nicht feste lr bei variablem B.
- **Compagnoni et al. (2025), ICLR, https://arxiv.org/abs/2411.15958** [S]: SDEs für SignSGD/AdamW; adaptive Verfahren skalieren linear mit dem Rauschen.
- **Granziol, Zohren, Roberts (2022), JMLR 23, https://arxiv.org/abs/2006.09092** [A]: maximale stabile lr ∝ √B für Adam (Stabilitätsgrenze, keine Festlegungszeit).
- **Jastrzebski et al. (2020), ICLR, https://arxiv.org/abs/2002.09572** [A]: Break-even-Punkt (SGD) früher bei großer lr/kleinem B — entgegengesetzte B-Richtung, kein Exponent.
- Frankle et al. 2020 (LMC), Achille et al. 2019, Kleinman et al. 2024 (schon oben): laut Agent keine Batchgrößen-Abhängigkeit des Einsetzens berichtet.
- **Gromov (2023)**, *A Simple and Interpretable Model of Grokking Modular Arithmetic Tasks* [S]: bei großem Batch verstärkt das Training die „Fourier-Lücke“ des Anfangsgradienten; kein Festlegungszeitpunkt.

**Einschränkung des Neuheitsanspruchs:** Eine Messung der Festlegungszeit ∝ (N/B)^0.5 bei fester lr wurde nicht gefunden (vorläufig, „nicht gefunden“). Die √B-Skalierung der Drift normierter Updates ist bekannt (Li et al. 2024); unser Beitrag wäre höchstens die Messung an einer frühen Merkmalsfestlegung und die teilweise Abweichung bei doppelter lr (EXP-109, Bestätigung N54b läuft). Für die menschliche Prüfung: Li et al. 2024 und Malladi et al. 2022 im Volltext.

**Nachtrag Sitzung 47 (05:48): nicht monotone lr-Abhängigkeit der Festlegung bei kleinem Batch (EXP-110, Pilot).** Agent-Suche 29.09.: nicht gefunden. Nächstverwandt: Li et al. 2024 (s. o.; Thm. 3 ε_opt(B) mit Maximum bei B_noise, für kleines B ∝ √B; Ziel Verlustabnahme je Schritt), **Chen, Kunin, Yamamura, Ganguli (2023), *Stochastic Collapse*, NeurIPS, https://arxiv.org/abs/2306.04251** [A] (Rauschen macht invariante/symmetrische Mengen attraktiv), **Ziyin et al. (2024), ICML, https://arxiv.org/abs/2309.16932** [S], **Li, Wei, Ma (2019), NeurIPS, https://arxiv.org/abs/1907.04595** [A/S] (große Anfangs-lr verzögert das Lernen memorierbarer Muster). Keine davon misst Festlegungszeiten oder grokkende Netze. Für die menschliche Prüfung: Li et al. 2024 Thm. 3 und Gl. 14 im PDF.

**Nachtrag Sitzung 49 (2026-09-29, 10:46 Berlin): Suche zu „Verlust auf den Operanden vs. nur auf der Antwort“ (Anhang K, EXP-113).** Suchbegriffe (WebSearch): „grokking modular addition next-token loss on operands vs answer-only loss delays generalization“; „arXiv 2025 2026 "loss masking" arithmetic language model from scratch grokking prompt loss answer tokens memorization“; „transformer arithmetic "loss on all tokens" versus "loss only on the answer" generalization modular arithmetic memorize operands“. Nächstverwandte Treffer (nur Titel/Snippet [S], nicht gelesen): Principled Understanding of Generalization for Generative Transformer Models in Arithmetic Reasoning Tasks (ACL 2025, https://arxiv.org/html/2407.17963; Positionskodierung/Basis, nicht Verlustmaske); A Pre-Training Analogue of Grokking in Language Models (https://arxiv.org/pdf/2606.00230; verzögerte Generalisierung im LM-Pretraining); Making Hard Problems Easier with Custom Data Distributions and Loss Regularization (https://arxiv.org/pdf/2410.03569; Datenverteilung bei modularer Arithmetik); The Norm-Separation Delay Law of Grokking (https://arxiv.org/pdf/2603.13331). **Eine Messung, wie der Verlust auf den Operanden-Positionen das Grokking verzögert und die Datensteuerung der Frequenzen schwächt, haben wir nicht gefunden** (nur „nicht gefunden“, nicht „neu“; der in Sitzung 48 genannte Blogbeitrag zu D3 bleibt die nächste Quelle). Menschliche Prüfung nötig; Volltexte nicht gelesen.


**Nachtrag Sitzung 50 (2026-09-29, ≈ 11:35 Berlin, geschätzt; 11:39 gemessen danach): Nachsuche vor der Fertigstellung der Kurzfassung.** Suchbegriffe (WebSearch): „grokking training set composition determines which Fourier frequencies learned arXiv 2026“; „"data selection" OR "training split" steer Fourier features modular addition transformer September 2026“; „LeDoux 2026 grokking data order fundamental frequency follow-up citing arXiv 2603.25047“. Kein Treffer, der die Steuerung vorgegebener Frequenzen über die Paarauswahl (K2) oder die frühe Festlegung (K4/R6/R8) vorwegnimmt (nur „nicht gefunden“). Neu gefunden und relevant für die Grenzen: **Khanh 2026, „At-Grok Is Not Converged: A Measurement-Validity Audit for Grokking Representation Metrics“** (arXiv 2607.06639, 07.07.2026) [A, Abstract über WebFetch]: Auf modularer Arithmetik komprimiert die Einbettung noch zehntausende Schritte nach der Generalisierung weiter; die effektive Rangzahl am Grokking-Punkt überschätzt den konvergierten Wert (MLP ×3–5, Transformer ×1.3–1.5). **Bezug zu uns:** Unser Δ_pow wird bei festem Schritt 2000 gelesen (oft um den Grokking-Punkt), Endmodelle bei 2000–12 000 Schritten; dass Repräsentationsmaße danach weiter wandern, ist ein berechtigter Einwand gegen „Endzustand“-Lesarten (bei uns: r0 driftet in EXP-102 von 8.0 bei 2000 auf 10.5 bei 30 000 Schritten, Exploration). Im Paper als Grenze (§7 (v)) zitiert. Weitere Treffer schon in dieser Datei: 2609.17571, 2609.15047, 2607.07066, 2602.16849. Neu, nicht gelesen [S]: „A Systematic Empirical Study of Grokking: Depth, Architecture, Activation, and Regularization“ (arXiv 2603.25009).

*Nachsuche Sitzung 51 (2026-09-29, ≈ 14:40 Berlin), LM-Leiter (LM1/EXP-116/EXP-117):* WebSearch „small language model trained from scratch arithmetic facts subset determines Fourier features number token embeddings 2026“ und „tied vs untied embeddings Fourier structure number tokens modular addition transformer unembedding“. Treffer bereits bekannt: Zhou, Fu, Sharan, Jia 2024 (arXiv 2406.03445; von Grund auf trainierte Additionsmodelle nutzen nur niederfrequente Merkmale, vortrainierte Embeddings retten sie), Fu et al. 2026 (2604.20817), 2609.17571, 2607.07066, 2606.17399, 2505.15624. Neu gesichtet [A]: Smithline & Mascioli 2026, *Sparsity Moves Computation: How FFN Architecture Reshapes Attention in Small Transformers* (arXiv 2605.09403): Architektur (dicht/GLU/MoE) verschiebt die Fourier-Struktur zwischen FFN und Attention; **keine Datenauswahl** → schränkt K2 und die LM-Leiter nicht ein. Keine Arbeit gefunden, die in einem von Grund auf trainierten LM über die *Auswahl der Rechenfakten* vorgegebene Frequenzen in den Zahl-Embeddings steuert (nach unserer Suche, vorläufig).

## Nachsuche Sitzung 54 (2026-09-29, ≈ 23:35 Berlin): Datenstruktur und Plateau nach der Memorisation im LM (Anlass EXP-119)

**Suchbegriffe (WebSearch):** „language model arithmetic facts held-out generalization depends on which facts are in training set structure grokking plateau random subset“; „arXiv 2025 2026 training data selection structured subset modular addition language model generalization memorization plateau Fourier“; „"grokking" language model trained from scratch on text with arithmetic facts, data distribution determines whether held-out facts generalize, memorization without generalization random facts“. Treffer überwiegend schon hier geführt (2606.00230, 2609.17571, 2603.23784, 2602.16849, 2607.05104) oder in [[paper/lit_grokking_speed_2026-09-27]] (2502.01774).

- **Wang, Yue, Su, Sun 2024, „Grokked Transformers are Implicit Reasoners“, NeurIPS 2024, https://arxiv.org/abs/2405.15071** (Volltext §3.2 gelesen): „critical data 'distribution', not size, may be the actual deciding factor behind grokking and generalization“; die Grokking-Geschwindigkeit korreliert mit dem Verhältnis abgeleiteter zu atomaren Fakten und hängt nicht von der Datenmenge ab. **Abgrenzung:** Dort ändert sich der *Anteil einer Faktenart* (Komposition), bei uns bei gleicher Größe, gleicher Wiederholung und gleicher Aufgabe nur *welche* Paare gewählt werden (Maskenspektrum); gemessen werden Frequenzen und Lernzeit. **Einschränkung unseres Anspruchs:** Die allgemeine Aussage „Verteilung statt Menge bestimmt das Grokking-Tempo“ ist bekannt und muss bei R5/EXP-119 zitiert werden; nach unserer Suche vom 29.09. nicht gefunden: dass bei gleicher Menge die spektrale Struktur der Paarauswahl entscheidet, ob ein kleines LM nach dem Memorisieren sofort generalisiert oder auf einem Plateau bleibt (EXP-119 ist aber nur eine Exploration mit 2 Seeds).

**Nachsuche Sitzung 54 (≈ 23:42): Kommutativität als Zwischenstufe.** Suchbegriff: „grokking modular addition commutativity intermediate stage model learns a+b=b+a before generalizing symmetric pairs test accuracy plateau“. Gefunden: Kommutativität wird als Abkürzung zum Memorisieren behandelt, die man durch das Datendesign ausschließt (z. B. Grokking of Diffusion Models: Case Study on Modular Addition, https://arxiv.org/abs/2604.17673, nur Suchzusammenfassung gelesen, Volltext nicht geprüft); Nanda et al. (2023) beschreiben einen glatten Übergang von Memorisation zu Generalisierung. Nach dieser Suche nicht gefunden: eine Messung, dass das Plateau eines kleinen LM auf einem Zufallssplit vollständig aus Kommutativitäts-Nachschlagen besteht (EXP-119 Nachtrag 1, post hoc, 2 Läufe). Vorläufig; vor einer Aussage im Haupttext gezielter suchen.

**Nachsuche Sitzung 54 (30.09., ≈ 00:04): Kommutativität vor dem Grokking (Anlass EXP-122).** Suchbegriff: „grokking test accuracy before generalization explained by commutative pairs (b,a) in training set symmetric counterpart modular addition transformer“. Nächstverwandt (nur Suchzusammenfassungen gelesen, Volltexte nicht geprüft): **Controlling Grokking with Nonlinearity and Data Symmetry**, https://arxiv.org/abs/2411.05353 (entfernt die Kommutativitäts-Symmetrie durch j ≥ i und beobachtet schlechtere Endgenauigkeit); **Acceleration of Grokking … via Kolmogorov–Arnold Representation**, https://arxiv.org/abs/2405.16658 (kommutative Datenaugmentation beschleunigt Grokking); Exploring Grokking, https://arxiv.org/abs/2412.10898; The Geometric Inductive Bias of Grokking, https://arxiv.org/abs/2603.05228 (Transformer hat mehr Freiheitsgrade als die Symmetrie verlangt). **Einordnung:** Dass Kommutativität beim Grokking eine Rolle spielt und sich per Augmentation nutzen lässt, ist bekannt. Nach dieser Suche nicht gefunden: die Messung, dass die Test-Genauigkeit auf dem Plateau vor dem Grokking fast nur auf Paaren mit trainiertem Tauschpartner liegt (EXP-122, 4 Läufe; im LM EXP-119, 2 Läufe). Vorläufig; vor einer Aussage Volltexte (v. a. 2411.05353, Nanda et al. 2023) prüfen.

**Nachsuche Sitzung 55 (2026-09-30, ≈ 00:55 Berlin): Kommutativität vor dem Grokking, Volltexte (Anlass EXP-122/123).** Suchbegriffe: „grokking commutativity test accuracy mirrored pair“; „grokking symmetric pairs (b,a) training set modular addition test accuracy before grokking“; „modular addition grokking commutativity learned first two-stage generalization“; „grokking plateau commutativity intermediate test accuracy“; „language model arithmetic facts commutativity generalization held-out facts plateau“; „grokking training set selection symmetric closure commutative pairs shortens time to generalization modular arithmetic“; „"commutativity" grokking "memorization" test accuracy transposed pairs transformer random split“; „"transpose effect" grokking modular arithmetic split unordered pairs“.
- **He, Wang, Chen, Yang 2026**, On the Mechanism and Dynamics of Modular Addition: Fourier Features, Lottery Ticket, and Grokking, https://arxiv.org/abs/2602.16849 (§2, §3.3, Fig. 10 / App. A.1; HTML geprüft; Präzisierung Sitzung 55 nach Prüfung: die Aufteilung „Tauschpartner richtig, echte ungesehene Paare nicht“ steht bei Fig. 10 zum Ende der Memorisation, §3.3 behandelt die Reihenfolge *innerhalb* der Trainingsdaten, zuerst beidseitig trainierte Paare): Zweischicht-Netz mit Eingabe h_x + h_y; beim Grokking mit Zufallssplit werden die Trainingsdaten und ihre Tauschpartner in der Testmenge richtig, echte ungesehene Paare nicht; „Common-to-Rare“; Memorisation + zwei Generalisierungsphasen. **Schränkt N57 ein:** Das Muster ist für Netze mit eingebauter Kommutativität bekannt. Abgrenzung: Unser Transformer (Positionseinbettung) muss die Kommutativität lernen; die Verkürzung der zweiten Stufe durch die Paarauswahl und das LM-Plateau sind dort nicht untersucht. **Zitieren, falls N57 ins Paper kommt.**
- **Salah & Yevick 2024**, https://arxiv.org/abs/2411.05353 (§3.5, Volltext): Entfernen der Kommutativität (j ≥ i) senkt die Endgenauigkeit (P = 53: 0.85); MLP; keine Aufteilung nach Tauschpaar.
- **Park, Kim, Kim 2024**, https://arxiv.org/abs/2405.16658 (§4.2, Tab. 1): Tauschpaar-Augmentation verkürzt Grokking bei x1 + x2 (27 167 → 10 171 Schritte), nicht einheitlich. Datenauswahl über Tauschpaare, nicht über das Paarspektrum.
- Power et al. 2022 (§3.1): symmetrische Operationen brauchen weniger Daten (Transformer kann die Positionseinbettung ignorieren). Nanda et al. 2023, Liu et al. 2022, Chughtai et al. 2023: nichts zur Aufteilung nach Tauschpaar (Liu: Modell kommutativ gebaut).
- Weitere: https://arxiv.org/abs/2603.01968 (Stufe „Symmetry Acquisition“, nur global gemessen); Howe 2026, https://arxiv.org/abs/2607.12735 (kontrastiver Prior auf Tauschpaaren beschleunigt, Trainings-Prior statt Datenauswahl); https://arxiv.org/abs/2411.16260 (GPT-2 auf synthetischer Arithmetik generalisiert Kommutativität, kein Plateau); GitHub marshallchen99/grokking-mechinterp („transpose effect“ nach dem Training, nicht begutachtet). Die letzten vier nur über den Agenten-Bericht (Zusammenfassungen), nicht selbst im Volltext geprüft.

**Nachsuche Sitzung 56 (30.09., 04:33–04:35 Berlin gemessen; Anlass EXP-113/116, Verlustmodus und Rechenanteil im LM).** Suchbegriffe: „language model trained from scratch arithmetic facts mixed with natural text Fourier features number embeddings which facts training data“, „arXiv 2026 small language model pretraining synthetic arithmetic data fraction number token embedding periodic structure emergence“, „next-token loss on operands vs answer-only loss arithmetic generalization memorization transformer grokking delay“.
- **Lin, Zhang, Xu 2025**, *Reasoning Bias of Next Token Prediction Training*, https://arxiv.org/abs/2502.02007 [A]: Training auf allen Tokens (NTP) generalisiert in Reasoning-Benchmarks besser als nur auf den Antwort-Tokens (CTP), erklärt über regularisierendes Rauschen; CTP besser fürs Feintuning. **Gegenläufig zu unserem Befund** (Verlust auf allen Positionen verzögert Grokking > ×10, EXP-102; im LM nur Auswendiglernen, EXP-113 all). Abgrenzung: bei uns stammen die Operanden aus einer festen Faktentabelle und sind nur auswendig vorhersagbar. Zitiert in Anhang K. Volltext nicht gelesen.
- **Fu et al. 2026** (2604.20817, schon zitiert), Abstract erneut gelesen: Zahlmerkmale entstehen aus Text-Zahl-Kookkurrenz oder Mehr-Token-Addition; keine kontrollierte Beimischung von Rechensätzen in wechselndem Anteil und keine Auswahl der Fakten. Schränkt die LM-Leiter (EXP-113/116, LM3) nach dieser Suche nicht ein.
- Sonst nichts gefunden, das beantwortet, ob die Faktenauswahl die Zahl-Frequenzen eines von Grund auf trainierten LM bei wenigen Prozent Rechentext steuert (vorläufig, nur Abstracts und Suchtreffer).

**Nachsuche Sitzung 57 (2026-09-30, 06:12 Berlin gemessen), R12-Umfeld (Geschwindigkeit auf anderen Aufgaben):** WebSearch „grokking faster training set selection modular multiplication Fourier 2026 arXiv“ und „data selection accelerates grokking structured training subset grokking speedup curriculum 2026“. Bekannt und schon eingeordnet: Howe 2026a/b (2607.12735, 2607.04333), He et al. 2026a (2602.16849), Yang 2026 (2609.17571), Hidajat et al. 2026 (2605.15787), Discrete-Log Clock (2606.17399). **Neu gesichtet:** Hancock (2026), *The Effects of Online Batch Selection on Grokking* (April 2026; nur GitHub-README gelesen, https://github.com/PJHancock/Grokking, Paper als Google-Drive-Link, kein arXiv gefunden) [S]: Subtraktion mod 96 und MNIST, Online-Auswahl der Minibatches aus der festen Trainingsmenge (RHO-Loss, DivBS, bayessch) ändert die Grokking-Dynamik kaum, GrokFast beschleunigt stark. **Abgrenzung:** Dort wird innerhalb einer festen Trainingsmenge umgewichtet (welche Beispiele wann), bei uns wird festgelegt, *welche* Paare überhaupt in der Trainingsmenge liegen (Full-Batch). Schränkt R5/R12 nicht ein; passt zu L0 (Reihenfolge/Auswahl innerhalb der Menge wirkt schwach, die Menge wirkt). Menschliche Prüfung: PDF lesen, falls zitiert wird.

**Nachsuche Sitzung 58 (30.09., 09:22), vortrainiertes LM nachtrainieren (EXP-127, N58):** WebSearch „fine-tuning pretrained language model modular addition Fourier features number token embeddings training data selection frequencies“, „arXiv 2026 pretrained LLM fine-tuned modular arithmetic which Fourier frequencies emerge data composition Pythia“, „fine-tuning GPT-2 OR Pythia modular addition Fourier embeddings grokking pretrained initialization frequencies selected“. Neu gesichtet [S]: **FoNE** (arXiv 2502.09741): Pythia lernt Fourier-Zahlmerkmale schrittweise im Vortraining; Vorschlag fester Fourier-Zahleinbettungen – keine Datenauswahl beim Nachtrainieren. Gomezjurado Gonzalez 2026 (arXiv 2604.13082; Abstract gelesen): Collatz-Grokking von Grund auf, keine Fourier-Messung der Zahleinbettungen. Bereits eingeordnet: Zhou, Fu, Sharan, Jia 2024 (vortrainierte Fourier-Merkmale, Nachtraining auf Addition; Beispielauswahl nicht variiert), GrokTransfer (2504.13292), Fu et al. 2026. **Schränkt ein:** Vortrainierte Fourier-Zahlmerkmale und ihre Nutzung beim Nachtrainieren sind bekannt. **Nicht gefunden (vorläufig):** Steuerung der beim Nachtrainieren hinzukommenden Frequenzen durch die Auswahl der Fakten. Eigene Basismessung: Pythia-160M/GPT-2 tragen über 0–112 vor allem Frequenzen 1–3 und 11/23/45 (≈ Perioden 10/5/2.5), passend zu Zhou et al. 2024.

**Nachsuche Sitzung 59 (30.09., ≈ 12:05 Berlin), Kernaussagen K2/K4 vor dem Paper-Ziel 01.10.:** WebSearch „grokking training set composition Fourier frequencies modular arithmetic arXiv September 2026“, „arXiv 2609 grokking data selection which frequencies learned modular addition transformer“, „language model number embeddings Fourier features fine-tuning data selection 2026“, „critical period data switch early training features persist transformer grokking 2026 arXiv lock-in“. Neu gesichtet (Abstract [A]): **Tang, Wang, García-Redondo, Monod 2026** (arXiv 2605.06352, *Topological Signatures of Grokking*: persistente Homologie der Einbettung trennt Generalisierung von Memorisation; keine Datenauswahl, keine Festlegung → schränkt nichts ein); **Exoo, Bietti, Sous 2026** (arXiv 2605.31497, *Assign and Add*: Komposition Variablenzuweisung + modulare Addition, disjunkte Trainingsteilmengen für Generalisierung auf ungesehene Kombinationen; keine Frequenzsteuerung → schränkt nichts ein); **Khanh, Hoa, Trung, Duc 2026** (arXiv 2604.13123, *Spectral Entropy Collapse …*: Kollaps der spektralen Entropie sagt Grokking voraus, Eingriff durch Repräsentationsmischung verzögert ihn; keine Datenauswahl, kein Datenwechsel → schränkt nichts ein; nicht zu verwechseln mit Khanh 2026, 2607.06628). Alle übrigen Treffer (2602.16849, 2603.23784, 2603.25009, 2604.17673, 2605.04396, 2605.15787, 2605.20441, 2606.17399, 2609.19000, 2609.26679, FoNE, Zhou et al. 2024) sind hier oder in [[NOVEL_DIRECTIONS]] schon eingeordnet. Ergebnis: Einordnung „nach unserer Suche nicht gefunden (vorläufig)“ für K2 und K4 unverändert.

**Nachsuche Sitzung 60 (30.09., Anlass EXP-129 „Uhr des Faktenlernens“; Anfragen: „grokking modular arithmetic mixed with natural language pretraining data fraction of arithmetic tokens“, „synthetic facts mixed into pretraining corpus how many exposures needed learning onset steps versus repetitions“):**
- Zucchet, Bornschein, Chan, Lampinen, Pascanu, De 2025, *How do language models learn facts? Dynamics, curricula and hallucinations*, https://arxiv.org/abs/2503.21676 (Abstract gelesen): Faktenlernen im LM in drei Phasen mit Plateau; die Datenverteilung bestimmt die Dynamik. Abgrenzung: einzelne Fakten (Erinnern), nicht eine Rechenregel mit zurückgehaltenen Fakten und nicht die Frequenzwahl der Zahl-Einbettung. Schränkt K2 nicht ein; relevant für die Plateau-Beobachtungen in Anhang K (Zitierkandidat).
- „Facts in Stats“ (https://arxiv.org/abs/2510.16096, nur Suchtreffer, nicht gelesen): Vielfalt der Vortrainingsdaten und Generalisierung bei Fakten. Noch einzuordnen.
- Nichts gefunden, das die Steuerung der Zahlmerkmale bei wenigen Prozent Rechen-Tokens im gemischten Text prüft (vorläufig, nach unserer Suche vom 30.09.).
- **Nachsuche S60, Teil 2 (N59, Anfrage „language model plateau length before learning depends on training steps not number of exposures per example arithmetic mixed pretraining“, mehrere Umformulierungen):** Zucchet, d'Angelo, Lampinen, Chan 2025, *The emergence of sparse attention: impact of data distribution and benefits of repetition*, https://arxiv.org/abs/2505.17863 (NeurIPS 2025; Abstract gelesen): Der Zeitpunkt der Emergenz folgt Potenzgesetzen in Aufgabenstruktur, Architektur und Optimierer; **Wiederholung kann die Emergenz stark beschleunigen**. Einordnung für N59/EXP-129: gegenläufige Erwartung zu unserer Beobachtung (K = 8 mit ≈ 3× mehr Wiederholungen nur ×1.3 früher) – Zitierpflicht, falls N59 berichtet wird; schränkt K2 nicht ein. Gomezjurado Gonzalez 2026 (https://arxiv.org/abs/2604.13082, Abstract): verzögerte Generalisierung bei Arithmetik (Collatz, Zahlbasen), kein gemischter Text, keine Datenauswahl → nicht einschränkend.

## Nachsuche Sitzung 62 (30.09.2026, ≈ 20:10 Berlin): Nachtrainieren vortrainierter Modelle und Wiederverwendung von Merkmalen (für EXP-127/130/131/133)

- **Suchbegriffe (WebSearch):** „pretrained language model reinitialize number token embeddings fine-tune modular addition Fourier features emerge“; „"re-initialized embeddings" pretrained transformer fine-tuning arithmetic …“; „fine-tuning reuses pretrained features regardless of fine-tuning data "feature reuse" transfer learning what is being transferred“; „Neyshabur Sedghi Zhang 2020 "What is being transferred in transfer learning" arXiv“.
- **Zhou, Fu, Sharan, Jia 2024** ([arXiv 2406.03445](https://arxiv.org/abs/2406.03445)), schon zitiert: vortrainierte LMs rechnen Addition mit vortrainierten Fourier-Merkmalen (tiefe Frequenzen für die Größe, hohe für Modulo-Anteile wie gerade/ungerade); vortrainierte Einbettungen in ein Modell von Grund auf → volle Genauigkeit. *Abgrenzung:* Dort wird die Auswahl der Trainingsbeispiele nicht variiert; unser EXP-130 zeigt für mod 113 (nicht dezimal ausgerichtet), dass die Nutzung {1, 2, 11, 23, 56} von der Faktenauswahl unabhängig ist. Schränkt unseren Anspruch nicht ein, stützt die Lesart „Wiederverwendung“.
- **Neyshabur, Sedghi, Zhang 2020** ([arXiv 2008.11687](https://arxiv.org/abs/2008.11687), NeurIPS 2020 laut Suchergebnis; nur Abstract/Snippet gelesen): trennt beim Transferlernen (Bilder) Merkmals-Wiederverwendung von gelernten Niedrig-Statistiken. *Abgrenzung:* allgemeiner Rahmen für „vortrainierte Merkmale werden wiederverwendet“, keine Fourier-/Frequenzwahl, keine Datenauswahl. Als allgemeine Einordnung zitierbar (Venue vor dem Zitieren am arXiv-Kommentar prüfen).
- Kalra et al. 2024 „On Initializing Transformers with Pre-trained Embeddings“ ([arXiv 2407.12514](https://arxiv.org/abs/2407.12514), nur Snippet): vortrainierte gegen zufällige Einbettungen beim Training von Grund auf; nicht unsere Frage.
- **Einordnung (vorläufig):** Dass vortrainierte Modelle vorhandene (Fourier-)Zahlmerkmale wiederverwenden, ist bekannt. Dass die Auswahl der Nachtrainingsfakten daran nichts ändert (Energie, Nutzung, Schichten) und ob das an den Zahlzeilen oder am Rumpf liegt (EXP-133), haben wir nach unserer Suche vom 30.09.2026 nicht gefunden.

**Nachsuche Sitzung 63 (30.09., 22:05 gemessen), Umfeld L0b (Menge gegen Reihenfolge, lange Epochen):** WebSearch „"The Order Is The Message" LeDoux grokking data ordering Fourier frequency“ und „grokking modular arithmetic data order versus training set composition frequency selection minibatch 2026 arXiv“; Treffer (2603.25047, 2607.05104, 2608.25813, 2406.02550, 2310.03789, 2501.04697, 2604.17673) alle schon geführt oder ohne Bezug. **Vorwärtszitate von LeDoux 2026** über die Semantic-Scholar-API (`/graph/v1/paper/arXiv:2603.25047/citations`, 30.09.): genau ein zitierendes Werk, Sweeney 2026 (2606.29554, oben eingeordnet). Damit bleibt offener Punkt 5 (Vorwärtszitate) für LeDoux erledigt; nach dieser Suche hat niemand Menge und Reihenfolge im Konflikt gemessen. Einordnung bleibt „nach unserer Suche nicht gefunden“, nicht „neu“.

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

### Nachtrag Sitzung 29 (2026-09-27, 18:05 Berlin, gemessen): Init-Skala und Festlegungszeit (für EXP-040)

Suchbegriffe (WebSearch, 2026-09-27): „initialization scale critical period feature commitment time grokking embedding Adam“; „arXiv 2026 grokking data switch early training commitment Fourier features initialization scale“; „"initialization scale" feature learning time Adam linear versus exponential growth small initialization rich regime timescale“; „initialization scale shifts critical period timing neural network data switch first task persists steps“; „Adam sign-like updates linear feature growth small initialization time to escape scales with initialization magnitude“.
- **Khanh, Viet, Trung, Duc 2026**, *The Weight Norm Sets the Grokking Timescale: A Causal Delay Law* (arXiv 2606.13753, 2026-06-11; [A] Abstract per WebFetch). Eingriff: Gewichtsnorm auf Vielfache ρ eines kritischen Werts geklemmt; Grokking-Verzögerung ∝ exp(α ρ), α ≈ 7.5 über vier Moduli; Norm wirkt ≈ 19× stärker als die Lernrate (≈ 2×); LayerNorm hebt die Abhängigkeit auf. Keine Frequenzwahl, keine Festlegung nach Datenwechsel. *Einordnung:* schränkt K2/K4 nicht ein; **Kontext für EXP-040**: Eine größere W_E-Init (s = 2) kann das Grokking von „nur F“ verzögern (dort schon als Ausfallgrund „Zelle unklar“ geregelt); Beleg neben Kumar et al. 2023. Klemmen der Gesamtnorm ≠ unsere Skalierung nur des Nicht-Gleichanteils von W_E.
- **Das, Beneventano, Dey, McKinley, Poggio 2026**, *Do Deep Networks Forget Initialization? A Forgetting-Time View of Practical Inductive Bias* (arXiv 2605.29152, 2026-05-27; [A]). „Initialisierungsgedächtnis“: SGD mit kleiner Lernrate behält die Abhängigkeit von der Init-Skala, Adam-Familie löscht sie weitgehend (ResNet-9). Keine Aufgabe mit Frequenzen, kein Datenwechsel. *Einordnung:* Kontext zu H40 (unter Adam wirkt die Init-Skala vor allem früh); schränkt nichts ein.
- Nichts gefunden, das prüft, ob die Init-Skala das **Festlegungsfenster gegen einen Datenwechsel** verschiebt (H40). He et al. 2026a (2602.16849, schon zitiert) behandeln die Init-Lotterie ohne Datenwechsel. EXP-040 bleibt „nach unserer Suche nicht gefunden“ (vorläufig).

### Nachtrag Sitzung 29 (2026-09-27, 18:05 Berlin, gemessen): Init-Skala und Festlegungszeit (für EXP-040)

Suchbegriffe (WebSearch, 2026-09-27): „initialization scale critical period feature commitment time grokking embedding Adam“; „arXiv 2026 grokking data switch early training commitment Fourier features initialization scale“; „"initialization scale" feature learning time Adam linear versus exponential growth small initialization rich regime timescale“; „initialization scale shifts critical period timing neural network data switch first task persists steps“; „Adam sign-like updates linear feature growth small initialization time to escape scales with initialization magnitude“.
- **Khanh, Viet, Trung, Duc 2026**, *The Weight Norm Sets the Grokking Timescale: A Causal Delay Law* (arXiv 2606.13753, 2026-06-11; [A] Abstract per WebFetch). Eingriff: Gewichtsnorm auf Vielfache ρ eines kritischen Werts geklemmt; Grokking-Verzögerung ∝ exp(α ρ), α ≈ 7.5 über vier Moduli; Norm wirkt ≈ 19× stärker als die Lernrate (≈ 2×); LayerNorm hebt die Abhängigkeit auf. Keine Frequenzwahl, keine Festlegung nach Datenwechsel. *Einordnung:* schränkt K2/K4 nicht ein; **Kontext für EXP-040**: Eine größere W_E-Init (s = 2) kann das Grokking von „nur F“ verzögern (dort schon als Ausfallgrund „Zelle unklar“ geregelt); Beleg neben Kumar et al. 2023. Klemmen der Gesamtnorm ≠ unsere Skalierung nur des Nicht-Gleichanteils von W_E.
- **Das, Beneventano, Dey, McKinley, Poggio 2026**, *Do Deep Networks Forget Initialization? A Forgetting-Time View of Practical Inductive Bias* (arXiv 2605.29152, 2026-05-27; [A]). „Initialisierungsgedächtnis“: SGD mit kleiner Lernrate behält die Abhängigkeit von der Init-Skala, Adam-Familie löscht sie weitgehend (ResNet-9). Keine Aufgabe mit Frequenzen, kein Datenwechsel. *Einordnung:* Kontext zu H40 (unter Adam wirkt die Init-Skala vor allem früh); schränkt nichts ein.
- Nichts gefunden, das prüft, ob die Init-Skala das **Festlegungsfenster gegen einen Datenwechsel** verschiebt (H40). He et al. 2026a (2602.16849, schon zitiert) behandeln die Init-Lotterie ohne Datenwechsel. EXP-040 bleibt „nach unserer Suche nicht gefunden“ (vorläufig).

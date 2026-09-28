---
id: FINDINGS_DETAILS
status: laufend
datum: 2026-09-27
tags: [lab/synthese]
verwandt: ["[[FINDINGS]]", "[[LAB]]"]
---
# FINDINGS, Einzelheiten (Wortlaute, Belege, Programmgeschichte)

Zurück zu [[FINDINGS]] (einseitige Übersicht) · [[LAB]]. *Sitzung 24 (27.09., 12:59 Berlin): Dieser Text stand bis Sitzung 23 wortgleich in FINDINGS.md (Zeilen 10–250) und wurde nur verschoben,
damit FINDINGS nach Regel 15a eine Seite bleibt. Inhalt und Zahlen unverändert; einzige Ergänzung: Seed-Reservierung P2f (Nachtrag Sitzung 24).*

Zurück zu [[LAB]]. **Nachtrag Sitzung 21 (27.09., 04:46): P1 und P2 sind eingefroren** (Manifest 733e829, Seeds 1000–1049; [[confirm/P1_REGISTRATION_DRAFT|P1]], [[confirm/P2_REGISTRATION_DRAFT|P2]]). P2 misst jetzt das log-Loss-Verhältnis bei halber Dosis statt der Genauigkeit. P3-Pilot [[experiments/EXP-056-overlap-persistence/README|EXP-056]] läuft. **Nachtrag Sitzung 20: Pilotnacht mit neuen Läufen, siehe Abschnitt unten.** Nachtrag Sitzung 14: nur Vorbereitung und Nachrechnung gespeicherter Läufe, keine neuen Läufe, Kernaussagen unverändert. Stand 2026-09-26, Sitzung 13 (nach 48 angelegten Versuchen; Kernaussagen seit Sitzung 11 unverändert, keine neuen Läufe). „Neu“ heißt immer: nach unserer Suche vom
2026-09-26 nicht gefunden, vorläufig. **Alle Aussagen gelten bisher nur für eine Aufgabe (Addition mod 113) und im Kern eine
Architektur (1-Schicht-Transformer der Studie, AdamW, lr 1e-3, wd 1).** Einzelheiten: [[BEFUND-split-mechanismus]], [[BEFUND-festlegung]].

## Kurzfassung (Stand Sitzung 23, 27.09.; alle Aussagen: 1-Schicht-Transformer der Studie, AdamW, konstruierte Splits; Einzelheiten und Wortlaut in den Abschnitten darunter)

| | Aussage (kurz) | Beleg | Stand |
|---|---|---|---|
| **K2** | Konstruierte Trainingssplits steuern, welche Frequenzen W_E lernt: add 113, mul 113, add 97, D₅₉ | P1 (50 Seeds je Aufgabe) | bestätigt |
| **K2-Funktion** | Gleich große W_E-Schritte entlang der gesteuerten Frequenzen senken den Logit-Abstand stärker als entlang von Kontrollen: add 113, mul 113, add 97 | P2d, P2e | bestätigt; **folgt der Energie**, keine Nutzung darüber hinaus belegt (EXP-068) |
| **K4 / K4b** | Schon 25 Schritte auf dem ersten Split prägen das Endspektrum nach einem Wechsel; ein gelöschtes Adam-Momentum wirkt wie weniger Vorschritte | P3, N28 | bestätigt |
| **K4c** | Wechsel nach 25 Schritten: Endmodell auf die neuen Frequenzen angewiesen; nach 50: auf die alten | N29 | bestätigt (Ablationskontrast) |
| **K4d** | Ein Reset der Attention (Gewichte + AdamW-Zustand) beim Wechsel nach 50 Schritten senkt diesen Kontrast stark, stärker als der geprüfte MLP-Reset; beschreibend danach auf die neuen angewiesen | N29b | bestätigt (Reset-Empfindlichkeit, kein Speicherort) |
| **K4e** | Der Reset des Wertepfads (W_V, W_O) wirkt stärker als der gleich große Reset des Musters (W_Q, W_K); danach beide Mengen genutzt | N29c | bestätigt (Reset-Empfindlichkeit) |
| **Offen** | *Warum* entsteht die Festlegung gerade zwischen 25 und 50 Schritten, wenn die OV-Ausrichtung gleichmäßig steigt (EXP-070)? Gilt K2-Funktion bei D₅₉? Hängt die Festlegungszeit an der aufsummierten Lernrate (EXP-039 unklar)? | EXP-069, EXP-070, BACKLOG | laufend |

## BESTÄTIGT (Sitzung 23, 27.09., 12:25 Berlin; Wortlaut nach Codex 12:27): N29c, Wertepfad-Reset stärker als Muster-Reset #befund/positiv

**Kernaussage K4e** (Wortlaut nach Codex-Prüfung der Schlussfolgerung): *Bei Addition mod 113 im Protokoll „50 Schritte auf A, Wechsel auf paar-disjunktes B, 4000 weitere Schritte“ senkte das Zurücksetzen von
W_V und W_O auf die Init zusammen mit dem Löschen ihres AdamW-Zustands den registrierten W_E-Ablationskontrast gegenüber keinem Reset um 0.850 [0.685, 0.998] und gegenüber dem gleich großen Reset von W_Q
und W_K um 0.752 [0.596, 0.897] (20 gepaarte Seeds; Holm-p 2.1·10⁻⁴ bzw. 1.9·10⁻⁵; 17/20 generalisiert). Das zeigt stärkere Reset-Empfindlichkeit für diesen VO-Eingriff als für den geprüften QK-Eingriff,
nicht einen Speicherort oder dass der Wertepfad mechanistisch „mehr trägt“: Gewichte und Optimiererzustand wurden gemeinsam zurückgesetzt, und die Eingriffe sind nur nach Parameterzahl, nicht nach
funktioneller Störung oder Trainingsdynamik angeglichen.* Beschreibend: R nach VO-Reset −0.04 (beide Mengen genutzt), nach QK-Reset 0.72, normal 0.81.
Belege: [[confirm/N29c_REGISTRATION|Registrierung + Ergebnis]], Manifest 3c9cb63, 120 gebundene Läufe; Pilot [[experiments/EXP-069-attention-part/README|EXP-069]]. Zeitliche Erklärung offen ([[experiments/EXP-070-ov-alignment/README|EXP-070]]).

## BESTÄTIGT (Sitzung 23, 27.09., 11:31 Berlin; Wortlaut nach Codex 11:53): N29b, Reset der Attention beim Wechsel senkt den Ablationskontrast #befund/positiv

**Kernaussage K4d** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, Sitzung 23; ersetzt den vorläufigen Wortlaut darunter): *Bei Addition mod 113 im Protokoll „50 Schritte auf A, Wechsel auf paar-disjunktes B, 4000 weitere Schritte“ senkte das Zurücksetzen von W_Q, W_K, W_V, W_O auf die Init zusammen mit dem Löschen ihres AdamW-Zustands den registrierten W_E-Ablationskontrast um 1.49 [1.36, 1.61] gegenüber keinem Reset und um 1.42 [1.28, 1.56] gegenüber dem geprüften MLP-Reset (20 gepaarte Seeds, Holm-p 4.7·10⁻¹², 19/20 generalisiert). Nach dem Reset lag R beschreibend bei −0.63 [−0.73, −0.52], vereinbar mit größerer Empfindlichkeit gegen das Entfernen der neuen als der alten Frequenzen. Das zeigt Reset-Empfindlichkeit, nicht, dass die frühe Frequenzinformation in der Attention gespeichert ist, und nicht, welcher Teil des zusammengesetzten Eingriffs (Gewichte, Optimiererzustand, Normen) wirkt.*
**Grenzen (Codex, übernommen):** Gewichte und AdamW-Zustand werden gemeinsam zurückgesetzt (Plastizität/effektive Lernrate nicht getrennt); der Reset ändert auch die Normen von QK-Logits und OV-Ausgabe; die MLP-Kontrolle hat doppelt so viele Parameter und ist weder nach Verschiebung noch nach Ausgabestoß oder Dynamik angeglichen; H2 zeigt nur „stärker als dieser MLP-Reset“, nicht „MLP-Reset wirkungslos“. EXP-069 (Wertepfad) und EXP-070 (kein Sprung der OV-Ausrichtung) sind Piloten bzw. Exploration.
*Vorläufiger Wortlaut (vor der Codex-Prüfung, zur Nachvollziehbarkeit belassen):* *Bei Addition mod 113 und einem Wechsel zwischen paar-disjunkten konstruierten Splits nach 50 Schritten (4000 weitere Schritte, 20 frische
Seeds, Mittel über beide Richtungen) senkte das Zurücksetzen der Attention-Parameter (W_Q, W_K, W_V, W_O auf die Init, ihr AdamW-Zustand gelöscht) den Ablationskontrast R = acc(ohne neue) − acc(ohne alte)
um 1.49 [1.36, 1.61] gegenüber dem normalen Wechsel und um 1.42 [1.28, 1.56] gegenüber einem Reset von W_in, W_out (doppelte Parameterzahl) (je 20/20, Holm-p 5·10⁻¹²). Beschreibend lag R nach dem
Attention-Reset bei −0.63 [−0.73, −0.52] (40/40 Richtungen < 0), nach MLP-Reset bei 0.79, normal bei 0.86.*
Belege: [[confirm/N29b_REGISTRATION|Registrierung + Ergebnis]], Manifest db31564, 120 gebundene Läufe; Pilot [[experiments/EXP-067-exclusion-part/README|EXP-067]].
**Grenzen:** Reset auf die Init entfernt alles Gelernte der Attention (Reset-Empfindlichkeit, kein Mechanismusnachweis); ein Zeitpunkt; Reset-Größe nur über die Parameterzahl kontrolliert; Ablation folgt der Energie (EXP-068).
Einordnung: [[NOVEL_DIRECTIONS]] N32, nach unserer Suche vom 27.09. nicht gefunden (vorläufig); verwandt: Plastizitätsverlust und Attention-Entropie (Lyle et al.).

## BESTÄTIGT (Sitzung 23, 27.09., 10:44 Berlin): P2e, P2d-Befund auch bei mul 113 und add 97 #befund/positiv

**Kernaussage K2-Funktion verallgemeinert (P2e)** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, Sitzung 23): *Nach 8000 Trainingsschritten senkte ein einseitiger W_E-Schritt der Norm
0.02·‖X‖_F (X = Zahlenzeilen in Gruppenordnung) entlang der amplitudengewichteten Richtung der gesteuerten Zielfrequenzen den Logit-Abstand (richtige gegen beste falsche Klasse) auf Paaren außerhalb
beider Splits stärker als das Mittel von vier vorab festgelegten Kontrollmengen aus je 5 Frequenzen. Gemittelt über die zwei Arme je Seed: mul 113 0.291 [0.268, 0.308], add 97 0.294 [0.275, 0.312]
(getrennte Seed-Bootstrap-KI, je 20/20 positive Seed-Mittel, Holm über beide Aufgaben).* Diese aufgaben-, dosis- und kontrollspezifische Empfindlichkeit trennt Frequenzidentität nicht von gelernter
Amplitude und Ausrichtung und **belegt deshalb keine Nutzung über die Energie hinaus**.
Belege: [[confirm/P2e_REGISTRATION|Registrierung + Ergebnis]], Manifest 3c484ef, 80 gebundene Läufe; Pilot [[experiments/EXP-066-p2d-other-tasks/README|EXP-066]].
**Grenzen (Codex, übernommen):** Einheit = Seed (Mittel über zwei unabhängig trainierte Arme); Kontrollen zufällig aus einem eingeschränkten Pool, nicht energiegleich; mul 113 in 19/20 Seeds in beiden Armen
generalisiert (primär alle 20); Vergleich mit P2d (add 113) nur qualitativ (4000 statt 8000 Schritte, anderer Seed-Block); eine Architektur, zwei zyklische Aufgaben, eine Dosis. D₅₉ steht aus ([[BACKLOG]]).

## BESTÄTIGT (Sitzung 23, 27.09., 10:17 Berlin): N29, Ablationskontrast kehrt sich zwischen Wechsel bei t = 25 und t = 50 um #befund/positiv

**Kernaussage K4c** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, Sitzung 23, selbst nachgerechnet): *Bei Addition mod 113 (einschichtiger Transformer), nach einem Wechsel zwischen paar-disjunkten
konstruierten Splits (beide Richtungen) und 4000 weiteren Schritten, hing der Genauigkeitsverlust durch vollständiges Entfernen der Zielfrequenzen aus W_E[:113] vom Wechselzeitpunkt ab.
Gemittelt über beide Richtungen je Seed (20 frische Seeds) kostete nach einem Wechsel bei t = 50 das Entfernen der **alten** Ziele 0.903 mehr Testgenauigkeit als das der neuen (95-%-KI 0.846–0.953;
20/20 Seed-Mittel > 0.3), nach einem Wechsel bei t = 25 das Entfernen der **neuen** 0.603 mehr (0.498–0.700; 17/20 > 0.3). Die beiden Zeitpunkte schließen eine Umkehrung dieses Ablationskontrasts ein;
eine netzweite oder unumkehrbare funktionale Festlegung ist damit nicht gezeigt.*
Belege: [[confirm/N29_REGISTRATION|Registrierung + Ergebnis]], Manifest 087e042, 80 gebundene Läufe, Holm-p 7·10⁻¹⁵ / 1·10⁻⁵. Pilot [[experiments/EXP-064-functional-regimes/README|EXP-064]].
**Grenzen (Codex, übernommen):** ein Eingriff (alle 5 Frequenzen auf einmal, nur W_E, nicht energiegleich); Genauigkeit hat Boden und Decke, 0.90 gegen 0.60 ist kein Maß für „Stärke“; zwei Zeitpunkte
lokalisieren keinen Übergang; Einheiten sind 20 richtungsgemittelte Seeds (Läufe eines Seeds teilen die Init). Bei t = 25 ist die Richtung uneinheitlicher: 38/40 Richtungen mit erwartetem Vorzeichen,
29/40 über 0.3 (Seeds 2253 A→B und 2267 B→A umgekehrt); bei t = 50 40/40 und 39/40. 19/20 Seeds generalisiert (primär waren alle 20 vorab festgelegt).
**Post hoc:** Nach 4000 Schritten zeigt auch die W_E-Energie in dieselbe Richtung (38/40 bzw. 40/40). Ablation und Energie sind hier nicht getrennt; die Frage „Funktion ohne Energie?“ bleibt offen.
Einordnung: Fortsetzung von K4/K4b (Persistenz nach 25 Schritten) auf die Funktion; nach unserer Suche vom 27.09. nicht gefunden (vorläufig, [[NOVEL_DIRECTIONS]] N29 „Zwei Regime“).

**Grenze für K2-Funktion (P2d) und K4c (Sitzung 23, Explorationen EXP-064 post hoc, [[experiments/EXP-068-matched-sensitivity/README|EXP-068]]):** Die gemessene Empfindlichkeit geht in allen
gesehenen Modellen mit der Energie- bzw. Amplitudenverteilung in W_E einher (Ablation und Energie zeigen immer in dieselbe Richtung; bei gleicher *entfernter Energie* kein Vorteil der dominanten Menge).
Eine funktionale Nutzung *über die Energie hinaus* ist damit nicht gezeigt, und mit Ablationen am selben Modell kaum zu trennen.

## BESTÄTIGT (Sitzung 22, 27.09., 09:30 Berlin): P2d, stärkere Margin-Reaktion entlang der gesteuerten Frequenzen #befund/positiv

**Kernaussage K2-Funktion (P2d)** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 09:31–09:34): *Bei Addition mod 113 nach 4000 Trainingsschritten verringerte eine auf W_E[:113] beschränkte Perturbation
W' = W − δ·P_S W / ‖P_S W‖ mit δ = 0.02·‖W‖ den mittleren Logit-Abstand der richtigen Klasse auf der gemeinsamen, in beiden Split-Armen ungezeigten Testmenge für die fünf dem Arm konstruktiv
zugewiesenen Zielfrequenzen im Mittel um 0.250 Logit-Einheiten stärker als für vier vorab festgelegte Fünfer-Kontrollmengen aus dem eingeschränkten P2-Kontrollpool (seedweises Bootstrap-95-%-KI
[0.229, 0.270]; D_s > 0 in 20/20 frischen Seeds). Das belegt eine stärkere Margin-Reaktion von W_E unter dieser einseitigen Perturbation bei dieser Dosis und diesen Kontrollen.*
- **Beleg:** [[confirm/P2d_REGISTRATION|P2d]] (eingefroren c0cd65f, 40 gebundene Läufe, Seeds 2230–2249), p = 1.6·10⁻¹⁵. Pilot [[experiments/EXP-065-p2d-pilot/README|EXP-065]].
- **Grenzen:** eine Dosis, einseitig, kein Gradient und keine Dosis-Kurve; Genauigkeitsverlust und Nutzung der ganzen Repräsentation sind nicht belegt. u_S ist innerhalb jedes Unterraums amplitudengewichtet,
  Frequenzidentität und gelernte Norm/Orientierung sind also nicht getrennt. Kontrollen nur aus dem P2-Pool. Eine Aufgabe, eine Architektur.
- **Zu P2c:** P2d ist mit einer Dosisgeometrie-Erklärung für das nicht bestätigte P2c vereinbar, **bestimmt dessen Ursache aber nicht** (Eingriff, Zielmaß, Kontrollen, Seed-Block und Basisregime änderten sich gleichzeitig).

## BESTÄTIGT (Sitzung 22, 27.09., 08:29 Berlin): N28, Momentum-Reset und Ausgleich durch zusätzliche Vorschritte #befund/positiv

**Kernaussage K4b-bestätigt** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 08:34): *Nach 25 Schritten auf dem konstruierten Split A und 2000 Schritten auf einem paar-disjunkten Split B
senkte das Nullsetzen von Adams erstem Moment (exp_avg) beim Wechsel den normierten spektralen Persistenzindex π des End-W_E um 0.151 (0.340 → 0.189; registrierter Mindesteffekt 0.05 überschritten).
Ein eigener Arm mit 35 statt 25 Vorschritten und demselben Reset lag nicht unter normal@25 (Nichtunterlegenheit, Marge 0.05; 0.410 gegen 0.340). Zehn zusätzliche Vorschritte können den Reset-Effekt
auf diesem Maß also ausgleichen. Das ist vereinbar mit einer Deutung als verlängerte Exposition, belegt sie aber nicht.* Beschreibend lag normal@50 bei π = 0.998, nahe dem reinen A-Endpunkt dieses Index.
- **Beleg:** [[confirm/N28_REGISTRATION|N28]] (eingefroren fa154bd, 300 gebundene Läufe, Seeds 2200–2229, alle 30 gültig): H1 Y = Δ − 0.05 = 0.101 [0.077, 0.126], Holm-p 2·10⁻⁸, 29/30;
  H2 X = 0.120 [0.090, 0.152], Holm-p 3·10⁻⁸, 29/30. Piloten [[experiments/EXP-058-optim-part/README|EXP-058]], [[experiments/EXP-059-momentum-exposure/README|EXP-059]].
- **Grenzen:** π ist ein unbeschränkter, je Seed affin normierter Index des Log-Energieverhältnisses in W_E, keine Wahrscheinlichkeit und kein Anteil „behaltener“ Wahl.
  Die mehrstufige π(t)-Kurve (0.01 / 0.19 / 0.30 / 0.56 / 1.05 bei t = 10 / 20 / 25 / 35 / 50) stammt aus dem Piloten an 10 bekannten Seeds; frisch reproduziert ist nur der Kontrast t = 25 gegen 50.
  Eine Aufgabe (add 113), ω = 0, eine Architektur und ein Optimierer, eine Split-Familie.

**Zwei spektrale Signaturen (Vorhersage an frischen Seeds erfüllt, keine Kernaussage über Funktion):** *Bei t = 25 war die Abweichung des End-W_E von passenden reinen B-Läufen vor allem
überschüssige Energie der alten Ziele, kaum fehlende Energie der neuen (a = 2.24, b = 0.36; a > b in 29/30 Seeds). Bei t = 50 war das Defizit der neuen Ziele viel größer (b = 3.80; Anstieg 3.44;
> 0.5 in 30/30).* Wir nennen das koexistenz- bzw. ausschlussartige **Spektralsignaturen**. Ob beide Frequenzmengen funktional genutzt werden oder B funktional nicht gelernt wird, ist **nicht geprüft**.
Die Regel stammt aus dem Piloten [[experiments/EXP-062-rate-race/README|EXP-062]] (Seeds 400–409) und wurde um 07:51 während der N28-Datenerhebung (seit 07:34) committet, vor jeder Einsicht
in N28-Ergebnisse; ohne nominale Fehlerrate, deshalb „erfüllte Vorhersage“, nicht „vorregistrierte Bestätigung“.
*Funktion, beschreibend ([[experiments/EXP-064-functional-regimes/README|EXP-064]], nach eigener Regel nicht auswertbar, 7/10 gültig):* Nach dem Wechsel bei t = 50 zerstört das Entfernen der alten Zielfrequenzen die Testgenauigkeit (0.01–0.09 in 10/10 Seeds), das der neuen kaum. Bei t = 25 ist es umgekehrt (ohne neue 0.04–0.38). Die spektral erhaltene alte Energie bei t = 25 ist also funktional weitgehend entbehrlich: eher **funktionaler Umstieg (t = 25) gegen funktionales Festhalten (t = 50)** als Koexistenz. Bestätigung an frischen Seeds steht aus.
*Pilot ([[experiments/EXP-063-exclusion-locus/README|EXP-063]], 10 bekannte Seeds):* Ein Reset des Rests des Netzes oder von W_E beim Wechsel bei t = 50 verkleinerte das Defizit der neuen Ziele
stark (b 4.25 → 1.05 bzw. 0.44), die überschüssige alte Energie blieb (a 3.10 bzw. 2.51). Das zeigt Reset-Empfindlichkeit und mögliche Koadaptation, keinen lokalisierten oder funktional belegten Mechanismus.
**Negativ:** [[experiments/EXP-060-early-lead/README|EXP-060]] (der W_E-Vorsprung bei t erklärt die Seed-Streuung von π nicht) und [[experiments/EXP-061-grad-alignment/README|EXP-061]]
(ein Kosinus des Rohgradienten der neuen Daten zeigt keine Verstärkung der alten Struktur; verworfen ist nur dieses eine Maß).

**P2b abgebrochen** (Designfehler: Trainer-Standard `--stop-after-gen 2000`), ersetzt durch [[confirm/P2c_REGISTRATION|P2c]]. **P2c (09:03): nicht bestätigt, Vorzeichen umgekehrt:** R̄ = −0.108 [−0.149, −0.070], 99/100 Seeds, 30/99 > 0. Nach 4000 Schritten kostet das Entfernen von 0.5·E_ctrl aus den eigenen Zielen *weniger* Loss als aus der Kontrolle. Das ist keine registrierte Bestätigung der Gegenhypothese. P2c belegt keine bevorzugte funktionale Nutzung der gesteuerten Frequenzen **unter diesem W_E-Eingriff, dieser Kontrolle und dieser Dosis**; es zeigt weder, dass die Ziele ungenutzt sind, noch, dass Kontrollfrequenzen allgemein funktionaler sind. Ursache nicht identifiziert (Trainingsstand, Seed-Block, Dosisgeometrie mit 2.4 % gegen 50 % der jeweiligen Energie, Kontrollzusammensetzung, Basis-Loss ändern sich gleichzeitig). Wortlaut nach Codex (09:05–09:12). *Exploration danach ([[experiments/EXP-065-p2d-pilot/README|EXP-065]], gleiche Modelle, Maß nach dem Ergebnis gewählt):* Bei **gleicher Schrittnorm** fällt der Logit-Abstand entlang der eigenen Ziele in 80/80 Modellen stärker als entlang gleich großer Kontrollmengen (Median 0.25 gegen 0.0007). Vereinbar mit der Dosisgeometrie als Grund der P2c-Umkehrung, ohne sie zu belegen; P2d bestätigt den Effekt selbst (siehe oben).

## BESTÄTIGT (Sitzung 21, 27.09., 06:04 Berlin): P3, starke Wirkung einer 25-Schritt-Vorgeschichte gegen paar-disjunktes Weitertraining #befund/positiv

**Kernaussage K4-bestätigt** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 06:10): *Nach 25 Schritten auf dem ersten konstruierten Split lagen die Wechselmodelle nach 2000 Schritten auf
einem paar-disjunkten zweiten Split im Mittel noch bei 0.351 der normierten log-W_E-Leistungsdistanz zwischen dem reinen Endpunkt des zweiten und dem des ersten Splits. Der registrierte
Überschuss über jede geprüfte statische additive W_E-Spur betrug 0.293 [0.263, 0.322] (30 frische Seeds, 30/30 > 0; add 113; bestätigt).* Der Befund zeigt eine **starke Wirkung der
frühen Trainingsvorgeschichte**. Er trennt aber eine Festlegung im Netz **nicht** von Optimiererzustand oder allgemein verlangsamter Anpassung (Codex: Der reine Lauf des zweiten Splits ist
der richtige Nullpunkt für den Gesamteffekt, nicht für eine A-spezifische Festlegung; dafür fehlen B→B/A→A mit 2025 Schritten und ein Optimierer-Reset beim Wechsel).
**Sekundär:** In den registrierten, auf gleiche Steuerstärke kalibrierten Konstruktionen war kein Einfluss der Überlappung nachweisbar: Δπ(0.4 − 0) = 0.005 [−0.030, 0.042].
Das ist kein Äquivalenztest, und ε unterscheidet sich zwischen den Stufen.
**Post hoc (06:13, beschreibend, nach Ergebnis und Codex):** In den Wechselläufen tragen die Ziele des *ersten* Splits im Mittel 20 % der W_E-Leistung (Zufall 8.9 %, reiner Lauf des zweiten Splits 2.7 %;
über Zufall in 48/60 Richtungen). Die Ziele des zweiten Splits tragen 48 % statt 78 %. Ein bloß träges, diffuses Modell läge bei höchstens Zufallsniveau. Es gibt also Hinweise auf **beides**:
eine A-spezifische Erhaltung und eine langsamere Anpassung. Belege: [[confirm/P3_REGISTRATION_DRAFT|P3]], Manifest f8adf45, `P3_summary.json`, `lab/confirm/p3_posthoc_decompose.py`.
Zusammenhang: Pilot [[experiments/EXP-056-overlap-persistence/README|EXP-056]], [[experiments/EXP-038-where-lockin/README|EXP-038]] (Festlegung doppelt vorhanden, Pilot). **Größte offene Frage jetzt:**
Ist die Erhaltung A-spezifisch im Netz, oder steckt sie im Optimiererzustand? Nächster Versuch: Wechsel mit Adam-Reset und Kontrollen gleicher Länge.
**Erster Hinweis (Pilot [[experiments/EXP-057-optim-reset/README|EXP-057]], 06:21, 10 bekannte Seeds, keine Bestätigung):** Setzt man beim Wechsel nur den AdamW-Zustand zurück (Gewichte bleiben), fällt π von 0.30 auf 0.11, und die Ziele des ersten Splits sinken unter Zufall (7.1 % gegen 8.9 %). Die A-spezifische Erhaltung nach 25 Schritten sitzt demnach vor allem im **Optimiererzustand**. Die gleich lange Referenz ändert nichts (0.304). Formal *teilweise*; eine Bestätigung an frischen Seeds und die Trennung m / v / Schrittzähler stehen aus.
*Korrektur (Codex, eingearbeitet 06:31):* Nicht identifiziert, ob das Gedächtnis im Zustand sitzt oder ob die vorzeichenartigen Schritte nach dem Reset die kleine Spur überschreiben. Gestützt ist nur: Eine volle Neuinitialisierung des Optimierers senkt die spätere A-Persistenz. „Unter Zufall“ ist nicht signifikant (t = −1.2).
**Folgepilot [[experiments/EXP-058-optim-part/README|EXP-058]] (06:50, 10 bekannte Seeds):** Nur das erste Moment (m) zu löschen senkt π genauso (0.30 → 0.12) wie der volle Reset (0.11), obwohl die ersten Schritte danach **kleiner** sind (Update-Norm 0.25 gegen 0.27 normal, 0.42 beim vollen Reset). Das Überschreiben erklärt den Abfall also nicht, das **Momentum der ersten 25 Schritte trägt den größten Teil der Persistenz** (Pilot, Bestätigung an frischen Seeds ausstehend). Kandidat [[NOVEL_DIRECTIONS]] N28.
**Einordnung nach [[experiments/EXP-059-momentum-exposure/README|EXP-059]] (Sitzung 22, 07:22, 10 bekannte Seeds, Pilot):** Der Momentum-Anteil ist **verlängerte Exposition**, kein eigenes Gedächtnis: Mit gelöschtem m und 10 zusätzlichen A-Schritten liegt π mindestens so hoch wie normal bei t = 25 (0.36 gegen 0.30); m zu löschen kostet ≈ 6–10 A-Schritte. Die frühe Festlegung ist **sehr steil**: π_normal = 0.01 / 0.19 / 0.30 / 0.56 / 1.05 bei t = 10 / 20 / 25 / 35 / 50. Größte offene Frage für Programm B bleibt damit, **was** in den ersten ≈ 50 Schritten die Wahl so fest macht (nicht wo sie im Optimierer liegt). Bestätigung der engen Aussage: [[confirm/N28_REGISTRATION|N28]] (Entwurf). *Wortlaut dieses Absatzes zu stark (Codex, 08:34): gilt nur in der engeren Fassung „K4b-bestätigt“ oben.*

## BESTÄTIGT (Sitzung 21, 27.09., 05:39 Berlin): P1, Steuerung der W_E-Repräsentation durch konstruierte Splits #befund/positiv

**Kernaussage K2-bestätigt** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 05:47): *Bei Schritt 2000 verschiebt eine konstruierte Auswahl der Trainingspaare die relative
W_E-Energie hin zu fünf vorgegebenen zyklischen Fourier-Frequenzen (bzw. D₅₉-Irreps), gemessen gegen fünf disjunkte Vergleichskomponenten. Das gilt in je 50 vorab registrierten,
frischen Seed/Split-Paaren für vier nach dem Pilot gewählte Aufgaben mit dem 1-Schicht-Transformer der Studie.* Das ist eine **zurückgehaltene Replikation** (held-out) der
Repräsentationssteuerung, **kein** Beleg für funktionale Nutzung.

| Aufgabe | Δ_pow (95-%-KI) | positiv | Holm-p (ungünstigster Fall) |
|---|---|---|---|
| add 113 (primär) | 8.24 [7.92, 8.54] | 50/50 | 1.5·10⁻⁵ |
| mul 113 | 8.09 [7.75, 8.43] | 50/50 | 1.5·10⁻⁵ |
| add 97 | 6.11 [5.79, 6.43] | 50/50 | 1.5·10⁻⁵ |
| D₅₉ | 2.64 [2.55, 2.73] | 50/50 | 1.5·10⁻⁵ |

Belege: [[confirm/P1_REGISTRATION_DRAFT|Registrierung + Ergebnis]], Manifest 733e829, 420 gebundene Läufe, `lab/confirm/P1_summary.json`. **Grenzen:** keine natürlichen Splits, keine
unverzerrte Aufgabenpopulation, eine Architekturfamilie, ein Zeitpunkt (2000). Δ_pow misst die relative Anreicherung eigener gegen fremde Ziele, keine Konzentration gegenüber der Init.
Der Kreuzblock (5 Einheiten × 3 Inits) zeigt „stabil über diese Inits“; der ICC ist bei 5 Einheiten ungenau und enthält die Wechselwirkung Init × Split.
**P2 (funktionale Nutzung): nicht auswertbar** (3/50 Modelle bei Schritt 2000 nicht generalisiert, Regel „alle gültig“). Beschreibend R̄ = 0.12 über 47, womöglich durch die Auswahl verzerrt.
Die Funktionsfrage bleibt **offen**; Nachfolger: [[confirm/P2_REGISTRATION_DRAFT|P2]] Ergebnisabschnitt. **P3** (Persistenz ohne geteilte Daten) ist eingefroren und läuft ([[confirm/P3_REGISTRATION_DRAFT|P3]]).

## Pilotnacht 27.09. (Sitzung 20, Stand 03:23 Berlin): K2 hält außerhalb von Addition mod 113

Alle Urteile vorab festgelegt, GPU nach bestandenem [[experiments/GPU-001-equivalence/README|GPU-001]] (gleichwertig zur CPU, ≈ 17× schneller). **Alles Piloten**, keine unabhängige Bestätigung.

| Fall | Versuch | Δ̄ (Maß) | n positiv | p | Urteil |
|---|---|---|---|---|---|
| Addition mod 97 | [[experiments/EXP-043-generalize-steering/README\|EXP-043]] | 7.7 (Top-5-Δ) | 10/10 | 0.001 (Holm) | *steuerbar* |
| Multiplikation mod 113 (≈ Z₁₁₂ + Null) | EXP-043 | 7.7 | 10/10 | 0.001 (Holm) | *steuerbar* |
| Diedergruppe D₅₉ (nicht-abelsch, Irreps) | [[experiments/EXP-046-dihedral-steering/README\|EXP-046]] | 9.6 | 10/10 | 0.001 | *steuerbar* |
| a + b ohne mod | [[experiments/EXP-048-intadd-steering/README\|EXP-048]] | 2.2 (Δ_pow, trendbereinigt) | 10/10 | 0.001 | *steuerbar* |
| 4× breiter (d = 512) | [[experiments/EXP-049-width-steering/README\|EXP-049]] | 7.8 (Δ_pow); d = 128: 8.7 | 10/10 | 0.001 | *steuerbar* |
| MLP statt Transformer (10 000 Schritte, nach dem Grokking) | [[experiments/EXP-045-mlp-steering/README\|EXP-045]] | 7.9 (Top-5-Δ; bei 2000: 10.0) | 10/10 | 0.001 | *steuerbar* |
| Mechanismus: Häufigkeiten gegen Paarstruktur (Z₁₁₃) | [[experiments/EXP-047-marginal-control/README\|EXP-047]] | Häufigkeiten 0.3 (n. s.); Paarstruktur 6.8 | 10/10 | 0.001 | *Paarstruktur trägt* |
| K4 frühe Festlegung (Wechsel F→G, ≈ 38 % geteilt) | [[experiments/EXP-044-generalize-lockin/README\|EXP-044]] | d(150) 3.3 / 3.5; Kipp zwischen t 25 und 50 | 10/10 je Aufgabe | 0.001 (Holm) | *festgelegt* (add 97, mul 113) |
| K1 an unberührten Fällen (eingefrorene Vorhersage, Paket C) | [[experiments/EXP-052-oos-mask-prediction/README\|EXP-052]] | ρ eigen 0.34–0.45, fremd ≈ 0 | 4/4 Fälle | 0.0002 (Holm) | *K1 gilt hier* (Assoziation) |
| Mechanismus: kohärentes M0c gegen M0 (Phasen-Dissoziation, Paket C) | [[experiments/EXP-050-phase-dissociation/README\|EXP-050]] | quadlm − anti 6.5; anti allein 1.4 | 10/10 / 10/10 | 0.001 (Holm) | *M0c selektiert*, aber M0 trägt auch (erste Ordnung nur halb) |
| Funktion (P2) | [[experiments/EXP-051-functional-ablation/README\|EXP-051]], [[experiments/EXP-055-ablation-dose/README\|EXP-055]] | Genauigkeit am Boden; ΔL primär n. s., Teildosen 10/10 (post hoc) | – | – | *unklar* |

**Lesart nach [[LESART-nacht-2026-09-27]] Regel 2:** Drei echt andere Aufgaben sind *steuerbar*, gefordert waren zwei. **K2 gilt damit über die gezeigten Aufgaben hinweg** (Pilotstufe):
anderer Primmodulus, zusammengesetzter Modulus, nicht-abelsche Gruppe, nicht-modulare Addition, 4× Breite. Grenze 4 (Mechanismus) ist für Z₁₁₃ zugunsten der Paarstruktur (M0) entschieden,
wie die Theorie erster Ordnung vorab vorhersagte. Offen bleiben: Bestätigung an frischen Seeds und Splits (P1), funktionale Nutzung je Energieeinheit (P2; Test-Loss bei Teildosis,
BACKLOG), Persistenz (K4) in den neuen Aufgaben (EXP-044), andere Architektur (EXP-045 MLP), Häufigkeiten gegen Paarstruktur in D₅₉ und int-add.
Nebenbefund (post hoc, [[NOVEL_DIRECTIONS]] Nachprüfung s20): Die gepflanzte Wahl klingt nach dem Grokking bis Schritt 2000 nicht ab. Das ist der Unterschied zu Zhou et al. 2024, der nächsten bekannten Vorarbeit.

## Programm (Regel 18c, festgelegt 2026-09-26 20:45 Berlin; Planungsgrundlage für alle neuen Versuche)

**Arbeitshypothese (Astra-Review Punkt 4):** Die *Zusammensetzung einer festen Trainingsmenge* (Full-Batch) steuert, welche
Frequenzen/Irreps ein Netz repräsentiert und nutzt, und diese Wahl ist nach kurzer Zeit gegen einen Datenwechsel persistent.
„Daten beeinflussen Frequenzen“ allein ist als Neuheit zu breit (Zhou et al. 2024, LeDoux 2026, AGF, He et al. 2026).

| Paket | Frage | Stand | Aktiv? |
|---|---|---|---|
| **A** | Split-Steuerung unabhängig replizieren, verallgemeinern **und funktional** nachweisen | Pilot/Verallgemeinerung vorbereitet: EXP-043, 045, 046, 047, 048, 049. Funktionaler Pilot: [[experiments/EXP-051-functional-ablation/README|EXP-051]] (Ablation an den EXP-047-Modellen gegen energiegleiche Kontrolle). K1 an unberührten Fällen (add 97, mul 113, D₅₉), Vorhersage vor den Läufen eingefroren: [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]]. **Fehlt:** unabhängiger Bestätigungsblock | ja |
| **B** | Persistenz nach Datenwechsel: F→G **und** G→F, kontrollierte Überlappung, festes Nachtrainingsbudget; „festgelegt“ = „nach B Schritten persistent“ | EXP-044 (bedingt auf EXP-043); CPU EXP-035–042 (`night_program.py --cpu`). Konkurrenzmodell: effektive Lernrate steuert die Merkmalsersetzung (Lyle et al. 2025, https://arxiv.org/abs/2507.20057) → EXP-039/040 trennen ELR und Datenauswahl. *Sitzung 14:* kontinuierliches Persistenzmaß π (post hoc an EXP-020: 0.15/0.38/0.72/≈1 bei t = 10/25/50/150), Überlappungskonstruktion [[experiments/EXP-053-p3-overlap-design/README|EXP-053]] (Entwurf), eingefrorene Uhr-Vorhersagen für EXP-039 und Lesarten (i)/(ii) für EXP-044 | ja |
| **C** | Eine mechanistische Vorhersage an unberührten Fällen | EXP-050 (M0c gegen M0, Kontrolle quadlm), Theorie erster Ordnung ([[BEFUND-split-mechanismus]]); *Sitzung 14:* [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]] (40 Vorhersagen aus dem Split, per Commit vor den Läufen eingefroren; läuft ohne eigene Läufe mit den Nacht-R-Armen) | vorbereitet, nicht aktiv |

Höchstens zwei Pakete aktiv (derzeit A und B). Andere Linien nur, wenn sie zwischen ausdrücklich genannten Konkurrenzmodellen entscheiden.

**Primäre Kernaussagen (vorläufig; werden erst nach der Pilotnacht mit Analysemanifest eingefroren):**
- **P1 (A):** Konstruierte Splits erhöhen die Leistung der Zielfrequenzen in W_E: Δ_pow > 0 auf frischen Seeds und Splits
  (Transformer, add 113), praktischer Mindesteffekt Δ_pow ≥ 1.
- **P2 (A, funktional):** Das Entfernen der Zielfrequenzen senkt die Testgenauigkeit stärker als das Entfernen energiegleicher anderer Frequenzen.
- **P3 (B):** Nach einem Wechsel bei t = 150 überwiegen die Frequenzen des ersten Splits nach 2000 Schritten auf dem zweiten, in beiden Richtungen. *Vor dem Einfrieren prüfen (Sitzung 14):* bei t = 150 liegt die Persistenz π an EXP-020 schon an der Decke (1.00 ± 0.04); empfindlicher ist t = 25 ([[BACKLOG]] „Wechselzeitpunkt für P3“).
- **Eine Bestätigungsfamilie P1–P3, Holm.** Effektgrößen mit 95-%-Konfidenzintervall (Bootstrap über Seeds) primär berichten.
- **Stichprobengröße:** Pilot EXP-016: Δ_pow 8.41 ± 1.20 (n = 10; ohne den doppelten Seed 19: 8.27 ± 1.19). Für P1 reicht damit
  der kontinuierliche Vorzeichen-Permutationstest mit wenigen Seeds; für neue Aufgaben ist die Streuung unbekannt → n aus der Pilotnacht.
  Nur-Vorzeichen-Zählregeln sind schwach (exakt gerechnet: n = 10 braucht ≥ 9/10, Power 38 % bei q = 0.8, 74 % bei q = 0.9;
  n = 12 braucht ≥ 10/12, 89 % bei q = 0.9). Ziel: Power ≥ 80 % für den vorab genannten Mindesteffekt.
- **Nullkalibrierung von Δ_pow (21:02, reine Nachrechnung gespeicherter Läufe):** Zufallssplits (EXP-003d-Baselines 10–19, Schritt 2000), zufällige disjunkte Zielmengen, F- und G-Lauf aus verschiedenen Seeds, 20 000 Ziehungen: Mittel −0.01, SD 0.48, 95-%-Quantil 0.79, |Δ_pow| ≥ 1 in 4 %. Der Mindesteffekt 1 liegt damit bei ≈ 2 Null-SD. Bei einer Streuung wie im Pilot EXP-016 (SD 1.2) braucht ein einseitiger Test auf Mittel ≥ 1 mit 80 % Power grob 10–12 Seeds (Normalnäherung, d ≈ 0.8); für neue Aufgaben mit der Pilotstreuung der Nacht neu rechnen.
- **Bestätigungsblock reserviert:** Init-Seeds **1000–1099**, Splits über `SeedSequence([1000001, Versuch, Seed, Arm, Zweck])`. *Präzisiert (Sitzung 14, vor jeder Nutzung):* `[1000001, Versuch, Aufgabe, p, Seed, Arm, Zweck]`, damit add 113 und mul 113 bei gleichem Seed keinen Strom teilen; Werkzeug `lab/tools/confirm_splits.py`, schreibt nur mit eingefrorenem Manifest. *Gekreuzter Split×Init-Block (Astra 5, Sitzung 16, vor jedem Lauf festgelegt, ungetestet):* Die ersten 5 Seeds von add 113 trainieren dieselben F/G-Splits zusätzlich mit 2 weiteren Inits (s + 200, s + 300, reserviert 1200–1399; 20 Zusatzläufe). Das ist sekundär und beschreibend und gehört nicht zur Holm-Familie. P1 zählt weiter nur ein Δ je Seed. Berichtet werden die Varianzanteile Einheit (Split-Paar + Ziele) gegen Init. Lesart: „stabil über Inits“ bei ≥ 90 % Δ > 0 und Init-SD < Mittel/2; „init-abhängig“ bei < 75 % oder Init-SD ≥ Mittel; sonst „gemischt“. Die P1-Einheit hält die Init schon fest (F und G mit derselben Init) und zieht Init, Ziele und beide Splits aus getrennten Strömen. Der Kreuzblock ergänzt die fehlende Richtung: derselbe Split mit anderer Init.
  Erst öffnen, wenn das Analysemanifest (Commit-ID) eingefroren ist. Jede Registrierung nennt „bereits gesehene Daten und davon
  beeinflusste Entscheidungen“. Bereits ausgewertete Seeds sind keine unabhängige Bestätigung.
- **Zweiter Bestätigungsblock reserviert (Sitzung 22, 2026-09-27, vor jeder Nutzung):** Seeds **2000–2099** für [[confirm/P2b_REGISTRATION|P2b]] (Splits `confirm_splits` mit Versuchs-ID 2), **2200–2229** für [[confirm/N28_REGISTRATION|N28]] (EXP-053-Splits, ω = 0). 2230–2299 bleiben frei. *Nachtrag 08:06:* P2b abgebrochen (Designfehler, Seeds 2000–2099 verbraucht); **2100–2199** für [[confirm/P2c_REGISTRATION|P2c]] (Versuchs-ID 3), vor jeder Nutzung. *Nachtrag 09:17:* **2230–2249** für [[confirm/P2d_REGISTRATION|P2d]] (Versuchs-ID 4), vor jeder Nutzung; 2250–2299 frei. *Nachtrag Sitzung 23 (vor jeder Nutzung):* **2250–2269** für [[confirm/N29_REGISTRATION|N29]], **2270–2289** für [[confirm/P2e_REGISTRATION|P2e]] (Versuchs-ID 5), **2300–2319** für [[confirm/N29b_REGISTRATION|N29b]], **2320–2339** für [[confirm/N29c_REGISTRATION|N29c]]; 2290–2299 frei. Familie Sitzung 22 = {N28-H1, N28-H2, P2b}, Holm. *Nachtrag Sitzung 24 (vor jeder Nutzung):* **2340–2359** für [[confirm/P2f_REGISTRATION|P2f]] (D₅₉, Versuchs-ID 6); 2290–2299 frei. *Nachtrag Sitzung 25 (2026-09-27, vor jeder Nutzung):* **2360–2419** für [[confirm/P4_REGISTRATION_DRAFT|P4]] (Versuchs-ID 7; 45 davon genutzt), **2420–2509** für [[confirm/R1_REGISTRATION_DRAFT|R1]] (Versuchs-ID 8, 6 × 15). *Nachtrag Sitzung 26 (2026-09-27, vor jeder Nutzung):* **2510–2539** für [[confirm/R2_REGISTRATION_DRAFT|R2]] (EXP-053-Splits, ω = 0, Konstruktion wie N29). **2540–2559** für [[confirm/R3_REGISTRATION_DRAFT|R3]] (gleiche Konstruktion; Sitzung 26, vor jeder Nutzung). *Nachtrag Sitzung 32 (2026-09-27, vor jeder Nutzung):* **2800–2829** für [[confirm/R6_REGISTRATION_DRAFT|R6]] (n nach Codex-Prüfung von 20 auf 30 erhöht, noch vor jeder Nutzung) (EXP-053-Splits, ω = 0, Konstruktion wie N28). Bereits vergeben ohne Eintrag hier: 2600–2719 (R4), 2720–2779 (R5), 2780–2789 (EXP-084). *Nachtrag Sitzung 37 (2026-09-28, vor jeder Nutzung):* **3100–3129** für [[confirm/R8_REGISTRATION_DRAFT|R8]] (Frequenzkonflikt, n geplant 20).
- *Nachtrag Sitzung 39 (2026-09-28):* **3200–3212** von [[experiments/EXP-087-planted-signal-mediation/README|EXP-087]] genutzt (Pilot 3200–3209, Kalibrierung 3210–3212; Eintrag nachgeholt). **Vor jeder Nutzung reserviert:** **3230–3249** für [[experiments/EXP-088-common-dose-curve/README|EXP-088]] (Einheiten 0–19), **3250–3252** für dessen Kalibrierung.
- *Nachtrag Sitzung 40 (2026-09-28, vor jeder Nutzung):* **830–839** von [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (Pilot, reserviert seit Sitzung 27), **3260–3269** für [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]] (Pilot). **3270–3285** für [[experiments/EXP-090-beta-window-lambda/README|EXP-090]] (Pilot). **3300–3335** für [[confirm/R9_REGISTRATION_DRAFT|R9]] (Bestätigung, vor jeder Nutzung; Fassung 2 erweitert von 3300–3323).
- **Messgrößen getrennt:** Repräsentationsenergie (Δ_pow, kontinuierlich), funktionale Nutzung (Ablation), Persistenz (nach B Schritten).
  Korrelationen nicht als direkte Wirkung formulieren (z. B. EXP-030 nur als konditionale Assoziation).

**Einschränkung zu K2 (Astra Punkt 5, selbst geprüft):** EXP-016 ist ein starker Befund, aber die Unabhängigkeit der Seeds ist
eingeschränkt: Seed 12/G und 19/F haben einen identischen Split, 10/G ↔ 17/F und 11/G ↔ 18/F teilen Phasen und Zufallsschlüssel
(EXP-016 Nachtrag c). Die Sensitivität „ohne Seed 19“ (n = 9) beseitigt nicht alle Abhängigkeiten. Neue Versuche (ab EXP-047)
nutzen getrennte Ströme (`SeedSequence`); für eine Bestätigung zählen nur unabhängige Seeds und Splits.

## Kernaussagen mit Belegen

| # | Aussage | Beleg (vorab festgelegt, sofern nicht anders markiert) | Literatur |
|---|---|---|---|
| K1 | **Der Trainingssplit sagt die gelernten Frequenzen voraus** (Masken-Spektrum M0, ohne Gewichte). | [[experiments/EXP-015-mask-spectrum/README\|EXP-015]]: frische Seeds 10–17, r̄ 0.277 vs. fremde Masken 0.499, p 2.5e-5. Assoziation. | Frequency Principle (Zhou et al. 2024) verwandt, andere Aufgaben; M0 für Z_p nicht gefunden |
| K2 | **Die Frequenzwahl ist über die Daten steuerbar.** Konstruierte Splits geben die gelernten Frequenzen vor. | [[experiments/EXP-016-engineered-split/README\|EXP-016]]: 10/10 Seeds, Δ̄ +7.7 von 10, p ≈ 0.001; Abweichungen 2k-Oberwellen der Ziele | LeDoux 2026 (Datenreihenfolge), He et al. 2026 (Init-Lotterie); kausale Split-Steuerung nicht gefunden |
| K3 | Der erste Gradient an W_E sagt die Wahl besser voraus als die Init. | [[experiments/EXP-012-init-gradient/README\|EXP-012]]: r̄ 0.254 vs. 0.369, p 0.031 | — |
| K4 | **Die Wahl legt sich sehr früh fest**, weit vor Memorisierung und Grokking. | [[experiments/EXP-020-data-switch/README\|EXP-020]] (5 Seeds): Dominanzmaß kippt bei Wechsel nach (25, 50] Schritten in 5/5 (beschreibend; Urteil *nicht bestätigt* 4/5); exakt „nur F“ ab t = 150. [[experiments/EXP-032-early-lockin/README\|EXP-032]] (Zwei-Hot-Netz, anderes Protokoll): halbe End-Neigung nach 5 Schritten, p 1e-4. *Post hoc kontinuierlich (Sitzung 14):* Persistenz π(t) an EXP-020 0.15 / 0.38 / 0.72 / 1.00 bei t = 10 / 25 / 50 / 150 (5 Seeds, enge Streuung). *Sitzung 15 (post hoc):* π und die ganze Spektrumsform ändern sich nach Schritt 250 in der G-Phase kaum (Mischung spätestens dann gesetzt); Top-5-Kreuzungen hängen auch unter reinem Takt von der Stärke des zweiten Splits ab → Zeitfragen mit π | Kritische Perioden (Achille 2019) allgemein; Festlegungszeit der Frequenzwahl nicht gefunden |
| K5 | Die frühe Festlegung braucht AdamW in der ersten Phase nicht. | [[experiments/EXP-033-optimizer-lockin/README\|EXP-033]]: GD 10/10 (eingeschränkt: Phase 2 immer AdamW) | — |
| K6 | Datenauswahl und Aktivierung zusammen bestimmen die Frequenzen (ReLU folgt dem Split, x² nur richtungsgleich). | [[experiments/EXP-024-quadratic-agf-mask/README\|EXP-024]] (ReLU bestätigt, aber memorierend; x² n. s.) | AGF (Kunin et al. 2025) |

**Negativ / nicht gezeigt:** Die natürliche Split-Konzentration sagt die Grokking-Zeit nicht voraus (Sitzung 5, post hoc);
Breitenabhängigkeit der Split-Auswahl verworfen ([[experiments/EXP-027-width-selection/README\|EXP-027b]]); Init-Tausch
([[experiments/EXP-010-init-swap/README\|EXP-010]]) bisher 1/10 Paare.

## Wichtigste Grenzen

1. **Eine Aufgabe, ein Modulus, im Kern eine Architektur.** Nichts ist an Multiplikation, anderem p, tieferen Modellen oder einer
   nicht-modularen Aufgabe geprüft.
2. K4 nur gegen einen Teilwechsel (F und G teilen ≈ 73 % der Paare); der harte Test [[experiments/EXP-041-imprint/README|EXP-041]] läuft nachts.
3. Viele Einzelversuche mit 3–5 Seeds; ab jetzt ≥ 10 Seeds für Urteile (Regel 15b).
4. **K2-Mechanismus nicht eindeutig (Sitzung 12):** Die konstruierten Splits verzerren auch das Spektrum der bloßen Token-Häufigkeiten
   zu den Zielen hin (Zielrang 14.5 von 56, Zufall 27.5). Ob die Steuerung über die Paarstruktur (M0) oder über die Häufigkeiten läuft,
   prüft [[experiments/EXP-047-marginal-control/README|EXP-047]] (gemischte Kontrolle mit exakt gleichen a/b-Häufigkeiten).
   *Theorie (Sitzung 13, erste Ordnung, vorab notiert):* Bei gleichverteilter Ausgabe fällt der Häufigkeitsanteil aus dem ersten
   W_E-Gradienten exakt heraus (er sieht nur das „zentrierte M0“); Erwartung für EXP-047 deshalb: Häufigkeiten allein steuern nicht.

## Größte offene Frage

*Stand Sitzung 20: für K2 im Pilot beantwortet (ja, siehe „Pilotnacht“ oben). Neue größte offene Frage: Hält K2 im vorab eingefrorenen Bestätigungsblock, und gilt K4 in den neuen Aufgaben?* **Verallgemeinern K2 (Steuerung über die Daten) und K4 (frühe Festlegung) über Addition mod 113 hinaus?** Nächster Test:
[[experiments/EXP-043-generalize-steering/README|EXP-043]] (Modulus 97 und Multiplikation mod 113, GPU, 10 Seeds je Aufgabe;
Multiplikation ist nach Umbenennung der Token fast exakt Addition mod 112, also vor allem ein Test eines *zusammengesetzten*
Modulus), [[experiments/EXP-044-generalize-lockin/README|EXP-044]] (K4 dort, bei ≈ 62 % neuen Paaren) und
[[experiments/EXP-045-mlp-steering/README|EXP-045]] (andere Architektur) und
[[experiments/EXP-046-dihedral-steering/README|EXP-046]] (**nicht-abelsche** Gruppe D₅₉, erste echt andere Aufgabe).
[[experiments/EXP-048-intadd-steering/README|EXP-048]] (**nicht-modulare** Addition a + b, deren bekannte Lösung eine Zahlengerade ist;
Primärgröße Log-Leistungskontrast, an EXP-016 kalibriert).
Wie die Kombination der Nachtergebnisse zu lesen ist, steht vorab in [[LESART-nacht-2026-09-27]].
Danach: Uhr-Frage (Λ-Uhr / Amplitudenschwelle, EXP-039/040) nur, soweit die Verallgemeinerung trägt.

## Archiv aus FINDINGS (verschoben in Sitzung 43, 2026-09-28, wortgleich)

Die folgenden Absätze standen bis Sitzung 42 in [[FINDINGS]] (Literatur-Einordnung, Programm, Größte offene Frage). Sie wurden wegen Regel 15a (FINDINGS höchstens eine Seite) unverändert hierher verschoben.

*Ergänzt Sitzung 25 (Volltextprüfung, [[paper/fulltext_check_2026-09-27]]):* Teil-Resets in Transformern: in Sprachmodellen stellt ein Re-Init der Query-Key-Anteile die Lernfähigkeit her, Value-Anteile nicht (Dong 2026, arXiv 2607.27281); Frequenzidentität im selben Modelltyp über die Gewichtsrichtung übertragbar (Khanh 2026, arXiv 2607.06628).

*Ergänzt Sitzung 26:* Vorwärtszitate über die Semantic-Scholar-API (9 Ausgangsarbeiten, zitierende Arbeiten bis 2026-09-23; [[paper/related_work]] Nachtrag) ohne einschränkenden Treffer; Kernel-Vorläufer zu K2: Tomàs Bernal et al. 2026 (*korrigiert 15:42:* bei RFM-Kernels bestimmt eine absichtlich symmetrische Trainingsmenge, **welche** Gruppenstruktur die Merkmale kodieren; schränkt K2 konzeptionell **teilweise** ein, K2 bleibt in der engeren Form: vorgegebene Fourier-Frequenzen in Transformern über das Maskenspektrum); Komponentenrollen im gleichen Modelltyp ohne Resets: Jia 2026. *Ergänzt Sitzung 27:* Adams erstes Moment als Gedächtnis, das Daten über ihr Entfernen bzw. ihre Position hinaus weiterträgt und bei einem Zustands-Reset zusammenbricht: Xu 2026, Sweeney 2026, Sevetlidis & Pavlidis 2026 → **die K4b-Lesart („Momentum = fortgesetzte Exposition“) ist bekannt**; nicht gefunden nur die parameterfreie Größenabschätzung (Momentum-Schwanz ≈ 9 Schritte gegen gemessene 6.5–9.6 bei t = 25–35, post hoc, [[NOVEL_DIRECTIONS]] N38).

*Ergänzt Sitzung 28 (Exploration, gesehene Seeds):* **C** hat wieder eine Vorhersage an unberührten Fällen: Die Rangfolge der fünf Ziele innerhalb eines Splits folgt dem Maskenspektrum (P1, alle vier Aufgaben, ρ 0.21–0.44, Init nur 0.08–0.15) → registriert als [[confirm/C1_REGISTRATION|C1]] an den R1-Seeds. **B** fein: Nach einem Wechsel bei t = 50 behalten die alten Ziele ihre Rangfolge vom Wechselzeitpunkt (N29, ρ 0.58; bei t = 25 0.17), die neuen Daten ordnen sie nicht um (ρ 0.02) → [[confirm/C2_REGISTRATION|C2]] an den R2-Seeds. Absolut trägt K2 bei add 113 im Mittel 80 % der W_E-Energie auf den 5 Zielen (Init 8.9 %). *Später in Sitzung 28:* Die Feinordnung überdauert im Transformer das Grokking (add/mul/D₅₉), zeigt sich auch bei 4× Breite, Integer-Addition und MLP (→ [[confirm/C3_REGISTRATION|C3]]; D₅₉ nach dem Grokking → [[confirm/C4_REGISTRATION|C4]]), folgt aber nicht der architekturspezifischen Herleitung (MLP: M0c > M0). Die Rangerhaltung der alten Ziele liegt bei t = 50 weit über einer Nicht-Ziel-Kontrolle (0.58 gegen −0.04), bei t ≤ 25 nur ≈ 0.1 darüber; C2 prüft das jetzt mit (Fassung 3).

*Ergänzt Sitzung 30:* **A** Rahmenfrage aus dem Gutachter-Durchgang: K2 gilt bisher nur für *konstruierte* Splits; ob ein gewöhnlicher Zufallssplit die Wahl mitformt, ist nur assoziativ und seed-gekoppelt belegt (EXP-015) → Bestätigungsentwurf [[confirm/R4_REGISTRATION_DRAFT|R4]] (gekreuzt Init × Split, 40 Einheiten; Designprüfung: Hebel eines Zufallssplits klein, Top-5/Rest 1.28).

*Ergänzt Sitzung 30 (Beobachtungen, post hoc):* (1) Die Steuerung überdauert das Grokking und wächst danach weiter (P2d/P2e, 20/20 Seeds je Aufgabe bis 4000/8000 Schritte). (2) Konstruierte Splits groken ≈ 9× früher als zufällige (CPU 662 gegen 5975 Schritte; EXP-047: 20/20 gegen 0/20 bei gleichen Token-Häufigkeiten), auch mit gemeinsamer Testmenge (EXP-041-Läufe auf den EXP-018-Splits: 9/10 gegen 0/10 bis 2150 Schritte, post hoc). Offen ist, ob die spektrale Konzentration wirkt oder jede strukturierte Ungleichverteilung → Kontrollarm D in [[experiments/EXP-018-split-speed/README|EXP-018]] (registriert seit Sitzung 5, D prospektiv, GPU, Nacht 27./28.).

*Ergänzt Sitzung 31 (post hoc, gesehene Seeds 30–34):* (1) **Dosis-Wirkung der Beschleunigung:** Bei gleicher Init, Testmenge und Größe generalisieren Splits umso früher, je konzentrierter ihr Paarspektrum ist (ε 8 / 2 / 1: 425–450 / 700–900 / keine bis 2000 Schritte; Ordnung 4/4 Seeds; `EXP-042/posthoc_speed_dose.py`) → Designvorschlag für [[confirm/R5_REGISTRATION_DRAFT|R5]]. (2) [[experiments/EXP-042-bias-strength/README|EXP-042]] (vorab festgelegt, n = 4): ***unklar***; ein stärkerer zweiter Split kippt die Top-5-Menge später, etwa so weit, wie der vor dem Lauf eingefrorene reine Takt es vorhersagt (eps 8: 3/4 Intervalle getroffen). Für die größte offene Frage heißt das: kein Hinweis auf einen Mechanismus jenseits eines Takts; die trennende π-Lesart steht aus.

(3) **Auch in mul 113 und add 97** generalisieren konstruierte Splits früher als gleichverteilte mit gleicher Init (EXP-043, je 10/10 Seeds, p = 0.001; R nie bis 2000, Komplement-Testmengen; `lab/confirm/speed_posthoc_other_tasks.py`). Bestätigt ist bisher nichts davon; Bestätigung: R5 (add 113), Pilot EXP-084 (Kurvenform).

*Ergänzt Sitzung 32 (vorab registriert, Pilot):* **EXP-018 *beschleunigt*:** Ein konstruierter Split E groks im Mittel 2.69 log2 (≈ ×6.5) früher als die prospektive Kontrolle D mit gleicher Gewichtsverteilung je Antidiagonale (10/10 Seeds, p = 0.001; gemeinsame Testmenge, beschränkte Zeit bis 8000). D ist so langsam wie ein Zufallssplit (L_RD 0.17, n. s.). Die Beschleunigung braucht also die konstruierte Paaranordnung. E/R-Seeds waren gesehen; Bestätigung R5 (n = 20 aus der Power-Regel) steht aus.

*Ergänzt Sitzung 32 (post hoc, Exploration; Zeiten gespeicherter Blöcke erstmals gelesen):* **B** hat eine funktionale Signatur der Festlegung. Ein Datenwechsel bei t = 25 verzögert das Grokking gegen den Lauf nur auf dem Ziel-Split (N28 28/30 Seeds, ≈ ×1.4; Replikation P3 28/30, Hypothese vorher festgelegt). Bei t = 50 gibt es in N28 keine Verzögerung (24/30 sogar früher). In add 97 und mul 113 (EXP-044) reicht sie bis 50, bei 150 sind alle Blöcke schneller. Auf Blockebene verschwinden die Kosten dort, wo die Persistenz π(t) ≈ 1 erreicht ([[NOVEL_DIRECTIONS]] N43). Bestätigung mit frischen Seeds: [[confirm/R6_REGISTRATION_DRAFT|R6]] (Entwurf, n = 30, Codex dreimal). Zur Beschleunigung: **EXP-084 (frische Seeds, Vorhersage vor dem Lauf) trifft M_share.** Die Grokking-Zeit sättigt mit dem M0-Zielanteil (Median log2(b32/b8) = −0.11, vorhergesagt −0.14; Gegenmodell „Ziehgewichte“ −0.82). Am unteren Ende (ε 1) versagt das Modell: dort ist es viel langsamer als vorhergesagt.

*Ergänzt Sitzung 34 (post hoc, N29-Seeds, keine Bestätigung):* **Die Festlegung klingt nach dem Grokking nicht ab.** Zwischen 2000 und 4000 Schritten nach einem Wechsel bei 50 wächst das log-Leistungsverhältnis alt/neu leicht weiter (D +3.68 → +4.12, Änderung +0.44 [0.26, 0.62], |D| kleiner nur in 4/20); nach einem Wechsel bei 25 legen die neuen Ziele weiter zu (20/20). Vorab festgelegte Regel: H_hold (`lab/confirm/N29_posthoc_decay_s34.py`, Commit a374f38 vor dem Lesen). Paper §6.

**Was macht die frühe Wahl gegen einen Datenwechsel fest, wenn keine gemessene Zustandsgröße den Zeitverlauf besser erklärt als die Schrittzahl?** Die Reset-Befunde (K4d/e) zeigen, *wo* ein Eingriff wirkt,

nicht *warum* die Festlegung glatt mit den Vorschritten wächst. Kandidaten vorab: **Amplitudenrennen unter Adam** (Zielamplituden wachsen ≈ linear in der aufsummierten Lernrate und legen fest, sobald sie die Init-Amplitude der

Konkurrenz einholen; H40, direkter Test [[experiments/EXP-040-we-init-scale/README|EXP-040]], passt zu EXP-039 „Λ-Uhr besser“ und EXP-059 „Momentum = Vorschritte“); welcher Netzteil dafür empfindlich ist

([[experiments/EXP-073-part-rewind/README|EXP-073]]); Zustand des Adam-Zweitmoments. *Ergänzt Sitzung 26:* Direkter Bestätigungstest der Uhr (Λ gegen Schritte, Lernrate nur vor dem Wechsel skaliert): [[confirm/R3_REGISTRATION_DRAFT|R3]]; Kandidat β₂-Horizont (50 Schritte) als Schrittuhr: [[NOVEL_DIRECTIONS]] N37. *Sitzung 27:* N37 hat im Adam-Skalarmodell keinen Mechanismus (nur noch Skalierungshypothese); der Momentum-Schwanz (N38) erklärt die K4b-Größe bei t = 25–35 (post hoc). Test beider: [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (Entwurf, nach R3). Zweite offene Frage: Hält K2-Funktion bei D₅₉ (P2f)?

*Ergänzt Sitzung 28 (Exploration):* Das Momentum trägt die Menge der alten Frequenzen, nicht ihre innere Ordnung (Momentum-Reset: Anteil −0.15 bis −0.23 bei t = 25–35, Rangerhaltung ≈ unverändert); die Ordnung steckt schon beim Wechsel in W_E.

*Ergänzt Sitzung 32 (Exploration, post hoc):* Die Festlegung hat eine **Zeitsignatur**. Ein Datenwechsel verzögert das Grokking, solange π(t) unter ≈ 0.9 liegt (Spitze bei t ≈ 25, schon t = 10 kostet), und nicht mehr, sobald die Wahl persistiert (N28, P3, EXP-056/059, N29, EXP-044). Resets, die die Persistenz stärker senken, verzögern stärker (VO > QK 19/20; Attention > MLP nur knapp), und der unmittelbare Verlustschaden erklärt das nicht. Offen bleibt, *warum* halb aufgebaute Merkmale so viel Zeit kosten. Dazu ist ungeklärt, ob es überhaupt einen Frequenz*konflikt* braucht oder ob jede frühe Datenänderung Zeit kostet (Skeptiker-Prüfung; Kontrolle [[experiments/EXP-086-same-spectrum-switch/README|EXP-086]]). *Sitzung 37 (Pilot, bekannte Seeds 400–409, vorab festgelegte Regel und Vorhersage):* Es braucht ihn. Ein Wechsel bei 25 zu einem Split mit **denselben** Zielfrequenzen kostet keine Zeit (C −0.26 log2, 4/10), zu anderen Zielen schon (+0.57); D = +0.82, 9/10, p = 0.011. Zwischen Zufallssplits beschleunigt ein Wechsel sogar (−0.80, 0/10). Die erste-Ordnung-Gegenrichtung bei F ist in A2 genauso groß wie in B, erklärt die Kosten also nicht. Ein Viertel (N28) bis die Hälfte (EXP-058, gesehene Seeds) der Kosten bei 25 verschwindet mit dem Optimizer-Zustand. Bestätigung: [[confirm/R6_REGISTRATION_DRAFT|R6]]; Architektur: [[experiments/EXP-085-mlp-switch-cost/README|EXP-085]].

*Ergänzt Sitzung 33 (post hoc, nur Split-Dateien und eingefrorene Zusammenfassungen):* Ein disjunkter zweiter Split drückt in erster Ordnung **gegen** die alten Frequenzrichtungen (N28/P3 cos −0.53/−0.54, 30/30; Projektion ≈ −0.38 des alten Eigenschubs). Bei P3 ω 0.4 verschwindet dieser Gegenterm fast (−0.02), die Persistenz bleibt aber gleich (π 0.351/0.355; registriertes Δπ 0.005 [−0.030, 0.042]). **Die Persistenz zeigt keine erkennbare Abhängigkeit von diesem Gegenterm erster Ordnung** (an der Init berechnet, nicht beim Wechsel; KI ±0.04; ε und gemeinsame Paare sind mit ω vermischt). Offen bleibt, was im Netz sie hält (Kandidat weiter: Amplitudenrennen H40, EXP-040). Neue Bestätigung für Grenze 3: [[confirm/R7_REGISTRATION_DRAFT|R7]] (2 Schichten, symmetrisch, nach dem Piloten EXP-078).

*Ergänzt Sitzung 38 (bestätigt an frischen Seeds):* **K2 verallgemeinert** ([[confirm/P4_REGISTRATION_DRAFT|P4]], je n = 15, Holm über 3): MLP mit geteiltem Embedding Δ_pow 8.89 [7.86, 9.84] (bei 10 000), Transformer d = 512 7.84 [7.23, 8.38], nicht-modulare Integer-Addition 2.35 [2.05, 2.72] (dort generalisiert kein Arm in 2000 Schritten); die Feinordnung der Ziele folgt auch dort dem Maskenspektrum ([[confirm/C3_REGISTRATION|C3]] S = 0.30 [0.20, 0.40]). Auch im 2-Schicht-Transformer: Pilot [[experiments/EXP-078-two-layer-steering/README|EXP-078]] 5.84, Bestätigung [[confirm/R7_REGISTRATION_DRAFT|R7]] 6.15 [5.86, 6.47] (10/10).

*Ergänzt Sitzung 38 (bestätigt an frischen Seeds, [[confirm/R3_REGISTRATION_DRAFT|R3]], n = 20):* Die Festlegung folgt **nicht allein** der Schrittzahl: 25 Schritte mit doppelter Lernrate legen fest wie 50 Standardschritte (HL_hold bestätigt, Holm-p 5e-6), 50 Schritte mit halber Lernrate lassen überwiegend umsteigen (Richtung 18/20), aber schwächer als die Λ-Uhr mit Mindestdifferenz 0.3 verlangt (HL_switch nicht bestätigt) → registriert *Λ-Uhr nicht bestätigt*; die Schrittuhr passt in keiner Zelle (beschreibend registriert: kein Seed erreicht ihre Mindestdifferenz).

*Ergänzt Sitzung 38 (vorab festgelegt, n = 4, bekannte Seeds):* [[experiments/EXP-040-we-init-scale/README|EXP-040]] *unklar* (registriert), inhaltlich gegen die Amplitudenschwelle H40: Die W_E-Init-Skala (0.5 bzw. 2) verschiebt das Festlegungsfenster nicht (3/4 Seeds beide (25, 50], 0/8 Zellen wie vorhergesagt), die Invarianzprüfung bevorzugt die Λ-/Schrittuhr. Offene Frage „welche Uhr“ bleibt bei R3.

*Stand Sitzung 38 (07:43), Synthese:* Von den Kandidaten für die Uhr der Festlegung ist die **Amplitudenschwelle (H40) geschwächt** (EXP-040: Init-Skala 0.5/2 verschiebt das Fenster nicht) und die **reine Schrittuhr passt nicht** (R3, beschreibend); die aufsummierte Lernrate trifft die Richtung beider R3-Zellen, als Uhr bestätigt ist sie nicht (beide Zellen beschreibend ≈ 80–86 % des Weges). Übrig: eine Mischuhr bzw. Adam-Zustand (EXP-081 Teil A/C, nach R4) und attention-gebundene Zwischenzustände (K4d/e). Programm A (Verallgemeinerung von K2) ist mit P4, R7 und R1 weitgehend abgeschlossen; offen ist dort nur, ob die Split-Beschleunigung (R5) ganz über das frühe W_E-Signal läuft (EXP-087). *Sitzung 39:* R4 bestätigt (auch ein Zufallssplit verzerrt die Wahl, siehe Tabelle). Zur R5-Frage (Exploration, frische Seeds, kein Manifest): Eingepflanztes frühes W_E-Zielsignal beschleunigt einen Zufallssplit ×11 (EXP-087), und Eingriffs- und Datenarme liegen nahe an einer gemeinsamen Kurve „Zielanteil bei 250 → Zeit“ (EXP-088: Residuum −0.39 log2 [−0.55, −0.24], registriert *unklar*). Der frühe Zielanteil ist damit der Hauptmittler; ein eigener Datenbeitrag ist nicht zu sehen.

*Ergänzt Sitzung 37 (bestätigt an frischen Seeds):* Die Zeitsignatur ist jetzt Kernaussage (**R6**), und ihre Ursache ist eingegrenzt (**R8**): Ein früher Wechsel kostet nur, wenn die **Zielmenge** wechselt. Neue Paare mit denselben Zielen kosten im Mittel nichts, obwohl sie in erster Ordnung genauso gegen A drücken. Weniger Ziel-Updates allein erklären die Kosten also nicht, eine generische frühe Störung auch nicht. Die offene Frage verschiebt sich damit zu: **Warum kostet der Umbau halb aufgebauter Merkmale auf eine andere Frequenzmenge mehr Zeit als der Aufbau von null?** Kandidaten: das Amplitudenrennen (H40, EXP-040 läuft auf der CPU); Attention-gebundene Zwischenzustände (EXP-085 beschreibend: im MLP keine Wechselkosten; K4d/e und EXP-074: VO-Reset kostet Zeit, VO > QK 18/18); ein reiner Phasenkonflikt (durch R8 nicht ausgeschlossen, weil A2 neue Phasen hat).

*Ergänzt Sitzung 40 (drei Piloten an frischen Seeds, Exploration, keine Kernaussage):* **Die Uhr der Festlegung ist eingegrenzt.** [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]]: Bei gleicher Lernratensumme Λ = 25 hält die Wahl nach 100 Schritten mit lr × 0.25 stärker fest als nach 25 Standardschritten (Δπ +0.24 [0.17, 0.34], 10/10); der Unterschied steckt schon im Zustand beim Wechsel. [[experiments/EXP-090-beta-window-lambda/README|EXP-090]]: Werden Adams Fenster vor dem Wechsel in Λ gleich lang gemacht (β′ = 1 − c(1 − β)), verschwindet der Vorsprung (e +0.16 [0.10, 0.23], 15/16; Rest +0.002 [−0.024, 0.024]); das β₁-Fenster allein genügt. [[experiments/EXP-081-optimizer-clock/README|EXP-081]]: Der Momentum-Schwanz trägt in der vom Adam-Skalarmodell vorhergesagten Größe bei (N38 gestützt, 9/10); das Fenster skaliert nicht mit β₂ (N37 verworfen); post hoc senkt ein längeres β₁-Fenster die Festlegung beim Wechsel (9/10). **Zusammen:** Die frühe Festlegung tickt in aufsummierter Lernrate Λ, wenn man Adams β₁-Verzögerung ebenfalls in Λ misst; die „Mischuhr“-Lücke von R3 ist diese Verzögerung, keine Eigenschaft der Schrittweite. Offene Frage damit: *Warum macht eine kürzere Momentum-Verzögerung die frühe Bewegung frequenzselektiver?* Nächster Schritt: Bestätigung mit eingefrorenem Manifest und zweiter c-Stufe; Literaturabgleich (Momentum als Tiefpass / Adam-Zeitskalen).

*Ergänzt Sitzung 40, 13:12 (bestätigt an frischen Seeds, eingefrorenes Manifest):* **R9 bestätigt** ([[confirm/R9_REGISTRATION_DRAFT|R9]], 8b22879a, n = 36, Holm über 3): Bei gleichem Λ legt lr × 0.25 über 100 Schritte stärker fest als mit in Λ angeglichenen β-Fenstern (+0.161 [0.132, 0.192], 36/36); mit angeglichenen Fenstern ist sie äquivalent zu 25 Standardschritten (+0.015 [0.005, 0.027], ±0.1); bei lr × 2 hebt die Angleichung die Festlegung (+0.057 [0.042, 0.073], 34/36) auf die Λ-Erwartung (beschreibend −0.007). → **Kandidat für eine Kernaussage (K5, nach Paper-Prüfung eintragen):** Die frühe Festlegung der Frequenzwahl tickt in aufsummierter Lernrate, wenn Adams β₁-Verzögerung in derselben Einheit gemessen wird; die R3-Lücke ist diese Verzögerung. Neu ist nach unserer Suche nur der Befund, nicht die β-Umskalierung (Malladi et al. 2022). *Sitzung 41, Exploration (EXP-092/093, je 16 frische Seeds, kein Urteil):* Eine Momentum-Verzögerungs-Uhr Λ_eff = c·t − c·lag(β₁, t) sagt die Festlegung bei c ≤ 1 gut voraus (MAE ≈ 0.01 ohne c = 4; β₁ nur vor dem Wechsel wirkt wie vorhergesagt), versagt aber bei größeren Lernraten zunehmend: Bei festem Λ = 24 fällt π von 0.27 (c = 2) auf 0.09 (c = 8), die frühe Bewegung ist gleich groß, aber weniger zielgenau. **Offene Frage (neu):** Hängt die Zielgenauigkeit an der Zahl der Gradientenauswertungen? EXP-094: Angleichen der β-Fenster in Λ erklärt bei c = 4 etwa die Hälfte des Rückstands; ein mit c wachsender Rest bleibt (c = 8: 0.17). K5 bleibt davon unberührt (R9 nur c = 0.25 und 2 mit angeglichenen β). *Sitzung 41: als K5 in die Tabelle eingetragen (Paper §3.15 geprüft); Korrektur: Malladis Regel ist 1 − β ∝ lr², unsere 1 − β ∝ lr ist die deterministische ODE-Angleichung (vgl. Barakat & Bianchi).*

*Ergänzt Sitzung 42 (Exploration, 16 frische Seeds, kein Urteil):* **Antwort auf die offene Frage: ja, die Zahl der Gradientenauswertungen zählt.** [[experiments/EXP-095-gradient-feedback/README|EXP-095]]: 24 normale Adam-Schritte, aber der Gradient wird vor dem Wechsel nur alle k Schritte neu ausgewertet. Mit 3 Auswertungen (g8) ist der Rückstand gegen 24 Auswertungen +0.141 [0.060, 0.211], genau so groß wie mit 3 großen Schritten und angeglichenen Fenstern (g8 − c8b = 0.000 [−0.036, 0.035]; Vorbehalt: verschiedener Adam-Zähler nach dem Wechsel, 3 gegen 24, eine Aufhebung ist möglich). Mit 6 Auswertungen ist er fast weg (+0.020, n. s.). Mit nur dem Anfangsgradienten (g24) +0.187: W_E bewegt sich weiter, aber unselektiver. **Lesart:** Die frühe Festlegung braucht neu ausgewertete Gradienten entlang des Wegs (Selbstverstärkung der Ziele oder Korrektur der veralteten Anfangsrichtung, nicht getrennt); die erste Ordnung (§5 im Paper) trägt nur einen kleinen Teil der Persistenz (π 0.10 gegen 0.28). Grenzen: Anzahl und Abstand der Auswertungen nicht getrennt, Adam statt Gradientenfluss, eine Aufgabe. *Post hoc (Nachtrag a, gesehene Daten):* Ohne Auffrischung (g24) wachsen die Ziele normal, aber die Nicht-Ziele um ×1.48 mehr; bei seltener Auffrischung (g8) wachsen vor allem die Ziele weniger (×0.75). Zwei Wege, noch kein Test.

*Ergänzt Sitzung 43 (post hoc an EXP-095, numpy, gesehene Daten, Exploration):* **Einschränkung der g24-Lesart.** Mit eingefrorenem Gradienten sind Adams Momente exakt m̂ = g₀, v̂ = g₀², jeder Schritt ist also ≈ lr · sign(g₀) je Element (99.9 % der W_E-Einträge innerhalb 10 % eines vollen Vorzeichenschritts). Binarisiert man die normale n24-Bewegung, sinkt ihr Zielanteil um 56 % [53, 59] der Lücke zu g24 (f 0.182 → 0.160, g24 0.143; um den Weight-Decay-Schwund korrigierte Bewegung; sign(D_n24) ist nur ein Ersatz für sign(g₀); über das π-Defizit selbst sagt das nichts). „Nur der Anfangsgradient legt schwach fest“ heißt deshalb „unter Adam ≈ signSGD (mit entkoppeltem Weight Decay)“. Wie viel die lineare erste Ordnung trägt, ist offen. Trennender Versuch: [[experiments/EXP-097-sign-vs-staleness/README|EXP-097]] (vorbereitet, nach R10). Die Aussage „Auswertungen zählen“ (g8 ≈ c8b, e8) berührt das vermutlich nicht direkt (nicht getestet): Die Bewegungen von g8 (45 % reine Vorzeichenschritte) und c8b (33 %) sind weniger quantisiert als n24 (54 %) (beschreibend).

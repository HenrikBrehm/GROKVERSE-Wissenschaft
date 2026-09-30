---
id: logic_audit_S55_appK
status: teilweise umgesetzt
datum: 2026-09-30
tags: [paper, pruefung]
---
# Zusammenhangsprüfung Anhang K (Sitzung 55, 03:20 gemessen)

Zurück: [[paper/STATUS]] · [[LAB]]. Unabhängiger Agent, nur lesend, nach den Einschüben der Sitzung 55 (EXP-121, Kommutativitätsabsatz, Abb. 15). Zahlen nicht erneut geprüft.

**Umgesetzt (03:20):** 3 (EXP-121: „did not stall within 4000 steps“, „avoid“ statt „leave“, „did not stay on the plateau“), 5 („would be needed“), 6 (LM: „behaved as if it had learned the swap“), 7 (Satz „toy model: mostly first stage; LM stalled in the second; need not share a mechanism“; Bildunterschrift „a change of shape, not of duration“), 8 (die zwei nicht bestimmbaren Einheiten genauer), 9 (Mindesteffekt vor dem p-Wert), 11 (Kopf nennt Pilot EXP-122 und Hauptblock EXP-123).

**Offen für die nächste Sitzung:**
1. **Kopfzeile des Anhangs (kursiv) veraltet:** nennt nur LM1 als Bestätigung und Seeds 3800–3809/3850–3851; inzwischen auch LM1-F, EXP-118 (Seed 3862), EXP-122/123 (R5-Einheiten); „independently recomputed“ widerspricht dem Text. Vorschlag des Prüfers: „All results … except the two LM1 confirmations (LM1, LM1-F; fresh seeds 4000–4009) are explorations, with readings fixed before each run; seeds are given per block. Results marked 'independently recomputed' were checked; the others were not.“ – vorher prüfen, welche Nachrechnungen es wirklich gab.
2. **Zwei Maße des Maskenspektrums kollidieren:** Absatz „Token frequencies“ (EXP-104): „mask target share 0.65–0.74 against 0.17–0.19“; EXP-121-Satz: „top-5 mask share … 0.27–0.30 (equal-count F/G) … 0.17–0.19 (engineered EXP-119)“. Zielanteil kann den Top-5-Anteil nicht übersteigen → Maße/Normierungen klären (EXP-104 `m0_target_share` vs. `mask_power`-Top-5 in Sitzung 55; evtl. m = 0 gegen m = 500 Tauschzüge), dann einheitlich benennen. **Geklärt und umgesetzt (Sitzung 55, 03:21 gemessen):** kein Widerspruch der Maße, sondern verschiedene Tauschzug-Stufen: EXP-104 `m0_target_share` 0.64–0.74 bei m = 0/10, 0.27–0.30 bei m = 500 (= die im LM genutzten Splits; bei m = 500 sind die Ziele die Top-5). Der Satz „0.65–0.74 against 0.17–0.19“ galt nicht für alle drei Stufen → „0.64–0.74 with 0 or 10 swap moves and 0.27–0.30 after 500“.
4. ~~Satz „a count effect is not excluded“ auf EXP-121 und Kontrolle D verweisen.~~ Umgesetzt 03:21.
10. Reihenfolge im langen Absatz (LM1-F vor LM1), doppelter Satz „with tied embeddings this ablation acts on input and output vectors alike“, veraltetes „queued“ (EXP-116/EXP-113; 03:21: auf „running“ gesetzt, nach den Auswertungen durch Ergebnisse ersetzen), Nummerierung „Figure K1“ gegen „Figure 15“ (Abbildungsliste Z. 90 nennt Abb. 15 nicht).
12. Den langen Absatz in fünf Absätze mit fetten Einleitungen teilen (Vorschlag: Aufbau/EXP-118 · Bestätigungen LM1, LM1-F · Beginn · Häufigkeiten/gebundene Einbettung EXP-115/117/120 · Zufallssplits und Kommutativitäts-Plateau EXP-119/121).
- ~~Zusatz „… in the language model“~~ umgesetzt 03:21 (Satz nach EXP-119 Nachtrag 2 ersetzen).

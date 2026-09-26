---
id: EXP-031
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-031: Ist der frühe W_E-Abdruck kausal? Verpflanzung bei Schritt 500

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N13) · Vorgänger
[[experiments/EXP-030-imprint-residue/README|EXP-030]] (Mediation, korrelativ) · verwandt
[[experiments/EXP-010-init-swap/README|EXP-010]] (Eingriff bei der Init) · [[experiments/EXP-020-data-switch/README|EXP-020]] (Datenwechsel).

## Anlass

EXP-030: Was die Maske über die Endfrequenzen verrät, steckt fast ganz im W_E-Zustand bei Schritt 250. Das ist eine
Mediation über Korrelation. Der Eingriff dazu: Man gibt einem Lauf B bei Schritt 500 (Memorisierungsphase) die
Einbettung eines anderen Laufs A und trainiert auf B's Daten mit B's übrigen Gewichten weiter. Wählt das Netz dann die
Frequenzen von A (Abdruck kausal) oder die von B (Daten und übrige Gewichte bestimmen)?

## Versuch (vorab festgelegt 2026-09-26 10:02 Berlin, vor jedem EXP-031-Lauf)

| Punkt | Festlegung |
|---|---|
| **Daten** | Studienläufe Seeds 0–9 (Checkpoints bei Schritt 500: nur Gewichte). B ∈ {0, 2, 4, 6, 8}, Spender A = B + 1 |
| **Arme** | *transplant*: B's Gewichte bei 500, W_E (alle 114 Zeilen) von A bei 500, frisches AdamW, B's Split, weiter bis Schritt 3000. *control*: dasselbe ohne Tausch (trennt den Effekt des AdamW-Neustarts ab). 10 Läufe |
| **Zielmengen** | T_X = Top-5 des gespeicherten Endmodells (25 000 Schritte) von Lauf X (`freq_ban._stored_final_W_E`); verglichen werden nur die unterscheidenden Teile T_A∖T_B und T_B∖T_A |
| **Messgröße** | K = Top-5 von W_E bei Schritt 3000; d = \|K ∩ (T_A∖T_B)\| − \|K ∩ (T_B∖T_A)\| |
| **Gültigkeit** | Kontrollarm: mittleres d < 0 (das Netz findet ohne Eingriff zu B's Frequenzen). Sonst *nicht auswertbar* (Messung taugt nicht). Läufe vollständig und endlich |
| **Primär** | Arm transplant: d > 0 in 5/5 Paaren → *Abdruck kausal* (Vorzeichentest p = 1/32); mittleres d ≤ 0 → *Daten/übrige Gewichte bestimmen*; sonst *gemischt* |
| **Sekundär** | dasselbe mit den Top-5 bei Schritt 500 statt der Endmodelle; Genauigkeit direkt nach dem Tausch; Test-Genauigkeit bei 3000; Zeitverlauf der Überlappungen |
| **Was dagegen spräche** | d ≤ 0 im Transplantationsarm: Dann ist der frühe Abdruck nur Anzeiger, und die übrigen Gewichte oder die Daten legen die Wahl fest |
| **Grenzen** | Der Tausch bricht das Zusammenspiel von W_E mit den übrigen Gewichten (Genauigkeit fällt vermutlich stark). Messung bei 3000 statt am Ende (Budget; die Top-5 stehen laut EXP-003/012 früh fest). Nur 5 Paare, Explorationsseeds 0–9 der Studie. Frisches AdamW in beiden Armen |
| **Budget** | 2500 Schritte × ~0.13 s ≈ 5.5 min je Lauf, 10 Läufe ≈ 55 min; Smoke: 20 Schritte (Laden, Tausch, Endlichkeit) |

## Befehle

    sh lab/experiments/EXP-031-we-transplant/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-031-we-transplant/analyze.py

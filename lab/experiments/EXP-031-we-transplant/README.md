---
id: EXP-031
status: zurückgestellt
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

## Nachtrag a (10:09 Berlin): zurückgestellt nach Codex-Review, kein Lauf

Codex (`codex_review_2026-09-26.txt`, „needs-attention“, 3 × high, 2 × medium), selbst geprüft, alle zutreffend:
1. Die `=`-Zeile (W_E[p]) wird mitverpflanzt und verändert jede Vorhersage; nur W_E[:p] tauschen, dazu ein Schein-Arm
   nur mit der `=`-Zeile.
2. **Spender-Identität verwechselt Split-Abdruck und Init-Lotterie:** A's W_E bei 500 trägt A's Init und A's Split. Ein
   Folgen von A belegt nur, dass etwas in W_E kausal ist. Nötig: gekreuzte Spender (gleiche Init/anderer Split und
   umgekehrt, bis Schritt 500 eigens trainiert).
3. **Endpunkt bei 3000 instabil:** Die Studienläufe generalisieren erst bei 5600–10 300; bei ~3040 teilen die Top-5 mit dem
   Endmodell teils nur 2/5 (Seed 2) oder 3/5 (Seeds 5, 7). Primär müsste Δd = d_transplant − d_control je Paar sein, mit
   Gültigkeit je Paar, gemessen nach der Generalisierung.
4. Thread-Zahl (Studie 1, hier 4), Konfiguration und Split-Hash werden nicht gegen das Manifest geprüft.
5. Läufe mit falschem Budget würden unbemerkt akzeptiert.
**Entscheidung:** nicht ausführen. Der nötige Umbau (gekreuzte Spender, Läufe bis nach der Generalisierung, ~15–20 min je
Lauf) sprengt diese Sitzung. Die Frage bleibt im BACKLOG; der Code hier ist als **ungeprüfter Entwurf** zu lesen.

## Befehle

    sh lab/experiments/EXP-031-we-transplant/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-031-we-transplant/analyze.py

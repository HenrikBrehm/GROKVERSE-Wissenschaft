---
id: EXP-135
status: vorbereitet
datum: 2026-10-01
tags: [exp/vorbereitet, lab/lm, neu/kandidat]
verwandt: ["[[confirm/LM1_REGISTRATION|LM1]]", "[[experiments/EXP-020-data-switch/README|EXP-020]]", "[[experiments/EXP-107-lockin-epochs/README|EXP-107]]", "[[experiments/EXP-134-text-pretrain-steering/README|EXP-134]]", "[[FINDINGS]]"]
---
# EXP-135: Frühe Festlegung (K4) im Sprachmodell? Faktenwechsel F → G nach t Schritten (Pilot)

Zurück zu [[LAB]]. **Exploration (2 Seeds × 3 Wechselzeitpunkte), keine Bestätigung.**

**Bezug zu FINDINGS:** Verallgemeinerung des zweiten Hauptbefunds (K4/K4c: Festlegung in den ersten 25–50 Schritten; unter Minibatch ≈ √(N/B), N54b) auf das Sprachmodell (Regel 15c, Programm B „Persistenz nach Datenwechsel“). Bisher gibt es im LM nur K2 (LM1/LM3), keinen Wechselversuch. Entscheidet zwischen zwei ausdrücklichen Konkurrenzmodellen (Regel 18c).

## Vorab (Sitzung 64, 01.10. 00:02 Berlin gemessen, vor jedem Lauf)

- **Frage:** Legt sich das LM früh auf die Frequenzen des ersten Faktensatzes fest, obwohl die Steuerung im LM erst mit dem Faktenlernen sichtbar wird?
- **Konkurrenzmodelle:** (Start) wie im Spielzeugmodell legt sich die Wahl innerhalb weniger Epochen fest (eine LM1-Epoche = 3831 Fakten / 608 je Schritt ≈ 6.3 Schritte) → schon t = 250 hinterlässt F im Endspektrum. (Lernen) Die Wahl entsteht erst mit dem Faktenlernen (LM1-Partner: F-Neigung L bei Schritt 2000 noch ≈ 0 (−0.01 / +0.05), bei 3000 schon 1.95 / 2.78; S59: keine Steuerung bei 1000) → Wechsel bei 250 und 1000 hinterlassen nichts, bei 3000 bleibt F.
- **Aufbau:** unveränderter Trainer `lm_stage2.py`, Wrapper `ft_switch.py` tauscht nur die Stream-Klasse: nach t·32 Sequenzen wird der Faktensatz G (neue Permutation aus demselben Faktengenerator); Modell, AdamW-Zustand und Textstrom laufen weiter. LM1-Konfiguration (K = 19, Antwortverlust, 6000 Schritte nach dem Wechsel = G-Budget der LM1-Referenz), Modell-Seeds 4100/4101, LM1-Splits 4000/4001 (F und G disjunkt, je 3831 Fakten, gemeinsame Testmenge). t ∈ {250, 1000, 3000} → 6 Läufe mit 6250 / 7000 / 9000 Schritten.
- **Messgröße:** F-Neigung L(P) = log(P(Ziele F) / P(Ziele G)) des Zahlzeilen-Spektrums; Persistenz π = (L_Wechsel − L_G) / (L_F − L_G) am Ende, mit L_F, L_G aus den LM1-Läufen F und G desselben Modell-Seeds bei 6000 (von Grund auf, gleicher Trainer und Gerät; Bestätigungsblock, schon gesehen). π ≈ 1: F bleibt, π ≈ 0: wie nur G.
- **Lesarten (`analyze.py`):** je t „haelt fest“ (π > 0.5 in beiden Seeds), „ueberschrieben“ (π < 0.2 in beiden), sonst „teilweise“. Tor: Testgenauigkeit > 0.5 in ≥ 5/6 Läufen, sonst „nicht auswertbar (lernt G nicht)“. Gesamt: **„Festlegung am Anfang“** (alle drei t halten fest), **„Festlegung mit dem Lernen“** (250 und 1000 überschrieben, 3000 hält fest), **„keine Festlegung“** (alle überschrieben), sonst „unklar“.
- **Erwartung:** „Festlegung mit dem Lernen“ (Steuerung entsteht spät; das Spielzeugmodell legt sich dagegen fest, bevor es lernt – dort ist die frühe Bewegung schon frequenzselektiv, im LM mit 19 Fakten je Sequenz nach S59 nicht).
- **Was gegen die Erwartung spräche:** t = 250 hält fest (dann wirkt eine unsichtbare frühe Prägung wie im Spielzeugmodell), oder t = 3000 wird überschrieben (dann ist das LM plastischer als das Spielzeugmodell; die Festlegung wäre dort eine Eigenschaft des kleinen Datensatzes/Modells).
- **Deutung vorab:** „am Anfang“ → K4 überträgt sich trotz später Sichtbarkeit (stark, dann Bestätigung erwägen). „mit dem Lernen“ → im LM ist die Festlegung an das Faktenlernen gebunden, nicht an eine feste frühe Schrittzahl; passt zu N54b (Festlegung zählt nicht in Schritten) und zu EXP-114 (Steuerung kommt mit dem Lernen). „keine Festlegung“ → Grenze von K4 im LM (Pilot). Immer: 2 Seeds, keine Größen- oder Allgemeinheitsaussage.
- **Beschreibend:** L beim Wechsel, L-Verlauf, Genauigkeit auf den alten F-Fakten am Ende (Vergessen), Testgenauigkeit.
- **Budget/Abbruch:** LM1 allein ≈ 0.12 s/Schritt, unter Last bis ≈ 0.35 → 6 Läufe mit zusammen 44 750 Schritten ≈ 1.5–4.4 GPU-h; 3 Worker, gpu_gb 3.5, job_minutes 300, stall_minutes 20. Abbruch bei NaN (Trainer) oder Absturz.
- **Bereits gesehene Daten:** LM1 vollständig (Referenzen, L-Verläufe oben), EXP-114/S59 (spätes Entstehen der Steuerung). Davon beeinflusst: die Wahl t = 3000 (nach dem Sprung der F-Neigung) und t = 1000 (vorher).
- **Selbsttest** (`--selftest`): Faktenwechsel genau nach t·Batch Sequenzen, danach nur G-Fakten; Wiederaufnahme aus einem Checkpoint nach dem Wechsel auf der CPU bitgleich (01.10. 00:01, 41 s; auf der GPU nicht bitgleich wegen nichtdeterministischer Kernel, dort nur Funktionsprobe).
- **Unabhängige Codeprüfung (Claude-Agent, nur lesend, vor 00:07):** keine Blocker; Wechselzeitpunkt exakt (jede Sequenz 257 Tokens, Wechsel bei der ersten Sequenz von Schritt t + 1, Snapshot bei t vor dem Wechsel), Splits disjunkt, Konfiguration = LM1. **Ein echter Fehler übernommen:** Wiederaufnahme aus dem Checkpoint genau bei Schritt t (t = 1000/3000 fallen auf Checkpoint-Schritte) hätte die Faktenreihenfolge verändert (`>=` → `>`); Selbsttest um diesen Fall erweitert und gegen eine Kopie mit dem alten Code geprüft (alte Fassung fällt durch, neue besteht, CPU, vor 00:07). Außerdem: `switch.json` wird vor dem Lauf verglichen/geschrieben (Wrapper-Hash); Gesamtlesart „am Anfang“ jetzt monoton (alle drei t); Hinweis: Bei Seed 4100 ist die F-Neigung bei 3000 (1.95) größer als bei 6000 (1.29), π > 1 ist bei t = 3000 möglich (Einordnung unberührt).

## Befehle

Jobs: `jobs_45zz_exp135_switch.txt` → `lab/queue/inbox/45zz_exp135_switch.jobs`. Auswertung: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-135-lm-switch-lockin/analyze.py`.

## Ergebnis

(offen)

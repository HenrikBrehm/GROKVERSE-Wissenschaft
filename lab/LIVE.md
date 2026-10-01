---
tags: [lab/live]
---
# LIVE: Laborsitzung 70

- **Sitzungsstart:** 2026-10-01 13:49 Berlin (11:49Z, vom Runner)
- **Deadline:** 2026-10-01 16:49 Berlin (14:49Z)
- **Zuletzt aktualisiert:** 14:10

## Gerade

- Warte auf den letzten EXP-141-Lauf (Zahlen bis 502, 18 100 Paare); bisher lernen 5 von 5 Läufen die Regel (gen 5 200–10 275 Schritte).
- Schreibe derweil die Auswertung für EXP-143.

## Als Nächstes

1. EXP-141 auswerten (Frage 1 + Nachtrag a/b).
2. EXP-143-Auswertung vorbereiten; R15 (Teil bis 400) läuft nach EXP-141, dann EXP-143.

## Verlauf dieser Sitzung
- 14:07 **EXP-143 eingereiht:** der LeDoux-Test selbst – Zahlen bis 9972, nur 0,3 % der Aufgaben, kleine Stapel. Vier Läufe: zufällige oder gezielte Auswahl × gemischte oder sortierte Reihenfolge. Frage: Gewinnt die Auswahl oder die Reihenfolge? Kurzer Probelauf auf der Grafikkarte lief (0,025 s pro Schritt, 2,1 GB).
- 14:05 Gleichwertigkeitstest bestanden: Mit der Hülle kommen exakt dieselben Gewichte heraus wie ohne.
- 13:59 Hülle `freq_ban_large.py` geschrieben; erster Test: Gewichte bitgleich, Genauigkeit nur in der 7. Stelle verschieden (float32-Mittel) → Toleranz 1e-6; Konstruktion für p = 9973 nachgebaut (bei p 113/307 identisch zum Original).
- 13:50 Start; STATE gelesen, kein STOP, Fenster offen; Dienst läuft (EXP-141 Lauf 9/12).

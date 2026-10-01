---
tags: [lab/live]
---
# LIVE: Laborsitzung 70

- **Sitzungsstart:** 2026-10-01 13:49 Berlin (11:49Z, vom Runner)
- **Deadline:** 2026-10-01 16:49 Berlin (14:49Z)
- **Zuletzt aktualisiert:** 14:18

## Gerade

- GPU-Dienst rechnet R15 (Teil „Zahlen bis 400“, 3 parallel, ≈ 2 von 30 fertig); EXP-143 (LeDoux-Test) startet danach automatisch.
- Ich bereite die nächsten Schritte vor (Auswertungen stehen schon bereit).

## Als Nächstes

1. R15-Fortschritt beobachten; EXP-143-Start prüfen (erste Schritte, Speicher, Tempo).
2. Nach 60/60: R15 auswerten und unabhängig nachrechnen lassen.

## Verlauf dieser Sitzung
- 14:18 Vor dem Start von EXP-143 geprüft: Die gezielte Auswahl bei Zahlen bis 9972 trägt ihr Frequenzmuster sehr sauber (viel klarer über dem Rauschen als bei 400/502); die „sortierte Reihenfolge“-Frequenzen sind in beiden Mengen neutral.
- 14:15 Literatur: Gromov (2023) hat schon vermutet, dass eine geschickte Auswahl der Trainingsdaten mit weniger Daten auskommt – ohne es zu testen. Wir zitieren das; unser Beitrag ist der Test mit Kontrollen und die Frequenzrichtung. Gromov fehlt bisher im Paper (vermerkt).
- 14:14 Unabhängige Nachrechnung von EXP-141: alle Zahlen stimmen; der Exponent ist unsicherer als ich schrieb (zwischen etwa 1,1 und 1,6). Korrigiert.
- 14:12 **EXP-141 fertig:** Bei Zahlen bis 502 lernen beide Datenmengen (16 100 und 18 100 Paare) die Regel. Das passt zur Erklärung „es zählt, wie viele Paare jede einzelne Zahl sieht“ (≈ 30 je Zahl), nicht zur Margin-Theorie. Die gezielte Auswahl steuert die Frequenzen weiter. Die nötige Datenmenge wächst etwas schneller als die Zahlengröße (Exponent ≈ 1,2–1,3).
- 14:07 **EXP-143 eingereiht:** der LeDoux-Test selbst – Zahlen bis 9972, nur 0,3 % der Aufgaben, kleine Stapel. Vier Läufe: zufällige oder gezielte Auswahl × gemischte oder sortierte Reihenfolge. Frage: Gewinnt die Auswahl oder die Reihenfolge? Kurzer Probelauf auf der Grafikkarte lief (0,025 s pro Schritt, 2,1 GB).
- 14:05 Gleichwertigkeitstest bestanden: Mit der Hülle kommen exakt dieselben Gewichte heraus wie ohne.
- 13:59 Hülle `freq_ban_large.py` geschrieben; erster Test: Gewichte bitgleich, Genauigkeit nur in der 7. Stelle verschieden (float32-Mittel) → Toleranz 1e-6; Konstruktion für p = 9973 nachgebaut (bei p 113/307 identisch zum Original).
- 13:50 Start; STATE gelesen, kein STOP, Fenster offen; Dienst läuft (EXP-141 Lauf 9/12).

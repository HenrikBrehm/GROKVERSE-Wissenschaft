---
tags: [lab/live]
---
# LIVE: Laborsitzung 70

- **Sitzungsstart:** 2026-10-01 13:49 Berlin (11:49Z, vom Runner)
- **Deadline:** 2026-10-01 16:49 Berlin (14:49Z)
- **Zuletzt aktualisiert:** 14:21

## Gerade

- Ein unabhängiger Prüfer greift die neue Hülle und den Aufbau von EXP-143 an, bevor die Läufe starten.
- GPU-Dienst: R15 (Zahlen bis 400) 3/30 fertig, 3 laufen; danach EXP-143 (zuerst mit schwächerem Weight Decay 0,1).

## Als Nächstes

1. Prüfbericht lesen; nötige Korrekturen vor dem Start einbauen.
2. EXP-143-Start beobachten (Tempo, Speicher); R15 nach 60/60 auswerten.

## Verlauf dieser Sitzung
- 14:21 EXP-143 vor dem Start verbessert: Mit unserem üblichen starken Weight Decay (1,0) lernt das Netz bei kleinen Stapeln in früheren Versuchen gar nicht. Deshalb rechnet EXP-143 jetzt zuerst mit 0,1 (wie LeDoux); die 1,0-Läufe bleiben als Nebenvergleich.
- 14:18 Vor dem Start von EXP-143 geprüft: Die gezielte Auswahl bei Zahlen bis 9972 trägt ihr Frequenzmuster sehr sauber (viel klarer über dem Rauschen als bei 400/502); die „sortierte Reihenfolge“-Frequenzen sind in beiden Mengen neutral.
- 14:15 Literatur: Gromov (2023) hat schon vermutet, dass eine geschickte Auswahl der Trainingsdaten mit weniger Daten auskommt – ohne es zu testen. Wir zitieren das; unser Beitrag ist der Test mit Kontrollen und die Frequenzrichtung. Korrektur 14:18: Gromov ist im Paper schon zitiert (Einleitung); neu ist nur der Bezug auf seine Vermutung zur Datenauswahl.
- 14:14 Unabhängige Nachrechnung von EXP-141: alle Zahlen stimmen; der Exponent ist unsicherer als ich schrieb (zwischen etwa 1,1 und 1,6). Korrigiert.
- 14:12 **EXP-141 fertig:** Bei Zahlen bis 502 lernen beide Datenmengen (16 100 und 18 100 Paare) die Regel. Das passt zur Erklärung „es zählt, wie viele Paare jede einzelne Zahl sieht“ (≈ 30 je Zahl), nicht zur Margin-Theorie. Die gezielte Auswahl steuert die Frequenzen weiter. Die nötige Datenmenge wächst etwas schneller als die Zahlengröße (Exponent ≈ 1,2–1,3).
- 14:07 **EXP-143 eingereiht:** der LeDoux-Test selbst – Zahlen bis 9972, nur 0,3 % der Aufgaben, kleine Stapel. Vier Läufe: zufällige oder gezielte Auswahl × gemischte oder sortierte Reihenfolge. Frage: Gewinnt die Auswahl oder die Reihenfolge? Kurzer Probelauf auf der Grafikkarte lief (0,025 s pro Schritt, 2,1 GB).
- 14:05 Gleichwertigkeitstest bestanden: Mit der Hülle kommen exakt dieselben Gewichte heraus wie ohne.
- 13:59 Hülle `freq_ban_large.py` geschrieben; erster Test: Gewichte bitgleich, Genauigkeit nur in der 7. Stelle verschieden (float32-Mittel) → Toleranz 1e-6; Konstruktion für p = 9973 nachgebaut (bei p 113/307 identisch zum Original).
- 13:50 Start; STATE gelesen, kein STOP, Fenster offen; Dienst läuft (EXP-141 Lauf 9/12).

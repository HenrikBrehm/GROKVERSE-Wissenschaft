---
tags: [lab/live]
---
# LIVE: Laborsitzung 9

- **Sitzungsstart:** 2026-09-26 14:49 Berlin (12:49Z, vom Runner)
- **Deadline:** 2026-09-26 17:49 Berlin (15:49Z)
- **Zuletzt aktualisiert:** 15:33 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

Neue Warteschlange queue_s9.sh läuft: EXP-020 Seed 33 (danach 34, bis ~16:25), dann **EXP-037** (~42 min), dann EXP-035.

## Als Nächstes

Seeds 33/34 auswerten (Vorhersage Nachtrag d); EXP-037 auswerten, danach Ablation der fremden Frequenzen (von Hand).

## Verlauf dieser Sitzung

- 15:33 EXP-020 Seed 33 (vorläufig, ohne t = 400/1000): wieder Festlegung zwischen Schritt 25 und 50, 4. Seed in Folge.

- 15:15 Codex fand 3 Schwächen in EXP-037 (Urteile überlappten, Kontrolle fehlte, Smoke zu schwach). Alles behoben; zusätzlich Kontrolllauf „F 100 Schritte, dann G“. Warteschlange umgestellt, EXP-037 läuft heute noch.

- 15:06 **EXP-037 vorbereitet:** Was passiert, wenn F und G sich in den ersten 200 Schritten ständig abwechseln? Gewinnt dann die Initialisierung? 6 kurze Läufe.
- 15:04 Dauerhaft oder nur langsam? In der G-Phase wird die F-Festlegung sogar stärker (F-Anteil 0,36 → 0,91). Kein Langlauf nötig.

- 15:02 **EXP-020 Seed 32:** wieder Festlegung zwischen Schritt 25 und 50, vor der Memorisierung. 3 von 3 Seeds, gleiches Intervall.
- 15:02 Codex fand 4 Schwächen im EXP-036-Entwurf (u. a. Frequenzen als unabhängig gezählt). Umgebaut: 7 unabhängige Inits, Test über Paare, strenge Laufprüfung. Weiter nicht gestartet.

- 14:54 **EXP-036 vorbereitet:** Gleicher Split, neue Initialisierung. Wenn die fremden Frequenzen aus der Init stammen, müssen sie mit ihr wandern. 15 Läufe, ~65 min, noch nicht gestartet.
- 14:52 **Neue Beobachtung:** Wechselt man früh (≤ 50 Schritte) die Daten, tauchen in allen 3 Seeds Frequenzen auf, die zu keinem der beiden Splits gehören, meist solche, die schon in der Initialisierung stark waren. Als Vorhersage für Seeds 33/34 festgelegt (noch nicht gelaufen).
- 14:50 Stand gelesen, Wächter ok (bis 17:49 Berlin), keine Prozesse aktiv; `queue_s8.sh` gestartet.

---
tags: [lab/live]
---
# LIVE: Laborsitzung 9

- **Sitzungsstart:** 2026-09-26 14:49 Berlin (12:49Z, vom Runner)
- **Deadline:** 2026-09-26 17:49 Berlin (15:49Z)
- **Zuletzt aktualisiert:** 17:15 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

EXP-035 (Warmup) läuft an: Seed 30 „nur F“ mit Warmup. Abschlussbericht ist geschrieben (JOURNAL), wird am Ende ergänzt.

## Als Nächstes

Nächste Sitzung 19:49 (nur Denkarbeit), Läufe ab 00:00: `queue_s10.sh` (EXP-035 → EXP-038 → EXP-036 → EXP-034).

## Verlauf dieser Sitzung

- 17:15 Codex hat die EXP-037-Schlüsse angegriffen: zu weit formuliert. Eingeengt: Belegt ist nur, dass *wiederholtes* Wechseln in den 3 bekannten Seeds dieselben fremden Frequenzen bringt; ob es am Konflikt oder an der Init liegt, ist nicht gezeigt. Die neue Vorhersage für EXP-036 gilt nur noch beschreibend, bis sie sauber kalibriert ist.
- 17:12 EXP-035, erster Wechsellauf: Mit Warmup ist das Netz bei Schritt 50 noch nicht festgelegt (ohne Warmup schon). Ein Lauf, noch kein Urteil.

- 17:06 Abschlussbericht und Wiederaufnahme geschrieben. Reihenfolge für die Nacht festgelegt.
- 17:05 **Neue Idee aus den Daten:** Die Konfliktfrequenzen sind genau die, die *beide* Datensätze früh als Zweitbeste stützen (7 von 7). Als Vorhersage für EXP-036 festgelegt, bevor es läuft.
- 17:03 EXP-037 Nebenarm (Blöcke von 25 Schritten): gleiches Bild, wieder dieselben Konfliktfrequenzen.

- 16:50 **EXP-037 Ergebnis (vorab festgelegt: gestützt):** Wechseln sich F und G in den ersten 200 Schritten ständig ab, entstehen in allen 3 Seeds „Konfliktfrequenzen“, und zwar jeweils dieselben wie beim frühen Einzelwechsel. Gleiche Datenmenge ohne Wechselspiel: keine. Die Konfliktfrequenzen werden wirklich genutzt (Entfernen kostet so viel wie bei Zielfrequenzen). **Ob sie aus der Initialisierung stammen, bleibt offen.**

- 16:31 **EXP-038 vorbereitet:** Nach der Festlegung wird entweder nur das Embedding oder alles andere zurückgesetzt. Hält das Netz dann an F fest? Codex: 3 Einwände, alle eingebaut.
- 16:31 EXP-037, erste Läufe: Im Wechselspiel tauchen dieselben fremden Frequenzen auf wie beim Einzelwechsel desselben Seeds (34 bzw. 22).

- 16:22 **EXP-020 abgeschlossen:** In allen 5 Seeds legt sich das Netz zwischen Schritt 25 und 50 fest. Das vorab festgelegte Urteil lautet trotzdem „nicht bestätigt“ (4 von 5), weil eine zu strenge Regel an einer Oberwelle hängen blieb. **Die Init-Deutung der fremden Frequenzen hält an neuen Seeds nicht.** EXP-028: teilweise.

- 15:48 Seed 33 fertig: wieder Festlegung bei 25–50 Schritten, aber nach strenger Regel „gegen“ (nur wegen einer Oberwelle). Fremde Frequenz 38 hat einen **mittleren** Init-Rang (34), passt nicht zur Init-Deutung. Ehrlich so notiert.

- 15:33 EXP-020 Seed 33 (vorläufig, ohne t = 400/1000): wieder Festlegung zwischen Schritt 25 und 50, 4. Seed in Folge.

- 15:15 Codex fand 3 Schwächen in EXP-037 (Urteile überlappten, Kontrolle fehlte, Smoke zu schwach). Alles behoben; zusätzlich Kontrolllauf „F 100 Schritte, dann G“. Warteschlange umgestellt, EXP-037 läuft heute noch.

- 15:06 **EXP-037 vorbereitet:** Was passiert, wenn F und G sich in den ersten 200 Schritten ständig abwechseln? Gewinnt dann die Initialisierung? 6 kurze Läufe.
- 15:04 Dauerhaft oder nur langsam? In der G-Phase wird die F-Festlegung sogar stärker (F-Anteil 0,36 → 0,91). Kein Langlauf nötig.

- 15:02 **EXP-020 Seed 32:** wieder Festlegung zwischen Schritt 25 und 50, vor der Memorisierung. 3 von 3 Seeds, gleiches Intervall.
- 15:02 Codex fand 4 Schwächen im EXP-036-Entwurf (u. a. Frequenzen als unabhängig gezählt). Umgebaut: 7 unabhängige Inits, Test über Paare, strenge Laufprüfung. Weiter nicht gestartet.

- 14:54 **EXP-036 vorbereitet:** Gleicher Split, neue Initialisierung. Wenn die fremden Frequenzen aus der Init stammen, müssen sie mit ihr wandern. 15 Läufe, ~65 min, noch nicht gestartet.
- 14:52 **Neue Beobachtung:** Wechselt man früh (≤ 50 Schritte) die Daten, tauchen in allen 3 Seeds Frequenzen auf, die zu keinem der beiden Splits gehören, meist solche, die schon in der Initialisierung stark waren. Als Vorhersage für Seeds 33/34 festgelegt (noch nicht gelaufen).
- 14:50 Stand gelesen, Wächter ok (bis 17:49 Berlin), keine Prozesse aktiv; `queue_s8.sh` gestartet.

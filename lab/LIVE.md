---
tags: [lab/live]
---
# LIVE: Laborsitzung 10

- **Sitzungsstart:** 2026-09-26 17:29 Berlin (15:29Z, vom Runner)
- **Deadline:** 2026-09-26 20:29 Berlin (18:29Z)
- **Zuletzt aktualisiert:** 18:03 Berlin
- **Run-Fenster:** offen bis 18:00 (heutige Ausnahme), danach erst wieder ab 00:00.

## Gerade

Denkarbeit (Fenster zu). Offene Frage für den nächsten Zyklus: Stimmt die Oberwellen-Deutung der fremden Frequenzen auch für die frischen Seeds 33/34 in EXP-020? (Gespeicherte Daten.)

## Als Nächstes

Ab 00:00 (nächste Sitzung, Start 22:29) läuft `queue_s10.sh`: EXP-035 Rest → EXP-038 → EXP-036 → EXP-039 → EXP-040 → EXP-034.

## Verlauf dieser Sitzung

- 18:01 **Neue Idee EXP-040:** Vielleicht fällt die Wahl, sobald das Lernsignal so groß ist wie die zufälligen Startwerte. Test: Startwerte halb so groß → Festlegung früher, doppelt so groß → später. Codex fand 3 Schwächen, eingebaut. Literatur: nächstverwandte Arbeit (He et al. 2026, „Frequenz-Lotterie“) sagt nichts über den Zeitpunkt.
- 17:53 **Neuer Versuch EXP-039 „Lernraten-Uhr“ vorbereitet:** Wenn die Festlegung an der aufsummierten Lernrate hängt, muss doppelte Lernrate sie auf 12–25 Schritte vorziehen und halbe auf 50–100 verschieben. Codex fand 3 Schwächen im Design, eingebaut. Testlauf ok. Läuft in der Nacht nach EXP-036.
- 17:51 EXP-035 Seed 31: Auch hier legt sich das Netz mit Warmup später fest (bei t = 50 noch auf der G-Seite, ohne Warmup schon F).
- 17:41 Codex hat die neue Prüfung angegriffen (4 Punkte, alle berechtigt). Eingebaut: Beide Datensätze müssen die Frequenz wirklich wachsen lassen, und ein zusätzlicher Test prüft, ob „beide“ mehr erklärt als „einer allein“. Die Protokoll-Option wurde im Fenster getestet und funktioniert.
- 17:35 **Vorhersage für EXP-036 jetzt sauber festgelegt:** Sind die „Konfliktfrequenzen“ die, die beide Datensätze in den ersten 20 Schritten anschieben? Dafür speichert das Training jetzt auch sehr frühe Spektren.
- 17:36 EXP-035 Seed 30 fertig: Mit Warmup legt sich das Netz erst zwischen Schritt 100 und 150 fest (ohne Warmup: 25–50). Ein Seed, noch kein Urteil.
- 17:30 Stand gelesen; EXP-035 läuft (Seed 30: 5 von 7 Läufen fertig).

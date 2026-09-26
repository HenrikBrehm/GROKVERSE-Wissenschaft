---
tags: [lab/live]
---
# LIVE: Laborsitzung 10

- **Sitzungsstart:** 2026-09-26 17:29 Berlin (15:29Z, vom Runner)
- **Deadline:** 2026-09-26 20:29 Berlin (18:29Z)
- **Zuletzt aktualisiert:** 17:43 Berlin
- **Run-Fenster:** offen bis 18:00 (heutige Ausnahme), danach erst wieder ab 00:00.

## Gerade

Zwei letzte Läufe im heutigen Fenster: EXP-035 (Warmup), Seed 31, Wechsel bei t = 50 und 150. Fertig bis ~17:52.

## Als Nächstes

Nach 18:00 nur Denkarbeit: Warum legt sich das Netz schon in 25–50 Schritten fest? (Theorie + Literatur.) Läufe erst ab 00:00 (`queue_s10.sh`).

## Verlauf dieser Sitzung

- 17:41 Codex hat die neue Prüfung angegriffen (4 Punkte, alle berechtigt). Eingebaut: Beide Datensätze müssen die Frequenz wirklich wachsen lassen, und ein zusätzlicher Test prüft, ob „beide“ mehr erklärt als „einer allein“. Die Protokoll-Option wurde im Fenster getestet und funktioniert.
- 17:35 **Vorhersage für EXP-036 jetzt sauber festgelegt:** Sind die „Konfliktfrequenzen“ die, die beide Datensätze in den ersten 20 Schritten anschieben? Dafür speichert das Training jetzt auch sehr frühe Spektren.
- 17:36 EXP-035 Seed 30 fertig: Mit Warmup legt sich das Netz erst zwischen Schritt 100 und 150 fest (ohne Warmup: 25–50). Ein Seed, noch kein Urteil.
- 17:30 Stand gelesen; EXP-035 läuft (Seed 30: 5 von 7 Läufen fertig).

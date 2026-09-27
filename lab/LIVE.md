---
tags: [lab/live]
---
# LIVE: Laborsitzung 28

- **Sitzungsstart:** 2026-09-27 16:49 Berlin (14:49Z, vom Runner)
- **Deadline:** 2026-09-27 19:49 Berlin (17:49Z)
- **Zuletzt aktualisiert:** 17:34 Berlin (gemessen)
- **Run-Fenster:** zu bis 00:00: kein Training, keine Tests; nur Auswertung gespeicherter Läufe, Denk- und Schreibarbeit.

## Gerade

Denkarbeit ohne Rechenfenster. Die Feinordnung der Zielfrequenzen (N39) ist jetzt an allen gespeicherten Daten geprüft und für die Nacht an drei Blöcken vorab registriert (C1–C3).

## Als Nächstes

Stand sichern (STATE); danach eine weitere offene Frage aus FINDINGS angehen oder die Nacht-Befehle für C1–C3 gegenprüfen.

## Verlauf dieser Sitzung

- 17:34 C2 verschärft (Fassung 3, a606ed0): Die alten Ziele müssen eine Nicht-Ziel-Kontrolle schlagen; sonst würde C2 womöglich nur eine Grundrate bestätigen. Codex: kein Blocker, Punkte übernommen.
- 17:29 Rangerhaltung der alten Ziele gegen t: leicht über der Grundrate bis t = 25, deutlich ab t = 30 (parallel zu π).
- 17:27 D₅₉ und P2d/P2e: Die Feinordnung überdauert im Transformer das Grokking; im MLP verblasst sie.
- 17:26 Eigener Messfehler (mul-Basis) gefunden → dabei echten Fehler in `repro/k2.py` behoben.
- 17:21 C3 nach Codex korrigiert (kein Blocker).

- 17:19 C3 registriert (b199107): In den Piloten zeigt sich die Feinordnung überall (ρ 0.29–0.60, Init ≈ 0).
- 17:15 Negativ: Die Theorie sagt fürs MLP „M0 statt M0c“ voraus; für die Feinordnung stimmt das nicht (M0c 0.60 > M0 0.46). Paper korrigiert.
- 17:14 Codex-Nachprüfung: 1 neuer Blocker in C2 (Seed zählte schon mit einem Lauf), behoben (f445f94).

- 17:05 C1/C2 Fassung 2 committet (d50e7b0): engere Aussagen, bereinigter Koeffizient, Code-Tor. Diagnose vor dem Lauf: in den R1-Splits hängt M0c nicht von k ab.
- 17:04 Codex zu C1: 2 Blocker, 6 größere Punkte; alle geprüft, fast alle übernommen (JOURNAL).
- 17:00 C2 registriert (Programm B): nach einem Wechsel bei t = 50 behalten die alten Ziele ihre Rangfolge (N29 ρ 0.58; die neuen Daten ordnen sie nicht um).
- 16:55 Artefakt-Kontrolle: keine Abhängigkeit von k (ρ ≈ 0.01), vertauschte Arme ρ ≈ −0.08.
- 16:53 C1 registriert und committet (d330f1c), vor jedem R1-Lauf.
- 16:52 Exploration P1: Rangfolge der Ziele folgt M0/M0c (ρ 0.21–0.44, alle 4 Aufgaben), Init nur 0.08–0.15.
- 16:51 P1 absolut: 80 % der W_E-Energie auf den 5 Zielen (add 113; Init 8.9 % = Zufall); mul 79 %, add 97 69 %, D₅₉ 44 % (Zufall 17 %).

---
tags: [lab/live]
---
# LIVE: Laborsitzung 63

- **Sitzungsstart:** 2026-09-30 21:10 Berlin (19:10Z, vom Runner)
- **Deadline:** 2026-10-01 00:09 Berlin (22:09Z)
- **Zuletzt aktualisiert:** 23:42

## Hinweis für den Assistenten (21:41)

- **Vorschlag des Assistenten** (stall_minutes 15 → 7 für die noch nicht gestartete Datei `lab/queue/inbox/44zzzz_exp133_reset.jobs`): **ich stimme zu**, meine Änderung wurde von der Sicherheitsprüfung abgelehnt (Interfere With Workloads); nicht umgangen.
- **Beleg:** gleicher Trainer wie EXP-132 (ft_pythia.py), Ausgabe alle ≈ 2.3 min, Laden < 1 s, Ablation am Ende ≈ 1 min → 7 min sicher.
- **Maßnahme:** nur die Kopfzeile ändern (atomar). Nichts geht verloren; sonst bleibt 15.

## Gerade

- **Sitzung beendet (23:42).** Nächster Start laut Runner: 01.10. 00:44 Berlin (vorläufig, der Runner setzt ihn neu).
- Beim Dienst: **L0b** (Menge gegen Reihenfolge, 420 Läufe) läuft jetzt mit bis zu 8 Läufen, fertig grob in 4–5 h; danach EXP-125 (größeres Sprachmodell), EXP-128, EXP-129.

## Als Nächstes

1. L0b auswerten + unabhängig nachrechnen, dann Paper-Sätze (liegen vorab bereit).
2. EXP-125 beobachten.

## Verlauf dieser Sitzung
- 23:42 Sitzung beendet; L0b läuft beim Dienst mit 6–8 Läufen.
- 23:32 Pythia-Absatz unabhängig geprüft: Zahlen richtig, 1 Fehler korrigiert (Splits von EXP-130 waren nicht „neu“).
- 23:28 **EXP-133: „nicht auswertbar“** – mit neuen Zahlzeilen lernt Pythia nur auswendig. **Pythia-Reihe abgeschlossen**, ein Absatz im Paper (Anhang K).
- 22:32 Pythia-Absatz fürs Paper fertig vorbereitet (wartet auf die EXP-133-Auswertung).
- 22:31 **EXP-133 Seed 4000: nur auswendig** (Test ≈ 0.001) – nicht einmal die Vertauschungsregel gelernt, obwohl 30 % der Testaufgaben ihr Spiegelpaar im Training haben.
- 22:03 Literatur-Nachsuche (wer zitiert LeDoux?): nur eine bekannte Arbeit, nichts Neues.
- 22:02 Unabhängige L0b-Nachrechnung fertig (stimmt am Vorversuch exakt).
- 21:55 Tageserklärung 30.09. um den Abend ergänzt.
- 21:54 **L0b beim Dienst** (420 Läufe); Smoke durch den eingefrorenen Lader grün.
- 21:46 **L0b eingefroren** (bce36b1a) nach unabhängiger Prüfung: keine Blocker, 6 Punkte übernommen (u. a. strengere Gleichheitsgrenze 0.02, 70 statt 64 Seeds).
- 21:44 EXP-133 gestartet (beim Dienst).
- 21:41 Vorschlag des Assistenten (kürzere Stillstands-Grenze für Pythia) befürwortet, meine Änderung abgelehnt -> Hinweis oben, nicht umgangen.

- 21:31 **EXP-132 abgeschlossen: „nicht auswertbar“** – Pythia lernt Multiplikation mod 113 nur auswendig (Test ≤ 0.07 in 4/4).
- 21:29 L0b-Code (`confirm_l0b.py`) + Registrierung geschrieben, Selbsttest grün; Power: 64 Seeds nötig.
- 21:22 Bemerkt: die in Sitzung 46 geplante Bestätigung L0b wurde nie angelegt -> jetzt vorbereitet.
- 21:20 Paper-Sätze für jeden Ausgang von EXP-125 (größeres LM) vorab geschrieben.
- 21:18 Zenodo-Paket geprüft: R12, LM3, LM3-F sind drin.
- 21:12 Sitzung 63 gestartet; Stand, Fenster (offen) und Dienst geprüft.

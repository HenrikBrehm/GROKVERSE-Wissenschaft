---
tags: [lab/live]
---
# LIVE: Laborsitzung 13

- **Sitzungsstart:** 2026-09-26 19:59 Berlin (17:59Z, vom Runner)
- **Deadline:** 2026-09-26 22:59 Berlin (20:59Z)
- **Zuletzt aktualisiert:** 20:13 Berlin (gemessen)
- **Run-Fenster:** zu, wieder ab 00:00. Die nächste Sitzung (Start 00:59 Berlin) startet die Nacht-Queues. Diese Sitzung: Prüf-, Code- und Denkarbeit.

## Gerade

Ein Subagent prüft den neuen EXP-048-Code. Parallel bereite ich EXP-049 vor: Hält die Datensteuerung auch in einem 4× breiteren Transformer? Die Splits sind fertig.

## Als Nächstes

Review-Ergebnis einarbeiten, dann Trainer und Vorab-Festlegung für EXP-049.

## Verlauf dieser Sitzung

- 20:13 Idee „frühe Festlegung aus Init-Skala und Lernrate vorhersagen“ verworfen: Sie steht schon als Vorhersage in EXP-040 (Nachtrag c). Stattdessen EXP-049 (Modellbreite) begonnen.
- 20:11 **Neuer Versuch [[experiments/EXP-048-intadd-steering/README|EXP-048]]:** Klappt die Steuerung über die Daten auch bei gewöhnlicher Addition *ohne* Modulo? Dort lernen Netze normalerweise eine Zahlengerade statt einer Uhr. Das ist die erste nicht-modulare Aufgabe. Beim Bau einen Fehler gefunden und behoben (Split-Dateien überschrieben sich). Außerdem fünf Queue-Skripte auf LF-Zeilenenden gebracht.
- 20:07 **Unabhängige Prüfung von EXP-046/047** (Claude-Subagent statt Codex): kein Blocker. Einschränkung für EXP-046 notiert: Das Ergebnis heißt nur „der Split steuert“, noch nicht „über die Paarstruktur“.
- 20:05 **Theorie für EXP-047:** Im ersten Lernschritt fallen die bloßen Token-Häufigkeiten exakt heraus. Vorhersage vor dem Lauf: Die Häufigkeitskontrolle zeigt keine Steuerung.
- 20:04 Codex nicht verfügbar („out of credits“), nicht umgangen.
- 20:02 Eigene Prüfung von EXP-046/047: Code passt zur Trainingsbibliothek (Konfiguration, Auswertung, Namen der Läufe). Die 40 EXP-047-Splits haben exakt gleiche a/b-Häufigkeiten zwischen „eng“ und „shuf“. Einen Fehler habe ich nicht gefunden.
- 20:00 Stand gelesen: kein STOP, kein Training aktiv, Fenster zu. Die Zeitangaben in Sitzung 12 nach 19:50 waren geschätzt und liegen in der Zukunft; das korrigiere ich im JOURNAL.

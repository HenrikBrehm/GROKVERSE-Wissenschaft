---
tags: [lab/live]
---
# LIVE: Laborsitzung 13

- **Sitzungsstart:** 2026-09-26 19:59 Berlin (17:59Z, vom Runner)
- **Deadline:** 2026-09-26 22:59 Berlin (20:59Z)
- **Zuletzt aktualisiert:** 20:51 Berlin (gemessen)
- **Run-Fenster:** zu. **Neu (Regel 18, Nutzer 20:30): heute Nacht Läufe erst ab 03:00.** Bis dahin setze ich den Astra-Review als Code um.

## Gerade

Ich setze den Astra-Review um (Regel 18). Erledigt, aber erst ab 03:00 testbar: eindeutige Fingerabdrücke für Läufe (kein falsches Überspringen mehr), korrekte GPU-Durchsatzmessung, ein gemeinsamer Ergebnislader, ein neues Programm für die GPU-Nacht statt Shell-Skripten, STATE auf eine Seite gekürzt, FINDINGS als Forschungsprogramm A/B/C.

## Als Nächstes

Ein Subagent prüft die neue gemeinsame Technik (Trainer, Ergebnislader, Nachtprogramm). Danach Befunde einarbeiten; bis 03:00 läuft nichts.

## Verlauf dieser Sitzung

- 20:51 Nachtprogramm auch für die CPU-Versuche gebaut; die schon fertigen Läufe werden erkannt und nicht wiederholt. Tests für die neuen Sicherungen geschrieben (laufen ab 03:00).
- 20:45 **Regel 18 entdeckt (Nutzer-Auftrag von 20:30)** und umgesteuert: Plan der Nacht geändert (Läufe erst ab 03:00, vorher Umbau nach dem Astra-Review). Sechs von acht Code-Punkten stehen (ungetestet).
- 20:33 **EXP-050 verbessert:** Die Prüfung fand eine versteckte Nebenwirkung. Die gleichphasigen Trainingsmengen enthalten viel mehr „Spiegelpaare“ (a+b und b+a), und die lernt ein Netz schneller. Neue Kontrolle „quadlm“ mit gleich vielen Spiegelpaaren gebaut.
- 20:28 GPU-001 (Eingangsprüfung der Nacht) unabhängig prüfen lassen: kein Blocker, eine Schwachstelle behoben (abgelehnte Durchsatzläufe gingen unter). Neuer Kausaltest [[experiments/EXP-050-phase-dissociation/README|EXP-050]] vorbereitet.
- 20:23 Theorie: Eine einfache Rechnung zum ersten Lernschritt erklärt, warum im Transformer eine andere Maskengröße (M0c) passt als im MLP (M0). Vorab festgelegt, wie die sechs Nachtergebnisse zusammen zu lesen sind ([[LESART-nacht-2026-09-27]]).
- 20:21 Alle sieben Auswertungen der Nacht abgesichert: Ein abgestürzter Lauf (NaN) hätte sonst still ein falsches Urteil erzeugt. Gefunden bei der Prüfung von EXP-049. Werkzeug für den Morgenbericht auf die GPU-Versuche erweitert.
- 20:17 EXP-048 nach Review verbessert: Die Hauptmessgröße entfernt jetzt vorab den Zahlengeraden-Anteil (der sonst Scheineffekte erzeugt). Dabei einen eigenen fehlerhaften Selbsttest gefunden, der die Nacht-Queue gestoppt hätte. [[experiments/EXP-049-width-steering/README|EXP-049]] (Modellbreite) vorab festgelegt und eingereiht.
- 20:13 Idee „frühe Festlegung aus Init-Skala und Lernrate vorhersagen“ verworfen: Sie steht schon als Vorhersage in EXP-040 (Nachtrag c). Stattdessen EXP-049 (Modellbreite) begonnen.
- 20:11 **Neuer Versuch [[experiments/EXP-048-intadd-steering/README|EXP-048]]:** Klappt die Steuerung über die Daten auch bei gewöhnlicher Addition *ohne* Modulo? Dort lernen Netze normalerweise eine Zahlengerade statt einer Uhr. Das ist die erste nicht-modulare Aufgabe. Beim Bau einen Fehler gefunden und behoben (Split-Dateien überschrieben sich). Außerdem fünf Queue-Skripte auf LF-Zeilenenden gebracht.
- 20:07 **Unabhängige Prüfung von EXP-046/047** (Claude-Subagent statt Codex): kein Blocker. Einschränkung für EXP-046 notiert: Das Ergebnis heißt nur „der Split steuert“, noch nicht „über die Paarstruktur“.
- 20:05 **Theorie für EXP-047:** Im ersten Lernschritt fallen die bloßen Token-Häufigkeiten exakt heraus. Vorhersage vor dem Lauf: Die Häufigkeitskontrolle zeigt keine Steuerung.
- 20:04 Codex nicht verfügbar („out of credits“), nicht umgangen.
- 20:02 Eigene Prüfung von EXP-046/047: Code passt zur Trainingsbibliothek (Konfiguration, Auswertung, Namen der Läufe). Die 40 EXP-047-Splits haben exakt gleiche a/b-Häufigkeiten zwischen „eng“ und „shuf“. Einen Fehler habe ich nicht gefunden.
- 20:00 Stand gelesen: kein STOP, kein Training aktiv, Fenster zu. Die Zeitangaben in Sitzung 12 nach 19:50 waren geschätzt und liegen in der Zukunft; das korrigiere ich im JOURNAL.

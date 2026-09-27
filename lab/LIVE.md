---
tags: [lab/live]
---
# LIVE: Laborsitzung 20

- **Sitzungsstart:** 2026-09-27 01:29 Berlin (23:29Z, vom Runner)
- **Deadline:** 2026-09-27 04:29 Berlin (02:29Z)
- **Zuletzt aktualisiert:** 03:09 Berlin (gemessen)
- **Run-Fenster:** offen seit 02:25 (Freigabe des Nutzers, 03:00-Sperre aufgehoben), bis Sitzungsende 04:29.

## Gerade

GPU: EXP-048 (nicht-modulare Addition) laeuft. CPU: Paket-B-Piloten (EXP-035). Ich lege derweil den Nachfolger fuer den Funktionstest EXP-051 fest.

## Als Naechstes

Beobachten; Urteile je Versuch nach der Lesart-Notiz eintragen. Um ~04:20 Stand sichern (Deadline 04:29 beendet alle Laeufe; Folgesitzung setzt mit denselben Befehlen fort).

## Verlauf dieser Sitzung

- 03:06 EXP-051: formal "nicht genutzt", aber Bodeneffekt (Eingriff zu klein, alle Verluste 0). Kein Beleg; Nachfolger noetig.
- 03:06 **EXP-047: Die Paarstruktur steuert, nicht die Token-Haeufigkeiten** (wie vorab aus der Theorie erwartet).
- 03:01 **EXP-046: Steuerung gilt auch in der Diedergruppe D59** (nicht-abelsch; 10/10, p 0.001).
- 02:56 **EXP-043: Steuerung ueber die Daten gilt auch bei add 97 und mul 113** (je 10/10 Seeds, p 0.001; Pilot).
- 02:56 CPU-Programm gestartet (Paket-B-Piloten).
- 02:53 GPU-001 bestanden: gleichwertig zur CPU, ~17x schneller, 8 Laeufe parallel am besten (~1600 kurze Laeufe/h).
- 02:49 Diagnoselauf mit venv-torch auf CPU abgebrochen (10x zu langsam), dokumentiert.
- 02:34 Nachtprogramm neu gestartet: Umgebung ok (torch 2.9.1+rocm, RX 7900 XT erkannt).
- 02:32 Erster Start scheiterte: Windows fand den venv-Python-Pfad mit / nicht. Behoben (absoluter Pfad).
- 02:30 Tests: 11/11 gruen, nachdem zwei Fehler im Testaufbau behoben waren (nicht im Code).
- 02:26 Waechter-Abnahme: A/B/C bestanden. Job-Objekt-Fehler gefunden und an die Nutzersitzung gemeldet, dort behoben.
- 02:25 Fenster offen (Waechter allowed: true; Nutzer hat die 03:00-Sperre aufgehoben).
- 01:34 Kontrolle: Auch Zufallssplits verdichten sich nach dem Grokking. Haltbar ist nur "kein Abklingen", eine Verstaerkung durch den Split nicht.
- 01:33 Nachrechnung EXP-016: Gepflanzte Frequenzen klingen nach dem Grokking nicht ab (Anteil 0.56 -> 0.82, 20/20). Gegenprobe zu Zhou et al.
- 01:31 Trockenlaeufe GPU- und CPU-Nachtprogramm: vollstaendig, nichts geschrieben.
- 01:30 Sitzung gestartet: Fenster zu (Exit 3), kein STOP, keine Python-Prozesse. Sitzung 19 endete 23:21Z.

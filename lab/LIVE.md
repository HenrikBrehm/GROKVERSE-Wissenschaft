---
tags: [lab/live]
---
# LIVE: Laborsitzung 20

- **Sitzungsstart:** 2026-09-27 01:29 Berlin (23:29Z, vom Runner)
- **Deadline:** 2026-09-27 04:29 Berlin (02:29Z)
- **Zuletzt aktualisiert:** 02:36 Berlin (gemessen)
- **Run-Fenster:** offen seit 02:25 (Freigabe des Nutzers, 03:00-Sperre aufgehoben), bis Sitzungsende 04:29.

## Gerade

GPU-Nachtprogramm laeuft (seit 02:34): GPU-001 Stufe 0, Vergleich der Einzelbausteine CPU gegen GPU. Ohne PASS keine GPU-Laeufe.

## Als Naechstes

GPU-001 beobachten (alle ~5-10 min). Nach dem Urteil das CPU-Programm (Paket-B-Piloten) daneben starten.

## Verlauf dieser Sitzung

- 02:34 Nachtprogramm neu gestartet: Umgebung ok (torch 2.9.1+rocm, RX 7900 XT erkannt).
- 02:32 Erster Start scheiterte: Windows fand den venv-Python-Pfad mit / nicht. Behoben (absoluter Pfad).
- 02:30 Tests: 11/11 gruen, nachdem zwei Fehler im Testaufbau behoben waren (nicht im Code).
- 02:26 Waechter-Abnahme: A/B/C bestanden. Job-Objekt-Fehler gefunden und an die Nutzersitzung gemeldet, dort behoben.
- 02:25 Fenster offen (Waechter allowed: true; Nutzer hat die 03:00-Sperre aufgehoben).
- 01:34 Kontrolle: Auch Zufallssplits verdichten sich nach dem Grokking. Haltbar ist nur "kein Abklingen", eine Verstaerkung durch den Split nicht.
- 01:33 Nachrechnung EXP-016: Gepflanzte Frequenzen klingen nach dem Grokking nicht ab (Anteil 0.56 -> 0.82, 20/20). Gegenprobe zu Zhou et al.
- 01:31 Trockenlaeufe GPU- und CPU-Nachtprogramm: vollstaendig, nichts geschrieben.
- 01:30 Sitzung gestartet: Fenster zu (Exit 3), kein STOP, keine Python-Prozesse. Sitzung 19 endete 23:21Z.

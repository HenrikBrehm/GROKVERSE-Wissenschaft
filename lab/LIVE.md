---
tags: [lab/live]
---
# LIVE: Laborsitzung 58

- **Sitzungsstart:** 2026-09-30 08:29 Berlin (06:29Z, vom Runner)
- **Deadline:** 2026-09-30 11:29 Berlin (09:29Z)
- **Zuletzt aktualisiert:** 09:20 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Ein unabhängiger Agent prüft den Code von EXP-127, bevor die Piloten starten. Der GPU-Dienst beendet gerade seinen sanften Neustart (letzter LM3-Lauf bei Schritt ≈ 14 500 von 15 000).

## Als Nächstes

1. EXP-127-Pilot läuft, sobald der Dienst Platz hat (nach LM3/R12). 2. LM3 und R12 auswerten, wenn fertig (Deutungssätze liegen bereit).

## Dienst (09:01)

Sanfter Neustart (DRAIN, P-017-Fix): startet nichts Neues, bis die 3 laufenden LM3-Läufe fertig sind; dann startet die geplante Aufgabe den neuen Code. LM3 5/20 fertig, 3 laufen; R12 22/200 (pausiert); EXP-125 und **EXP-127 (neu)** warten.

## Verlauf dieser Sitzung

- 09:18 EXP-127: Messgröße vor dem Start verbessert – Weight Decay schrumpft die vortrainierten Einbettungen und hätte das Ergebnis verfälschen können; jetzt wird dieser Anteil herausgerechnet.
- 09:12 Literatur: dass vortrainierte Modelle Fourier-Zahlmerkmale haben, ist bekannt (Zhou et al. 2024); dass die Faktenauswahl beim Nachtrainieren die Frequenzen vorschreibt, nach unserer Suche nicht gefunden.
- 09:05 Vortrainierte Zahl-Einbettungen (Pythia, GPT-2) tragen schon Frequenzen 1–3 und 11/23/45 (Zehnerrhythmus).

- 09:00 **EXP-127 vorbereitet und eingereiht:** Pythia-160M (vortrainiert, 162 M Parameter, getrennte Ein-/Ausgabe-Einbettung) lernt Rechenfakten mod 113 nach. Zahlen 0–112 sind dort je ein Token. Selbsttest und Smoke grün (4.4 GB, ≈ 1.4 s/Schritt unter Last). Lesarten vorab.
- 08:50 `transformers 5.15.1` in .venv-gpu installiert (tokenizers festgehalten, damit LM3 unberührt bleibt).
- 08:45 **Paper: LM1/LM1-F im Abstract (1907 Zeichen) und als eigener Absatz in §7**, unabhängig geprüft: alle Zahlen richtig, 8 Formulierungen verbessert (z. B. „beeinträchtigt“ statt „genutzt“, weil Energie und Nutzung nicht getrennt sind).
- 08:30 Start: Stand gelesen, Fenster offen, kein STOP.

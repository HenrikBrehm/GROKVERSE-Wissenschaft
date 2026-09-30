---
tags: [lab/live]
---
# LIVE: Laborsitzung 57

- **Sitzungsstart:** 2026-09-30 05:50 Berlin (03:50Z, vom Runner)
- **Deadline:** 2026-09-30 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 05:58 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **R12 vorbereiten:** Gilt „konstruierte Trainingsdaten → schnelleres Grokking“ (Ergebnis 2 im Paper, bisher nur Addition mod 113) auch für Addition mod 97 und Multiplikation mod 113? Code + Selbsttest fertig, Registrierung geschrieben; zwei Smoke-Läufe rechnen, ein unabhängiger Agent prüft den Code.

## Als Nächstes

Prüfbericht einarbeiten → Smoke durch den Lader → einfrieren (Commit) → 200 Läufe beim GPU-Dienst ablegen (neben LM3, klein: ≈ 1 GB je Lauf).

## Dienst (05:50)

LM3: 3 Läufe gleichzeitig, 0/20 fertig (zwei bei 14 500/15 000, einer bei 1 000).

## Verlauf dieser Sitzung

- 05:54 R12-Code (`confirm_r12.py`) geschrieben, Selbsttest grün; Splits offline geprüft (Zielanteil konstruiert 0.18–0.20, Kontrolle 0.09–0.11).
- 05:50 Stand gelesen; LM3 läuft, GPU hat Platz für kleine Läufe.

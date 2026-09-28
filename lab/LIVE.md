---
tags: [lab/live]
---
# LIVE: Laborsitzung 39

- **Sitzungsstart:** 2026-09-28 08:09 Berlin (06:09Z, vom Runner)
- **Deadline:** 2026-09-28 11:09 Berlin (09:09Z)
- **Zuletzt aktualisiert:** 09:28 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

EXP-088 registriert (gemeinsame Dosiskurve: Liegen eingepflanztes und datengesteuertes frühes Zielsignal auf einer Kurve „Anteil → Grokking-Zeit“?). Eine unabhängige Prüfung vor dem Lauf läuft; danach 140 GPU-Läufe (≈ 50 min).

## Als Nächstes

EXP-088 rechnen und auswerten; Abschlussbericht vor 11:00.

## Verlauf dieser Sitzung

- 09:25 EXP-088 entworfen, Code-Selbsttest grün, registriert (ec46a05b).
- 09:22 **EXP-083:** Größen-Erklärung für VO/QK *widersprochen* (QK nimmt mehr Bewegung zurück, wirkt aber schwächer; 20/20); Attention/MLP *unklar*.
- 09:19 **EXP-087 Pilot:** registriert *unklar*; Einpflanzen beschleunigt einen Zufallssplit ×11 (10/10) und ist schneller als der konstruierte Split; der frühe Zielanteil ordnet die Zeit über alle Arme.
- 09:10 R4-Papertext nach unabhängiger Prüfung korrigiert (48/60 statt 42/60 positiv; beschreibende Kennzeichnung).
- 09:04 EXP-087: Trainer-Option (Tests grün, Smoke exakt), Kalibrierung C = 2, Pilot gestartet.
- 09:00 **R4 fertig: H1a und H1b bestätigt** (Spearman 0.33, 60/60; Kosinus 0.118, 42/60). Paper §3.14, FINDINGS.
- 08:31 **EXP-014 fertig:** registriert *kein dominanter Faktor* (Top-5-Überlappung, p 0.41); sekundär folgt die Rangstruktur dem benutzten Split in 5/5 Paaren (p 1/32). Pilotstreuung für R4: Δ_split ≈ 0.29 ± 0.08 (Mindesteffekt 0.05).
- 08:19 EXP-087-Code vorbereitet (Einpflanz-Eingriff + Auswertung, Selbsttests grün); Trainer-Option folgt nach R4.

- 08:12 R4 (`--workers 8`) und EXP-040/014 (CPU) neu gestartet.
- 08:11 Keine Prozesse aktiv; 2 verwaiste R4-Sperren (Status „running“) nach `.stale_s38` umbenannt.

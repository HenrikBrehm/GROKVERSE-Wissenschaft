---
tags: [lab/live]
---
# LIVE: Laborsitzung 39: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 08:09 Berlin (06:09Z, vom Runner)
- **Deadline:** 2026-09-28 11:09 Berlin (09:09Z)
- **Zuletzt aktualisiert:** 10:27 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

**Sitzung beendet.** Keine Läufe aktiv. Heute bestätigt: **R4** (ein Zufallssplit verzerrt die Frequenzwahl). Explorationen: EXP-014, EXP-083, EXP-087, EXP-088 (der frühe W_E-Zielanteil ist der Hauptmittler der Split-Beschleunigung). Nächster geplanter Start laut runner-state.json: **11:44 Berlin**.

## Als Nächstes

Nächste Sitzung: EXP-081 (Optimierer-Uhr) vorbereiten und rechnen; EXP-087/088 ins Paper (§4). Nächster geplanter Start laut runner-state.json: 11:44 Berlin (oder direkt nach dieser Sitzung).

## Verlauf dieser Sitzung

- 10:25 β-Zusatz geprüft (kein Blocker); EXP-081-Designpunkte notiert. Sitzung beendet.
- 10:20 Trainer-Zusatz `--beta1/--beta2` für EXP-081 (Tests grün).
- 10:17 **EXP-088 fertig:** *unklar*. Eingepflanztes und datengesteuertes Frühsignal liegen nahe an einer gemeinsamen Dosiskurve (Eingriff ≈ ×1.3 wirksamer, 17/20); der frühe Zielanteil ist der Hauptmittler der Split-Beschleunigung.
- 09:40 Abstract-Satz zu R4 geprüft und korrigiert; Paper-STATUS aktualisiert.
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

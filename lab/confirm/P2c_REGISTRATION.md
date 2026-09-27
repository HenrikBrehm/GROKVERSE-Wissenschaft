---
id: P2c-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P2b_REGISTRATION|P2b]]", "[[confirm/P2_REGISTRATION_DRAFT|P2]]", "[[confirm/N28_REGISTRATION|N28]]", "[[JOURNAL]]"]
---
# P2c-Bestätigung (funktionale Nutzung): Registrierung (Sitzung 22). **ENTWURF, nicht eingefroren**

Zurück zu [[FINDINGS]] (Programm A) · ersetzt [[confirm/P2b_REGISTRATION|P2b]] (abgebrochen, Designfehler) · Familie Sitzung 22 mit [[confirm/N28_REGISTRATION|N28]] (P2c übernimmt den Platz von P2b).

**Es gilt die P2b-Registrierung vollständig, einschließlich aller Codex-Abschnitte, mit genau diesen Änderungen:**
- **Seeds 2100–2199** (frisch, in [[FINDINGS]] reserviert; kein Lauf vor der Registrierung). Splits über `confirm_splits.build` mit **Versuchs-ID 3** (eigene Zufallsströme).
- **Jede Jobzeile mit `--stop-after-gen 4000`**, damit jeder Lauf genau 4000 Schritte trainiert (die P2b-Läufe endeten 2000 Schritte nach der Generalisierung). Der Selbsttest verlangt für jede Zeile `stop-after-gen ≥ steps`.
- Code `lab/tools/confirm_p2c.py` (Kopie von `confirm_p2b.py`, nur diese Änderungen und die Pfade `p2c_*`), Manifest `lab/confirm/P2c_manifest.json`.
- **Bereits gesehene Daten, zusätzlich zu P2b:** nur Trainer-Logzeilen einzelner P2b-Läufe (Generalisierungsschritt, Top-5-Frequenzen), keine Ablation. Keine Entscheidung wurde davon beeinflusst außer dem Fehlerfund.
- **Speicher:** höchstens 8 GPU-Prozesse gleichzeitig insgesamt (07:53 scheiterten zwei Starts bei 12 Prozessen an Hauptspeicher bzw. Auslagerungsdatei).

```
python lab/tools/confirm_p2c.py --splits lab/confirm/P2c_manifest.json
python lab/tools/confirm_p2c.py --jobs lab/confirm/P2c_manifest.json > lab/confirm/P2c_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/P2c_jobs.txt --workers 5
python lab/tools/guarded_run.py -- python lab/tools/confirm_p2c.py --analyze lab/confirm/P2c_manifest.json
```

## Codex-Prüfung (Sitzung 22, 08:07–08:12)

Gezielte Nachprüfung der Änderungen gegenüber P2b: volle 4000 Schritte garantiert, Lauf-ID und Lader korrekt; zwei Kommentarfehler behoben. Sonst keine Einwände.

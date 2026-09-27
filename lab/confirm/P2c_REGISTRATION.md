---
id: P2c-registrierung
status: eingefroren
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P2b_REGISTRATION|P2b]]", "[[confirm/P2_REGISTRATION_DRAFT|P2]]", "[[confirm/N28_REGISTRATION|N28]]", "[[JOURNAL]]"]
---
# P2c-Bestätigung (funktionale Nutzung): Registrierung (Sitzung 22). **EINGEFROREN**

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

## Codex-Prüfung (Sitzung 22, 08:07–08:09 gemessen)

Gezielte Nachprüfung der Änderungen gegenüber P2b: volle 4000 Schritte garantiert, Lauf-ID und Lader korrekt; zwei Kommentarfehler behoben. Sonst keine Einwände.

## EINGEFROREN (Sitzung 22, 08:09 Berlin, gemessen)

Manifest-Commit **e8e0cfa** (Commit-Feld b7dfa94), Splits und Jobs 4aa4544, Herkunftsprüfung für alle 100 Seeds bestanden. Vor dem Einfrieren kein Lauf mit Seeds 2100–2199.
Start 08:10 mit 3 Arbeitern (freier virtueller Speicher nur 3.3 GB).

## ERGEBNIS (Sitzung 22, Block 08:10–09:02, Auswertung 09:03 Berlin; `lab/confirm/P2c_summary.json`): ***nicht bestätigt***, Vorzeichen umgekehrt

200/200 Läufe gebunden (zwei Warteschlangen über dieselben Zeilen; die Exit-4-Meldungen am Treffpunkt sind die vorgesehenen `run.lock`-Ablehnungen), 0 technische Ausfälle,
99/100 Seeds geeignet (1 nicht generalisiert), 0 gekappte Arme.
- **Primär:** R̄ = **−0.108**, SD 0.202, 95-%-KI **[−0.149, −0.070]**, 30/99 > 0, d_z −0.54 → ***nicht bestätigt***. Die Aussage P2 („das Entfernen aus den eigenen Zielen kostet bei f = 0.5 mehr Loss“)
  gilt nach 4000 Schritten **nicht**. Der Mittelwert lag entgegen der gerichteten Hypothese; das beschreibt einen negativen Effekt unter diesem Maß, ist aber **keine** registrierte Bestätigung der Gegenhypothese (Wortlaut nach Codex).
- Sekundär: rohes D −9·10⁻⁵ [−2.5·10⁻⁴, −1·10⁻⁶]. Sensitivität über alle 100 Seeds: R̄ −0.112 [−0.153, −0.073].
- **Beschreibend, nach dem Ergebnis angesehen (keine Deutung mit Beweiskraft):** Median E_own/E_ctrl je Modell 20.5 (P2 bei 2000 Schritten: 12.2), Median-Basis-Loss 8.9·10⁻⁵ (P2: 4.1·10⁻³).
  Die feste Dosis 0.5·E_ctrl ist für die eigenen Ziele also eine sehr kleine relative Störung (≈ 2.5 % ihrer Energie), für die Kontrollmenge 50 %. „Je Energieeinheit“ war nie Teil der Aussage;
  ob die Umkehrung an der Dosis-Geometrie, am späteren Trainingsstand (2000 statt 4000 Schritte) oder an den Seeds liegt, ist offen.
- **Folge für Programm A:** Die funktionale Nutzung der gesteuerten Frequenzen ist mit diesem Maß **nicht** belegt. Ein Nachfolger bräuchte ein Maß, das die relative Störung angleicht
  (z. B. gleicher Anteil der jeweiligen Energie) oder eine Dosis-Kurve, vorab festgelegt; vor jeder weiteren Aussage Codex-Prüfung der Schlussfolgerung.

## Codex-Prüfung der Schlussfolgerung (Sitzung 22, 09:05–09:12 gemessen), übernommen

Urteil korrekt. Übernommen: (1) keine Gegenhypothese behaupten (oben geändert). (2) Post hoc, beschreibend: Die Dosis entfernte median 2.44 % der Energie im Eigenziel-Unterraum, aber 50 % im Kontrollunterraum
(Skalierungsfaktoren ≈ 0.988 bzw. 0.707); mögliche Erklärung, kein getesteter Mechanismus. (3) Die Ursache ist nicht identifiziert: Trainingsstand, Seed/Split-Block, Energiegeometrie, Kontrollzusammensetzung
(5 eigene gegen 41–44 Kontrollfrequenzen) und Basis-Loss-Regime unterscheiden sich gleichzeitig. Nach Codex bleibt R̄ auch innerhalb der Basis-Loss-Quartile negativ. (4) P2c belegt keine bevorzugte funktionale
Nutzung unter diesem Eingriff, dieser Kontrolle und dieser Dosis; es zeigt weder, dass die Zielfrequenzen ungenutzt sind, noch allgemein, dass Kontrollfrequenzen funktionaler sind.
(5) Nachfolgemaß siehe [[BACKLOG]] „P2d“.

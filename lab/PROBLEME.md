---
tags: [lab/probleme, lab/betrieb]
angelegt: 2026-09-29
---
# Probleme im Labor – Protokoll

Alle Probleme, auf die wir beim Betrieb des Labors stoßen, mit Ursache, Auswirkung und Lösung. Auftrag des Nutzers
vom 29.09.2026: „Halte von jetzt an fest, auf welche Probleme wir gestoßen sind.“ Geführt vom Assistenten des Nutzers
(Claude-Code-Sitzung neben dem Labor); Laborsitzungen melden ihre Probleme weiter im [[JOURNAL]], der Assistent
übernimmt sie hierher. Uhrzeiten: Berlin.

Zurück zu [[LAB]] · [[STATE]] · Betrieb: `lab/runner/README.md` · **Automatische Lösungen (seit 30.09.):** [[runner/RUNBOOK]] – der stündliche Check löst die Klassen A1–A6 ohne Rückfrage, Protokoll in `lab/runner/logs/auto_actions.jsonl`

**Status:** 🔴 offen · 🟡 in Arbeit · 🟢 gelöst · ⚪ nur dokumentiert (kein Fehler, sondern Eigenschaft)

## Übersicht

| Nr. | Datum, Zeit | Problem | Folge für den Zeitplan | Status |
|---|---|---|---|---|
| P-001 | 29.09., 08:24 | Laborsitzung abgestürzt (Ausfall der Auto-Mode-Sicherheitsprüfung) | ≈ 25 min | 🟢 |
| P-002 | 29.09., 08:50 | Zwei abgestürzte EXP-105-Läufe beenden sich nicht | 2 GPU-Plätze 90 min blockiert | 🟢 |
| P-003 | 29.09., ≈ 08:55 | Priorität im GPU-Dienst wirkungslos | Pilot-Fortsetzung verzögert | 🟢 |
| P-004 | 29.09., ≈ 09:30 | Sanfter Neustart (DRAIN) wirkt bei alter Dienst-Instanz nicht | keine | 🟢 |
| P-005 | 29.09., ≈ 10:00 | Prüfung findet Schwächen in der neuen Hänger-Erkennung | keine (vor Einsatz behoben) | 🟢 |
| P-006 | 29.09., 10:03 | Lauf-Protokoll: 7 von 14 888 Zeilen zerstört | keine | 🔴 (niedrig) |
| P-007 | 29.09., 10:03 | Windows darf 03–11 Uhr für Updates neu starten; Aufgaben laufen nur bei Anmeldung | Risiko: eine Nacht | 🟢 (Updates bis 06.10. pausiert) |
| P-008 | 29.09., 09:36 | L0-Reproduktion auf der GPU nicht ganz bitgleich | keine | ⚪ |
| P-009 | 29.09., ≈ 13:00 | Grafikspeicher überbucht: 10 Sprachmodell-Läufe à 3,1 GB auf 20 GB | ≈ 1 h LM-Rechnen bei 1/8 Tempo | 🟢 |
| P-010 | 29.09., 13:15 | Freier Platz auf C: fällt schnell (106 → 67 GB) | keine | 🟢 |
| P-011 | 29.09., 13:58 | Startdatei des GPU-Dienstes verlor beim Bearbeiten ihre Windows-Zeilenenden | keine (sofort behoben) | 🟢 |
| P-012 | 29.09., 14:10 | Speicherschutz-Entwurf: Grenze für freie Speicherzusage (8 GB) hätte jeden Start blockiert | keine (vor dem Einsatz behoben) | 🟢 |
| P-013 | 29.09., 14:26 | Speicherschutz blockierte zu Unrecht: freie Speicherzusage 1,4 GB, weil Windows die Auslagerungsdatei verkleinert hatte | ≈ 25 min nur 3 statt 5–6 Läufe | 🟢 |
| P-014 | 29.09., 16:22 | Auto-Mode-Sicherheitsprüfung 2 min ohne Entscheidung (Laborsitzung konnte keine Befehle ausführen) | keine | 🟢 |
| P-015 | 29.09., 20:18 | Auto-Mode-Sicherheitsprüfung erneut ≈ 4 min gestört (8 Fehlversuche in Sitzung 53) | keine | 🟢 |
| P-016 | 30.09., 01:24 | lab/LIVE.md mit kaputten Umlauten (Kodierungsfehler beim Schreiben, Sitzung 55) | keine | 🟢 |
| P-017 | 30.09., ≈ 04:20 | GPU-Dienst las eine noch leere Jobdatei (LM3) ein und legte sie mit 0 Jobs als erledigt ab | wenige Minuten (neu eingereicht) | 🟢 |
| P-018 | 30.09., 09:31 | CPU-Test der Laborsitzung (EXP-127 first_gradient.py) viel langsamer als geplant, belegt ≈ 9 Kerne; Abbruch von der Sicherheitsprüfung verweigert | CPU ≈ 1 h ausgelastet, GPU-Läufe liefen weiter | 🟢 |
| P-019 | 30.09., 14:41 | Plattenplatz: Sprachmodell-Checkpoints füllen C: mit ≈ 12 GB pro Tag | bis 06.10. reicht es knapp (≈ 35–40 GB übrig), unter 60 GB etwa ab 03./04.10. | 🔴 (Nutzer, bis ≈ 03.10.) |
| P-020 | 30.09., 14:41 | Wichtige Werkzeuge nicht in Git (GPU-Dienst, Speicherschutz, parallel_queue.py); .gitignore deckt Checkpoints nicht ab | keine; Blocker für das Repro-Paket | 🔴 (Nutzer) |
| P-021 | 30.09., 16:25 | Zwei fertige Pythia-Läufe (EXP-127) hängen beim Beenden und halten 11 GB Grafikspeicher; Beenden durch die Laborsitzung abgelehnt | GPU-Leerlauf ≈ 20 min (16:25–16:45) und ≈ 53 min (17:24–18:16) | 🟢 |
| P-022 | 30.09., 19:13 | CPU-Zeittest der Laborsitzung (EXP-133) belegt ≈ 5 Kerne und bremst die LM3-F-Nachrechnung; Abbruch von der Sicherheitsprüfung abgelehnt | ≈ 20 min langsamere Nachrechnung | 🟢 |
| P-023 | 01.10., 11:59 | Umbenannte Jobdateien bleiben im GPU-Dienst als „Geister“ mit offenen Jobs stehen (52bz_exp140_p401, 52bzz_exp141_alpha) | keine | 🟢 |
| P-024 | 01.10., 16:07 | EXP-143-Läufe (freq_ban_large.py, p = 9973) belegen je 1–2 GB *geteilten* GPU-Speicher; gemeldet gpu_shared 4,4 GB > 3 | weniger parallele Läufe, solange EXP-143 rechnet | ⚪ |
| P-025 | 01.10., 19:29 | Während der Pause (Regel 23) startet der Runner alle 10 min eine Leersitzung, die nur „Pause aktiv“ meldet und committet (S73–S78 …) | keine für Daten und Dienst; ≈ 6 Sitzungen pro Stunde verbrauchen Nutzungskontingent (≈ 0,75 $ API-Gegenwert je Sitzung) | 🟢 |

## Einzelheiten

### P-001 · Laborsitzung abgestürzt (29.09., 08:24) 🟢
- **Symptom:** Sitzung 48 endete mit „Auto mode is unavailable – no safety verdict“; der Runner zählte das als Fehler (2 von 3 bis zum Stopp); die in der Sitzung laufenden Trainingsjobs starben mit.
- **Ursache:** vorübergehender Ausfall eines externen Dienstes, kein Laborfehler.
- **Lösung:** Fehlerzähler zurückgesetzt; `tick.ps1` stuft solche Ausfälle jetzt als `service_unavailable` ein (Neustart nach 15 min, zählt nicht als Fehler). Lange Jobs laufen seitdem über den sitzungsunabhängigen GPU-Dienst (`lab/tools/gpu_daemon.py`, Regel 21), sodass ein Sitzungsabsturz sie nicht mehr beendet.

### P-002 · Abgestürzte Läufe beenden sich nicht (29.09., 08:50–10:20) 🟢
- **Symptom:** Zwei EXP-105-Fortsetzungen brachen beim Laden des Checkpoints ab (`TypeError: RNG state must be a torch.ByteTensor`), die Prozesse liefen aber mit 100 % CPU weiter, ohne sich zu beenden, und blockierten 2 von 10 GPU-Plätzen, bis der Wächter sie nach 90 min beendete.
- **Ursache:** (1) Fehler im Checkpoint-Laden des Trainers (RNG-Zustand lag auf der GPU); (2) die ROCm-Laufzeit hängt beim Beenden nach einem Absturz.
- **Lösung:** Der Lab-Agent hat das Laden repariert (`lm_stage2.py`, RNG-Resume-Fix, Selbsttest). Der GPU-Dienst hat seit 10:21 eine **Hänger-Erkennung**: Endet ein Job-Log in einem Python-Traceback und wächst 10 min nicht mehr, wird der Job beendet (`failed:hung`); optional `stall_minutes` für Jobs ohne jede Ausgabe.

### P-003 · Priorität im GPU-Dienst wirkungslos (29.09., ≈ 08:55) 🟢
- **Symptom:** Eine später eingereichte Datei mit kleiner Nummer (höhere Priorität) wartete hinter allen früheren.
- **Ursache:** Der Dienst startete Jobs in Einreichungsreihenfolge statt nach Dateinamen (vom Lab-Agenten gemeldet).
- **Lösung:** Start nach Namensreihenfolge; aktiv seit dem Neustart 10:21.

### P-004 · DRAIN bei alter Instanz wirkungslos (29.09., ≈ 09:30) 🟢
- **Symptom:** Ein sanfter Neustart per `lab/queue/DRAIN` hätte nichts bewirkt.
- **Ursache:** Die laufende Dienst-Instanz war vor dem Einbau von DRAIN gestartet worden und hatte den alten Code.
- **Lösung:** Einmaliger harter Neustart um 10:21 (vom Nutzer freigegeben; Kosten: 10 angefangene Repro-Läufe neu). `status.json` zeigt seitdem unter `features`, was die laufende Instanz kann.

### P-005 · Schwächen in der neuen Hänger-Erkennung (29.09., ≈ 10:00) 🟢
- **Symptom:** Ein unabhängiger Prüf-Agent fand: ein Schreibfehler beim Protokollieren hätte den ganzen Dienst samt aller Jobs abstürzen lassen; bis zu 30 s Blockieren; ein Job, der gerade von selbst endet, hätte als Hänger markiert werden können.
- **Lösung:** Vor dem Einsatz behoben (Fehler abgefangen, kein Warten, Platz erst frei, wenn der Prozess wirklich weg ist; Wartezeit 10 statt 5 min). Selbsttest bestanden.

### P-006 · Lauf-Protokoll teilweise zerstört (29.09., 10:03) 🔴 niedrig
- **Symptom:** In `lab/runner/logs/guarded_runs.jsonl` sind 7 von 14 888 Zeilen nur Bruchstücke.
- **Ursache:** Viele Wächter schreiben gleichzeitig ans Dateiende; unter Windows können sich solche Schreibvorgänge überlagern.
- **Auswirkung:** Nur das Protokoll (≈ 0,05 % der Einträge fehlen), nicht die Ergebnisse (die stehen in den `result.json` der Läufe).
- **Lösung (vorgeschlagen):** Dateisperre beim Schreiben im Wächter.

### P-007 · Neustart-Risiko durch Windows-Update (29.09., 10:03) 🟢
- **Symptom:** Nutzungszeit ist 11–03 Uhr, Windows darf also zwischen 03 und 11 Uhr für Updates neu starten. Die geplanten Aufgaben laufen nur, solange der Nutzer angemeldet ist.
- **Risiko:** Ein Update-Neustart in der Nacht würde das Labor bis zur nächsten Anmeldung stoppen.
- **Lösung (beim Nutzer):** Updates für eine Woche pausieren (Einstellungen → Windows Update); nicht abmelden (Sperren ist in Ordnung).
- **Stand 30.09., 14:45 (geprüft):** Updates sind vom 29.09., 23:45 bis 06.10., 23:45 pausiert (Registry `PauseUpdatesExpiryTime`, gefunden von Prüfagent A4). Bleibt als Eigenschaft: Beide Aufgaben laufen nur bei Anmeldung (LogonType Interactive) – nach einem Stromausfall oder Neustart rechnet das Labor erst nach der Anmeldung weiter.

### P-008 · L0-Reproduktion auf der GPU nicht ganz bitgleich (29.09., 09:36) ⚪
- **Beobachtung:** Beim Nachrechnen von L0 ist Batchgröße 256 exakt gleich, bei 64 gleiches Urteil, aber 3 von 20 Läufen weichen spät ab.
- **Ursache (vom Lab-Agenten belegt):** seltene nicht-deterministische Rechenschritte der GPU.
- **Umgang:** im Paper dokumentiert (Anhang R, Reproduktionsstand); die Aussagen hängen nicht davon ab.
- **Nachtrag 21:22:** Dasselbe bei der Reproduktion von R4: 239 von 240 Läufen bitgleich, einer weicht spät ab – die vorab festgelegte Prüfschwelle wurde damit knapp verfehlt; der Lab-Agent hat eine Wiederholung eingereiht und es im Paper vermerkt.

### P-009 · Grafikspeicher überbucht (29.09., ab ≈ 13:00) 🟢 gelöst (Speicherschutz seit 14:25)
- **Symptom:** 10 Sprachmodell-Läufe gleichzeitig (4× LM1, 4× EXP-115, 2× EXP-113), je ≈ 3,1 GB → ≈ 31 GB bei 20 GB Grafikspeicher. Windows lagert ≈ 14,6 GB in den Arbeitsspeicher aus.
- **Folgen:** Läufe ≈ 8× langsamer (2,4 s statt 0,3 s pro Schritt; die „100 % GPU“ waren großteils Speicherverschieben); freier Arbeitsspeicher 1,8–2,2 GB; freie Speicherzusage zeitweise nur 1,5 GB (Absturzgefahr für Dienst und Sitzung); Windows vergrößerte die Auslagerungsdatei auf ≈ 54 GB → P-010.
- **Erkannt:** Der Lab-Agent bemerkte den Einbruch um ≈ 12:59, senkte die Obergrenzen in seinen Jobdateien und bat um Hilfe; Läufe abbrechen durfte er nicht (Sicherheitsprüfung, 13:21). Der stündliche Check meldete es um 13:15.
- **Ursache:** Der GPU-Dienst kannte keinen Grafikspeicher; die Obergrenzen der einzelnen Jobdateien addieren sich (4 + 4 + 2); gesenkte Obergrenzen liest der Dienst erst nach einem Neustart.
- **Prüfung vor der Umsetzung (Prüf-Agent, „umsetzen mit Änderungen“):** nur den Dienst beenden, nicht den ganzen Prozessbaum (sonst verbucht er abgebrochene Läufe als endgültig gescheitert); vor dem Neustart die alten Sperrdateien (`run.lock`) der Läufe löschen (Windows vergibt Prozessnummern neu); Dienst über die geplante Aufgabe starten, nicht von Hand; Speicherschutz mit fester Buchführung der angemeldeten Größen statt nur 60-s-Fenster, Grenze ≈ 16 statt 17,5 GB, Messung ohne den Dienst zu blockieren.
- **Schritt 1 (13:58, erledigt):** Dienst beendet (Job-Objekt nahm alle Läufe mit), 10 alte Sperrdateien gelöscht, Neustart über die Aufgabe mit vorübergehend höchstens 5 Läufen (`--max-workers 5` in `launch_daemon_hidden.vbs`). Kein Lauf als gescheitert verbucht; Sprachmodell-Läufe setzten am Checkpoint fort (z. B. LM1 ab Schritt 1 000). Danach: Grafikspeicher 13,2 GB, ausgelagert 0,8 GB, freier Arbeitsspeicher 15,6 GB, Windows verkleinerte die Auslagerungsdatei (C: 133 GB frei).
- **Schritt 2 (14:25, erledigt):** Speicherschutz im GPU-Dienst (`lab/tools/gpu_memory.py`): Jede Jobdatei meldet mit `gpu_gb` die Größe eines Laufs an (gemessen: Sprachmodell 3,4 GB, kleine Repro-Läufe 0,8 GB). Ein Job startet nur, wenn max(Messung, 2,5 GB Reserve + angemeldete Größen) + seine Größe ≤ 16 GB bleibt, nichts ausgelagert wird und RAM/Speicherzusage reichen; höchstens ein Start alle 6 s; unterbrochene Läufe zuerst; geänderte Kopfzeilen werden neu eingelesen. Zweite Prüfung (Code) fand u. a. fehlenden Absturzschutz in 4 von 6 Schritten (ein gesperrtes `status.json` hätte alle Läufe beendet), fehlende Prüfung unsinniger Werte (`gpu_gb=0.35`) und das Verwerfen einer Jobdatei bei beschädigter Fortschrittsdatei – alles vor der Aktivierung behoben und getestet (18 Selbsttests). Aktiviert per Neustart um 14:25 (nur Dienst beendet, Sperrdateien geräumt); die Zwischengrenze von 5 Plätzen ist wieder entfernt.

### P-010 · Freier Platz auf C: fällt schnell (29.09., 13:15) 🟢
- **Symptom:** C: fiel von 106 GB (10:00) auf 67 GB (13:15), zeitweise ≈ 20 GB pro Stunde.
- **Ursache:** P-009 (wachsende Auslagerungsdatei); sie schrumpft erst nach einem Windows-Neustart.
- **Lösung:** 27 GB alte Reste im Hugging-Face-Zwischenspeicher gelöscht (abgebrochene Datensatz-Datei vom 06.08., abgebrochener Modell-Download vom 20.09.; mit Freigabe des Nutzers) → 92,7 GB frei. Nach Schritt 1 von P-009 verkleinerte Windows die Auslagerungsdatei von selbst → 133 GB frei (13:59).

### P-011 · Startdatei des GPU-Dienstes verlor ihre Windows-Zeilenenden (29.09., 13:58) 🟢
- **Symptom:** Beim Eintragen der Zwischengrenze in `lab/runner/launch_daemon_hidden.vbs` speicherte das Bearbeitungswerkzeug die Datei mit Unix-Zeilenenden (LF statt CRLF).
- **Risiko:** Der Windows-Skript-Host hätte die Datei womöglich nicht mehr richtig gelesen; dann hätte die geplante Aufgabe den GPU-Dienst nicht mehr starten können.
- **Lösung:** Vor dem Start bemerkt und auf CRLF zurückgesetzt; der Dienst startete normal. Vorbeugung: nach jeder Bearbeitung von Windows-Dateien die Zeilenenden prüfen.

### P-012 · Speicherschutz-Entwurf mit zu strenger Grenze (29.09., 14:10) 🟢
- **Symptom:** Der Probelauf der echten Messung zeigte bei gesundem System (17,7 GB RAM frei) nur 7,4 GB freie Speicherzusage – unter der geplanten Grenze von 8 GB. Der Speicherschutz hätte jeden Start blockiert.
- **Ursache:** Jeder GPU-Prozess reserviert ≈ 3 GB virtuellen Speicher; Windows vergrößert die Auslagerungsdatei nach Bedarf, daher ist die freie Zusage im Normalbetrieb klein. Die Grenze war ohne Messung geschätzt.
- **Lösung:** Grenze auf 2 GB gesenkt (beim Vorfall P-009 waren es 1,5 GB); vor dem Einsatz behoben. Lehre: Grenzwerte vor dem Einsatz an echten Messwerten prüfen.

### P-013 · Speicherschutz blockierte zu Unrecht (29.09., 14:26) 🟢
- **Symptom:** Direkt nach der Aktivierung des Speicherschutzes startete der Dienst nach 3 Sprachmodell-Läufen nichts mehr: „commit 1.4 GB free“ – obwohl 16,7 GB Arbeitsspeicher frei waren und die Grafikkarte Platz hatte.
- **Ursache:** Windows hatte die Auslagerungsdatei nach der Entlastung von selbst auf 14 GB verkleinert; sie wächst erst wieder, wenn ein Programm Speicher anfordert. Die Regel „mindestens 2 GB freie Zusage“ (P-012) blockierte also genau die Anforderung, die das Wachstum ausgelöst hätte. Die Tests mit vorgegebenen Messwerten konnten das nicht zeigen.
- **Lösung:** Die Prüfung rechnet jetzt mit dem Spielraum bis zur größtmöglichen Speicherzusage (RAM + Auslagerungsdatei bis 3 × RAM, begrenzt durch freien Plattenplatz): derzeit ≈ 82 GB; Grenze 8 GB. Getestet (auch mit echten Messwerten), aktiviert per sanftem Neustart (DRAIN, 14:29): die laufenden Läufe rechneten zu Ende, um 14:42 startete der neue Code; zuerst liefen die unterbrochenen Läufe an (EXP-113 ab Checkpoint 13 000, R4), Speicherzusage-Spielraum ≈ 81 GB, keine Sperre mehr. Der stündliche Check wertet die momentan freie Zusage nicht mehr als Alarm.
- **Lehre:** Grenzwerte nicht nur mit vorgegebenen Testwerten, sondern auch im echten Betrieb über einige Minuten beobachten.

### P-014 · Kurzer Ausfall der Auto-Mode-Sicherheitsprüfung (29.09., 16:22–16:24) 🟢
- **Symptom:** In Laborsitzung 51 lieferte die Sicherheitsprüfung etwa 2 Minuten lang keine Entscheidung; Befehle (Bash) waren blockiert, Lesen und Bearbeiten gingen weiter (gemeldet vom Lab-Agenten im JOURNAL, 16:24).
- **Ursache:** vorübergehender externer Dienstfehler (wie P-001, diesmal ohne Sitzungsabsturz).
- **Folge:** keine – der Hintergrundlauf (EXP-118 Nachtrag 1) und der GPU-Dienst liefen unberührt weiter; das zeigt, dass die Trennung von Sitzung und GPU-Dienst (P-001) wirkt.
- **Lösung:** keine nötig; Sitzung arbeitete danach normal weiter.

### P-015 · Erneute kurze Störung der Auto-Mode-Sicherheitsprüfung (29.09., ≈ 20:18–20:22) 🟢
- **Symptom:** Laborsitzung 53 meldete in LIVE 8 Fehlversuche der Sicherheitsprüfung innerhalb von ≈ 4 Minuten, danach normal.
- **Ursache:** vorübergehender externer Dienstfehler (wie P-001 und P-014); dritter Fall an diesem Tag.
- **Folge:** keine – GPU-Dienst und Läufe liefen weiter (53 Läufe in der Stunde fertig), alle Änderungen der Sitzung sind committet.
- **Lösung:** keine nötig. Beobachten: Häufen sich solche Störungen, verliert eine Sitzung Arbeitszeit; ein Sitzungsabbruch wird vom Runner als service_unavailable eingestuft und nach 15 min neu gestartet.

### P-016 · Kaputte Umlaute in lab/LIVE.md (30.09., 01:24) 🟢
- **Symptom:** In `lab/LIVE.md` stehen statt Umlauten Zeichenfolgen wie „unabhÃ¤ngiger“ oder „lÃ¤uft“ (28 Stellen); in Obsidian schlecht lesbar. Andere Notizen (JOURNAL, STATE) sind in Ordnung.
- **Ursache (vermutet):** Die Laborsitzung 55 hat die Datei einmal falsch dekodiert (UTF-8 als Windows-1252 gelesen) und wieder als UTF-8 gespeichert.
- **Folge:** nur Lesbarkeit der Live-Notiz; keine Daten oder Ergebnisse betroffen.
- **Lösung:** Sitzung 55 hat LIVE.md um ≈ 03:10 neu geschrieben; seit 03:34 keine kaputten Umlaute mehr (geprüft). Kein Eingriff nötig gewesen.

### P-017 · Leere Jobdatei als „erledigt“ abgelegt (30.09., ≈ 04:20) 🟢
- **Symptom:** Der Lab-Agent legte den Bestätigungsblock LM3 (20 Läufe) per Umleitung (`… > lab/queue/inbox/43_lm3.jobs`) in die Warteschlange. Der GPU-Dienst griff die Datei auf, als sie noch leer war, und legte sie mit 0 Jobs in `done/` ab – ohne Warnung. Der Agent bemerkte es und reichte den Block als `43_lm3b` neu ein.
- **Ursache:** Der Dienst liest den Eingangsordner alle 2 s und nimmt jede neue Datei sofort; eine Datei, die gerade erst angelegt wird, ist in diesem Moment leer. Eine Jobdatei mit 0 Jobs gilt als „fertig“.
- **Folge:** Ein ganzer Bestätigungsblock wäre beinahe unbemerkt ausgefallen; tatsächlich nur wenige Minuten Verzug.
- **Umgehung (aktiv):** Der Lab-Agent schreibt Jobdateien jetzt erst außerhalb des Eingangsordners und verschiebt sie fertig hinein (als Regel in seinem Gedächtnis).
- **Lösung (vom Nutzer freigegeben 30.09. ≈ 08:20):** Der Dienst liest neue Dateien erst, wenn sie 5 s unverändert sind (solange zählen sie als Arbeit, der Dienst beendet sich nicht), und lehnt eine Datei ohne Jobzeilen mit Begründung ab. Getestet (Datei wird nachträglich gefüllt → vollständig gelesen; leere Datei → abgelehnt; Speicherschutz, Vorrang, DRAIN und Hänger-Erkennung unverändert). Aktiviert per sanftem Neustart: DRAIN 08:29, alle laufenden Jobs regulär beendet, neuer Dienst seit 09:06 (status.json → features: settled_pickup); kein Lauf verloren.

### P-018 · Zu langsamer CPU-Test, Abbruch verweigert (30.09., ab 09:31) 🟢
- **Symptom:** Der Vortest zum Pythia-Versuch (`first_gradient.py`, Laborsitzung 58) läuft viel langsamer als geplant und belegt ≈ 9 der 12 CPU-Kerne (CPU-Last 98 %). Der Lab-Agent wollte ihn beenden, die Auto-Mode-Sicherheitsprüfung hat das abgelehnt; er hat den Nutzer in LIVE darauf hingewiesen.
- **Ursache:** Der Test rechnet auf der CPU mit allen Kernen statt auf der GPU bzw. mit begrenzten Threads; ein Beenden von Prozessen dürfen die Laborsitzungen nicht (wie schon bei P-002).
- **Folge:** CPU bis ≈ 11:30 ausgelastet (dann beendet der Wächter den Test); die GPU-Läufe laufen weiter, eventuell etwas langsamer.
- **Lösung:** Nutzer entscheidet: sofort beenden mit `taskkill /T /F /PID 24808` (Startprozess des Tests samt Kindprozess) oder bis 11:30 laufen lassen. Vorbeugung: CPU-Tests neben dem GPU-Dienst mit begrenzten Threads starten.
- **Ausgang:** Der Nutzer war nicht am Rechner; der Test lief nach 61,8 min um 10:32 regulär zu Ende (Ergebnis gesichert). Der Lab-Agent begrenzt künftig die Threads und misst vorher die Zeit an einem Batch (als Merkregel gespeichert).

### P-019 · Plattenplatz schrumpft durch Sprachmodell-Checkpoints (30.09., 14:41) 🔴
- **Symptom:** In 24 h hat `lab/` 12,4 GB geschrieben, davon 11,5 GB `.pt`-Checkpoints (83 Dateien, je ≈ 140 MB; v. a. `lab/confirm/lm3_raw`, `lm1_raw` und die LM-Experimente EXP-113 bis EXP-121). C: hat 106 GB frei (Prüfagent A4, 30.09., 14:41).
- **Ursache:** Jeder Sprachmodell-Lauf speichert seinen Checkpoint; es gibt keine Regel, explorative Checkpoints nach der Auswertung zu löschen oder auszulagern. Wächter und GPU-Dienst prüfen den freien Plattenplatz nicht (der Speicherschutz rechnet ihn nur gedeckelt in die Speicherzusage ein).
- **Folge:** Bei gleichem Tempo fällt C: etwa am 03./04.10. unter 60 GB, am 06.10. bleiben ≈ 35–40 GB. Bei voller Platte würden Läufe beim Speichern scheitern. Der stündliche Gesundheitscheck meldet < 60 GB.
- **Lösung (Vorschlag, Entscheidung Nutzer):** Regel für Checkpoints: explorative `.pt`-Dateien nach der Auswertung löschen oder auf eine externe Platte verschieben, Bestätigungs-Checkpoints behalten; freien Platz täglich prüfen.
- **Beobachtung (01.10., 04:07):** Der freie Platz auf C: schwankt von Stunde zu Stunde um ±15–18 GB (30.09./01.10.: 107 → 93 → 121 → 111 → 107 → 89 → 107 → 90 → 103 → 85 GB). Das Labor schreibt nur ≈ 1 GB/h, Temp, Caches und Absturzabbilder sind unauffällig, die Auslagerungsdatei schwankt zwischen 36 und 43 GB. Der Rest liegt vermutlich in Windows-Systemdateien (z. B. Schattenkopien) und ist ohne Adminrechte nicht prüfbar. Kein Datenverlust-Risiko, solange der Tiefstwert über 60 GB bleibt; der stündliche Check meldet darunter.

### P-020 · Werkzeuge ohne Git-Sicherung, Lücken in .gitignore (30.09., 14:41) 🔴 Nutzer
- **Symptom:** `lab/tools/gpu_daemon.py`, `gpu_memory.py`, `parallel_queue.py`, `lab/runner/install_gpu_daemon_task.ps1` und `launch_daemon_hidden.vbs` sind nicht versioniert (`git status`: `??`). Die Repro-Anleitung (`lab/paper/repro/README.md`, Zeile 18) ruft `parallel_queue.py` auf. `lab/confirm/*_raw/`, `*_smoke/` (mit `checkpoint.pt`), `lab/experiments/**/raw/` und `lab/queue/` sind weder versioniert noch ignoriert.
- **Ursache:** Die Werkzeuge entstanden in der Assistenten-Sitzung (29./30.09.); Runner- und Dienst-Dateien werden nicht ohne den Nutzer committet.
- **Folge:** Keine Sicherung der Werkzeuge; das Repro-Paket ist aus Git allein nicht lauffähig. Ein versehentliches `git add lab/` würde mehrere GB Checkpoints aufnehmen (je ≈ 140 MB, über der GitHub-Grenze von 100 MB).
- **Lösung (Nutzer):** Die Dateien gezielt einzeln committen (kein `git commit -a`); `.gitignore` um `*.pt`, `lab/confirm/*_raw/`, `lab/confirm/*_smoke/`, `lab/experiments/**/raw/` und `lab/queue/` ergänzen.

### P-021 · Fertige Pythia-Läufe hängen beim Beenden (30.09., 16:25–16:45 und 17:24–18:16) 🟢
- **Symptom:** Die Läufe EXP-127 Seed 4000 F und G (Dienst-Jobs `44z_exp127_pythia` #0/#1, gestartet 15:44/15:49) sind um 16:20/16:25 fertig, `result.json` ist geschrieben (Test 0.987/0.974). Die Prozesse (PIDs 24416→19156 und 28528→31860) beenden sich aber nicht, belegen je 5,5 GB Grafikspeicher und rechnen nicht mehr (CPU ≈ 1 %). GPU-Auslastung 0 %; der Speicherschutz lässt die nächsten Pythia-Läufe (je 5 GB) nicht zu, die ganze Warteschlange steht (geprüft 16:34).
- **Ursache:** Der ROCm-Abbau am Prozessende bleibt hängen (im EXP-127-README als 2–3 min bekannt, hier > 10 min). Die Hänger-Erkennung des Dienstes greift nicht: kein Traceback (crash_minutes) und keine stall_minutes im Kopf der Jobdatei. Das Beenden per taskkill hat die Sicherheitsprüfung der Laborsitzung abgelehnt (wie bei P-002/P-018); die Sitzung hat den Nutzer in LIVE darauf hingewiesen.
- **Folge:** GPU leer seit ≈ 16:25. Ohne Eingriff beendet der Wächter die Prozesse erst an der Zeitgrenze job_minutes 300 (≈ 20:45/20:50) → ≈ 4 h Leerlauf; Pythia-Auswertung und alle folgenden Blöcke (EXP-125, -128, -129) verschieben sich um ≈ 4 h.
- **Lösung (Nutzer):** Die zwei Prozessbäume beenden: `taskkill /T /F /PID 24416` und `taskkill /T /F /PID 28528`. Es geht nichts verloren (beide `result.json` liegen vor); der Dienst verbucht die zwei Jobs vermutlich als fehlgeschlagen. Vorbeugung (Laborsitzung 61, 16:50): `ft_pythia.py` endet schon seit Sitzung 58 mit `os._exit(0)` – der Hänger liegt also im Prozessende von ROCm selbst und lässt sich per Code nicht vermeiden. Neue Pythia-Jobdateien (ab EXP-130) bekommen `stall_minutes=15` im Kopf (das Log wächst im Training alle ≈ 2,3 min); danach beendet der Dienst solche Hänger selbst. Die laufende Datei `44z_exp127_pythia` (#2/#3) bleibt ohne.
- **Ausgang:** Der Nutzer hat um 16:45 zugestimmt („Ja beenden“); der Assistent hat nach Prüfung der Befehlszeilen `taskkill /T /F` auf die Starter 24416 und 28528 ausgeführt, die Kindprozesse endeten mit. Grafikspeicher frei (3,2 GB belegt), der Dienst startete sofort die Läufe #2/#3 (Seed 4001). Die Jobs #0/#1 stehen im Dienst als `failed:1` (exit 1), ihre `result.json` sind unberührt. Offen: Die Läufe #2/#3 nutzen denselben Code und können beim Beenden wieder hängen (≈ 17:25).
- **Wiederholung (geprüft 17:34):** Auch #2/#3 (Seed 4001 F/G, fertig 17:23/17:24, `result.json` geschrieben und von Sitzung 61 ausgewertet) hängen beim Beenden (PIDs 6572→1616 und 15624→13336, je 5,5 GB Grafikspeicher). GPU 0 %, EXP-130 wartet dahinter. Beenden nur mit Zustimmung des Nutzers (angefragt 17:31).
- **Ausgang 2:** Der Nutzer hat zugestimmt („ja fixe das problem“); um 18:16 hat der Assistent nach Prüfung der Befehlszeilen die Starter 6572 und 15624 samt Kindprozessen beendet. Der Dienst startete sofort EXP-130 (#0/#1); die Jobs #2/#3 stehen als `failed:1`, ihre `result.json` sind unberührt und ausgewertet. **Dauerhafte Lösung:** Pythia-Jobdateien tragen `stall_minutes=15` (EXP-130, EXP-132 geprüft), damit beendet der Dienst solche Hänger nach 15 min selbst; als Pflicht in Regel 21 von `lab/runner/SESSION_PREAMBLE.md` festgehalten (gilt ab der nächsten Laborsitzung).
- **Bewährt (geprüft 21:07):** Die EXP-132-Läufe Seed 1000 F/G (Pythia, mit `stall_minutes=15`) hingen nach dem Speichern ebenfalls beim Prozessende; der GPU-Dienst hat sie um 20:51 selbst beendet (`killed_stalled`, Ergebnisse vollständig), ohne Eingriff von Nutzer oder Assistent. Leerlauf nur die 15 min Wartezeit.
- **Offener Vorschlag (21:41, geprüft 22:07):** Jeder Pythia-Hänger kostet bis zur Stillstands-Grenze 15 min GPU-Leerlauf (so auch EXP-132 Seed 1001, fertig 21:28, beendet ≈ 21:43). Die Läufe schreiben alle ≈ 2,3 min ins Log, `stall_minutes=7` würde ≈ 8 min je Paar sparen. Die Laborsitzung stimmt zu, ihre Änderung der Kopfzeile von `44zzzz_exp133_reset.jobs` lehnte ihre Sicherheitsprüfung ab. Die Änderung einer Jobdatei ist keine Runbook-Klasse → wartet auf die Entscheidung des Nutzers.

### P-022 · Zu schwerer CPU-Zeittest, Abbruch abgelehnt (30.09., 19:13–19:34) 🟢
- **Symptom:** Der CPU-Zeittest `first_gradient_reset.py --device cpu --threads 4 --limit 256` (EXP-133, PID 18524, Wächter 23656) belegte ≈ 5 Kerne und bremste die LM3-F-Nachrechnung des Dienstes. Das Beenden durch die Laborsitzung lehnte die Sicherheitsprüfung ab (Interfere With Workloads).
- **Ursache:** CPU-Test neben dem laufenden Dienst mit mehr Last als geplant (wie P-018); Sitzungen dürfen Prozesse nicht beenden.
- **Folge:** Die LM3-F-Nachrechnung lief ≈ 20 min langsamer; sonst keine.
- **Lösung:** Die Sitzung hat nach Regel 22 einen „Hinweis für den Assistenten“ in LIVE geschrieben (PID, Startzeit, Befehl, warum nichts verloren geht) – erster Einsatz der neuen Regel. Der Test endete um 19:34 von selbst, bevor der stündliche Check lief; ein Eingriff nach Runbook A4 war nicht mehr nötig (geprüft 20:07).

### P-023 · Umbenannte Jobdateien als Geister-Einträge im GPU-Dienst (01.10., 11:59) 🟢
- **Symptom:** `status.json` führt `52bz_exp140_p401` (3 offen) und `52bzz_exp141_alpha` (12 offen), obwohl die Dateien in `52a55_…` bzw. `52a6_…` umbenannt wurden (Hinweis der Laborsitzung 69 in LIVE, geprüft 12:07).
- **Ursache:** Der Dienst hält aufgegriffene Jobdateien im Speicher. Jobzeilen liest er nie neu, und `retire()` räumt nur Dateien, die noch existieren (`gpu_daemon.py`, `refresh`/`retire`). Umbenennen, während der Dienst läuft, erzeugt deshalb Doppel-Einträge.
- **Folge:** Kein Lauf geht verloren. Die Geister stehen in der Namensreihenfolge hinter den echten Dateien; wenn sie drankommen, überspringt `freq_ban.py` fertige Läufe per Fingerabdruck → ≈ 15 kurze Leerstarts. Kleines Restrisiko: Erreicht der Dienst einen Geister-Job, während derselbe Lauf der umbenannten Datei noch rechnet, laufen beide gleichzeitig in denselben Ausgabeordner (unwahrscheinlich, weil die Geister ganz hinten stehen).
- **Lösung:** Keine Sofortmaßnahme. Ein Neustart über DRAIN würde die GPU bis zu ≈ 1 h teilweise leer laufen lassen, und jeder ohnehin anstehende Neustart des Dienstes räumt die Geister von selbst. Vorbeugung: Jobdateien nicht umbenennen, solange der Dienst läuft; die Reihenfolge nur über DRAIN und Neustart ändern (der Laborsitzung mitgeteilt). Vorschlag für den nächsten geplanten Dienst-Neustart: Einträge, deren Datei verschwunden ist, nicht mehr starten und mit Hinweis aus `status.json` nehmen (`gpu_daemon.py`, mit Selbsttest und unabhängiger Prüfung).
- **Erledigt (geprüft 18:16):** Mit der Pause-Entscheidung des Nutzers wurde der Dienst um ≈ 17:15 per DRAIN beendet (EXP-139-Reste nach `lab/queue/parked/`); die neue Instanz läuft seit 17:48 und führt nur noch `52a7zzz_exp144_width` und `52a8_exp143_ledoux` – die Geister-Einträge sind weg, Leerstarts gab es keine. Die Laborsitzungen benennen Jobdateien nicht mehr um (seit 12:09).

### P-024 · Geteilter GPU-Speicher bei sehr großem p (01.10., 16:07) ⚪
- **Symptom:** `status.json → memory.gpu_shared_gb` = 4,39 (Schwelle 3). Per Prozesszähler: die drei EXP-143-Läufe (`lab/tools/freq_ban_large.py`, p = 9973) belegen dediziert 1,3 / 2,2 / 2,2 GB und *geteilt* 1,9 / 1,0 / 1,0 GB; die übrigen Prozesse (R15, Browser) fast nichts. Dedizierter Grafikspeicher insgesamt nur ≈ 13 von 20 GB.
- **Ursache (Analyse):** Keine klassische Auslagerung wegen vollem Grafikspeicher (7 GB waren frei), sondern Speicher, den die Hülle für sehr großes p im Hauptspeicher anlegt und der GPU zugänglich macht (stückweise Auswertung, Paare bei Bedarf). Der Speicherschutz zählt geteilten Speicher mit und hält deshalb weitere Starts zurück (`52a7z_exp143_wd01#3`: 17,4 + 2,5 > 16).
- **Folge:** Alle vier stillen Läufe rechnen normal (Hänger-Prüfung 16:07: CPU ≈ 1 Kern, GPU 53–96 %, Schreiben aktiv). Solange EXP-143 läuft, starten weniger Läufe parallel; kein Datenverlust, keine Verlangsamung erkennbar.
- **Lösung:** Keine nötig (Speicherschutz arbeitet wie vorgesehen). Hinweis an die Laborsitzung: Für weitere Läufe mit `freq_ban_large.py` `gpu_gb` ≈ 4 statt 2,5 anmelden, damit die Buchung zur Messung passt.
- **Umgesetzt (16:16, Laborsitzung 71):** `gpu_gb` in den Kopfzeilen von `52a7zz_exp143_stride600k` und `52a8_exp143_ledoux` von 2,5 auf 4 gesetzt (Datei unter gleichem Namen atomar ersetzt, Jobzeilen unverändert, per `cmp` geprüft); die laufenden `52a7z`-Jobs blieben unangetastet.

### P-025 · Leersitzungen alle 10 min während der Pause (01.10., 19:29 – 02.10., 02:32) 🟢
- **Symptom:** Seit dem Abschluss der LeDoux-Linie (Sitzung 72, Commit 19:26) startet der Runner bei jedem Takt eine neue Laborsitzung (S73 19:29, S74 19:39 … S78 20:19, laut tick.log). Jede prüft kurz STOP, Dienst und LIVE, schreibt „Pause aktiv (Regel 23)“ und committet „status check, pause active“. Je ≈ 1 min, 4–5 Züge, ≈ 79 000 neu geschriebene Cache-Tokens, ≈ 0,73–0,78 $ API-Gegenwert (`lab/runner/logs/session_*.out.json`).
- **Ursache:** `tick.ps1` setzt nach jedem regulären Sitzungsende `next_start_utc` = Ende (Zeile 299, „continue at the next tick“). Regel 23 lässt jede Sitzung nach kurzer Lagekontrolle enden, verhindert aber den nächsten Start nicht. Fehleinschätzung des Assistenten beim Schreiben von Regel 23.
- **Folge:** Keine für Daten, Dienst oder Ergebnisse. Ohne Änderung ≈ 6 Sitzungen pro Stunde, also ≈ 4,5 $ API-Gegenwert pro Stunde bzw. ≈ 100 $ pro Tag an Nutzungskontingent ohne Nutzen, dazu ≈ 144 Leer-Commits pro Tag. Die Lagekontrolle macht der stündliche Check ohnehin.
- **Lösung (Vorschlag, wartet auf den Nutzer):** In `lab/runner-state.json` `status` = `stopped` und `pause_reason` = „Pause nach Regel 23 (Nutzerentscheidung 01.10.)“ setzen. `tick.ps1` beendet sich dann bei jedem Takt sofort (Zeile 173); die geplante Aufgabe bleibt aktiv, nichts wird gelöscht. Umkehrbar: zum Aufheben der Pause `status` = `idle`, `next_start_utc` = jetzt, `pause_reason` = null. Der stündliche Check behandelt `stopped` mit diesem Grund dann als erwartet. Nicht automatisch angewendet: Die Änderung stellt keinen Betrieb wieder her und verhindert keinen Leerlauf, sondern hält den Betrieb an (Runbook, „Neue Probleme ohne passende Klasse“, erste Bedingung).
- **Nachtrag 22:16:** Bis 22:10 liefen S73–S89, also 17 Leersitzungen. Die Sitzungen schreiben in LIVE „Nächster geplanter Start: 02.10. 01:44“. Das ist aber nur der Schutzwert, den `tick.ps1` während einer laufenden Sitzung setzt (Start + 215 min, Zeile 209). Nach dem Ende setzt `tick.ps1` ihn auf das Ende zurück (Zeile 299), und die nächste Sitzung startet 10 min später. Die Angabe in LIVE ist also irreführend; sie fällt weg, wenn der Vorschlag umgesetzt wird.
- **Umgesetzt (02.10., 02:32, Zustimmung des Nutzers):** In `lab/runner-state.json` ist `status` = `stopped` und `pause_reason` gesetzt. Geändert per Python, sonst bytegleich; geprüft mit `ConvertFrom-Json` wie in `tick.ps1`. Bei status stopped beendet sich tick.ps1 sofort (Zeile 173). Der erste Takt danach (02:39) war bei Ende der Assistenten-Sitzung noch nicht gelaufen. Nachprüfen: Nach 2026-10-02T00:30:45Z darf in tick.log kein „session start“ mehr stehen. Bis dahin liefen 43 Leersitzungen (S73–S115). Fortsetzen nach `lab/runner/hourly_check_prompt.md` („Beim Aufheben der Pause“). Die stündlichen Checks enden mit der Assistenten-Sitzung; ihr Text und das Auslastungs-Skript liegen jetzt in `lab/runner/`.

## Frühere Probleme (26.–28.09., Kurzfassung)

- 🟢 `tick.ps1`: eine leere Fehlerausgabe-Datei führte bei jedem Sitzungsende zu einem Runner-Fehler (26.09., behoben, Zähler zurückgesetzt).
- 🟢 Wächter: das Job-Objekt scheiterte mit `OverflowError` (fehlende ctypes-Signaturen; vom Lab-Agenten gefunden, 27.09.).
- 🟢 Wächter: Kindprozesse der GPU-Umgebung wurden zu spät ans Job-Objekt gebunden (Wächter tritt jetzt vor dem Start bei).
- 🟢 Zeitfenster über Mitternacht brach Läufe um 23:57 ab (Fenster werden jetzt verkettet); Restzeit bei Sommerzeit falsch berechnet (jetzt in UTC).
- 🟢 Codex „astra“ verlangte eine neuere Codex-CLI (separat installiert).
- 🟢 Word-Brief: leeres Inhaltsverzeichnis, falsche Nummerierung, zerrissene Tabellen; erfundene Literaturtitel durch echte ersetzt.
- 🟢 Neuheitsprüfung: falsche Aussage über Fu et al. 2026 (per Volltext korrigiert); Kontaktliste: falsch zugeordnete Webseite entfernt.

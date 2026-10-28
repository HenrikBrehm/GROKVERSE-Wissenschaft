DIESE SITZUNG WURDE VOM ÄUSSEREN RUNNER GESTARTET (lab/runner/tick.ps1).
Der vollständige, unveränderte Auftrag folgt unten. Betriebsregeln dieses Labors dazu:
VORRANG: Diese Betriebsregeln gehen dem Auftrag (PROMPT.md) vor, wo sie sich widersprechen; spätere Regeln gehen
früheren vor. Insbesondere gelten NICHT mehr: „8 Zyklen / 90 min“, „ein Job gleichzeitig“, „20 min pro Job“ (§9) und
die Quote „jeder dritte Zyklus neu“ (§4, ersetzt durch Regel 9 und 15). PROMPT.md bleibt als historischer Auftrag
unverändert.

1. Lies ZUERST lab/STATE.md, dann lab/BACKLOG.md und das Ende von lab/JOURNAL.md.
   Keine vollständige Projektanalyse wiederholen. Prüfe `git status` (Branch lab/research)
   und ob Python-/Trainingsprozesse laufen, bevor du etwas startest.
2. Existiert lab/STOP: nichts ausführen, STATE.md kurz aktualisieren, Sitzung beenden.
3. Jeder Testlauf, jede Testsuite und jedes Training läuft AUSSCHLIESSLICH über
   `python lab/tools/guarded_run.py -- <befehl>` (setzt 00:00–13:00 Europe/Berlin und die
   Sitzungsdeadline technisch durch; eine feste Jobgrenze gibt es nicht mehr, siehe Regel 14).
   AUSNAHME DES NUTZERS: Am 2026-09-26 dürfen Trainings und Tests bis 18:00 Berlin laufen (im Wächter
   als WINDOW_END_OVERRIDES hinterlegt). Ebenso am 2026-09-28: Läufe bis 18:00 Berlin (Nutzer, 27.09. 21:20).
   NACHT 27./28.09.: Nutzer 21:55: Läufe gestoppt, keine Läufe bis 28.09. 01:30 (im Wächter), dann bis 18:00.
   WOCHE 28.09.–05.10. (Nutzer, 28.09. abends): Läufe DURCHGEHEND vom 28.09. 23:59 bis 06.10. 00:00 (im Wächter als
   EXTRA_WINDOWS; nahtlos weiter im normalen Fenster bis 06.10. 13:00). Danach wieder 00:00–13:00.
   An allen anderen Tagen gilt 00:00–13:00. Prüfe vorher mit
   `python lab/tools/guarded_run.py --check`. Exit-Code 3 = verweigert → nicht umgehen.
4. Sitzungsdeadline (UTC) steht in der Umgebungsvariable LAB_SESSION_DEADLINE_UTC
   (Start + 180 min). Nach Ablauf: Stand sichern und Sitzung beenden, auch mitten im Plan.
   Die Deadline ist nur ein Abschnitt: Der Runner startet die nächste Sitzung direkt danach.
5. Aktualisiere lab/STATE.md und lab/JOURNAL.md nach jedem wesentlichen Schritt und VOR
   jedem längeren Lauf (nächste Aktion + Wiederaufnahmeweg). Committe lokal auf lab/research.
6. Den Runner (lab/runner/*, geplante Aufgabe "GROKVERSE-Lab-Runner") nicht umkonfigurieren,
   außer zur Reparatur eines dokumentierten Fehlers; runner-state.json-Felder `next_start_utc`,
   `status`, `lock` gehören dem Runner — nicht überschreiben.
7. Die Studie (RESULTS.md, docs/, training/results/) ist historisch: nicht umschreiben.
   Neue Befunde gehören nach lab/. Interpretation der Studie bleibt den menschlichen Autoren.
8. Beende die Sitzung mit dem Abschlussbericht nach Auftrag §10.
9. WUNSCH DES NUTZERS (2026-09-25): Du entscheidest vollständig selbst, woran du gerade
   arbeitest: wie lange, in welcher Reihenfolge, ob du an einer Sache über viele Sitzungen dranbleibst
   oder die Richtung wechselst. Es gibt keine Pflicht, pro Sitzung etwas anderes zu machen, und keine
   Quote. Ausdrücklich erwünscht ist auch Forschung an Dingen, die es noch GAR NICHT gibt, nicht nur
   für das Projekt neu, sondern für die Forschung neu. Wenn du so eine Richtung verfolgst:
   - Sammle Kandidaten in lab/NOVEL_DIRECTIONS.md (anlegen, falls es fehlt).
   - Vor einem Neuheitsanspruch: gezielte Suche (WebSearch/WebFetch, v. a. arXiv, Google Scholar, OpenReview)
     nach der konkreten Frage. Suchbegriffe, Datum und die nächstverwandten Arbeiten mit Link
     dokumentieren. Findet sich die Frage schon beantwortet, als „bekannt“ markieren und die
     Frage schärfen oder verwerfen.
   - Mutig sein bei neuen Aufgaben, Architekturen, Trainingsverfahren, Eingriffen, Messgrößen
     und Werkzeugen, die es so noch nicht gibt. Klein und billig zuerst testen.
   - Ehrlichkeit bleibt Pflicht: „neu“ heißt immer „nach unserer Suche vom <Datum> nicht gefunden“,
     nie „garantiert neu“. Das gilt ausdrücklich als vorläufige Einordnung (Auftrag §5).
10. OBSIDIAN: Das Projekt liegt im Obsidian-Vault des Nutzers (Vault-Root: Documents/Brain).
    Alle Notizen unter lab/ werden in Obsidian gelesen. Schreibe sie deshalb Obsidian-gerecht:
    - lab/LAB.md ist die Einstiegsnotiz (anlegen, falls sie fehlt): kurze Lage, Links auf
      [[STATE]], [[JOURNAL]], [[BACKLOG]], [[NOVEL_DIRECTIONS]] und auf jeden Versuch, mit Status
      und einer Zeile Ergebnis. Nach jedem Versuch aktualisieren.
    - Verlinke mit [[Wikilinks]]: Versuche untereinander, Versuch ↔ Backlog-Frage ↔ Journaleintrag
      ↔ Befund. Linkziele sind Dateinamen ohne .md; bei Mehrdeutigkeit den Pfad ab lab/ nehmen,
      z. B. [[experiments/EXP-001-freq-ban/README|EXP-001]].
    - Versuchs-READMEs und Befundnotizen bekommen YAML-Frontmatter (id, status, datum, tags).
    - Tags: #exp/vorbereitet, #exp/laufend, #exp/abgeschlossen, #exp/verworfen,
      #befund/positiv, #befund/negativ, #befund/unklar, #neu/kandidat, #neu/bekannt.
    - Nur Dateien unter lab/ ändern. Andere Teile des Vaults (Documents/Brain außerhalb
      GROKVERSE_Wissenschaft) nie anfassen.
    - Bestehende Inhalte nicht umschreiben, nur Links, Tags und Frontmatter ergänzen. Zahlen und
      Aussagen bleiben unverändert.
11. LIVE-ANZEIGE FÜR DEN NUTZER (liest sie auf dem iPad über Obsidian): Halte lab/LIVE.md aktuell.
    - Oben: Sitzungsstart, Deadline (aus LAB_SESSION_DEADLINE_UTC), jeweils in Berlin-Zeit, und der
      Zeitpunkt der letzten Aktualisierung.
    - „Gerade“: 1–3 Zeilen, was du in diesem Moment tust und warum.
    - „Als Nächstes“: der nächste geplante Schritt.
    - „Verlauf dieser Sitzung“: eine Zeile pro abgeschlossenem Schritt, neueste oben, mit Uhrzeit.
    - Aktualisieren bei jedem Schrittwechsel, vor jedem Lauf und mindestens alle ~10 Minuten
      Arbeitszeit. Kurz halten (unter 60 Zeilen). Ältere Verläufe gehören ins JOURNAL, nicht hierher.
    - Am Sitzungsende: Status „Sitzung beendet“ und nächster geplanter Start
      (next_start_utc aus runner-state.json, in Berlin-Zeit).
    - LIVE.md nicht bei jedem Update committen. Sie wird mit den normalen Commits mitgenommen.
12. CODEX (OpenAI) ALS ZWEITE MEINUNG: Plugin codex@openai-codex, vom Nutzer am 2026-09-25
    installiert. Die Codex-CLI ist per ChatGPT angemeldet.
    - Freigabe des Nutzers: Für dieses Projekt dürfen Code, Versuchsdefinitionen und Ergebnisse an
      Codex/OpenAI gesendet werden. Keine Geheimnisse, keine Dateien außerhalb dieses Projekts.
    - Zweck: unabhängige Prüfung durch eine andere Modellfamilie mit anderen blinden Flecken.
      Wofür: vor einem teuren Lauf das Versuchsdesign und den Auswertecode prüfen lassen
      (/codex:adversarial-review), nach einem Befund die Schlussfolgerung angreifen lassen, bei
      einem hartnäckigen Fehler /codex:rescue. Du entscheidest selbst, wann sich das lohnt.
    - Immer mit --wait (Vordergrund) aufrufen, damit das Ergebnis vor Sitzungsende vorliegt. Die
      Befehle so formulieren, dass keine Rückfrage an den Nutzer nötig ist (es antwortet niemand).
    - Nicht verwenden: /codex:transfer und /codex:setup --enable-review-gate. Das Review-Gate
      würde das Sitzungsende blockieren.
    - Codex-Aussagen sind Hinweise, keine Belege. Prüfe sie selbst und protokolliere im JOURNAL,
      was Codex gesagt hat, was du übernommen oder verworfen hast und warum.
    - Codex-Läufe zählen nicht als Test- oder Trainingsläufe, starten aber auch keine: Training und
      Tests laufen weiterhin nur über guarded_run.py im Fenster.
    - Wird ein Codex-Aufruf verweigert (Klassifikator, Limit, Fehler): dokumentieren, ohne Codex
      weitermachen, nicht umgehen.
13. DURCHGEHEND ARBEITEN (Wunsch des Nutzers, 2026-09-25): Der Loop ist dafür da, dass du
    ununterbrochen weiterforschst, bis das Usage-Limit erreicht ist. Danach setzt der Runner nach dem
    Reset automatisch fort. Das ersetzt die Grenze „8 Zyklen / 90 min“ aus Auftrag §9. Das Run-Fenster
    00:00–13:00 gilt weiter; mehrere Jobs gleichzeitig sind seit 2026-09-26 erlaubt (Regel 17).
    - Beende die Sitzung NICHT freiwillig. Nach jedem Zyklus beginnst du den nächsten, bis weniger
      als ~10 min bis LAB_SESSION_DEADLINE_UTC übrig sind. Dann sicherst du den Stand und schreibst
      den Abschlussbericht. Die nächste Sitzung knüpft über STATE.md an.
    - Außerhalb des Run-Fensters gibt es genug zu tun, und zwar echte Denk- und Sucharbeit:
      Literatur zu offenen Fragen und Befunden suchen, neue Hypothesen und Richtungen entwickeln
      und in lab/NOVEL_DIRECTIONS.md prüfen, eigene Befunde kritisch angreifen (auch mit Codex),
      gespeicherte Läufe neu auswerten, Folgeversuche vorab festlegen und ihren Code vorbereiten,
      den BACKLOG schärfen und priorisieren.
    - Jeder Zyklus braucht eine Frage und ein dokumentiertes Ergebnis im JOURNAL, auch ein negatives.
      Kein Beschäftigungs-Refactoring, keine kosmetischen Änderungen, nur um Zeit zu füllen.
    - STATE.md und JOURNAL laufend aktuell halten: Die Sitzung kann jederzeit am Usage-Limit abbrechen.
14. KEINE FESTE JOBGRENZE, DAFÜR LÄUFE BEOBACHTEN (Wunsch des Nutzers, 2026-09-25): Die Grenze
    „höchstens 20 min pro Einzeljob“ aus Auftrag §9 ist aufgehoben. Ein Lauf darf so lange dauern,
    wie er sinnvoll ist. Harte Grenzen bleiben nur 13:00 Berlin und die Sitzungsdeadline, beide setzt
    guarded_run.py durch. Lange Läufe deshalb früh in der Sitzung starten.
    - Starte Läufe, die länger als ein paar Minuten dauern, im Hintergrund (Bash run_in_background).
      Der Vordergrund-Timeout des Bash-Tools beträgt höchstens 10 min.
    - Beobachte jeden laufenden Job aktiv: Fortschritt (result.json/Log: Schritt, Loss, Accuracy)
      mindestens alle ~5–10 min prüfen und den Stand in LIVE.md eintragen. Nutze die Wartezeit für
      Denkarbeit (Regel 13), aber beende die Sitzung nie, solange ein Job läuft.
    - Brich einen Lauf selbst ab (Prozessbaum beenden), wenn er hängt (kein Fortschritt), divergiert
      (NaN, explodierender Loss), deutlich langsamer ist als geplant oder seine Frage schon beantwortet
      ist. Den Abbruch mit Grund im JOURNAL festhalten. Ein abgebrochener Lauf beweist nichts (§8).
    - Vor dem Start die erwartete Dauer aus s/Schritt abschätzen und notieren. Einen Lauf, der vor
      13:00 oder der Deadline nicht fertig werden kann, nicht starten, sondern teilen oder verkleinern.
    - FREIGABE DES NUTZERS (2026-09-26): Warteschlangen-Skripte (`sh lab/experiments/...queue....sh`) und
      `python lab/tools/guarded_run.py ...` sind per Berechtigungsregel in .claude/settings.local.json
      ausdrücklich erlaubt, auch im Hintergrund. Der Blocker aus Sitzung 5 ist damit aufgehoben. Jeder Lauf in
      einer Warteschlange muss weiterhin über guarded_run.py gehen.
15. FORSCHUNGSQUALITÄT VOR MENGE (Wunsch des Nutzers, 2026-09-26): Nach zwei Tagen gibt es über 40 kleine
    Versuche, viele mit Urteil „teilweise“ oder „n. s.“, alle zu einer Aufgabe. Ab jetzt gilt zusätzlich zu Regel 9:
    a) SYNTHESE-PFLICHT: Führe lab/FINDINGS.md (anlegen, falls es fehlt; Obsidian-Frontmatter, in [[LAB]] verlinken).
       Höchstens eine Seite: Kernaussagen mit Belegen (Versuch, n, p), Einordnung in die Literatur (was ist bekannt,
       was ist nach unserer Suche neu), die größte offene Frage. Aktualisieren mindestens einmal pro Tag und nach
       jeweils ~10 abgeschlossenen Versuchen. Jeder neue Versuch nennt in seiner README, auf welche Kernaussage oder
       offene Frage aus FINDINGS.md er zielt. Versuche ohne diesen Bezug nur mit Begründung im JOURNAL.
    b) WENIGER, DAFÜR STÄRKERE VERSUCHE: Mindestens 10 unabhängige Seeds für alles, was ein Urteil tragen soll
       (Explorationen und Smokes ausgenommen, als solche kennzeichnen). Keine Kette von Nachträgen: Braucht ein
       Versuch mehr als zwei Nachträge, lieber einen sauberen Nachfolgeversuch neu festlegen. Offene Reste eines
       Versuchs nicht automatisch mit einem Mini-Versuch verfolgen, sondern gegen die offene Frage in FINDINGS.md
       priorisieren.
    c) VERALLGEMEINERUNG ZUERST: Die Hauptbefunde (Frequenzwahl über die Daten steuerbar, EXP-016; Festlegung in den
       ersten ~5–50 Schritten, EXP-032/020) haben jetzt Vorrang vor weiteren Detailversuchen zur Addition mod p.
       Prüfe sie an anderen Aufgaben und Einstellungen, z. B. andere Moduli, Multiplikation oder andere
       Gruppenoperationen, größere oder anders gebaute Modelle, möglichst auch eine nicht-modulare Aufgabe. Ein
       Befund, der dort nicht hält, ist ein wichtiges Ergebnis und wird genauso dokumentiert.
    Bereits festgelegte Versuche in laufenden Warteschlangen (z. B. queue_s10.sh) dürfen zu Ende laufen; neu
    geplante Arbeit folgt dieser Regel.
16. GRAFIKKARTE NUTZEN (Wunsch des Nutzers, 2026-09-26): Der PC hat eine AMD Radeon RX 7900 XT (gfx1100, 20 GB).
    Eine eigene Umgebung mit PyTorch für ROCm liegt in `.venv-gpu` (torch 2.9.1+rocm7.2.1). Das globale Python
    (torch 2.13 CPU) bleibt unverändert. In PyTorch heißt die AMD-Karte trotzdem „cuda“:
    `.venv-gpu/Scripts/python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`.
    Aufgabe, sobald das Fenster offen ist (alles über guarded_run.py, wie jedes Training):
    a) `freq_ban.py` (und wo nötig die Auswerteskripte) bekommen eine Option `--device` (Standard `cpu`, damit alte
       Befehle gleich bleiben). Modell, Daten, Masken und alle Hilfstensoren auf das Gerät legen; CPU-Pfad unverändert.
       Das Gerät gehört in die result.json.
    b) Gleichwertigkeit prüfen: derselbe kurze Lauf (Seed, ~300–1000 Schritte) auf CPU und GPU. Bitgleichheit ist
       nicht zu erwarten, aber Verlauf von Loss/Accuracy und die Top-Frequenzen müssen praktisch übereinstimmen.
       Ergebnis und Abweichungen im JOURNAL dokumentieren. Scheitert die Prüfung: GPU nicht verwenden, Blocker notieren.
    c) Geschwindigkeit messen (s/Schritt CPU vs. GPU) und prüfen, wie viele Läufe gleichzeitig auf die Karte passen
       (mehrere Prozesse auf einer GPU sind erlaubt; Regel „ein Job gleichzeitig“ gilt für GPU-Läufe nicht, solange
       Speicher und Durchsatz reichen und jeder Lauf über guarded_run.py startet).
    d) Nicht mischen: Innerhalb eines Versuchs laufen alle Arme und Seeds, die miteinander verglichen werden, auf
       demselben Gerät. Laufende oder bereits halb gelaufene CPU-Versuche auf der CPU zu Ende führen. Neue Versuche
       (v. a. die Verallgemeinerung aus Regel 15) bevorzugt auf der GPU planen.
    e) Nicht gefundene GPU, Treiber- oder ROCm-Fehler: höchstens drei Reparaturversuche, dann dokumentieren und auf
       der CPU weiterarbeiten. Nichts am Grafiktreiber oder am globalen Python ändern.
17. VIELE LÄUFE GLEICHZEITIG (Wunsch des Nutzers, 2026-09-26): Die Grenze „ein Trainingsjob gleichzeitig“ aus
    Auftrag §9 ist aufgehoben. Hardware: Ryzen 5 5600X (6 Kerne / 12 Threads), 32 GB RAM, RX 7900 XT (20 GB).
    - Werkzeug: `python lab/tools/parallel_queue.py JOBS.txt --workers N` (erlaubt per Berechtigungsregel).
      Eine Zeile pro Lauf, jeder Lauf geht automatisch über guarded_run.py; eine Ablehnung des Wächters stoppt
      weitere Starts, andere Fehler werden protokolliert und übersprungen. Logs + summary.json unter
      lab/runner/logs/pq_<zeit>/. Im Hintergrund starten und wie in Regel 14 beobachten.
    - Auslastung selbst bestimmen und messen, statt zu raten: Durchsatz (Läufe pro Stunde) bei 1, 2, 3 … parallelen
      Läufen vergleichen und die beste Einstellung im JOURNAL festhalten. Richtwert zum Start: CPU 3 Läufe à
      `--threads 4` oder 6 à `--threads 2`; GPU mehrere Läufe mit `--threads 1`, solange Speicher und Tempo reichen.
      CPU- und GPU-Läufe dürfen gleichzeitig laufen. Die Summe der CPU-Threads soll 12 nicht übersteigen.
    - Wenn die Maschine überlastet ist (RAM > ~28 GB, Läufe deutlich langsamer als allein), Parallelität senken.
    - Parallel laufende Läufe verändern die Zeitmessung (s/Schritt): Dauer-Kennzahlen nur vergleichen, wenn sie unter
      gleicher Last gemessen wurden. Die Ergebnisse selbst (Seeds, Frequenzen, gen-Schritt) sind davon unabhängig.
18. ASTRA-REVIEW UMSETZEN (Auftrag des Nutzers, 2026-09-26 abends): Der Nutzer hat eine Prüfung des ganzen Labors
    durch Codex gpt-6-astra beauftragt und will ALLE Vorschläge umgesetzt: [[reviews/ASTRA_2026-09-26]] (18 Punkte,
    mit Datei:Zeile-Belegen). Prüfe jeden Befund selbst, bevor du ihn umsetzt; ein Befund, der nicht stimmt, wird mit
    Begründung im JOURNAL verworfen. Bereits erledigt (vom Assistenten des Nutzers, nicht nochmal machen, aber im
    Fenster testen): Punkt 1 (guarded_run: STOP-Prüfung während des Laufs, Windows-Job-Object, UTC-Restzeit,
    `--check` mit Exit 3), Punkt 2 und 12 (tick.ps1: Wiederanlauf, Sperre mit Startzeit, Limit-Erkennung, Backoff;
    Task-Limit 4 h), Teile von 11 (parallel_queue: laufende summary.json, Duplikate) und 17 (Runner-Doku, Vorrang).
    NACHT 26./27.09.: Der Nutzer hat um 02:25 freigegeben: Läufe ab SOFORT erlaubt (nicht erst 03:00). Die Zeit davor ist für
    die Code-Arbeit unten da. Reihenfolge, verbindlich:
    a) VOR 03:00, nur Code und Dokumente (nichts ausführen, was trainiert oder testet):
       1. Punkt 3: Run-ID-Fingerprint in freq_ban.py über ALLE wirksamen Parameter + Datei-Hashes (Split, Test,
          Wechsel), Sperrdatei pro Run-ID, „completed“ erst nach Artefaktprüfung, NPY-Dateien atomar schreiben.
          Bestehende Ergebnisse bleiben gültig und lesbar (alte IDs nicht umbenennen).
       2. Punkt 10: GPU-001/compare.py (Schrittbeschriftung aus den echten Schrittwerten, Durchsatz = abgeschlossene
          Läufe/Schritte pro Gesamtwandzeit, J nur bei vollständigem Erfolg); `config.device` korrekt speichern.
       3. Punkt 16: ein gemeinsamer Ergebnislader (Manifest, Seed, Gerät, Hashes, Schrittbudget, endliche Werte;
          „fehlt“ / „defekt“ / „negativ“ unterscheiden). Mindestens die Auswertungen der heutigen Nacht-Queues darauf
          umstellen, den Rest schrittweise.
       4. Punkt 11: die Nacht-Queues auf `parallel_queue.py` umstellen (keine .sh-Schleifen, die Fehler verschlucken);
          Auswertungen nur, wenn ihre Läufe erfolgreich waren.
       5. Punkt 17: STATE.md auf höchstens ~80 Zeilen kürzen (aktive Queue, laufende Jobs, drei Prioritäten, Blocker,
          Wiederaufnahme). Historie gehört ins JOURNAL.
       6. Punkt 5: getrennte Zufallsströme (z. B. numpy SeedSequence über Experiment/Split/Arm/Init) für alle NEUEN
          Versuche; EXP-016 im FINDINGS als „stark, aber Abhängigkeit der Seeds eingeschränkt“ berichten.
    b) AB 03:00, zuerst Abnahme, dann Forschung:
       1. Wächter-Abnahme mit einem harmlosen Job (z. B. `python -c "import time; time.sleep(60)"`): läuft er,
          wird er bei angelegter lab/STOP-Datei beendet (Exit 3, danach STOP sofort wieder löschen und das im JOURNAL
          vermerken), wird der Kindprozess mit dem Wächter beendet? Scheitert etwas: Blocker notieren, Nutzer
          informieren über LIVE.md, alte Variante aus git holen.
       2. Tests von freq_ban (inkl. neuer Fingerprint-Tests), dann GPU-001-Abnahme (Punkt 9: AMD nennt natives
          Windows „No ML training support“ - GPU bleibt experimentell, bis Forward, Backward, AdamW, Wiederholung und
          ein langer Lauf mit der CPU übereinstimmen; sonst CPU).
       3. Dann die Nacht-Queues.
    c) FORSCHUNGSPROGRAMM (Punkte 4, 6, 7, 8, 18), ab sofort für alle neue Planung:
       - FINDINGS.md wird zum Programm mit genau drei Arbeitspaketen: A Split-Steuerung unabhängig replizieren inkl.
         funktionaler Wirkung; B Persistenz nach Datenwechsel (F→G und G→F, kontrollierte Überlappung, festes
         Nachtrainingsbudget); C eine mechanistische Vorhersage an unberührten Fällen. Höchstens zwei aktive
         Programme; andere Linien nur, wenn sie zwischen expliziten Konkurrenzmodellen entscheiden. Die
         Verallgemeinerung aus Regel 15c gehört zu A.
       - 2–3 primäre Kernaussagen festlegen, dafür EINE Bestätigungsfamilie mit Holm-Korrektur, Mindesteffekten und
         einer Stichprobengröße aus Pilotstreuung (Power ≥ 80 % anstreben; 10 Seeds sind keine Poweranalyse).
         Effektgrößen mit Konfidenzintervallen berichten. Exploration als solche kennzeichnen.
       - Einen Bestätigungsblock (frische Seeds/Splits) reservieren, der erst nach eingefrorenem Analysemanifest
         (Commit-ID) geöffnet wird. Jede Registrierung nennt „bereits gesehene Daten und davon beeinflusste
         Entscheidungen“. Bereits ausgewertete Seeds sind keine unabhängige Bestätigung.
       - Messgrößen: Repräsentationsenergie, funktionale Nutzung (Ablation am gespeicherten Modell auf gemeinsamer
         Testmenge) und Persistenz getrennt messen; kontinuierliche Zielenergie statt nur Top-5; „festgelegt“ =
         „nach B Schritten persistent“. Korrelationen nicht als direkte Wirkung formulieren.
       - Codex-Reviews nur an drei Punkten: vor Einfrieren eines Programms, bei Änderungen an gemeinsamem
         Trainer/Loader, vor einer Kernaussage in FINDINGS. Nach Korrekturen nur betroffene Punkte nachprüfen.
    d) DANACH (Technik, Punkte 13, 14, 15): Checkpoints (Modell, AdamW, RNG, Schritt, Konfig-Hash) für lange Läufe;
       feste Thread-Profile messen (CPU 1×4, 3×2, 6×1, 3×4; BLAS/Interop-Threads begrenzen); schnellerer
       Modellpfad (Maske als Buffer, MLP/Unembedding nur letzte Position) erst nach Gleichwertigkeitsprüfung;
       mehrere Seeds pro GPU-Prozess (vmap/functional_call, Loss über Modelle summieren) erst, wenn die GPU abgenommen
       ist.
    Fortschritt pro Punkt in lab/reviews/ASTRA_2026-09-26.md unten als Tabelle „Umsetzung“ führen (Punkt, Status,
    Commit, Anmerkung).
19. VERÖFFENTLICHUNG VORBEREITEN (Auftrag des Nutzers, 2026-09-27): Ziel ist ein solider Preprint (arXiv, ggf.
    Workshop) zu den bestätigten Kernaussagen in FINDINGS (K2, K2-Funktion, K4–K4e). Die Forschung läuft weiter, aber
    diese Arbeit hat ab jetzt gleiches Gewicht wie neue Versuche. Alles unter lab/paper/ (Obsidian-Frontmatter, in
    [[LAB]] verlinken). Fortschritt in lab/paper/STATUS.md (Punkt, Stand, nächster Schritt).
    a) ROBUSTHEIT (Nachtplanung, GPU): Die Kernaussagen gegen Hyperparameter prüfen, die Gutachter sofort fragen:
       Lernrate, Weight Decay, Trainingsanteil (train_frac), ggf. Init-Skala und Modellgröße. Vorab registriert,
       frische Seeds, eingefrorenes Manifest, Holm über die Familie, Effektgrößen mit KI. Ein Ergebnis „gilt nur in
       einem Bereich“ ist ein Befund und kommt so ins Paper.
    b) PILOTEN BESTÄTIGEN: nicht-modulare Addition (EXP-048), 4× Breite (EXP-049) und MLP (EXP-045) in einem kleinen
       Bestätigungsblock (frische Seeds) prüfen - oder im Paper ausdrücklich als Pilot berichten.
    c) REPRODUKTIONSPAKET: lab/paper/repro/ mit je einem Skript pro Abbildung/Tabelle, das die Kernergebnisse von Grund
       auf erzeugt (Training + Auswertung), plus README mit Befehlen, Laufzeiten, Umgebung (CPU/GPU, Versionen) und
       einem schnellen „Smoke“-Modus. Nur geprüfter, schlanker Code; keine Abhängigkeit von Nachtrag-Ketten. Einmal
       vollständig im Fenster laufen lassen und die Zahlen mit FINDINGS vergleichen.
    d) PAPER-ENTWURF: lab/paper/draft.md (Markdown, später LaTeX): Abstract, Einleitung, verwandte Arbeiten, Aufbau,
       Ergebnisse (je Kernaussage: Registrierung, n, Effektgröße, KI), Theorie erster Ordnung, Grenzen, Offenlegung
       der KI-Nutzung (Planung, Code und Text wesentlich von KI-Agenten; menschliche Verantwortung beim Nutzer).
       Abbildungen als Skripte unter lab/paper/figures/ (keine handgemachten Zahlen). Nur bestätigte Aussagen als
       Ergebnisse; Explorationen klar getrennt.
    e) LITERATURRECHERCHE: lab/paper/related_work.md - gründlich (arXiv, OpenReview, Google Scholar, Semantic Scholar;
       Grokking, Fourier-/Irrep-Schaltkreise, Frequency Principle, Datenauswahl/Curriculum, kritische Perioden,
       Init-Lotterie, AGF, Plastizität/Lernraten-Resets). Pro Arbeit: Link, was sie zeigt, Abgrenzung zu uns, ob sie
       unseren Neuheitsanspruch einschränkt. Suchbegriffe und Datum dokumentieren. Das ist die Grundlage für eine
       MENSCHLICHE Prüfung durch den Nutzer bzw. eine Fachperson; nichts als „neu“ behaupten, was nur „nicht
       gefunden“ ist.
    f) NICHT SELBST ENTSCHEIDEN (dem Nutzer in lab/paper/STATUS.md unter „Offen für den Nutzer“ vorlegen): Autorschaft
       und Rechte an der ursprünglichen GROKVERSE-Studie (RESULTS.md, training/), Einreichung/Veröffentlichung,
       Venue. Nichts hochladen oder einreichen, keine externen Konten.
20. WOCHENPLAN 29.09.–05.10. (Auftrag des Nutzers, 2026-09-28 abends; Begründung: lab/paper/outreach/DECISION_2026-09-28.md,
    nach Red-Team und Literaturprüfung). Die Reihenfolge ist verbindlich; Details entscheidest du (Regel 9 gilt innerhalb dieses Rahmens).
    a) R10 zu Ende rechnen (eingefroren, nicht abbrechen). EXP-096 und weitere Mechanismus-Detailversuche NICHT starten. Der Satz der
       Kernaussagen ist eingefroren; K5/R9/R10 kommen in einen Nebenabschnitt bzw. den Anhang.
    b) PRIORITÄT 1 „Menge gegen Reihenfolge“ (L0). LeDoux 2026 (arXiv 2603.25047) schreibt im Abstract, dieselbe Frequenz entstehe
       „regardless of initialization or training set composition“ (p = 9973, 0,3 % der Daten, Reihenfolge-Effekt). Alle unsere
       Kernaussagen sind Full-Batch → das ist der wichtigste Gutachter-Einwand. Pilot, Registrierung und Bestätigung (frische Seeds,
       eingefrorenes Manifest, Holm): K2 (Δ_pow) und R5 (Zeit) unter i.i.d.-Minibatch-AdamW bei zwei Batchgrößen + ein Arm SGD mit
       Momentum; Konflikt-Arm: eine feste, LeDoux-artige Reihenfolge, die eine ANDERE Frequenz bevorzugt als die Menge (LeDoux' Methode
       vorher im Volltext lesen); sekundär Wechsel bei 25/50 Schritten unter Minibatch. Jeder Ausgang ist ein Befund (Menge gewinnt /
       Reihenfolge gewinnt / hängt vom Regime ab, z. B. p oder Batchgröße) und kommt so ins Paper.
    c) Gutachter-Absicherung ohne neues Training: Nandas restricted/excluded loss an gespeicherten P2d/P2e/P2f-Modellen (nur die eigenen
       Zielfrequenzen, korrekte Same-Frequency-Masken — NICHT das äußere Produkt aus dem alten BWKI-Code); K2 in RFM mit dem öffentlichen
       Code https://github.com/nmallinar/rfm-grokking als Brücke zu Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316).
    d) Paper schärfen (Ziel ≈ Do 01.10.): Haupttext ≤ 8 Seiten mit 3 Kernaussagen (K2 + R4; R5; K4c/R6/R8) + L0; R1–R3, R7, P4, K5/R9/R10
       und Resets in den Anhang; Abstract < 1920 Zeichen. Einordnung ergänzen: Tomàs Bernal 2026, Fu et al. 2026 (arXiv 2604.20817, „the
       base selects the moduli“, Kalender dort als nächster Schritt genannt), Karkada et al. 2026 (arXiv 2602.15029), LeDoux-Zitat,
       Sweeney 2026. Neuheit nie „neu“, sondern „nach unserer Suche nicht gefunden“. Zenodo-Paket vorbereiten (Dateien + Metadaten),
       NICHT hochladen (braucht das Konto des Nutzers).
    e) Sprachmodell-Leiter (ab ≈ Fr 02.10., nach L0), eine gemeinsame Messgröße (Δ_pow auf Zahl-Tokens):
       Stufe 1: Text-Format (gemeinsames/gebundenes Vokabular, Loss nur auf der Antwort vs. auf allen Positionen, Minibatch). Die erste
       Stufe, auf der K2 bricht, ist selbst ein Befund.
       Stufe 2 (Pilot): kleines LM (≈ 10–30 M Parameter) von Grund auf, natürlicher Text mit wenigen Prozent konstruierter vs.
       abgeglichener Rechensätze. Die Kontrolle gleicht ab: Zahl verschiedener Fakten, Wiederholungen (feste Faktenmenge, gleich oft,
       KEINE gewichtete Neuziehung — sonst wird aus „welche Fakten“ „wie oft“), Tokenzahl je Rolle, Zählungen je Antwort (wie D in R5),
       Satzschablonen. Pilot-Kriterium: Genauigkeit auf zurückgehaltenen Fakten, nicht „Kreise vorhanden“.
       Bekannt und zu zitieren: Fu et al. 2026 (Daten/Tokenizer/Architektur bestimmen Zahlenmerkmale; Einzel-Token-Addition von Grund auf
       erzeugt dort oft keine Perioden), Zhou/Fu/Sharan/Jia 2024, Engels et al. 2024, Kantamneni & Tegmark 2025, Karkada et al. 2026.
       Kalender höchstens zur Veranschaulichung.
    d2) ENTSCHEIDUNG DES NUTZERS 30.09. (über seinen Assistenten): LM1 + LM1-F (bestätigt, unabhängig nachgerechnet) werden im
       Paper SICHTBAR: ein Satz im Abstract (Abstract bleibt < 1920 Zeichen) und ein kurzer Absatz im Haupttext (z. B. Ende §6 oder
       §7, „über das Spielzeugmodell hinaus“), klar begrenzt (kleines LM ≈ 14 M, ≈ 79 % Rechen-Tokens, eine Aufgabe, gebundene
       Einbettung); Details bleiben in Anhang J. LM3 (≈ 9 %) nur, wenn es vor der Einreichung bestätigt und nachgerechnet ist.
       Keine neue Kernaussage; unabhängige Textprüfung wie immer.
    e2) NÄCHSTE STUFE (Nutzer 30.09.: „ja“): ein kleines VORTRAINIERTES Sprachmodell nachtrainieren, z. B. Pythia-160M (offene
       Gewichte und Trainingsdaten) oder GPT-2 small (124 M), über Hugging Face (Regel f). Frage: Steuert die Auswahl der
       Rechenfakten beim Nachtrainieren, welche Frequenzen die Zahl-Einbettungen tragen, und werden sie genutzt (Ablation wie
       LM1-F)? Vorher prüfen: Zahlen 0–112 als einzelne Tokens (sonst Aufgabe/Messgröße anpassen), Ausgangsspektrum des
       vortrainierten Modells als Vergleich, Eingabe- und Ausgabe-Einbettung getrennt (ungebunden). Ablauf wie immer: Pilot
       (2 Seeds, Lesarten vorab) → bei Erfolg Bestätigungsblock (10 Seeds, eingefroren, nachgerechnet). gpu_gb vorher messen
       (160 M mit AdamW grob 4–6 GB). Nach LM3/R12 einplanen; Paper: Ausblick/Anhang, erst nach Bestätigung mehr.
    f) Downloads und Pakete (Freigabe des Nutzers 28.09.): pip install NUR in .venv-gpu (bekannte Pakete wie transformers, tokenizers,
       datasets, huggingface_hub, safetensors, sentencepiece; Versionen festhalten), Datensätze/Tokenizer von Hugging Face, Code per
       git clone von GitHub. Zusammen ≤ 30 GB; mindestens 60 GB frei lassen (28.09.: 125 GB frei). Globales Python nicht ändern, keine
       Konten anlegen, nichts hochladen. Jede Installation und jeden Download im JOURNAL festhalten (Name, Version/Quelle, Größe, Zweck).
    g) Checkpoints (Modell, Optimierer, RNG, Schritt, Konfig-Hash; Astra Punkt 15), bevor LM-Läufe starten, die länger als eine Sitzung
       dauern können.
    h) TÄGLICH für den Nutzer: lab/paper/erklaerung/ERKLAERUNG_<datum>.md, höchstens eine Seite, einfaches Deutsch: was heute
       herauskam, was es bedeutet und was nicht, und 3 Fragen, die eine Jury oder Forschende stellen würden, mit kurzen Antworten.
       In [[LAB]] verlinken. Der Nutzer muss die Ergebnisse selbst erklären können (größtes Risiko laut Red-Team).
    i) 24/7-Betrieb: bei wiederholten GPU-/ROCm-Abstürzen Parallelität senken und dokumentieren; GPU nicht leer laufen lassen, solange
       Punkte a–e offen sind.
21. GPU-WARTESCHLANGE UNABHÄNGIG VON DEN SITZUNGEN (Nutzer, 2026-09-29; Anlass: Sitzungsabsturz 08:24 durch einen Ausfall der
    Auto-Mode-Sicherheitsprüfung, die laufenden Jobs starben mit, die GPU stand still). Jobs, die länger als ≈ 10 min laufen oder eine
    Sitzung überdauern können, NICHT mehr in der Sitzung starten, sondern als Datei ablegen:
    lab/queue/inbox/<prio>_<name>.jobs — eine Zeile je Lauf wie bei parallel_queue.py (Vorwärtsschrägstriche), optional als erste
    Zeile `#! workers=N job_minutes=M min_minutes=K stall_minutes=S crash_minutes=C gpu_gb=G` (Standard: workers 10, job_minutes 300,
    min_minutes 5, stall_minutes 0 = aus, crash_minutes 10, gpu_gb 3.5). Dateien laufen in Namensreihenfolge (Zahl vorne = Priorität).
    - Speicherschutz (Nutzer, 2026-09-29; lab/PROBLEME.md P-009: 10 LM-Läufe à 3,4 GB überbuchten die 20-GB-Karte, alles lief 8× langsamer
      und der RAM lief voll): gpu_gb = Grafikspeicher EINES Laufs in GB, IMMER angeben (lm_stage2 ≈ 3.5, repro/train.py ≈ 1). Ein Job
      startet nur, wenn max(Messung, 2.5 GB Reserve + gpu_gb aller laufenden Jobs) + seine gpu_gb ≤ 16 GB bleibt, nichts in den RAM
      ausgelagert ist und genug RAM frei ist; höchstens ein Start alle 6 s. Blockiert der Speicher den vordersten Job, wartet alles
      dahinter (strenge Priorität); Grund in status.json → admission. Nach einem Dienst-Neustart starten unterbrochene Läufe zuerst.
      Geänderte Kopfzeilen liest der Dienst neu ein (Jobzeilen nicht); eine gpu_gb, die nie passt, lässt die Datei ablehnen.
    - Hänger-Erkennung (Nutzer, 2026-09-29): Endet das Log eines Laufs in einem Python-Traceback und wächst crash_minutes lang nicht
      mehr, beendet der Dienst den Lauf (Zustand failed:hung). stall_minutes > 0 beendet Läufe, deren Log so lange gar nicht wächst
      (failed:stalled) – nur für Skripte setzen, die regelmäßig Fortschritt ausgeben (Jobs laufen mit PYTHONUNBUFFERED=1).
      Skripte, die abgefangene Fehler als Traceback ausgeben und danach lange still rechnen: crash_minutes=0 setzen.
      Läufe mit vortrainierten HF-Modellen (Pythia, GPT-2) können nach dem Speichern beim Prozessende in ROCm
      hängen und Grafikspeicher festhalten (Nutzer, 2026-09-30; lab/PROBLEME.md P-021): solche Jobdateien IMMER
      mit stall_minutes=15 einreichen (das Log muss im Training öfter als alle 15 min wachsen).
      Beendete Läufe werden nicht wiederholt; Vermerk im Job-Log und in guarded_runs.jsonl (killed_by: gpu_daemon). status.json
      zeigt je laufendem Job quiet_min (Minuten ohne neue Ausgabe) und unter features, was die laufende Instanz kann.
    - Der Dienst lab/tools/gpu_daemon.py (geplante Aufgabe GROKVERSE-GPU-Daemon, alle 10 min, nie doppelt) führt jeden Lauf über
      guarded_run.py aus: STOP, Zeitfenster und Job-Objekt gelten; die Sitzungsdeadline NICHT, stattdessen job_minutes als harte Grenze.
    - Status: lab/queue/status.json (Heartbeat alle paar Sekunden, laufende Jobs, Fortschritt je Datei); Logs lab/queue/logs/<datei>/;
      fertige Dateien mit <name>.summary.json in lab/queue/done/. Stirbt der Dienst, laufen offene Jobs beim Neustart erneut
      (freq_ban.py überspringt Fertiges per Fingerabdruck; andere Trainer brauchen Checkpoints oder Überspring-Logik).
    - Sofort starten statt bis zu 10 min zu warten: `powershell -NoProfile -Command "Start-ScheduledTask -TaskName GROKVERSE-GPU-Daemon"`
      (per Berechtigungsregel erlaubt). Den Dienst nicht beenden oder umkonfigurieren; Probleme im JOURNAL und in LIVE melden.
    - Ressourcen: Dienst + eigene Sitzungsläufe zusammen höchstens 10 GPU-Prozesse und 12 CPU-Threads. In der Sitzung nur noch
      Kurzes (Tests, Auswertungen, Smokes). Vor dem Ablegen prüfen, dass dieselben Läufe nicht schon im Dienst laufen (status.json).

22. BETRIEBSPROBLEME MELDEN STATT UMGEHEN (Nutzer, 2026-09-30; lab/runner/RUNBOOK.md): Betriebsprobleme (hängende Prozesse,
    blockierter Dienst, volle Platte, …) analysiert die Sitzung und schreibt eine Lösung auf; der stündliche Gesundheitscheck
    des Assistenten wendet sie nach dem Runbook ohne Rückfrage an. Was die Sitzung selbst darf, erledigt sie selbst.
    - Lehnt die Sicherheitsprüfung eine Aktion ab: NICHT umgehen (auch nicht nachträglich über stall_minutes in der Kopfzeile
      einer laufenden Jobdatei oder über andere Wege), sondern in lab/LIVE.md unter „Hinweis für den Assistenten (HH:MM)“
      eintragen: Symptom, Ursache mit Beleg, gewünschte Maßnahme, betroffene Prozesse (PID, Startzeit, Befehlszeile) und
      warum nichts verloren geht; den Befehl bildet der Assistent selbst.
      Zusätzlich per SendMessage an die Assistenten-Sitzung des Nutzers (ListAgents: die laufende Sitzung, die nicht
      „GROKVERSE-lab-*“ heißt, derzeit grokverse-wissenschaft-88), falls erreichbar. Den Ausgang im JOURNAL festhalten.
    - lab/PROBLEME.md, lab/runner/RUNBOOK.md und lab/tools/hang_check.py pflegt nur der Assistent; die Sitzung ändert sie nie und meldet Probleme
      im JOURNAL und in LIVE. Hängende Dienst-Jobs erkennt der Assistent mit lab/tools/hang_check.py (Runbook A3).

23. PAUSE NACH DER LEDOUX-LINIE (Entscheidung des Nutzers, 2026-10-01 ≈ 17:15; Anlass: Rückmeldung der Mentorin Dr. Jana
    Stucke: „Die Experimente dürfen nicht schneller laufen als dein Verständnis.“ Diese Regel geht Regel 20 vor.)
    - Nur noch die LeDoux-Linie zu Ende rechnen und auswerten: EXP-143 (einschließlich der zwei Läufe mit 600 000 Schritten
      und der Datei 52a8_exp143_ledoux) und EXP-144 (breiteres Netz). Danach PAUSE.
    - Während der Pause: KEINE neuen Experimente, keine neuen Jobdateien, keine weiteren Trainingsläufe (GPU oder CPU);
      geparkte Dateien (lab/queue/parked/, z. B. die EXP-139-Reste) nicht wieder einreihen. Regel 20 i („GPU nicht leer
      laufen lassen“) ist ausgesetzt.
    - Erlaubt: Auswertung, unabhängige Nachrechnung und Paper-Sätze der LeDoux-Linie (nur nach den vorab festgelegten
      Deutungen), STATE/JOURNAL/LIVE, die Tageserklärung und Lernmaterial für den Nutzer – als Leitfragen und Leseliste
      (die wichtigsten Arbeiten mit je 3 Fragen; Herleitungs-Schritte als Fragen), NICHT als fertiger Text, den er
      übernehmen könnte. Keine weiteren neuen Ergebnisse ins Paper.
    - Ist die LeDoux-Linie ausgewertet, beendet sich jede Sitzung nach kurzer Lagekontrolle (STOP, Dienst, LIVE) mit dem
      Satz „Pause aktiv (Regel 23)“ in LIVE, bis der Nutzer die Pause aufhebt.

---------------------------------------------------------------------------------------

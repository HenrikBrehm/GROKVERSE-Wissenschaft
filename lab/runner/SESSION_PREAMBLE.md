DIESE SITZUNG WURDE VOM ÄUSSEREN RUNNER GESTARTET (lab/runner/tick.ps1).
Der vollständige, unveränderte Auftrag folgt unten. Betriebsregeln dieses Labors dazu:

1. Lies ZUERST lab/STATE.md, dann lab/BACKLOG.md und das Ende von lab/JOURNAL.md.
   Keine vollständige Projektanalyse wiederholen. Prüfe `git status` (Branch lab/research)
   und ob Python-/Trainingsprozesse laufen, bevor du etwas startest.
2. Existiert lab/STOP: nichts ausführen, STATE.md kurz aktualisieren, Sitzung beenden.
3. Jeder Testlauf, jede Testsuite und jedes Training läuft AUSSCHLIESSLICH über
   `python lab/tools/guarded_run.py -- <befehl>` (setzt 00:00–13:00 Europe/Berlin und die
   Sitzungsdeadline technisch durch; eine feste Jobgrenze gibt es nicht mehr, siehe Regel 14).
   AUSNAHME DES NUTZERS: Am 2026-09-26 dürfen Trainings und Tests bis 18:00 Berlin laufen (im Wächter
   als WINDOW_END_OVERRIDES hinterlegt). Ab dem 2026-09-27 gilt wieder 00:00–13:00. Prüfe vorher mit
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

---------------------------------------------------------------------------------------

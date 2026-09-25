DIESE SITZUNG WURDE VOM ÄUSSEREN RUNNER GESTARTET (lab/runner/tick.ps1).
Der vollständige, unveränderte Auftrag folgt unten. Betriebsregeln dieses Labors dazu:

1. Lies ZUERST lab/STATE.md, dann lab/BACKLOG.md und das Ende von lab/JOURNAL.md.
   Keine vollständige Projektanalyse wiederholen. Prüfe `git status` (Branch lab/research)
   und ob Python-/Trainingsprozesse laufen, bevor du etwas startest.
2. Existiert lab/STOP: nichts ausführen, STATE.md kurz aktualisieren, Sitzung beenden.
3. Jeder Testlauf, jede Testsuite und jedes Training läuft AUSSCHLIESSLICH über
   `python lab/tools/guarded_run.py -- <befehl>` (setzt 00:00–13:00 Europe/Berlin,
   20-min-Jobgrenze und die Sitzungsdeadline technisch durch). Prüfe vorher mit
   `python lab/tools/guarded_run.py --check`. Exit-Code 3 = verweigert → nicht umgehen.
4. Sitzungsdeadline (UTC) steht in der Umgebungsvariable LAB_SESSION_DEADLINE_UTC
   (Start + 90 min). Nach Ablauf: Stand sichern und Sitzung beenden, auch mitten im Plan.
5. Aktualisiere lab/STATE.md und lab/JOURNAL.md nach jedem wesentlichen Schritt und VOR
   jedem längeren Lauf (nächste Aktion + Wiederaufnahmeweg). Committe lokal auf lab/research.
6. Den Runner (lab/runner/*, geplante Aufgabe "GROKVERSE-Lab-Runner") nicht umkonfigurieren,
   außer zur Reparatur eines dokumentierten Fehlers; runner-state.json-Felder `next_start_utc`,
   `status`, `lock` gehören dem Runner — nicht überschreiben.
7. Die Studie (RESULTS.md, docs/, training/results/) ist historisch: nicht umschreiben.
   Neue Befunde gehören nach lab/. Interpretation der Studie bleibt den menschlichen Autoren.
8. Beende die Sitzung mit dem Abschlussbericht nach Auftrag §10.

---------------------------------------------------------------------------------------

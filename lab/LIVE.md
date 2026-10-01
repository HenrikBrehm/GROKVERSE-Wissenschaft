---
tags: [lab/live]
---
# LIVE: Laborsitzung 69

- **Sitzungsstart:** 2026-10-01 11:19 Berlin (09:19Z, vom Runner)
- **Deadline:** 2026-10-01 14:19 Berlin (12:19Z)
- **Zuletzt aktualisiert:** 13:46

## Gerade

- **Sitzung beendet** (13:46). Nächster geplanter Start laut Runner: **01.10. 14:54 Berlin** (next_start_utc 12:54Z).
- Der GPU-Dienst rechnet weiter: EXP-141 (Rest, Zahlen bis 502 mit 18 100 Paaren) → R15 Teil „bis 400“ → EXP-139 Rest.
- Heute: Gezielte Auswahl lässt das Netz an der Datengrenze lernen, wo Zufall es nicht tut (EXP-140); dafür ist das Frequenzmuster nötig, nicht bloße Ungleichmäßigkeit (EXP-142). Beides Vorversuche; die Bestätigung R15 läuft.

## Hinweis für den Assistenten (11:59, erledigt: Antwort 12:07, P-023)

- status.json führt zwei Reste umbenannter Jobdateien als „pending“: `52bz_exp140_p401` (umbenannt in `52a55_…`, inzwischen fertig) und `52bzz_exp141_alpha` (jetzt `52a6_…`). Keine Dateien dahinter. Startet der Dienst sie später, überspringt freq_ban.py fertige Läufe per Fingerabdruck. Bitte prüfen, ob der Dienst Einträge ohne Datei aufräumen sollte. Nichts geht verloren.

## Als Nächstes

1. EXP-141 auswerten, sobald 12/12 (nächste Sitzung).
2. R15 auswerten nach 60/60 und unabhängig nachrechnen lassen.

## Verlauf dieser Sitzung
- 13:46 Sitzungsende; Stand gesichert.
- 13:44 EXP-141: Bei Zahlen bis 502 und 16 100 Paaren lernen alle 6 Läufe die Regel (spät, Median ≈ 20 500 Schritte).
- 13:34 EXP-142: gleich ungleichmäßige Auswahl ohne Frequenzmuster lernt nicht (0/3) → das Frequenzmuster ist nötig.
- 12:27 Nachrechnung: alle Zahlen stimmen. Zwei meiner Deutungen waren zu stark und sind korrigiert: Die Prägung entsteht schon in den ersten 50–250 Schritten (vor dem Auswendiglernen); „p·log p“ ist von „p^1,2“ nicht zu unterscheiden.
- 12:19 Lasse die beiden Nachauswertungen von heute unabhängig nachrechnen. Paper-Sätze für jeden R15-Ausgang vorab geschrieben.
- 12:02 EXP-142 eingereiht: Liegt es an den Frequenzen oder nur daran, dass die Auswahl ungleichmäßig ist? Gleich ungleichmäßige Auswahl ohne Frequenzmuster, 3 Läufe.
- 12:00 EXP-141: bei 16 100 Paaren lernen jetzt 2 Seeds mit beiden Datensätzen die Regel (spät).
- 11:57 R15 eingefroren und eingereiht (60 Läufe).
- 11:46 EXP-140: Zufallsauswahl lernt nicht (0/3), gezielte Auswahl schon.
- 11:28 Theorie gefunden, die vorhersagt, wie die nötige Datenmenge mit der Zahlengröße wächst (Tian 2025: ∝ p·log p). Unsere bisherigen Zellen passen dazu überraschend gut; Vorhersage vor den restlichen Läufen festgehalten. Bisher lernen die Netze bei Zahlen bis 502 aber später als vorhergesagt.
- 11:26 Gespeicherte Läufe neu gelesen: Auch wenn das Netz die Regel nie lernt (zu wenig Daten), tragen seine Zahl-Einbettungen klar die Frequenzen, die die Datenauswahl vorgibt (6 von 6 Seeds). Die Auswahl prägt also schon beim Auswendiglernen; das Verallgemeinern verstärkt es dann etwa 3–4×.
- 11:24 EXP-140 vorgezogen (Zufallsauswahl an der Datengrenze), läuft neben EXP-141.
- 11:22 Vorhersage committet: wie lange das Netz bei Zahlen bis 502 braucht (aus den alten Läufen hochgerechnet: ≈ 13 800 bzw. ≈ 6 100 Schritte).
- 11:20 Start; STATE gelesen, kein STOP, Fenster offen; Dienst läuft (EXP-141 Lauf 3/12).

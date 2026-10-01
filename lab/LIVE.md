---
tags: [lab/live]
---
# LIVE: Laborsitzung 66

- **Sitzungsstart:** 2026-10-01 03:09 Berlin (01:09Z, vom Runner)
- **Deadline:** 2026-10-01 06:09 Berlin (04:09Z)
- **Zuletzt aktualisiert:** 05:38

## Gerade

- **Sitzung beendet** (05:38). Nächster geplanter Start: **01.10. 06:44 Berlin** (runner-state next_start_utc 04:44Z).
- Heute herausgekommen: L0b (die feste Reihenfolge verschiebt die Frequenzen etwas, die Steuerung bleibt; „die Auswahl gewinnt“ ist nicht bestätigt), EXP-135 (Sprachmodell legt sich erst beim Lernen fest), EXP-136 (größere Zahlen: Steuerung bei 30 % Daten ja; mit wenig Daten lernt das Netz nicht).
- Dienst läuft weiter: EXP-128 (12/16), EXP-129 (1/4).

## Als Nächstes

1. EXP-128/129 auswerten; EXP-136-Satz in Anhang A (siehe [[STATE]]).
2. GPU-Folgearbeit planen (EXP-136 mit mehr Daten oder Bestätigungsblock).

## Verlauf dieser Sitzung
- 05:38 Sitzungsende: alles gesichert und committet; EXP-136-Halbsatz nach Prüfung präzisiert.
- 05:33 EXP-136 ausgewertet (Gesamtlesart „beschreibend“); README, LAB, FINDINGS, Tageserklärung, Grenze (ii) im Paper.
- 04:50 Manuskript neu gebaut; zwei überholte Pilot-Sätze im Anhang mit Hinweis auf L0b versehen.
- 04:40 L0b-Text nach unabhängiger Prüfung präzisiert (u. a.: die Reihenfolge wirkt auf Zufallsdaten nur *absolut* stärker; Abstract angepasst, 1916 Zeichen).
- 04:37 L0b ausgewertet und unabhängig nachgerechnet: H1, H3, H4 bestätigt, H2 nicht; Paper angepasst. EXP-135 ausgewertet: Im Sprachmodell legt sich die Wahl erst beim Lernen der Fakten fest, nicht in den ersten 1000 Schritten (Vorversuch).
- 03:13 EXP-134 nachgeprüft: Das 5-fache Wachstum der Zahl-Einbettungen beim reinen Textlernen ist zu 96 % eine für alle Zahlen gleiche Verschiebung, keine Zahlstruktur.
- 03:10 Start: kein STOP, Fenster offen, Dienst läuft (L0b 312/420, EXP-135 2/6 laufen).

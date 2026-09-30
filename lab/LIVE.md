---
tags: [lab/live]
---
# LIVE: Laborsitzung 55

- **Sitzungsstart:** 2026-09-30 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-30 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 03:10 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange LÃ¤ufe Ã¼ber den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet (03:10).** Nächster geplanter Start laut Runner: 30.09. 04:24 Berlin (02:24Z). Der GPU-Dienst rechnet weiter.

## Als Nächstes

EXP-113 und EXP-116 auswerten (letzte Läufe laufen), dann EXP-119 Nachtrag 2. EXP-124 bleibt vorbereitet (Regel 20a).

## Dienst (03:10)

EXP-123 fertig (60/60). EXP-113: 7/8, letzter Lauf bei 5000/16 000. EXP-116: 2/4, zwei Läufe bei ≈ 3500/16 000. EXP-119 Nachtrag 2 wartet auf Grafikspeicher.

## Verlauf dieser Sitzung

- 03:10 Prüfung von EXP-124 fand einen Designfehler (eine allgemeine Verlangsamung wäre falsch gelesen worden); vor jedem Lauf behoben.
- 03:02 EXP-124 vorbereitet (Bann-Test: Kommt die Vertauschungsstufe später, wenn die Zielfrequenzen verboten sind?); Code an zwei Smokes geprüft, bewusst nicht gestartet.
- 02:58 Deutungssätze für EXP-113 vorab; Zenodo-Liste ergänzt.
- 02:54 Nachträglich: Der Zeitpunkt der Vertauschungsstufe hängt bei konstruierten Splits so eng an der frühen Zielenergie wie das Grokking selbst; das trennt die Ursachen nicht. Trennender Versuch vorgemerkt.
- 02:52 Paper-Anhangsabsatz zu EXP-123 geprüft: Zahlen richtig; Bildunterschrift korrigiert (0.92 statt 0.85), Mediane mit Zensierung benannt.
- 02:45 **EXP-123:** Der Transformer lernt vor dem Grokking zuerst die Vertauschungsregel (18/18 Einheiten, vorher festgelegt). Meine Vermutung „die Datenauswahl beschleunigt vor allem den zweiten Schritt“ stimmt nicht: Sie beschleunigt beide, den ersten sogar stärker (×11 gegen ×4.6). Abb. 15 gezeichnet, Anhangsabsatz geschrieben.
- 02:25 Auswerteskript für EXP-119 Nachtrag 2 vorab geschrieben und getestet.
- 01:53 Paper §4: Satz zu Wang et al. 2024 nach Prüfung vorsichtiger formuliert.
- 01:42 Blinde Code-Prüfung von EXP-123: kein Fehler; vier Unschärfen der Vorab-Festlegung vor dem Ergebnis schriftlich geklärt; Zusatzauswertung vorab geschrieben.
- 01:23 **EXP-119 Nachtrag 2** eingereiht: Hält das Plateau des Zufallssplits im Sprachmodell bis 16 000 Schritte, oder kommt der Sprung doch noch?
- 01:15 Paper: R5-Abschnitt zitiert jetzt Wang et al. 2024; Manuskript neu gebaut (Zitatprüfung sauber). Abbildungsskript für EXP-123 vorbereitet.
- 01:13 Nachträglich: Die Stärke der Spektralspitze sagt die Grokking-Zeit *innerhalb* des Zufallsarms nur schwach voraus (ρ = −0.26).
- 01:11 **Korrektur:** Der â€žflache Zufallssplitâ€œ hat doch Spektralspitzen (bei zufÃ¤lligen Frequenzen), fast so stark wie die konstruierten Splits. Ungleiche Zahl-HÃ¤ufigkeiten erklÃ¤ren das Plateau nicht. Neue Lesart: Irgendeine Spitze scheint nÃ¶tig, nicht die Wahl der Ziele (nachtrÃ¤glich, nicht direkt getestet). Paper-Satz korrigiert. AuÃŸerdem geschÃ¤tzte Uhrzeiten durch gemessene ersetzt.
- 01:07 **EXP-121:** vorab â€žunklarâ€œ; der flache Zufallssplit verlÃ¤sst das KommutativitÃ¤ts-Plateau (ohne Tauschpaar 68 % / 98 %). Im Paper-Anhang eingetragen und geprÃ¼ft.
- 00:57 **EXP-123 vorab festgelegt und gestartet** (KommutativitÃ¤t zuerst? VerkÃ¼rzt die Datenauswahl den zweiten Schritt?).
- 00:55 **Literatur:** He et al. 2026 kennen das Tauschpaar-Muster, aber mit eingebauter Vertauschung.
- 00:54 **Paper-Anhang J geprÃ¼ft:** 5 Formulierungen korrigiert.
- 00:51 Stand gelesen, Dienst lÃ¤uft.

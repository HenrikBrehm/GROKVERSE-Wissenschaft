---
id: C2-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/B]
verwandt: ["[[FINDINGS]]", "[[confirm/R2_REGISTRATION_DRAFT|R2]]", "[[confirm/C1_REGISTRATION|C1]]", "[[JOURNAL]]"]
---
# C2: Behalten die alten Ziele nach einem Wechsel bei t = 50 ihre Rangfolge vom Wechselzeitpunkt? (Programm B, feine Persistenz)

Zurück zu [[FINDINGS]] (Programm B) · Datenquelle: [[confirm/R2_REGISTRATION_DRAFT|R2]] (frische Seeds 2510–2539, noch **kein** Lauf).
**Fassung 2 (gilt)**, Sitzung 28, 2026-09-27, vor jedem R2-Lauf; die Codex-Punkte zu C1 (`C1_codex_review_s28.txt`) sind sinngemäß übernommen. Gilt mit dem Commit dieser Datei und dem Code-Tor `C2_manifest.json`.
Fassung 1 (Commit 6e634da) ist ersetzt.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- N29 (Seeds 2250–2269, beide Richtungen, t = 25/50; gesehen) → Exploration `lab/confirm/N29_posthoc_within.py`, Ergebnis `N29_posthoc_within.json`. Rangkorrelation über die fünf **alten** Ziele
  zwischen W_E-Energie beim Wechsel und am Ende (t + 4000): t = 50: 0.58 (p < 5·10⁻⁵, 40 Läufe), t = 25: 0.17 (p 0.03). Spektrum des ersten Splits bei t = 50: 0.37; Spektrum des
  zweiten Splits an den alten Zielen: 0.02 (n. s.). Je Seed (Mittel beider Richtungen) bei t = 50: Mittel 0.580, SD 0.283, 19/20 positiv. Bereinigt um k und das Spektrum des zweiten Splits:
  Koeffizient 0.589; ρ(Energie beim Wechsel, k) im Mittel −0.12.
- **Davon beeinflusst:** Wahl des Prädiktors (Energie beim Wechsel), t = 50 als primärer Zeitpunkt, Mindesteffekt 0.10, Power-Rechnung.
- Ein erster Lauf des Explorationsskripts las die B→A-Läufe mit vertauschten alt/neu-Rollen; vor jeder Deutung korrigiert (Zahlen oben sind korrigiert).

## Aussage C2 (eng)

Im Mittel über die R2-Läufe mit Wechsel bei t = 50 (lr 2e-3 und wd 0.3 zusammen, beide Richtungen) behalten die fünf alten Zielfrequenzen im Endmodell (t + 4000) die Rangfolge ihrer
W_E-Energie vom Wechselzeitpunkt, auch nach Bereinigung um k und um die Stütze durch den zweiten Split. Keine Aussage je Zelle (beschreibend berichtet). Deutung, falls bestätigt: Die Festlegung
erhält neben der Menge der alten Frequenzen (K4/K4c) auch ihre innere Ordnung; beschreibende Persistenz, kein Mechanismus.

## Daten, Maß, Test (fest)

- **Daten:** alle R2-Läufe mit Wechsel bei t = 50 (Zellen lr2 und wd03, je 30 Seeds × beide Richtungen = 120 Läufe), W_E-Snapshots bei t und t + 4000 über Bindung und gemeinsamen Lader.
- **Maß je Lauf:** Spearman über die fünf alten Ziele (Ziele des ersten Splits) zwischen der W_E-Gruppenenergie (`group_power`, add 113) bei Schritt t und bei t + 4000. Exakte Bindungen → Lauf technisch.
- **Einheit = Seed:** Mittel über seine vier t = 50-Läufe (zwei Zellen × zwei Richtungen; dieselbe Init). Ein Seed zählt nur, wenn **alle vier** gültig sind (Fassung 2b); Bindungen in Energie, k oder Spektrum des zweiten Splits → Lauf technisch.
- **Bestätigt**, wenn alle drei gelten: (i) einseitiger Vorzeichen-Permutationstest Mittel > 0 (200 000 Ziehungen, p = (Überschreitungen + 1)/(B + 1); Annahme: unter H0 symmetrisch um 0) < 0.05;
  (ii) Untergrenze des 95-%-Bootstrap-KI über Seeds (10 000) ≥ 0.10; (iii) Untergrenze des 95-%-Bootstrap-KI (Seeds) des bereinigten Koeffizienten > 0: kleinste Quadrate über alle gültigen t = 50-Läufe,
  zentrierte Ränge je Lauf, Endenergie ~ Energie beim Wechsel + k + Spektrum des zweiten Splits. Eigene Familie (Programm B, eine Hypothese), nicht in der R2-Holm-Familie.
- **Nicht auswertbar**, wenn weniger als 20 Seeds alle vier t = 50-Läufe gültig haben. Fehlende Seeds werden gezählt; zusätzlich das Mittel, als hätten sie ρ = −1 (Schranke, kein Urteil).
- **Power:** N29-Streuung (SD 0.283 je Seed bei zwei Läufen) bei halbiertem Mittel (0.29): n = 30 → Power ≈ 0.92 (Bootstrap-Simulation); mit vier Läufen je Seed eher höher.
- **Beschreibend (kein Test):** je Zelle und Wechselzeit (lr2: t = 12, 25, 50; wd03: t = 25, 50): Mittel der Korrelationen alt/Wechsel, alt/erster Split, alt/zweiter Split, neu/Wechsel, neu/zweiter Split.
- **Was dagegen spräche:** Mittel ≤ 0, KI-Untergrenze < 0.10 oder der bereinigte Koeffizient nicht > 0.

## Umsetzung und Code-Tor

Kein neues Training (Snapshots bei t und t + 4000 stehen in den R2-Jobzeilen: `--spectra-at t,t+250,t+2000,t+4000`). `lab/confirm/C2_analyze.py` (Fassung 2) mit `rank_tools.py`, `P1_posthoc_within.py`;
Hashes in `lab/confirm/C2_manifest.json`, von der Auswertung geprüft, und der letzte Commit von Code-Tor und Registrierung muss ein Vorfahr des R2-Manifest-Commits sein; vorhandene `C2_summary.json` wird nie überschrieben. Selbsttest (nur im Fenster): Handwerte, synthetische Seeds (bestätigt /
nicht bestätigt, wenn die Ordnung k folgt / nicht auswertbar), N29-Wert 0.580. Wird R2 geändert, muss C2 neu registriert werden.

## Fassung 2b (Codex-Nachprüfung, Sitzung 28, vor jedem R2-Lauf)

Übernommen: **Blocker** „ein Seed zählt schon mit einem gültigen Lauf, C2 könnte aus einer Zelle/Richtung bestätigen“ → Seed nur mit allen vier t = 50-Läufen; Bindungen in den Kontrollen → Lauf technisch
(sonst Abbruch in der Bereinigung); Code-Tor an die Git-Geschichte gebunden. Nicht übernommen wie bei C1: Ersatz der Vorzeichenpermutation (Begründung dort).

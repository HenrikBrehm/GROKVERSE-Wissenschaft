---
id: EXP-051
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[BACKLOG]]"]
---
# EXP-051: Werden die gesteuerten Frequenzen funktional genutzt? (P2, Pilot)

**Status:** vorbereitet, **nicht ausgeführt, ungetestet** (Sitzung 13, 2026-09-26, außerhalb des Fensters). Festgelegt, bevor ein einziges
EXP-047-Modell existiert. **Kein eigenes Training:** Auswertung der gespeicherten Modelle aus [[experiments/EXP-047-marginal-control/README|EXP-047]]
(dort seit Sitzung 13 `--save-model`). Zurück zu [[LAB]] · [[FINDINGS]].

## Bezug zu [[FINDINGS]]

Paket **A**, Kernaussage **P2** („Entfernen der Zielfrequenzen schadet mehr als das Entfernen gleicher Energie anderswo“). Bisher war K2 nur eine
Aussage über *Repräsentationsenergie* in W_E (Astra-Review Punkt 8: Energie, Nutzung und Persistenz getrennt messen).

## Aufbau

- **Modelle:** EXP-047, Transformer der Studie, add 113, 2000 Schritte, GPU, Seeds 150–159, Arten eng (gesteuert) und shuf (Kontrolle mit gleichen
  Token-Häufigkeiten), Arme F und G. Gespeichert am Ende (Schritt 2000).
- **Gemeinsame Testmenge je Seed und Art:** alle Paare, die weder im F- noch im G-Split liegen (für beide Modelle dieselbe).
- **Eingriffe am unveränderten Modell (nur Auswertung, kein Nachtraining), nur in der Eingabeeinbettung W_E[0..112]:**
  *own* = eigene 5 Zielfrequenzen entfernen (cos/sin-Spalten der orthonormalen DFT-Basis auf null); *other* = die 5 Ziele des anderen Arms
  entfernen; *energy* = gleich viel W_E-Energie wie *own* aus allen Nicht-Ziel-Frequenzen (**ersetzt durch Nachtrag a**).
- **Messgröße:** Abfall der Test-Genauigkeit gegenüber dem ungestörten Modell (drop).

| | |
|---|---|
| **Fragestellung** | Nutzt das Netz die über den Split gesteuerten Frequenzen funktional, stärker als dieselbe Energiemenge in anderen Frequenzen? |
| **H51** | eng: D̄ > 0, D_i = Mittel über die beiden Modelle des Seeds von [drop_own − drop_energy] |
| **Test** | einseitiger Vorzeichen-Permutationstest über die gültigen Seeds (eng) |
| **Gültig** | beide eng-Modelle geladen (gemeinsamer Lader: Seed, Gerät, Budget, Split-Hash, `model_final.pt`), Basis-Test-Genauigkeit ≥ 0.9 (ohne Generalisierung ist ein Funktionstest sinnlos), Energieabgleich vollständig; < 8 gültige Seeds: *nicht auswertbar* |
| **Urteil** | *funktional genutzt*: D̄ > 0, p < 0.05 · *richtungsgleich, n. s.* · *nicht mehr genutzt als gleiche Energie anderswo*: D̄ ≤ 0 |
| **Sekundär (berichtet)** | D_cross = drop_own − drop_other (eigene gegen fremde Ziele); dieselben Größen für shuf (ungesteuerte Referenz: Erwartung D ≈ 0); Energieanteile |
| **Was dagegen spräche** | D̄ ≤ 0: Die Ziele sind in W_E vorhanden, tragen die Rechnung aber nicht mehr als beliebige Energie (Struktur ohne Nutzung) |
| **Grenzen** | Nur die Eingabeeinbettung wird verändert, nicht W_U oder der MLP-Pfad (die Studienmethode `causal_ablation.transformer_ablations` wäre die Erweiterung). Ein Modell pro Arm und Seed, Messpunkt Schritt 2000. Energie gleich heißt nicht „Information gleich“: die Kontrolle verteilt die Entfernung über viele schwache Frequenzen |
| **Bereits gesehene Daten** | Keine EXP-047-Modelle. Gesehen: EXP-016 (Steuerung vorhanden, gen meist < 1000 Schritte → bei 2000 generalisiert), EXP-016-Spektren (Ziele dominieren W_E). Deshalb die Energiekontrolle statt einer Zufallsfrequenz-Kontrolle |
| **Art** | Pilot/Exploration für Paket A; Bestätigung nur im reservierten Block (Seeds 1000–1099) |
| **Budget** | nur Auswertung (CPU, ≈ Minuten); läuft im Nachtprogramm direkt nach der EXP-047-Auswertung |

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-051-functional-ablation/analyze.py --selftest
python lab/tools/guarded_run.py --min-minutes 5 -- python lab/experiments/EXP-051-functional-ablation/analyze.py
```

## Nachtrag a (Sitzung 13, 21:09 Berlin, **vor jedem Lauf**): Energieabgleich war unmöglich, neu festgelegt

Unabhängige Prüfung (Claude-Subagent, numpy auf gespeicherten EXP-016-Spektren; selbst nachgerechnet): In gesteuerten Modellen tragen die 5 Ziele **76–89 %** der W_E-Energie (20/20 EXP-016-Läufe bei Schritt 2000). „So viel Energie anderswo entfernen wie die Ziele tragen“ war deshalb unmöglich; das Urteil wäre vor jedem Datum *nicht auswertbar* gewesen (**Blocker**). Außerdem hätte die Kontrolle die Oberwellen fold(2t) getroffen, die das Netz wegen der Ziele nutzt (**Hoch**). **Neu (Urteilsregeln sonst gleich):** Beide Eingriffe entfernen dieselbe, immer erreichbare Energie X = 0.5 · min(E_own, E_ctrl), durch gleichmäßiges Herunterskalieren der jeweiligen Frequenzen; Kontrollmenge = alle k außer den eigenen Zielen, den Zielen des anderen Arms und fold(2t) der eigenen Ziele. D_i = Mittel über beide Modelle von [drop_own − drop_ctrl]. Das vollständige Entfernen eigener/fremder Ziele bleibt sekundär (D_cross). Gültigkeit: Basis-Test-Genauigkeit ≥ 0.9. EXP-051 ist ein eigener Schritt im Nachtprogramm (ein Fehler hier markiert EXP-047 nicht mehr als gescheitert) und läuft nur, wenn EXP-047 im selben Programmlauf ok war.


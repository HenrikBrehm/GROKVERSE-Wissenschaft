---
id: EXP-055
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-051-functional-ablation/README|EXP-051]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[JOURNAL]]"]
---
# EXP-055: Werden die gesteuerten Frequenzen je Energieeinheit stärker genutzt? (Dosis-Wirkung am Test-Loss, P2-Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (Paket A, P2 funktional). Nachfolger von [[experiments/EXP-051-functional-ablation/README|EXP-051]] mit neuer ID
(Regel 15b: kein dritter Nachtrag). Festgelegt 2026-09-27 03:10 Berlin (Sitzung 20), **bevor dieser Code gelaufen ist**. Nur Auswertung
gespeicherter Modelle, kein Training. **Pilot**, keine Bestätigung.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** Das Ergebnis von EXP-051 an denselben 20 Modellen (EXP-047 eng, Seeds 150–159, F/G):
In 40/40 energiegleichen Eingriffen war der Genauigkeitsverlust 0, denn X war nur 3–9 % der Zielenergie. Die volle Ablation der eigenen Ziele kostet 0.95–0.99, die der
fremden 0. Daraus folgen das kontinuierliche Maß und die Dosisstufen. Die Loss-Werte dieser Eingriffe habe ich **nicht** gesehen.

| | |
|---|---|
| **Frage** | Kostet das Entfernen einer Energiemenge E aus den eigenen Zielfrequenzen mehr Test-Loss als das Entfernen derselben Menge aus den Kontrollfrequenzen? |
| **Modelle** | 20 gespeicherte EXP-047-Modelle (eng, add 113, Transformer, 2000 Schritte, GPU-trainiert), Auswertung auf der CPU; gemeinsame Testmenge je Seed (Paare in keinem der beiden Splits) wie EXP-051 |
| **Eingriff** | wie EXP-051: gleichmäßiges Herunterskalieren der Menge S (eigene Ziele bzw. Kontrolle = alle k außer eigenen Zielen, fremden Zielen und fold(2t) der eigenen Ziele) in W_E[:113], bis genau E entfernt ist |
| **Dosen** | E_j = f_j · E_ctrl mit f ∈ {0.1, 0.25, 0.5, 0.75, **1.0**} (immer erreichbar, da E_own > E_ctrl in allen 20 Modellen; bei f = 1 ist die Kontrolle ganz entfernt) |
| **Maß** | ΔL = mittlerer Kreuzentropie-Loss (Logits [:113]) auf der gemeinsamen Testmenge nach dem Eingriff minus vorher |
| **Primär** | D_i = Mittel über die zwei Modelle des Seeds von [ΔL_own − ΔL_ctrl] bei **f = 1.0** |
| **Test / Urteil** | einseitiger Vorzeichen-Permutationstest (exakt, 2^n) über die gültigen Seeds · *je Energie stärker genutzt*: D̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: D̄ > 0 sonst · *nicht stärker genutzt*: D̄ ≤ 0 · < 8 gültige Seeds: *nicht auswertbar* |
| **Gültig** | beide Modelle laden (gemeinsamer Lader, wie EXP-051), Basis-Test-Genauigkeit ≥ 0.9, alle ΔL endlich |
| **Sekundär (beschreibend)** | ganze Dosis-Kurve ΔL_own(f), ΔL_ctrl(f); Genauigkeitsverluste; mittlerer Logit-Abstand (richtige Klasse minus beste falsche) vorher/nachher |
| **Erwartung** | offen. Für H: Die Ziele tragen den Algorithmus, schon 7 % ihrer Energie weg sollte den Loss merklich heben. Dagegen: Die Kontrolle ist zwar schwach, könnte aber zusammen einen Rest tragen (z. B. Oberwellen anderer Ordnung) |
| **Was dagegen spräche** | D̄ ≤ 0: Je Energieeinheit sind die Ziele nicht wichtiger. Dann hieße die Notwendigkeit (D_cross) nur „viel Energie“, nicht „besondere Nutzung“ |
| **Grenzen** | Pilot an Modellen, deren Genauigkeitsdaten gesehen wurden; nur Z₁₁₃, 2000 Schritte; Skalieren ist ein Eingriff in W_E allein (nachgelagerte Gewichte unverändert) |

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-055-ablation-dose/analyze.py --selftest
python lab/tools/guarded_run.py -- python lab/experiments/EXP-055-ablation-dose/analyze.py
```

## Ergebnis (Sitzung 20, 2026-09-27, 03:10 Berlin, CPU-Auswertung, 23 s)

Code: Commit nach 67cc1a4 („EXP-055 analysis code“), Befehl wie oben. Zahlen `summary.json`.

- 10/10 Seeds gültig (Basis-Genauigkeit 1.0, Basis-Loss 0.001–0.007, Logit-Abstand ≈ 6.5–8).
- **Primär (f = 1.0): D̄ = 5.3·10⁻⁵, 4/10 positiv, p = 0.42 → *richtungsgleich, n. s.*** Das ist das Urteil.
- *Beschreibend (nicht vorab als Test festgelegt; die Dosen sind nicht unabhängig):* D̄ je Dosis f = 0.1 / 0.25 / 0.5 / 0.75 / 1.0: 1.2 / 3.0 / 5.9 / 8.1 ·10⁻⁴ / 0.5·10⁻⁴,
  positiv in **10 / 10 / 10 / 10 / 4 von 10** Seeds. Bei Teildosen kostet dieselbe Energie aus den Zielen also durchweg mehr Loss als aus der Kontrolle. Beim vollständigen
  Entfernen der Kontrolle (f = 1) wächst ΔL_ctrl überproportional (konvex) und holt ΔL_own ein. Deutung, ungeprüft: Die Kontrollfrequenzen tragen einen kleinen, aber nötigen Rest,
  der erst beim völligen Löschen fehlt. Oder das Löschen einer ganzen Menge ist ein anderer Eingriff als Skalieren.
- Größenordnung: Alle ΔL sind klein (≤ 4·10⁻³) gegen Basis-Loss 10⁻³. Entfernt werden bei f = 1 nur 5–18 % der Zielenergie. Die Modelle sind robust.
- **Entscheidung:** Kein Nachtrag. Für P2 folgt: primäre Dosis **vor** den Daten auf eine Teildosis legen (z. B. f = 0.5), Maß ΔL, an **frischen** Modellen
  (Bestätigungsblock oder neue Pilot-Seeds). Diese 20 Modelle sind jetzt zweimal gesehen und taugen nicht mehr zur Bestätigung.


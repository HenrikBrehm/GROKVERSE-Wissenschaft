---
id: P2-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P1_REGISTRATION_DRAFT|P1-Entwurf]]", "[[experiments/EXP-055-ablation-dose/README|EXP-055]]", "[[JOURNAL]]"]
---
# P2-Bestätigung (funktionale Nutzung): Registrierungsentwurf (Sitzung 21, 2026-09-27 04:30 Berlin, gemessen). **NICHT eingefroren**

Zurück zu [[FINDINGS]] · Pilot [[experiments/EXP-055-ablation-dose/README|EXP-055]] · [[confirm/P1_REGISTRATION_DRAFT|P1]].

- **Aussage P2:** In Modellen mit konstruiertem Split kostet das Entfernen einer Energiemenge aus den **eigenen Zielfrequenzen** in W_E mehr Test-Loss
  als das Entfernen derselben Menge aus den Kontrollfrequenzen (Nutzung je Energieeinheit, nicht nur Anwesenheit).
- **Modelle:** die gespeicherten `model_final.pt` der P1-Hauptläufe **add 113** (Seeds 1000–1049, Arme F/G, GPU, 2000 Schritte). Die P1-Jobs speichern sie seit Commit 5b03b7c.
  Diese Modelle sind bei der Festlegung trainiert oder noch nicht trainiert, aber **kein Ablationswert** an ihnen ist gesehen. Das muss beim Einfrieren stimmen und steht dann hier mit Datum.
- **Eingriff und Maß (wie EXP-055, unverändert übernommen):** gleichmäßiges Herunterskalieren der Menge S in W_E[:113], bis genau E entfernt ist. S = eigene Ziele bzw. Kontrolle
  (alle k außer eigenen Zielen, fremden Zielen und fold(2t) der eigenen Ziele). ΔL = mittlerer Kreuzentropie-Loss (Logits [:113]) auf der gemeinsamen Testmenge
  (Paare in keinem der beiden Splits des Seeds) nach minus vor dem Eingriff.
- **Primär:** Dosis **f = 0.5** (E = 0.5 · E_ctrl), festgelegt vor den Daten, begründet durch EXP-055 (dort f = 1 Bodeneffekt bzw. konvexe Kontrolle; Teildosen 10/10, post hoc).
  D_i = Mittel über die zwei Modelle des Seeds von [ΔL_own − ΔL_ctrl].
- **Test:** einseitiger Vorzeichen-Permutationstest auf D̄ > 0 (Monte Carlo, 200 000 Ziehungen), Holm in der Familie P1–P3.
  **„bestätigt“ = alle geplanten Seeds gültig, Holm-p < 0.05 und untere Grenze des 95-%-Bootstrap-KI von D̄ > 0.** Kein absoluter Mindesteffekt in Loss-Einheiten
  (die Skala hängt am Modell; ein Verhältnis ΔL_own/ΔL_ctrl ist nicht definiert, weil ΔL_ctrl im Pilot teils negativ ist, gemessen 04:27).
  Effektgröße berichtet: D̄ mit KI, Anteil positiver Seeds, d_z.
- **Gültig:** beide Modelle laden (gemeinsamer Lader + P1-Bindung an den eingefrorenen Code), Basis-Test-Genauigkeit ≥ 0.9, alle ΔL endlich. Fehlt ein Seed: *nicht auswertbar*.
- **Stichprobe:** Pilot EXP-055 bei f = 0.5 (gemessen 04:26): D̄ = 5.9·10⁻⁴, SD 3.6·10⁻⁴, d_z = 1.63, 10/10 positiv. Bootstrap-Power bei α/3: n = 10 → 0.80 bei halbem Effekt, n = 20 → 0.997.
  Mit 50 Seeds aus P1 ist die Power auch bei deutlich kleinerem Effekt hoch. Alle 50 werden ausgewertet (keine Teilauswahl).
- **Sekundär (beschreibend):** Dosis-Kurve f ∈ {0.1, 0.25, 0.5, 0.75, 1.0}; Genauigkeits- und Logit-Abstands-Verluste.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-051 und EXP-055 an den 20 EXP-047-Modellen (Seeds 150–159): Wahl des Maßes (ΔL statt Genauigkeit),
  der Dosis (f = 0.5) und der Stichprobe. Diese 20 Modelle zählen nicht als Bestätigung.
- **Grenzen:** nur add 113 und ein Modell; Skalieren nur in W_E (nachgelagerte Gewichte unverändert); dieselben Modelle wie P1 (P1 und P2 sind an denselben Läufen
  nicht unabhängig, messen aber verschiedene Größen: Repräsentationsenergie gegen Loss nach Eingriff).
- **Noch zu tun vor dem Einfrieren:** Auswertecode `lab/tools/confirm_p2.py` (übernimmt EXP-055/051-Helfer unverändert, liest die P1-Läufe über Lader + Bindung),
  Selbsttest, Codex-Prüfung (Regel 18c), dann Manifest `P2_manifest.json` mit `code_sha256` und `commit` einfrieren, **bevor** ein Ablationswert berechnet wird.
## Änderung vor dem Einfrieren (Sitzung 21, 04:35 Berlin): primäres Maß skalenfrei

Beim Nachrechnen des Piloten (04:34) fiel auf, dass das rohe D die Modelle nach ihrem Basis-Loss gewichtet: Seed 157 G hat Basis-Loss 2·10⁻⁷ und trägt praktisch
nichts bei, Modelle mit höherem Basis-Loss dominieren. **Neu primär:** R_s = Mittel über die zwei Arme von log(L_nach,own / L_nach,ctrl) bei f = 0.5 (immer definiert, da
Loss > 0; 0 = kein Unterschied). **„bestätigt“ = alle 50 gültig, Holm-p < 0.05 und untere Grenze des 95-%-Bootstrap-KI von R̄ ≥ log(1.05)** (Mindesteffekt: 5 % mehr Loss).
Das rohe D (Maß von EXP-055) wird sekundär berichtet. Pilot EXP-055 auf R (post hoc, bereits gesehen): R̄ = 0.150 (≈ 16 % mehr Loss), SD 0.065, d_z = 2.3, 10/10 positiv.
Geometrie (gemessen 04:34): Bei f = 0.5 ist die quadrierte Störungsnorm entlang der Ziele nur ≈ 5 % der Kontrollstörung (Ziele werden um ≈ 2 % skaliert, die Kontrolle um 29 %).
R > 0 folgt also nicht aus der Eingriffsgeometrie, sondern verlangt eine viel höhere Empfindlichkeit entlang der Ziele. Code: `confirm_p2.py` (Commit nach 935155b).

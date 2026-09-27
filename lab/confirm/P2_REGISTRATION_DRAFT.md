---
id: P2-registrierung
status: eingefroren
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
## Codex-Prüfung (Sitzung 21, 04:39) und endgültige Regeln (gelten allein, wo abweichend)

Codex (gegen Commit 935155b): 3 Blocker, 1 hoch, 3 mittel/niedrig. Selbst geprüft, übernommen:
- **Test (Blocker, stimmt):** Eigene Ziele und Kontrolle sind nicht vertauschbar, R ist unter H0 nicht symmetrisch. Der Vorzeichentest ist hier nicht begründet (anders als bei P1,
  wo Vertauschen von F/G das Vorzeichen von Δ umkehrt). **Primär: einseitiger Ein-Stichproben-t-Test auf R̄ > 0** (n = 50). Der Vorzeichentest wird nur sekundär berichtet.
- **Multiplizität (Blocker, stimmt als Unklarheit):** Entschieden wird mit **Holm im ungünstigsten Fall** (P1, P3 als p = 1, also 3p). Das ist konservativ, denn das gemeinsame Holm mit den echten p-Werten kann nur kleiner sein.
  So gilt es auch für P1 (`p_holm_worstcase`).
- **Einfrieren (Blocker, stimmt für den Text):** Es gibt **kein eigenes P2-Manifest**. `confirm_p2.py` und die übernommenen EXP-051/055-Helfer stehen in den Code-Hashes des P1-Manifests.
  **P1 und P2 werden gemeinsam eingefroren, bevor irgendein Bestätigungslauf startet.** Damit hat vor der Festlegung niemand Spektren, Energien oder Ablationen dieser Modelle gesehen.
- **Genau die Seeds 1000–1049** (hoch): im Code erzwungen. „bestätigt“ braucht alle 50 gültig.
- **Gültigkeit** betrifft die primäre Dosis. Die übrigen Dosen sind beschreibend und werden nur berichtet, wo sie machbar sind (E ≤ E_own).
- **Machbarkeit** mit `>` statt `>=` (niedrig).
- **Aussage enger gefasst (mittel):** P2 behauptet die Mehrnutzung **bei dieser endlichen Dosis (f = 0.5) und dieser Kontrollmenge**, keine allgemeine Ableitung
  „je Energieeinheit“. Für die weitere Fassung bräuchte es Dosen nahe 0 und einen Steigungsvergleich (nicht Teil von P2).
- Wiederverwendung der P1-Modelle: Codex hält sie für zulässig (Holm erlaubt abhängige p-Werte, keine Auswahl nach P1-Ergebnis).

Power (t-Test, α/3, n = 50, Pilot d_z = 2.3): praktisch 1; auch bei einem Viertel des Pilot-Effekts noch hoch.
## EINGEFROREN (Sitzung 21, 2026-09-27 04:46 Berlin, gemessen)

P2 ist mit dem Manifest `lab/confirm/P1_manifest.json` eingefroren: **Manifest-Commit 733e829** (enthält `code_sha256` über 60 Dateien, darunter
`confirm_p1.py` und `confirm_p2.py`), Commit-Feld nachgetragen in 0cd5ee5. Es gelten die Regeln dieses Dokuments einschließlich aller Abschnitte
„Codex-Prüfung“ und „Änderung vor dem Einfrieren“, jeweils mit ihren Übernahmen. Letzte Codex-Nachprüfung (04:45): zwei Punkte als Restrisiko abgelehnt
(Ändern und Zurücknehmen innerhalb von 2 s; untergeschobenes .pyc im Cache): Beides setzt absichtliche Manipulation voraus, gegen die ohnehin keine Datei geschützt ist.
Übernommen: Die Bindung speichert das Urteil des Wrappers, der Trainer bleibt nie verwaist zurück, P2 lädt genau die gebundenen Modellbytes, E = E_own ist erlaubt (d2ac48f).
Splits (600) und Jobliste (420) in 6babde7. Vor dem Einfrieren wurde **kein** Lauf mit Seeds 1000–1399 gemacht. Danach liefen zwei Jobs der eingefrorenen
Liste als Smoke (add 113 und D₅₉, Seed 1000 F). Beide sind gebunden und zählen als reguläre Läufe des Blocks.

## ERGEBNIS (Sitzung 21, Auswertung 05:40–05:44 Berlin; `P2_summary.json`): ***nicht auswertbar***

Nach der eingefrorenen Regel („bestätigt“ braucht alle 50 Seeds gültig) ist P2 **nicht auswertbar**: 3 von 50 Seeds (1001, 1008, 1026) verletzen die vorab festgelegte Gültigkeitsbedingung
„Basis-Test-Genauigkeit ≥ 0.9“. In allen drei ist der **G-Arm** bei Schritt 2000 noch nicht fertig generalisiert (0.82 / 0.70 / 0.73; der F-Arm jeweils 1.0). Dieses Urteil gilt.
Nachgerechnet oder ersetzt wird nichts.
*Nur beschreibend, keine Bestätigung:* Über die 47 gültigen Seeds ist R̄ = 0.12 (SD 0.20, 43/47 > 0, Minimum −0.74). Das ist deutlich kleiner und streut stärker als im Piloten
(R̄ 0.15, SD 0.065 an den 20 EXP-047-Modellen).
**Eigener Designfehler:** Die Kombination „alle 50 gültig“ + „Genauigkeit ≥ 0.9“ + nur 2000 Schritte war zu streng. Im Piloten hatten alle Modelle generalisiert, diese Streuung
der Generalisierungszeit hatte ich nicht eingeplant. Ein Nachfolger braucht Modelle nach sicherem Grokking (mehr Schritte) oder eine vorab festgelegte Behandlung nicht generalisierter Modelle,
eine Stichprobe aus der **jetzt beobachteten** Streuung (d_z ≈ 0.6, bereits gesehen) und frische Seeds. Diese 50 Modelle sind für P2 verbraucht.

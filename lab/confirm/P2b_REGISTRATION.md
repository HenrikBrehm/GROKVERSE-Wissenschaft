---
id: P2b-registrierung
status: abgebrochen
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P2_REGISTRATION_DRAFT|P2]]", "[[experiments/EXP-055-ablation-dose/README|EXP-055]]", "[[confirm/N28_REGISTRATION|N28]]", "[[JOURNAL]]"]
---
# P2b-Bestätigung (funktionale Nutzung, Nachfolger von P2): Registrierung (Sitzung 22). **ABGEBROCHEN (Designfehler), ersetzt durch [[confirm/P2c_REGISTRATION|P2c]]**

Zurück zu [[FINDINGS]] (Programm A) · Vorgänger [[confirm/P2_REGISTRATION_DRAFT|P2]] (nicht auswertbar) · Pilot [[experiments/EXP-055-ablation-dose/README|EXP-055]] · Familie mit [[confirm/N28_REGISTRATION|N28]].

- **Aussage P2b:** In Modellen mit konstruiertem Split (add 113) kostet das Entfernen der Energiemenge E = 0.5 · E_ctrl aus den **eigenen Zielfrequenzen** in W_E mehr Test-Loss
  als das Entfernen derselben Menge aus der Kontrollmenge. Enge Fassung wie P2 (endliche Dosis f = 0.5, diese Kontrollmenge; keine Ableitung „je Energieeinheit“).
- **Was sich gegenüber P2 ändert (und warum):** P2 scheiterte an der Regel „alle 50 gültig“, weil 3 G-Modelle bei Schritt 2000 nicht generalisiert waren.
  (1) **4000 statt 2000 Schritte.** (2) Ungültige Seeds (Basis-Genauigkeit < 0.9 auf der gemeinsamen Testmenge, undurchführbare Dosis, nicht endliche Verluste) werden **ausgeschlossen und berichtet**.
  Das Urteil verlangt ≥ 90 % gültige Seeds, sonst *nicht auswertbar*. Der Ausschluss hängt nur an der Basis-Genauigkeit und der Machbarkeit, nicht an R.
  (3) **Frische Seeds 2000–2099** und eigene Splits (P1-Konstruktion, `confirm_splits.build` mit Versuchs-ID 2, also kein gemeinsamer Zufallsstrom mit P1).
  (4) **n = 100 aus der beobachteten Streuung:** Bootstrap-Simulation aus den 47 P2-Werten (gemessen in Sitzung 22): Power 0.88 bei n = 80 und 0.92 bei n = 100 am beobachteten R̄ = 0.122.
  Ist der wahre Effekt 0.02 kleiner, sinkt sie auf etwa 0.7. Der Pilot-Mittelwert ist womöglich durch die Auswahl verzerrt.
- **Modelle:** je Seed zwei Läufe (Arme F, G), `freq_ban.py --steps 4000 --save-model`, GPU, `--threads 1`; Datei [[confirm/P2b_manifest.json]] nach dem Einfrieren.
- **Eingriff und Maß (unverändert aus P2/EXP-055, Code über `confirm_p2` importiert):** gleichmäßiges Herunterskalieren von S in W_E[:113], bis genau E entfernt ist.
  S = eigene Ziele bzw. Kontrolle (alle k außer eigenen Zielen, fremden Zielen und fold(2t) der eigenen). Loss = mittlere Kreuzentropie (Logits [:113]) auf den Paaren in keinem der beiden Splits.
- **Primär:** R_s = Mittel über die beiden Arme von log(L_nach,own / L_nach,ctrl). Einseitiger Ein-Stichproben-t-Test auf R̄ > 0.
  **Familie Sitzung 22** = {N28-H1, N28-H2, P2b}, Holm im ungünstigsten Fall (die anderen als p = 1, also 3p).
  **„bestätigt“ = ≥ 90 gültige Seeds, Holm-p < 0.05 und untere Grenze des 95-%-Bootstrap-KI von R̄ ≥ log(1.05)** (Mindesteffekt: 5 % mehr Loss). Sonst *nicht bestätigt*.
- **Sekundär (beschreibend):** rohes D (P2-Maß), Eignungsrate (nicht generalisiert / andere Gründe), d_z, Anteil R > 0.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-051/055 (20 Modelle, Seeds 150–159: Maß, Dosis); P2 (50 Modelle, Seeds 1000–1049, R̄ 0.12, SD 0.20, 3 nicht generalisiert):
  Schrittzahl, Ausschlussregel und n. Keines dieser Modelle zählt als Bestätigung. Vor der Registrierung wurde kein Lauf mit Seeds 2000–2099 gemacht.
- **Grenzen:** nur add 113, eine Architektur, Eingriff nur in W_E; 4000 Schritte sind ein anderer Trainingsstand als P1 (2000).
- **Technik:** `lab/tools/confirm_p2b.py` auf `lab/tools/bound_block.py` (Bindungslogik aus confirm_p3, parametrisiert). Selbsttest ok (Sitzung 22), ungetestet am echten Lauf.
  Vor dem Einfrieren: Codex-Prüfung (Regel 18c), dann Manifest mit `code_sha256` und `commit`.

```
python lab/tools/confirm_p2b.py --splits lab/confirm/P2b_manifest.json
python lab/tools/confirm_p2b.py --jobs lab/confirm/P2b_manifest.json > lab/confirm/P2b_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/P2b_jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/tools/confirm_p2b.py --analyze lab/confirm/P2b_manifest.json
```

## Codex-Prüfung (Sitzung 22, gegen b0676fb) und endgültige Regeln (gelten allein, wo abweichend)

Codex: 2 Blocker, 1 hoch, 2 mittel, Rest in Ordnung (Run-IDs und Bindungs-Refaktor bestätigt). Selbst geprüft, alle übernommen:
- **Herkunft der Splits (Blocker, stimmt):** Die Auswertung baut jeden Split und jede Zielmenge mit `confirm_splits.build` neu und verlangt exakte Gleichheit (Array, Ziele, fremde Ziele, Seed). Bei einer Abweichung ist die ganze Bestätigung ungültig (`split_mismatch`).
- **Technische Ausfälle (Blocker, stimmt):** *Jeder* technische Ausfall (Lauf fehlt, nicht gebunden, nicht ladbar, nicht endlicher Loss/R/D) macht P2b **nicht auswertbar**. Nur die wissenschaftliche Eignung (Basis-Genauigkeit ≥ 0.9 in beiden Armen) darf Seeds ausschließen. Die Bindung nimmt nur Läufe mit `status == "completed"` an (bound_block, gilt auch für N28). Wiederholung: Ein technisch gescheiterter Lauf darf **einmal** mit derselben Jobzeile neu gestartet werden, bevor irgendein R berechnet ist. Das wird berichtet.
- **Auswahl über die Machbarkeit (hoch, stimmt):** Die Dosis ist jetzt **E = min(0.5 · E_ctrl, E_own)**, also immer machbar. Die Zahl gekappter Arme wird berichtet. Die Aussage gilt **bedingt auf „beide Modelle generalisiert (≥ 0.9)“**. Als Sensitivitätsanalyse wird R über alle technisch gültigen Seeds (auch nicht generalisierte) mit KI berichtet.
- **Endlichkeit (mittel, stimmt):** Basis- und Eingriffsverluste, R und D werden geprüft; R = log L_own − log L_ctrl.
- **Power (mittel, stimmt teilweise):** eingefroren als `lab/confirm/p2b_power.py` (RNG 2022, 400 Simulationen, beide Kriterien, n_eff 90/100, gemessen 07:25): 0.92/0.94 am beobachteten Mittel, 0.80 bei 1.25-facher SD, **0.73 bei einem um 0.02 kleineren Mittel**, 0.41 bei −0.04. Die Pilotwerte sind ausgewählte Überlebende bei Schritt 2000. Diese Empfindlichkeit nehme ich bewusst hin; n bleibt 100 (GPU-Zeit).

## EINGEFROREN (Sitzung 22, 2026-09-27, 07:31–07:34 Berlin, gemessen)

Manifest `lab/confirm/P2b_manifest.json`, **Manifest-Commit fa154bd** (Commit-Feld in 888c2d9), Code-Hashes über `confirm_p2b.py`, `bound_block.py`, Trainer und Helfer.
Splits und Jobliste in 37448f6; die Herkunftsprüfung (`split_mismatch`) ist an den geschriebenen Dateien für alle Seeds bestanden. Vor dem Einfrieren wurde kein Lauf mit diesen Seeds gemacht.
Start des Blocks 07:34 (GPU, `parallel_queue.py lab/confirm/P2b_jobs.txt --workers 5`, parallel zum anderen Block der Familie).

## ABGEBROCHEN (Sitzung 22, 08:04–08:06 Berlin, gemessen): Designfehler, nicht auswertbar

Beim Prüfen zweier technischer Ausfälle (Speicher: `bad allocation` bzw. WinError 1455 um 07:53, bei 12 GPU-Prozessen plus CPU-Programm) zeigte ein Log: `EXP-016_baseline_seed2000_…_G completed: steps 2725, gen 725`.
**Ursache:** `freq_ban.py` beendet einen Lauf standardmäßig 2000 Schritte nach der Generalisierung (`--stop-after-gen 2000`). Die P2b-Jobzeilen haben das nicht überschrieben. Die meisten Läufe enden
deshalb vor Schritt 4000. Der eingefrorene Lader verlangt aber `steps_completed ≥ 4000` und hätte sie als defekt abgelehnt; nach der eigenen Regel wäre P2b *nicht auswertbar*.
Das ist **mein Designfehler** (auch in beiden Codex-Prüfungen nicht bemerkt). Der Block wurde nach 113 von 200 Läufen abgebrochen (Prozessbaum beendet, 08:05).
**Kein Ablationswert, kein R und keine Auswertung** eines P2b-Modells wurde berechnet. Gesehen habe ich nur Trainer-Logzeilen (Generalisierungsschritt, Top-5) einzelner Läufe.
Die Seeds 2000–2099 gelten als verbraucht. Nachfolger: [[confirm/P2c_REGISTRATION|P2c]] (Seeds 2100–2199, `--stop-after-gen 4000`, Selbsttest prüft volle Schrittzahl).

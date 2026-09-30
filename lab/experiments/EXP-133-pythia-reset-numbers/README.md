---
id: EXP-133
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, lab/lm, neu/kandidat]
verwandt: ["[[experiments/EXP-127-pretrained-lm/README|EXP-127]]", "[[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]]", "[[experiments/EXP-132-pythia-mul/README|EXP-132]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-133: Kommt die Datensteuerung zurück, wenn im vortrainierten Pythia-160M nur die Zahl-Einbettungen neu gestartet werden? (Pilot)

Zurück zu [[LAB]]. **Exploration (2 Seeds × F/G), keine Bestätigung.** Kandidat [[NOVEL_DIRECTIONS]] N61.

**Bezug zu FINDINGS:** K2 (Split-Steuerung) über das Spielzeugmodell hinaus, Geltungsgrenze beim Nachtrainieren (Exploration S61, [[experiments/EXP-127-pretrained-lm/README|EXP-127]] „bricht“). Regel 20 e2 (vortrainiertes LM).

## Vorab (Sitzung 62, 30.09., 18:45 Berlin, vor jedem EXP-133-Lauf)

**Bereits gesehen:** EXP-127 (gleiche Splits, gleiche Einstellungen, vortrainierte Zahlzeilen: Δ_pow der Rest-Änderung +0.13 / −0.17, Änderung in allen Armen auf {2, 3, 11, 23, 56}); der erste Gradient der Pythia-Architektur mit *vollständig* zufälliger Init trägt die Ziele (S59, Top 5 = eigene Ziele, Δ_pow 0.84 / 1.04). Keine EXP-133-Daten außer dem Smoke (2 Schritte).

- **Frage:** Liegt das „bricht“ von EXP-127 an den vortrainierten *Zahlzeilen* (Wiederverwendung vorhandener Frequenzen, Lesart a) oder am vortrainierten *Rumpf* (Attention/MLP zwingen jeder Zahldarstellung ihre Merkmale auf, Lesart b)?
- **Eingriff:** wie EXP-127 (Pythia-160M @ 50f5173d, AdamW lr 1e-4, wd 0.1, Warmup 100, Batch 32 × 16 Fakten, 4000 Schritte, Splits `lab/confirm/lm1_splits/seed4000/4001`), aber vor dem Training werden in der Eingabe- und der Ausgabematrix die *Abweichungen* der Zahlzeilen 0–112 von ihrer Mittelzeile durch Zufallsrichtungen ersetzt (Gauß, mittelwertfrei, mit einem gemeinsamen Faktor auf die mittlere Abweichungsnorm der vortrainierten Zahlzeilen skaliert: 0.648 Eingabe, 0.502 Ausgabe); die Mittelzeile (Norm 0.459 / 3.122) bleibt. Sie ist über die Zahlen konstant, trägt also keine Fourier-Leistung bei k ≥ 1, hält aber den gemeinsamen „ist eine Zahl“-Anteil. F und G eines Seeds starten von denselben Zufallszeilen (gepaart, `SeedSequence([133, seed, 5])`). Alle anderen Gewichte bleiben vortrainiert. Wrapper `ft_reset.py` um `ft_pythia.py` (unverändert).
- **Messgrößen:** unverändert aus EXP-127 (`analyze.py` lädt EXP-127s Auswertung über den Dateipfad, schreibt hierher): primär Δ_pow der Rest-Änderung U = E_in(T) − c·E_in(0) (E(0) = zurückgesetzte Zeilen), sekundär Zeilen selbst, Ausgabeseite, Ablation C_in/C_out/C_both, beschreibend Top 5 von U je Lauf und die gepaarten EXP-127-Werte.
- **Lesarten (wie EXP-127):** Tor: zurückgehaltene Genauigkeit ≥ 0.5 am Ende in ≥ 3 von 4 Läufen, sonst **„nicht auswertbar (lernt nicht)“**. **„gesteuert (neue Zahlzeilen)“**: Tor und Δ_pow(U, Eingabe) > 1 in beiden Seeds. **„nicht gesteuert (Rumpf)“**: Tor und |Δ_pow| ≤ 1 in beiden. Sonst **„unklar“**.
- **Deutung je Ausgang (vorab):** „gesteuert“ → in EXP-127 hat die Wiederverwendung der vortrainierten Zahlzeilen die Datensteuerung verdrängt; der vortrainierte Rumpf verhindert sie nicht (Lesart a). „nicht gesteuert“ → der vortrainierte Rumpf legt die Zahlmerkmale fest, auch bei frischen Zeilen (Lesart b); beschreibend prüfen, ob U wieder auf {2, 3, 11, 23, 56} liegt. „nicht auswertbar“ → der Rumpf kann mit neuen Zahlzeilen in 4000 Schritten nicht rechnen; kein Schluss auf a/b.
- **Was gegen a (für b) spräche:** Δ_pow ≈ 0 trotz frischer Zeilen, oder Top 5 von U wieder die vortrainierten Frequenzen.
- **Grenzen vorab:** 2 Seeds, gesehene Splits (wie EXP-127); die Zufallszeilen haben gleiche Norm, aber keine vortrainierte Richtung; der Rumpf hat die Zahl-Tokens im Vortraining gesehen (Positions- und Kontextwissen bleibt). Paarung mit EXP-127 ist nur beschreibend (GPU nicht bitgleich).
- **Budget:** 4 GPU-Läufe à ≈ 36–40 min (wie EXP-127/130), gpu_gb 5, 2 Worker, stall_minutes 15 (P-021), job_minutes 120. Dienst: `44zzzz_exp133_reset` (hinter EXP-132).

## Tests vor dem Lauf

- **Designänderung vor jedem echten Lauf (18:57–18:59):** Die erste Fassung ersetzte die ganzen Zeilen (Richtung zufällig, Norm 0.794 / 3.163). Der CPU-Smoke zeigte danach Verlust 830 nach 2 Schritten; `logit_scale_check.py` (64 Testaufgaben, Antwortposition): vortrainiert teilen alle Zahl-Logits einen Versatz von ≈ 835 (|h| ≈ 271, Streuung über die Zahlen 1.23, CE 5.79), mit ganz zufälligen Zeilen fehlt er (CE 840). Mit erhaltener Mittelzeile: Streuung 4.74, CE 14.8 (Zufallsraten wäre 4.73 bei gleichen Logits). Damit misst der Versuch den Neuaufbau der zahlspezifischen Anteile, nicht das Wiederfinden des Zahl-Versatzes.
- `--selftest-reset` (neue Fassung, CPU, 13 s, 18:59): grün – nur die 113 Zahlzeilen ändern sich (Eingabe und Ausgabe), Mittelzeile erhalten, mittlere Abweichungsnorm = vortrainiert (einzelne Zeilen ±15 %), |cos| der Abweichung zur alten < 0.25, gleicher Seed → gleiche Zeilen, anderer Seed → andere; Top-5-Anteil der neuen Eingabezeilen 0.094 (gleichverteilt 0.089, also kein vortrainiertes Spektrum mehr).
- `analyze.py` an synthetischen Läufen (eingepflanzte Ziele): „gesteuert (neue Zahlzeilen)“, Top 5 = Ziele; die EXP-127-Zusammenfassung bleibt unverändert (md5 geprüft).
- CPU-Smoke (Seed 4000 F, 2 Schritte, 100 Testaufgaben, 18:35–18:56, **erste Fassung**): Lauf, Snapshots, Ablation und Sidecar (Normen) vollständig; Snapshot-0-Normen = Ziel. Der Datenpfad ist in der neuen Fassung unverändert (nur `reset_rows`), deshalb kein zweiter Smoke.
- **Unabhängige Codeprüfung (Claude-Agent, nur lesend, 18:47–18:56, erste Fassung): keine Blocker.** Bestätigt: Patch greift vor Optimierer und Snapshot 0, nur Zahlzeilen, gepaart, Geräte/Typen, Glob, Zusammenfassung nur hier. Übernommen: Sidecar wird bei einem erneut gestarteten fertigen Lauf nicht mehr überschrieben; Wortlaut „gegen a“. Vermerkt: Wrapper-Änderungen stehen nicht in der Run-ID (Wrapper ab dem Einreihen nicht mehr ändern; `wrapper_sha256` im Sidecar).

## Befehl

```
python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-133-pythia-reset-numbers/ft_reset.py --seed 4000 --split-file lab/confirm/lm1_splits/seed4000_F.npy --test-file lab/confirm/lm1_splits/seed4000_test.npy --targets-file lab/confirm/lm1_splits/seed4000.json --steps 4000 --out-root lab/experiments/EXP-133-pythia-reset-numbers/raw
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-133-pythia-reset-numbers/analyze.py
```

## Ergebnis

(offen)

## Vorhersage erster Ordnung (Sitzung 62, Dienst-Job `44zzy_exp133_firstgrad`, 55 s GPU, ausgewertet 20:08 Berlin; vor jedem EXP-133-Trainingslauf)

`first_gradient_reset.py` (Lesart vorab im Skript): Gradient des Antwortverlusts über eine ganze erste Runde (K = 1, Trainingsreihenfolge), an genau den Startgewichten von EXP-133. **Δ_pow(Gradient, Eingabe) +0.04 (Seed 4000), +0.09 (4001) → Vorab-Lesart „unklar“** (weder > 1 noch ≤ 0 in beiden). Beschreibend praktisch null: Top 5 der Eingabe sind in F und G desselben Seeds fast dieselben und keine Ziele (4000: {56, 26, 31, 40, 49} / {26, 4, 56, 31, 23}; 4001: {2, 34, 44, 42, 19} / {34, 2, 44, 23, 33}); Ausgabe +0.01 / −0.01. Zum Vergleich (S59): ganz zufällig initialisierte Pythia-Architektur 0.84 / 1.04 mit Top 5 = eigene Ziele in allen vier Armen; vortrainiertes Pythia −0.13 / −0.01. → Erster Ordnung nach unterdrückt der **vortrainierte Rumpf** das Signal auch bei zufälligen Zahlzeilen (beschreibend, Lesart formal „unklar“). Vorhersage für EXP-133 damit eher „nicht gesteuert (Rumpf)“; ob die erste Ordnung hier trifft, wird erst nach den Läufen gelesen. Der CPU-Zeittest (256 Fakten, −0.09 / −0.18) war gesehen, änderte nichts.

## Zwischenstand (Sitzung 63, 30.09., 22:31 Berlin gemessen): Tor schon verfehlt → „nicht auswertbar (lernt nicht)“ steht fest

Seed 4000 F/G fertig (Dienst-Logs `lab/queue/logs/44zzzz_exp133_reset/job_000/001.log`): Training 0.99–1.00, zurückgehaltene Genauigkeit am Ende **0.0016 / 0.0012** (bei Schritt 1000–3000 genau 0.000; EXP-127 mit vortrainierten Zahlzeilen bei Schritt 1000 schon 0.905). Zwei von vier Läufen unter 0.5 → Tor (≥ 3/4) verfehlt, Vorab-Lesart **„nicht auswertbar (lernt nicht)“**: Der vortrainierte Rumpf kann mit neu gestarteten zahlspezifischen Zeilen in 4000 Schritten nicht rechnen; kein Schluss auf Lesart a oder b. Seed 4001 läuft wie registriert zu Ende; danach `analyze.py`.

**Beschreibend (post hoc, keine Lesart):** Ein Test von genau 0 ist bei 2554 Aufgaben kein Zufall (Zufall ≈ 0.9 %, also ≈ 23 Treffer). Er folgt aus der Arithmetik für einen reinen Auswendiglerner: Zu (a, c) gehört genau ein b; eine ungesehene Aufgabe (a, b) hat ihre Antwort c deshalb nie als Trainingsantwort neben demselben Operanden an derselben Stelle. Nur über die Vertauschung wäre sie erreichbar: 28–30 % der Testaufgaben haben ihr Spiegelpaar (b, a) im Training (LM1-Splits 4000/4001, in Sitzung 63 gezählt). Das Modell nutzt das nicht; es hat also nicht einmal die Vertauschungsregel gelernt (anders als das LM von Grund auf auf Zufallssplits, EXP-119: Plateau ≈ 0.3 aus Tauschpaaren). Beschreibend wächst der eigene Zielanteil der Eingabeänderung leicht (own_in 0.105 gegen other_in 0.087 bei Seed 4000 F, Schritt 3250); ohne Generalisierung ist das keine Lesart.

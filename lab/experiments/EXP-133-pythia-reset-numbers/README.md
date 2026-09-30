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

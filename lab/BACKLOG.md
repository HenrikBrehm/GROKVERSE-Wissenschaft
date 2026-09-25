# lab/BACKLOG.md — Forschungsfragen

Priorität: P1 als Nächstes · P2 bald · P3 Idee. Status: offen · vorbereitet · läuft · erledigt · verworfen.

| ID | P | Frage | Warum interessant | Status | Verweise |
|---|---|---|---|---|---|
| EXP-001 | P1 | Verzögert ein Verbot der bei t0 = 2000 entstehenden Top-5-Embedding-Frequenzen die Generalisierung stärker als ein Zufallsverbot? | H4 ist nur korrelativ (RESULTS §8). Das ist der erste kausale Eingriff in die *Dynamik* | vorbereitet | `experiments/EXP-001-freq-ban/` |
| EXP-002 | P2 | Verbot der „Ziel“-Frequenzen (Top-5 des fertigen 25k-Modells) ab Schritt 1: Sucht sich das Netz andere Frequenzen, und ändert sich das Timing? | Ist die Frequenzwahl früh determiniert oder zufällig? S3 (RESULTS §16.6) zeigt seed-abhängige Frequenzen | Code da (`--condition ban_destined`), Definition fehlt | EXP-001 |
| EXP-003 | P2 | Lässt sich der Generalisierungsschritt aus Metriken ≤ Schritt 2000 vorhersagen (Spearman über Seeds, dann Bedingungen)? | Auftragsfrage „Vorhersage aus frühen Phasen“. Die Daten liegen schon vor: `training/results/aggregate_all/structure_over_time.json` hat 51 Zeilen (eine je Lauf, alle Blöcke), jede mit `generalization_step`, `memorization_step` und Metriken je Checkpoint (`role__*`-Schritte). Achtung: Innerhalb einer Bedingung gibt es nur n = 10 bzw. 3 | offen | RESULTS §8, §10 |
| EXP-004 | P2 | Hängt die Dosis-Wirkung am Verbot, also wie viele Frequenzen (m = 1, 3, 5, 10) und wann (t0 = 500, 2000, 5000)? | Nur sinnvoll, wenn EXP-001 einen Effekt zeigt | offen, bedingt | EXP-001 |
| EXP-005 | P3 | Anderes p (z. B. 97 oder 59): Bleiben Frequenzzahl-Unterschied Transformer vs. MLP und Waveform-Verschiebung erhalten? | RESULTS §13 schlägt das selbst vor (Aliasing bei 113) | offen | RESULTS §7, §13 |
| EXP-006 | P3 | Schwellen-Sweep für die „structured neurons“ als *Labor*-Sensitivitätsanalyse (nicht als Änderung der Studie) | Die Schwelle trägt mehr als jede Messung (RESULTS §13) | offen | RESULTS §6, D6 |
| EXP-007 | P3 | Lokale Reproduktion eines S1-Seed-Paars (100k Schritte)? Dazu nötig: Checkpoint und Resume in ≤ 20-min-Stücken inkl. Adam-Zustand | Bedingung des Reviewer-Runbooks, bisher nicht erfüllt | offen, braucht Resume-Infrastruktur | RESULTS §16 |
| TOOL-1 | P2 | Explorer-Ansicht „Spektrum über Zeit mit Eingriffsmarke“ für EXP-001/002 (HTML aus `spectra.npy`) | Macht Verbote und Ausweichfrequenzen sichtbar | offen, erst nach Daten | — |

Hinweise: Seeds 3–9 der Primärsplits bleiben für die Bestätigung von EXP-001 unberührt. Die
`txf_mul_*`-Läufe und ihre Auswertung (`docs/ADD_VS_MUL_EIGENLEISTUNG.md`) gibt es bereits als
KI-Dokument. Die Interpretation bleibt den Autoren.

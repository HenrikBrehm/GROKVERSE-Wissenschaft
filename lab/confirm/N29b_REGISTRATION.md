---
id: N29b-registrierung
status: abgeschlossen
datum: 2026-09-27
tags: [lab/bestaetigung, befund/positiv]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-067-exclusion-part/README|EXP-067]]", "[[confirm/N29_REGISTRATION|N29]]", "[[experiments/EXP-063-exclusion-locus/README|EXP-063]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# N29b-Bestätigung (Attention-Reset beim Wechsel bei t = 50 verlagert die Abhängigkeit auf die neuen Frequenzen): Registrierung (Sitzung 23). **ENTWURF (vor dem Einfrieren)**

Zurück zu [[FINDINGS]] (Programm B, K4c) · Pilot [[experiments/EXP-067-exclusion-part/README|EXP-067]] (Attention-Reset hebt den Ausschluss auf, 10/10; MLP unklar; W_U nicht nötig) · Vorgänger [[confirm/N29_REGISTRATION|N29]].

- **Aussage (genau das Getestete):** Beim Wechsel A → B nach t = 50 Schritten (add 113, ω = 0) verringert das Zurücksetzen der Attention-Parameter (W_Q, W_K, W_V, W_O auf ihre Init, ihr AdamW-Zustand gelöscht)
  die Abhängigkeit des Endmodells von den alten Zielfrequenzen (R, unten) um mehr als 0.5 gegenüber dem normalen Wechsel (H1) und um mehr als 0.3 gegenüber einem MLP-Reset (W_in, W_out, doppelt so viele
  Parameter) (H2). Ob das Modell danach auf die *neuen* angewiesen ist (R(rsattn) < 0), wird beschreibend mit KI berichtet und ist nicht Teil des Urteils.
- **Modelle:** frische Seeds **2300–2319** (n = 20, neu reserviert, vorher nie benutzt), Splits wie N28/N29 (`overlap_split.build`, ω = 0), je Seed A→B und B→A, Wechsel bei t = 50, danach **4000** Schritte
  (`--stop-after-gen` = Schritte, `--save-model`), drei Arme: normal, rsattn (`--reset-at-switch attn`), rsmlp (`--reset-at-switch mlp`). 120 Läufe, GPU.
- **Maß (wie N29):** Genauigkeit auf der zurückgehaltenen Testmenge nach vollständigem Entfernen der alten bzw. neuen Zielfrequenzen aus W_E[:113]. Je Seed und Arm, Mittel beider Richtungen:
  R = acc_neu − acc_alt (acc_neu = Genauigkeit ohne die neuen; R > 0: Modell ist auf die alten angewiesen).
- **Primär:** X1 = R(normal) − R(rsattn) − 0.5, X2 = R(rsmlp) − R(rsattn) − 0.3. Familie {H1, H2}, Holm, einseitiger t-Test, 95-%-Bootstrap-KI. **„bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0.**
- **Stichprobe und Ausfälle:** Primär alle 20 Seeds (Lehre aus N29). Jeder technische Ausfall (fehlend, nicht gebunden, Lader-Fehler, nicht endlich, Reset nicht vermerkt oder unerwartet) → *nicht auswertbar*.
  Generalisierung (Basis ≥ 0.9 in allen sechs Läufen) wird berichtet, dazu beschreibend ohne Urteil der Test nur an diesen Seeds.
- **Pilotwerte (EXP-067 mit EXP-064, 2000 Schritte, 10 bekannte Seeds):** R(normal) ≈ 0.94, R(rsattn) ≈ 0.08 − 0.74 = −0.66, R(rsmlp) ≈ 0.90 − 0.03 = 0.87. Erwartete Kontraste ≈ 1.6 und 1.5, weit über den Schwellen.
  Ob 4000 Schritte das verändern, ist Teil der Frage.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-067 (Seeds 400–409: Wahl von attn als Kandidat und mlp als Vergleich, Richtung beider Hypothesen, Schwellen 0.5/0.3 deutlich unter den Pilotwerten);
  EXP-063/064 und N29 (Zeitpunkt t = 50, Maß, 4000 Schritte).
- **Grenzen:** Reset auf die Init entfernt alles Gelernte des Teils (Reset-Empfindlichkeit, kein Mechanismusnachweis); ein Zeitpunkt; ein Eingriff (alle 5 Frequenzen); Ablation folgt der Energie (EXP-068);
  die Parameterzahl ist nur mit einem Vergleichsarm (MLP) kontrolliert; W_U-Reset nicht im Block (im Piloten nicht nötig).
- **Familie:** eigene (nur N29b).
- **Vor dem Einfrieren:** Codex-Prüfung; ein echter Job bis zum Ende durch den eingefrorenen Lader; Manifest mit Code-Hashes.
- Code: `lab/tools/confirm_n29b.py` (Selbsttest ok, Sitzung 23, 11:01, inkl. Import-Prüfung). Trainer-Option `--reset-at-switch attn|mlp` seit 5d84666 (Codex geprüft, 18/18 Tests).

```
python lab/tools/confirm_n29b.py --splits lab/confirm/N29b_manifest.json
python lab/tools/confirm_n29b.py --jobs lab/confirm/N29b_manifest.json > lab/confirm/N29b_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/N29b_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_n29b.py --analyze lab/confirm/N29b_manifest.json
```

## Prüfung vor dem Einfrieren (Sitzung 23, 11:02–11:05 Berlin)

**Codex nicht verfügbar:** Der Aufruf brach mit „Your workspace is out of credits“ ab (Regel 12: dokumentiert, ohne Codex weiter, nicht umgangen). Übernommen wurde Codex' Zwischenbemerkung vor dem Abbruch:
H1 belegt keinen Umstieg *auf* die neuen Frequenzen, nur eine Verringerung um > 0.5 → Aussage oben auf das Getestete eingeschränkt, R(rsattn) nur beschreibend.
**Eigene Prüfung** (statt Codex; Punkte aus den Codex-Prüfungen von N29 übernommen): Run-IDs (`_rs<teil>` vor `_devcuda`, wie freq_ban; wird im Smoke gegen den echten Trainer geprüft), Reset-Ereignis
(normal: keins; rsattn/rsmlp: `which` und `check`), alt/neu je Richtung (A→B: alt = Ziele von A), Vorzeichen (R > 0 = auf alte angewiesen; H1 = R(normal) − R(rsattn)), Holm über zwei, alle Seeds primär,
Import-Hülle im Selbsttest. **Zusätzliche Grenze:** Die „Größe“ eines Resets ist nur über die Parameterzahl kontrolliert; die Verschiebung der Teile von ihrer Init bis t = 50 ist nicht angeglichen.

## EINGEFROREN (Sitzung 23)

Manifest-Commit **db31564**, Splits und Jobs committet. Vor dem Einfrieren kein Lauf mit Seeds 2300–2319. Smoke (Seed 2300, rsattn, A→B) durch den eingefrorenen Lader: Run-ID und Reset-Ereignis passen zum
echten Trainer, gebunden (zählt als regulärer Lauf; dieser eine Wert ist vor dem Block gesehen: Basis 1.0, ohne alte 1.0, ohne neue 0.01). Block ab 11:06 Berlin (Log), 7 GPU-Arbeiter.
Hinweis: Die Überschrift („verlagert … auf die neuen“) ist weiter als die geprüfte Aussage; maßgeblich ist der Abschnitt „Aussage (genau das Getestete)“.

## ERGEBNIS (Sitzung 23, Block 11:06–11:30 (Log), Auswertung 11:30–11:31 Berlin; `lab/confirm/N29b_summary.json`): ***H1 und H2 bestätigt***

120/120 Läufe gebunden, 0 technische Ausfälle, 19/20 Seeds generalisiert (primär alle 20).

| | Kontrast | 95-%-KI | Seeds über der Schwelle | Holm-p |
|---|---|---|---|---|
| **H1** R(normal) − R(rsattn) | **1.489** | [1.363, 1.613] | 20/20 über 0.5 | 5·10⁻¹² |
| **H2** R(rsmlp) − R(rsattn) | **1.421** | [1.281, 1.559] | 20/20 über 0.3 | 5·10⁻¹² |

Mittelwerte R (acc_neu − acc_alt): normal **0.86**, rsmlp **0.79**, rsattn **−0.63**. **Beschreibend (nicht Teil des Urteils):** R(rsattn) < 0 in 20/20 Seeds und 40/40 Richtungen, Bootstrap-KI [−0.73, −0.52]:
Nach dem Attention-Reset ist das Endmodell auf die *neuen* Zielfrequenzen angewiesen.
**Schlussfolgerung nicht von Codex geprüft** (kein Guthaben seit 11:04); Kernaussage in FINDINGS deshalb vorläufig markiert, Codex-Prüfung in einer späteren Sitzung.

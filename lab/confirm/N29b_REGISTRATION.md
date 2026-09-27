---
id: N29b-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-067-exclusion-part/README|EXP-067]]", "[[confirm/N29_REGISTRATION|N29]]", "[[experiments/EXP-063-exclusion-locus/README|EXP-063]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# N29b-Bestätigung (Attention-Reset beim Wechsel bei t = 50 verlagert die Abhängigkeit auf die neuen Frequenzen): Registrierung (Sitzung 23). **ENTWURF**

Zurück zu [[FINDINGS]] (Programm B, K4c) · Pilot [[experiments/EXP-067-exclusion-part/README|EXP-067]] (Attention-Reset hebt den Ausschluss auf, 10/10; MLP unklar; W_U nicht nötig) · Vorgänger [[confirm/N29_REGISTRATION|N29]].

- **Aussage:** Beim Wechsel A → B nach t = 50 Schritten (add 113, ω = 0) macht das Zurücksetzen der Attention-Parameter (W_Q, W_K, W_V, W_O auf ihre Init, ihr AdamW-Zustand gelöscht) aus einem Endmodell,
  das auf die alten Zielfrequenzen angewiesen ist, eines, das auf die neuen angewiesen ist; ein MLP-Reset (W_in, W_out, doppelt so viele Parameter) tut das deutlich weniger.
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

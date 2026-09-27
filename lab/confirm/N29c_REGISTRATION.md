---
id: N29c-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-069-attention-part/README|EXP-069]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[experiments/EXP-070-ov-alignment/README|EXP-070]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# N29c-Bestätigung (Wertepfad gegen Muster der Attention beim Wechsel bei t = 50): Registrierung (Sitzung 23). **ENTWURF**

Zurück zu [[FINDINGS]] (K4d, offene Frage „was in der Attention“) · Pilot [[experiments/EXP-069-attention-part/README|EXP-069]] · Vorgänger [[confirm/N29b_REGISTRATION|N29b]] · [[NOVEL_DIRECTIONS]] N32.

- **Aussage (genau das Getestete):** Beim Wechsel A → B nach t = 50 Schritten (add 113, ω = 0) senkt das Zurücksetzen von W_V und W_O (auf die Init, ihr AdamW-Zustand gelöscht) den Ablationskontrast
  R = acc(ohne neue) − acc(ohne alte) um mehr als 0.5 gegenüber dem normalen Wechsel (H1) und um mehr als 0.3 gegenüber dem Zurücksetzen von W_Q und W_K (gleiche Parameterzahl, H2).
- **Modelle:** frische Seeds **2320–2339** (n = 20, neu reserviert, vorher nie benutzt), Splits wie N29b, je Seed A→B und B→A, danach **4000** Schritte (`--stop-after-gen` = Schritte, `--save-model`),
  drei Arme: normal, rsvo (`--reset-at-switch vo`), rsqk (`--reset-at-switch qk`). 120 Läufe, GPU.
- **Maß, Primär, Ausfälle:** wie [[confirm/N29b_REGISTRATION|N29b]] (Code `lab/tools/confirm_n29c.py` ist `confirm_n29b.py` mit anderen Armen und Seeds). X1 = R(normal) − R(rsvo) − 0.5, X2 = R(rsqk) − R(rsvo) − 0.3;
  Familie {H1, H2}, Holm, einseitiger t-Test, 95-%-Bootstrap-KI; „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0. Primär alle 20 Seeds; jeder technische Ausfall → *nicht auswertbar*.
- **Pilotwerte (2000 Schritte, 10 bekannte Seeds):** R(normal) ≈ 0.94 (EXP-064), R(rsvo) ≈ 0.165 − 0.141 ≈ 0.023 und R(rsqk) ≈ 0.807 − 0.052 ≈ 0.755 (EXP-069). Erwartete Kontraste ≈ 0.9 und 0.7.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-069 (Seeds 400–409: Wahl von vo/qk, Richtung, Schwellen wie N29b und deutlich unter den Pilotwerten); N29b (Protokoll, Maß); EXP-070 (kein Einfluss auf das Design).
- **Grenzen:** Reset-Empfindlichkeit, kein Speicherort; Gewichte und AdamW-Zustand gemeinsam zurückgesetzt; Normen der OV-Ausgabe und QK-Logits ändern sich mit; rsqk ist größengleich, aber nicht nach
  Verschiebung oder Dynamik angeglichen; im Piloten nutzte das Netz nach rsvo beide Mengen (R ≈ 0), H1/H2 sagen nichts über ein Vorzeichen von R(rsvo).
- **Familie:** eigene (nur N29c).
- **Vor dem Einfrieren:** Codex-Prüfung; ein echter Job durch den eingefrorenen Lader; Manifest mit Code-Hashes. **Rechnen erst im nächsten Fenster (ab 00:00).**

```
python lab/tools/confirm_n29c.py --splits lab/confirm/N29c_manifest.json
python lab/tools/confirm_n29c.py --jobs lab/confirm/N29c_manifest.json > lab/confirm/N29c_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/N29c_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_n29c.py --analyze lab/confirm/N29c_manifest.json
```

## Codex-Prüfung vor dem Einfrieren (Sitzung 23, Ergebnis 11:59 Berlin)

Kein Blocker (Zuordnung rsvo→vo, rsqk→qk, Run-IDs, Selbsttest-Anpassungen konsistent). Übernommen: Pilotwerte genauer gerundet und R(normal) EXP-064 zugeordnet.

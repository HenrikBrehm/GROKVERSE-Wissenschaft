---
id: logic-audit-s54-appB-E-G
status: erledigt
datum: 2026-09-29
tags: [lab/paper]
---
# Logikprüfung Anhänge B, E, G (Sitzung 54, 22:15–22:40 Berlin)

Zurück: [[paper/STATUS]] · Vorgänger [[paper/logic_audit_S53_appA]], [[paper/logic_audit_S53_appC_D]]. Zwei unabhängige Claude-Agenten, nur lesend (Codex ohne Guthaben). Jeder Punkt selbst an der Quelle geprüft, bevor er in `draft.md` einging (§3.2 = Anhang B, §3.6 = Anhang E, §5 = Anhang G).

## Anhänge B/E (Zahlen: alle nachgeprüften stimmen, P2d/P2e/P2f/C4)

1. **Übernommen.** E-Grenze „as for the cyclic tasks (§3.2) … follows“ übertrug EXP-068 (nur 80 N29-add-113-Modelle) auf P2f; §3.2 sagt selbst, P2d/P2e seien nicht mit dem Gleichenergie-Maß geprüft → Widerspruch; ersetzt.
2. **Übernommen.** „follows the energy distribution“ → „goes along with“, plus „that measure changes the relative dose“ (belegt: EXP-068 README Z. 41–43).
3. **Übernommen.** „the steering of §3.1 … persists into the post-grokking embedding“: P2f hat eigene Splits, 37/40 Arme generalisiert → „steered targets also dominate the step-12 000 embedding (on its own splits; 37/40 arms generalized)“.
4. **Nicht übernommen.** „follows their rank order“ bei ρ̄ 0.37: der Absatz endet schon mit „A correlation, not a mechanism“.
5. **Nur Dokumentation:** `P2f_REGISTRATION.md` trägt noch den Kopf „VORBEREITET, NOCH NICHT EINGEFROREN“, obwohl eingefroren (Manifest 15539d8). Offen, eigene Notiz (Nachtrag in der Registrierung, nicht überschreiben).

## Anhang G (Theorie; Mathematik numerisch vom Prüfer bestätigt)

1. **Übernommen, echter Fehler.** „For the *final* frequencies M0c is only descriptively better than M0 in the MLP (r̄ 0.351 vs 0.323…)“: r̄ ist ein Rang (kleiner = besser), Quellen (JOURNAL Z. 587, BEFUND-split-mechanismus Punkt 4) sagen M0 0.323 besser als M0c 0.351 → Richtung korrigiert; die Schlussfolgerung „gilt für den ersten Gradienten, nicht für die spätere Ordnung“ stützt sich jetzt nur auf die Ordnung innerhalb der Ziele (EXP-045).
2. **Übernommen.** Veralteter Satz „a drafted pilot (EXP-081) varies β₁ and β₂“ – EXP-081 ist gelaufen, R9/R10/R11 bestätigt → Verweis auf die empirische Behandlung der Uhr.
3. **Übernommen.** EXP-040 verwies auf §5b (= Section 7, dort fehlt EXP-040) → Beschreibung direkt eingesetzt (Pilot, 4 bekannte Seeds, Lesart „unclear“).
4. **Übernommen.** Übersicht: „its Fourier power … is M0c“ → „expected power, proportional to M0c minus a marginal term“.
5. **Übernommen.** „own occurrence count cancels exactly“ → nur der ausgangsgleichförmige Anteil; die Paarzahl skaliert den Gradienten (‖P⊥ℓ_t‖² = n_t(1 − n_t/p), selbst nachgerechnet für 0/1-Einträge).
6. **Übernommen.** „weak marginals“ → „near-uniform … (target-enriched in spectrum)“ (eigener Widerspruch zu 5.2).
7. **Übernommen.** Fehlende Annahmen ergänzt: Attention-Score-Ableitung und MLP-Gating vernachlässigt; AdamW-Zerfallsterm im ersten Update trägt das Init-Spektrum.
8. **Übernommen.** „It predicts which frequencies the network starts to grow“ → „describes the initial gradient (and, approximately, the first sign-like Adam updates)“.

Manuskript und TeX neu erzeugt; Querverweise geprüft. Diff-Prüfung: siehe unten.

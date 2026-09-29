---
id: logic-audit-s54-appB-E-G
status: erledigt
datum: 2026-09-29
tags: [lab/paper]
---
# Logikprüfung Anhänge B, E, G (Sitzung 54, 22:13–22:35 Berlin laut Commit-Zeiten)

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

## Diff-Prüfung der B/E/G-Änderungen (≈ 22:30)

Keine sachlichen Fehler; Formel und Anhang-Zuordnung bestätigt. Vier Formulierungen übernommen: Reihenfolge der Verweise (EXP-Piloten zu §4, R3 zu §3.10), doppelte Klammer aufgelöst, Subjekt in 5.4(i) (AdamW-Zerfallsterm), „later order within the target set“.

## Anhang F (Explorationen) und H (Reproduktion), Sitzung 54, ≈ 22:33

**F:** keine Richtungsfehler, 24 Zahlengruppen vom Prüfer an den Quellen bestätigt. Übernommen (selbst geprüft: `speed_switch_decompose_s32.json` gap_share 0.924, 49/60; `speed_switch_optstate_s32.json` 0.57 → 0.26/0.25/0.28 = 54/56/51 %; FINDINGS R6-Spitze t = 20): (1) EXP-084 „follows the pair spectrum“ → „in this pilot is consistent with“; (2) „cannot be the cause“ → „do not explain the gap“; (3) „92 % over all 60 pairs“ war als Paaranteil lesbar → Anteil der mittleren Verzögerung, 49/60 Paare; (4) Pilotspitze bei 25 gegen R6-Spitze bei 20 vermerkt; (5) „a quarter and a half“ → „just over half“; (6) ε-Zuordnung der Anteile ergänzt.
**H** (Quelle `draft_short.md` Anhang R): (1) veraltet „R4 is pending“ gestrichen; (2) GPU-Nichtdeterminismus-Absatz um den Full-Batch-Fall R4 ergänzt; (3) Befehle mit Manifest-Argument (confirm-Werkzeuge verlangen `--analyze <manifest>`, C*_analyze.py ein Manifest) und (4) „am Manifest-Commit“ ergänzt. Alle Tabellenwerte vom Prüfer bestätigt.

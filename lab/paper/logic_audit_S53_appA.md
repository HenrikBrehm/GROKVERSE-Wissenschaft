---
id: logic-audit-s53-appA
status: offen
datum: 2026-09-29
tags: [lab/paper]
---
# Logikprüfung Anhang A (Sitzung 53, 22:05 Berlin) – NOCH NICHT SELBST NACHGEPRÜFT

Zurück: [[paper/STATUS]] · Vorgänger [[paper/logic_audit_S53_appC_D]]. Unabhängiger Claude-Agent, nur lesend; Zitate wörtlich aus `draft.md` (für exakte Ersetzung). Vorgehen wie bei C/D: jeden Punkt selbst prüfen → in draft.md einarbeiten → Manuskript neu erzeugen → Diff prüfen lassen.

1. **Überdehnung (widerspricht dem eigenen Absatz).** „they are not evidence for a separate effect of learning rate or weight decay on the steering beyond this rescaling“ – der Absatz selbst nennt Restabweichungen (lr 5·10⁻⁴ +5 bis +8 % bei jedem τ ≥ 250; EXP-103 gepaarte log-Verhältnisse −0.09 [−0.13, −0.05] und +0.07 [0.01, 0.15]) und endet mit „the larger learning rate steers sooner at equal lr·wd“. Vorschlag: „most of the size differences are captured by this rescaling; small learning-rate-specific residuals remain (see follow-up)“.
2. **Überdehnung.** „So the rescaling by lr·wd describes the steering from about 250 steps on“ – nur ein Toleranzband 0.10 bestanden, kein Äquivalenztest; systematische Versätze. Vorschlag: „So from about 250 steps on the rescaling by lr·wd describes the steering to within 10 % (the pre-set tolerance), with small systematic lr-dependent offsets“.
3. **Möglicher Fehler (Zensierungslogik, aus R2_REGISTRATION_DRAFT.md:68 übernommen).** „b is censored at 4000 in 54/60 runs @25 and 11/60 @50, so this is a lower bound“ – Zensierung im @25-Arm drückt die gepaarte Differenz nach unten, im @50-Arm nach oben; bei Zensierung in beiden Armen ist die Größe keine Schranke, nur die Richtung gestützt. Vorschlag: „…; censoring in both arms means the size is not a bound, only the direction is supported“. **Vor dem Ändern:** Definition der Differenz in R2 (welcher Arm minus welcher) und die Paare mit beidseitiger Zensierung selbst nachzählen.
4. **Überdehnung.** „in the MLP the initial order dominates the mask order at step 2000“ – Vergleich zweier beschreibender Korrelationen (0.54 gegen 0.27) ohne Test; C3 macht keine Aussage je Bedingung (C3_REGISTRATION.md:24). Vorschlag: „in the MLP the initial order correlates more strongly with the step-2000 order than the mask order does (descriptive)“.
5. **Querverweis:** In A.1 wird „(§4)“ zu „(Appendix F)“; das Material zum Δ_pow-Wachstum nach der Generalisierung steht laut Prüfer in Anhang K. Im Generator (`relabel`) prüfen.

## Teilprüfung Punkt 3 (22:05 gemessen)

R2_REGISTRATION_DRAFT.md Z. 68: R2_time T1 = log2 b(@25) − log2 b(@50), +1.34, „29/29 ohne Gleichstand“ (also 1 Gleichstand von 30), „b bei @25 meist bei 4000 zensiert, also Untergrenze“ (54/60 @25, 11/60 @50). Logik: Zensierung bei @25 → Differenz unterschätzt; bei @50 → überschätzt. Die Aussage „Untergrenze“ gilt nur, wenn jeder bei @50 zensierte Lauf mit einem bei @25 zensierten gepaart ist (dann Gleichstand 0, und der wahre Wert ist wegen @25 ≥ @50 vermutlich ≥ 0 – auch das nur plausibel, nicht gesichert). **Nächster Schritt:** in den R2-Rohdaten (`R2_time.py`) die 11 bei @50 zensierten Läufe mit ihren @25-Partnern paaren und zählen; je nach Ergebnis „lower bound“ halten oder durch „direction supported; size not bounded“ ersetzen (auch in der Registrierungs-Ergebniszeile als Nachtrag vermerken, nicht überschreiben).

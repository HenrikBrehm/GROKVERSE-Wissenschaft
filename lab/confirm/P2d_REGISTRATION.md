---
id: P2d-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P2c_REGISTRATION|P2c]]", "[[experiments/EXP-065-p2d-pilot/README|EXP-065]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# P2d-Bestätigung (funktionale Nutzung, Empfindlichkeit je gleicher Schrittnorm): Registrierung (Sitzung 22). **ENTWURF, nicht eingefroren, ungetestet am echten Lauf**

Zurück zu [[FINDINGS]] (Programm A) · Vorgänger [[confirm/P2c_REGISTRATION|P2c]] (nicht bestätigt, Dosisgeometrie) · Pilot [[experiments/EXP-065-p2d-pilot/README|EXP-065]].

- **Aussage P2d:** In Modellen mit konstruiertem Split (add 113, 4000 Schritte) senkt ein Parameterschritt gleicher Norm entlang der **eigenen Zielfrequenzen** in W_E den mittleren Logit-Abstand der
  richtigen Klasse stärker als derselbe Schritt entlang gleich großer Kontrollmengen (je 5 Frequenzen aus der P2-Kontrollmenge). Lokale Aussage (δ = 2 % von ‖W_E[:113]‖), nur W_E.
- **Modelle:** frische Seeds **2230–2249** (n = 20), je Arm F und G, `confirm_splits.build` mit Versuchs-ID 4, `--steps 4000 --stop-after-gen 4000 --save-model`, GPU.
- **Maß:** u_S = P_S W / ‖P_S W‖, W' = W − δ·u_S, drop_S = Logit-Abstand vorher − nachher auf der gemeinsamen Testmenge. 4 Kontrollmengen je Arm (RNG [4, Seed, Arm]).
  **Primär:** D_s = Mittel über beide Arme von (drop_eigen − Mittel drop_Kontrolle), immer definiert. Einseitiger t-Test, 95-%-Bootstrap-KI.
- **Urteil:** Jeder technische Ausfall → *nicht auswertbar*; < 90 % geeignet (Basis-Genauigkeit ≥ 0.9 in beiden Armen) → *nicht auswertbar*; sonst **„bestätigt“ = p < 0.05 und KI-Untergrenze ≥ 0.05** (Logit-Einheiten), sonst *nicht bestätigt*.
- **Stichprobe:** Pilot EXP-065 (bekannte P2c-Modelle): D je Seed 0.254 ± 0.038 (n = 40); n = 20 gibt eine erwartete KI-Untergrenze weit über 0.05.
- **Bereits gesehene Daten:** P2c-Modelle (R und EXP-065). Maß und δ nach dem P2c-Ergebnis gewählt; deshalb frische Seeds.
- **Familie:** eigene (nur P2d), falls beim Einfrieren nicht anders festgelegt.
- **Vor dem Einfrieren (nächste Sitzung):** Codex-Prüfung (Regel 18c); ein echter Job bis zum Ende durch den eingefrorenen Lader (Lehre aus P2b); Manifest mit Code-Hashes und Commit.
- Code: `lab/tools/confirm_p2d.py` (Selbsttest ok, Sitzung 22).

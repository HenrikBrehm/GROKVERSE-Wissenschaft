---
id: EXP-124
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-124 (Entwurf): Entsteht die frühe Kommutativität konstruierter Splits über die Zielfrequenzen?

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage N57, Sitzung 55) · Vorgänger [[experiments/EXP-123-commutativity-stages/README|EXP-123]] · [[NOVEL_DIRECTIONS]] N57 · [[JOURNAL]] Sitzung 55 Zyklus 15

**Stand 03:03:** Code, Jobdatei (`make_jobs.py` → `jobs.txt`, 20 Läufe; Kontrollfrequenzen je Einheit aus default_rng([124, u]) ohne Zielmenge A) und `analyze.py` (Lesarten wie unten, Technik: Bann wirksam < 10⁻⁶ der übrigen Energie) geschrieben und an den Smokes geprüft. **Nicht eingereiht:** Regel 20a (keine Mechanismus-Detailversuche in dieser Woche); Entscheidung in einer späteren Sitzung, dann blinde Code-Prüfung und Einfrieren.

**Status: Entwurf (02:58, Sitzung 55), kein Code, nichts gerechnet.** Vor dem Einfrieren: Code (inzwischen geschrieben, siehe „Stand“ oben), Smoke (ohne Bann bitgleich zu EXP-123), blinde Code-Prüfung, Abwägung gegen Regel 20 (Paper/LM-Leiter haben Vorrang; nur wenn die GPU Platz hat).

**Code-Stand (03:02):** `ban_trace.py` (Kopie von EXP-123 `swap_trace.py` + `--ban`; speichert zusätzlich das W_E-Spektrum am Ende). Smoke 1 (ohne Bann, u0_E2_0): Spur bitgleich zum EXP-123-Smoke (35/35 Messpunkte). Smoke 2 (Bann der u0-Ziele 2, 3, 40, 53, 54; 300 Schritte): Zielenergie am Ende ≈ 2·10⁻¹³ gegen Median 6.2 der übrigen Frequenzen → Bann wirkt. Offen vor dem Einfrieren: Ziehung der Kontrollfrequenzen (Arm C) festlegen, Jobdatei, Auswerteskript, blinde Code-Prüfung. E2_0 nutzt die Zielmenge A (`targets["0"]` in `r5_uN.json`, confirm_r5.py Kopf).

- **Beobachtung:** Konstruierte Splits (E2_0) erreichen die Kommutativitätsstufe ≈ 11× früher als Zufallssplits (EXP-123, post hoc), und t_swap hängt in E2_0 so eng an der frühen W_E-Zielenergie wie t_gen (ρ −0.80). Korrelation trennt nicht: Kommutativität *über* die Fourier-Struktur oder beides nur gemeinsam schneller?
- **Eingriff:** Auf den E2_0-Splits der R5-Einheiten u0–u9 (Init-Seeds wie EXP-123) die fünf eigenen Zielfrequenzen der Einheit ab Schritt 1 aus W_E bannen (Arm T) gegen einen Bann von fünf zufälligen Nicht-Zielfrequenzen (Arm C, feste Ziehung je Einheit). 20 Läufe, höchstens 8000 Schritte, Messung wie EXP-123 (acc_swap/acc_other alle 25 Schritte).
- **Maß:** L_swap = log2 t_swap(T) − log2 t_swap(C) je Einheit (zensiert als 8000); L_other entsprechend.
- **Lesarten, überarbeitet 03:10 nach blinder Code-/Designprüfung (maßgeblich; die Zeile darunter ist überholt):** Δ = L_swap − L_other je Einheit. „Kommutativität über die Zielstruktur“: Mittel L_swap ≥ 1, Mittel Δ ≥ 0.5 und Δ > 0 in ≥ 80 % der Einheiten; „allgemeine Verlangsamung“: L_swap ≥ 1 und L_other ≥ 1 bei |Mittel Δ| < 0.3; „eigener Pfad“: |Mittel L_swap| < 0.3 bei L_other ≥ 1; sonst „unklar“. Grund: Der Bann der genutzten Frequenzen verlangsamt vermutlich alles (EXP-001); nur ein *spezifischer* Aufschub der Kommutativitätsstufe spricht für den Weg über die Zielfrequenzen. **Offene Designpunkte vor dem Einfrieren:** Arm C entfernt kaum genutzte Frequenzen (≈ „kein Bann“) → beschreibend mit den EXP-123-Zeiten ohne Bann vergleichen; eine echte Kontrolle „genutzte Frequenzen entfernen“ bräuchte z. B. R-Splits mit Bann ihrer eigenen Top-5 (ban_destined-artig). No-Ban-Smoke mit der Endfassung wiederholen; C-Mengen ggf. ohne Zielmenge B ziehen. Bann-Semantik: W_E und alle Gradienten ab Init projiziert (exp_avg bleibt dadurch im erlaubten Raum; exp_avg_sq nicht, deshalb Projektion nach jedem Schritt); nicht schrittgleich zu freq_ban ban_destined (dort Schritt 1 unprojiziert).
- **Lesarten (Entwurf, überholt):** „Kommutativität über die Zielstruktur“: Mittel L_swap ≥ 1 (×2) und ≥ 8/10 positiv; „eigener Pfad“: |Mittel L_swap| < 0.3 bei Mittel L_other ≥ 1; sonst „unklar“. Beschreibend: Liegt t_swap(T) nahe am R-Niveau (EXP-123 Median 4150)?
- **Was dagegen spräche:** L_swap ≈ 0: Die frühe Kommutativität braucht die Zielfrequenzen nicht.
- **Bereits gesehen:** EXP-123 (alle Zeiten der E2_0- und R-Arme dieser Einheiten), R5-Zeiten. Der Bann ist eine starke Veränderung (EXP-001: Netz weicht auf andere Frequenzen aus); ein Befund betrifft „ohne Zielfrequenzen“, nicht „ohne Fourier-Struktur“.
- **Grenzen:** 10 Einheiten, eine Aufgabe; Exploration.

---
id: LEITFRAGEN_LEDOUX
datum: 2026-10-01
tags: [lab/erklaerung, lab/lernen]
---
# Leitfragen zur LeDoux-Linie (R15, EXP-143, EXP-144)

Zurück zu [[LAB]] · [[paper/erklaerung/ERKLAERUNG_2026-10-01]] · [[experiments/EXP-143-ledoux-regime/README|EXP-143]] · [[confirm/R15_REGISTRATION|R15]]

Angelegt in Sitzung 71 nach Regel 23: nur Fragen und Lesehinweise, keine fertigen Antworten. Die Zahlen zum Nachschlagen stehen in den verlinkten Notizen.

## Leseliste (je drei Fragen)

**1. LeDoux 2026, *The Order Is The Message* (arXiv 2603.25047), §4.1–5.1 und §6.4**
- Was genau ist die „Stride“-Reihenfolge? Schreib die ersten zehn Paare einer Epoche für p = 13 und Schlüssel a mod 3 auf.
- Warum ist bei LeDoux die zufällige Reihenfolge der Vergleich, der *nicht* lernt? Was heißt das für die Frage, ob Menge oder Reihenfolge wichtiger ist?
- Was sagt §6.4 über „data sparsity“ und „weight decay“? Wo liegen unsere Versuche auf dieser Skala?

**2. Gromov 2023, *Grokking modular arithmetic* (arXiv 2301.02679), §5.2**
- Welches Modell untersucht Gromov (Schichten, Aktivierung, Verlust)? Wie unterscheidet es sich von unserem Transformer?
- Was ist α_c, und warum sinkt es nach Gromov mit p?
- Ist sein Satz über die „sampling method“ eine Behauptung, eine Vermutung oder ein Ergebnis? Wie würdest du ihn in einem Satz zitieren?

**3. Nanda et al. 2023 (Fourier-Schaltkreis der modularen Addition)**
- Warum genügen wenige Frequenzen k, um a + b mod p zu berechnen?
- Was bedeutet „Leistung bei Frequenz k“ in der Einbettung W_E?
- Warum sind die Frequenzen k und p − k gleichwertig?

## Herleitungen als Fragen

- **Warum 101?** Berechne 99 · 101 mod 9973. Was sagt eine kleine Zahl dort über eine Funktion, die nur von a mod 99 abhängt?
- **Oberwellen:** Wenn W_E eine verzerrte Funktion von cos(2π · 101 · a / p) ist, bei welchen k erwartest du dann weitere Leistung? Vergleiche mit den Top-5 in der EXP-143-README.
- **R15:** Was ist L = ln(g_R / g_E), und warum ist L nur eine *untere* Schranke, wenn der Zufallsarm nie generalisiert?
- **Vorzeichen-Test:** Warum ist p = 2⁻¹⁰ der kleinste mögliche p-Wert bei 10 Seeds, die alle in dieselbe Richtung zeigen?
- **Budget:** Bei 307 brauchte der langsamste gezielte Lauf 21 250 Schritte, das Budget war 30 000. Was darfst du deshalb über die Zufallsarme sagen, was nicht?
- **EXP-143:** Wenn das Netz nicht einmal die Trainingsaufgaben lernt, warum kann man dann nicht entscheiden, ob Menge oder Reihenfolge „gewinnt“?

## Fragen, die du dir selbst stellen kannst, bevor du weitermachst

- Kann ich R15 in drei Sätzen einem Mitschüler erklären, ohne das Wort „Frequenz“ zu benutzen?
- Welcher Teil von EXP-143 ist *unser* Ergebnis und welcher Teil steht schon bei LeDoux?
- Was müsste EXP-144 zeigen, damit sich die Frage „Menge gegen Reihenfolge“ bei 0,3 % Daten überhaupt stellen lässt?

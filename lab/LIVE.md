---
tags: [lab/live]
---
# LIVE: Laborsitzung 12

- **Sitzungsstart:** 2026-09-26 19:29 Berlin (17:29Z, vom Runner)
- **Deadline:** 2026-09-26 22:29 Berlin (20:29Z)
- **Zuletzt aktualisiert:** 20:21 Berlin
- **Run-Fenster:** zu (heute bis 18:00), wieder ab 00:00. Diese Sitzung: nur Denk-, Code- und Vorbereitungsarbeit.

## Gerade

Warte auf Codex' Prüfung von EXP-046. Nebenher Rückblick nach drei Zyklen: Was haben wir gelernt, welche Annahme greifen wir als Nächstes an?

## Als Nächstes

Codex-Einwände zu EXP-046 einarbeiten; dann EXP-047 ebenfalls kurz prüfen lassen.

## Verlauf dieser Sitzung

- 20:18 **Neue Alternativerklärung gefunden und Test festgelegt ([[experiments/EXP-047-marginal-control/README|EXP-047]]):** Die konstruierten Splits verschieben nicht nur die Paarstruktur, sondern auch, wie oft jede Zahl vorkommt. Vielleicht folgt das Netz nur diesen Häufigkeiten? Kontrolle: dieselben Häufigkeiten, aber zufällig gemischte Paare. Offline ist die Trennung sauber. 40 GPU-Läufe heute Nacht.

- 19:58 **Codex hat zwei ernste Fehler in der Nacht-Queue gefunden** (Fehler wurden verschluckt; die GPU-Prüfung ließ sich umgehen) und einen Statistikfehler in EXP-044. Alles behoben, bevor irgendetwas läuft. Die Nacht-Reihenfolge ist jetzt: GPU-Prüfung → EXP-043 → EXP-046 → EXP-044 → EXP-045.

- 19:40 **Neuer Versuch [[experiments/EXP-046-dihedral-steering/README|EXP-046]] festgelegt:** Klappt die Steuerung über die Daten auch in einer *nicht-kommutativen* Gruppe (Symmetrien des 59-Ecks)? Das ist die erste echt andere Aufgabe. Alle 30 Splits erzeugt, sie treffen ihre Ziel-Darstellungen in 20/20 Fällen. Literatur: nichts Gleiches gefunden (N24).
- 19:35 Codex-Prüfung neu gestartet (die aus Sitzung 11 war ohne Ergebnis abgebrochen).
- 19:30 Stand gelesen; kein Training läuft, Fenster zu, kein STOP.

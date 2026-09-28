"""Suisse Meets On-Premise – 3 Folien, Deutsch (16:9, 13.333 x 7.5 in)."""
import sys
import ooxml
from ooxml import Slide, para, run, write_pptx

ooxml.LANG = "de-CH"

# ---- Marken-Farben (hier durch die offiziellen Suisse-Meets-Werte ersetzen) ----
RED = "D52B1E"
INK = "0F1115"
CARD_D = "1C2028"
MUTED_D = "A3ABB6"
SOFT_D = "D3D8DF"
TEXT = "1F2328"
MUTED = "5B6470"
TINT = "F2F3F5"
ARROW = "C4C9D0"
WHITE = "FFFFFF"

W, H, M = 13.333, 7.5, 0.6


def logo(s, x, y, size, dark, tw):
    """Platzhalter-Logo: rotes Quadrat mit Schweizerkreuz + Wortmarke."""
    s.shape(x, y, size, size, fill=RED, geom="roundRect", radius=18000, name="Logo")
    bar, arm = size * 0.2, size * 0.62
    s.shape(x + (size - bar) / 2, y + (size - arm) / 2, bar, arm, fill=WHITE, name="Logo Kreuz")
    s.shape(x + (size - arm) / 2, y + (size - bar) / 2, arm, bar, fill=WHITE, name="Logo Kreuz")
    fs = size * 40
    s.text(x + size + 0.14, y - 0.05, tw, size + 0.1,
           [para([run("Suisse Meets", fs, WHITE if dark else TEXT, b=True),
                  run("  On-Premise", fs, MUTED_D if dark else MUTED)])], anchor="ctr", name="Wortmarke")


def header(s, title, subtitle):
    logo(s, W - M - 2.78, 0.52, 0.3, dark=False, tw=2.34)
    s.text(M, 0.42, 8.8, 0.7, [para(run(title, 32, TEXT, b=True))], anchor="ctr", name="Titel")
    s.text(M, 1.12, 11.5, 0.45, [para(run(subtitle, 16, MUTED))], anchor="ctr", name="Untertitel")


# ================================ Folie 1 ====================================
s1 = Slide(bg=INK)
logo(s1, M, 0.55, 0.46, dark=True, tw=4.5)

s1.text(M, 1.75, 8.0, 0.35, [para(run("ON-PREMISE-LÖSUNG", 13, RED, b=True, spc=150))], anchor="ctr")
s1.text(M, 2.15, 10.5, 1.75,
        [para(run("Ihre Sitzungen verlassen", 46, WHITE, b=True), line=95),
         para(run("nie Ihr Haus.", 46, WHITE, b=True), line=95)], anchor="t")
s1.text(M, 3.95, 9.5, 0.95,
        [para(run("Transkription, Sprechererkennung und KI-Protokolle – "
                  "komplett auf Ihren eigenen Servern.", 20, SOFT_D), line=110)], anchor="t")

facts = [("100 % lokal", "Daten, Modelle und Speicher bleiben bei Ihnen"),
         ("Schweizerdeutsch", "Live-Transkription und Upload von Aufnahmen"),
         ("Ohne Internet", "Läuft auch in abgeschotteten Netzen")]
fw = (W - 2 * M - 2 * 0.3) / 3
for k, (big, small) in enumerate(facts):
    s1.shape(M + k * (fw + 0.3), 5.35, fw, 1.45, fill=CARD_D, geom="roundRect", radius=7000,
             inset=(0.3, 0.28, 0.3, 0.2), anchor="t", name="Fakt",
             paras=[para(run(big, 22, RED, b=True), after=4),
                    para(run(small, 14, SOFT_D), line=105)])

# ================================ Folie 2 ====================================
s2 = Slide(bg=WHITE)
header(s2, "So funktioniert's",
       "Eine Kopie der Suisse-Meets-Web-App plus KI-Modelle – alles bei Ihnen vor Ort.")

cw, gap, cy, ch = 2.45, 0.75, 2.4, 1.95
x0 = (W - (4 * cw + 3 * gap)) / 2
steps = [("1", "Aufnahme", "Browser und Konferenzmikrofon im Sitzungszimmer"),
         ("2", "Transkription", "Whisper, optimiert für Schweizerdeutsch"),
         ("3", "Sprecher", "pyannote erkennt, wer wann spricht"),
         ("4", "Protokoll", "Qwen3.8 schreibt Zusammenfassung und Pendenzen")]
xs = [x0 + k * (cw + gap) for k in range(4)]

# Rahmen „Ihr Rechenzentrum" um Schritte 2–4 + Speicher
fx0, fx1 = xs[1] - 0.2, xs[3] + cw + 0.2
s2.shape(fx0, 1.85, fx1 - fx0, 3.75, line=RED, line_w=1.5, dash="dash", geom="roundRect", radius=4000,
         name="Rahmen Rechenzentrum")
s2.text(fx0 + 0.25, 1.95, 5.0, 0.35,
        [para(run("BEI IHNEN VOR ORT  ·  MAC STUDIO", 12, RED, b=True, spc=150))], anchor="ctr")

for k, (n, title, desc) in enumerate(steps):
    s2.shape(xs[k], cy, cw, ch, fill=TINT, geom="roundRect", radius=7000, inset=(0.22, 0.2, 0.22, 0.2),
             anchor="t", name=f"Schritt {n}",
             paras=[para(run(n, 22, RED, b=True), after=2),
                    para(run(title, 18, TEXT, b=True), after=6),
                    para(run(desc, 13, MUTED), line=105)])
    if k < 3:
        ax = xs[k] + cw + (0.08 if k == 0 else 0.2)
        s2.shape(ax, cy + ch / 2 - 0.19, 0.36, 0.38, fill=ARROW, geom="rightArrow", name="Pfeil")

s2.shape(xs[1], 4.65, fx1 - 0.2 - xs[1], 0.68, fill=INK, geom="roundRect", radius=12000, anchor="ctr",
         inset=(0.2, 0.05, 0.2, 0.05), name="Speicher",
         paras=[para([run("Speicherung  ", 16, WHITE, b=True),
                      run("verschlüsselt, auf Ihrem eigenen NAS", 16, SOFT_D)], algn="ctr")])

bw = (W - 2 * M - 0.3) / 2
for k, (lab, txt, col) in enumerate([
        ("ENTHALTEN", "Web-App  ·  Live & Upload  ·  Protokolle  ·  SSO", RED),
        ("NICHT ENTHALTEN", "Teams-/Zoom-Bots  ·  Mediabot  ·  Mobile-/Desktop-Apps", MUTED)]):
    s2.shape(M + k * (bw + 0.3), 5.95, bw, 0.95, fill=TINT, geom="roundRect", radius=9000,
             inset=(0.3, 0.1, 0.3, 0.1), anchor="ctr", name=lab,
             paras=[para(run(lab, 11, col, b=True, spc=120), after=3),
                    para(run(txt, 14, TEXT))])

# ================================ Folie 3 ====================================
s3 = Slide(bg=WHITE)
header(s3, "Unsere Empfehlung: Mac Studio", "Einfach, leise und sofort einsatzbereit – kein Serverraum nötig.")

top, bot = 1.85, 6.3
# Komplettpaket (links)
px_, pw = M, 6.0
s3.shape(px_, top, pw, bot - top, fill=INK, geom="roundRect", radius=4000, name="Komplettpaket")
s3.shape(px_ + 0.4, top + 0.35, 1.95, 0.36, fill=RED, geom="roundRect", radius=50000, anchor="ctr",
         paras=[para(run("KOMPLETTPAKET", 11, WHITE, b=True, spc=120), algn="ctr")])
s3.text(px_ + 0.4, top + 0.85, pw - 0.8, 0.85, [para(run("CHF 55'000", 44, WHITE, b=True))], anchor="ctr")
s3.text(px_ + 0.4, top + 1.7, pw - 0.8, 0.35,
        [para(run("einmalig, inkl. Hardware, exkl. MWST", 14, MUTED_D))], anchor="ctr")
items = ["2 × Mac Studio M5 Ultra, 256 GB – redundant",
         "NAS-Speicher mit Backup und USV",
         "Konferenzmikrofone für 5 Sitzungszimmer",
         "Installation, Integration und Schulung",
         "Suisse Meets Lizenz und Support im 1. Jahr"]
s3.text(px_ + 0.4, top + 2.3, pw - 0.8, 1.95,
        [para(run(t, 15, WHITE), after=6, bullet="•", bullet_color=RED, indent=0.24) for t in items])

# Warum Mac Studio (rechts)
rx = px_ + pw + 0.45
rw = W - M - rx
s3.text(rx, top, rw, 0.3, [para(run("WARUM MAC STUDIO?", 12, RED, b=True, spc=150))], anchor="ctr")
reasons = [("Einfach", "Plug & Play – kein Serverraum, kein Rack, keine Spezialkühlung."),
           ("Leise und sparsam", "Steht im Büro und braucht nur einen Bruchteil des Stroms eines GPU-Servers."),
           ("Ausfallsicher", "Zwei Geräte teilen sich die Last. Fällt eines aus, übernimmt das andere.")]
for k, (t, d) in enumerate(reasons):
    y = top + 0.45 + k * 0.95
    num_y = y + 0.05
    s3.shape(rx, num_y, 0.46, 0.46, fill=RED, geom="ellipse", anchor="ctr",
             paras=[para(run(str(k + 1), 15, WHITE, b=True), algn="ctr")])
    s3.text(rx + 0.65, y, rw - 0.65, 0.85,
            [para(run(t, 17, TEXT, b=True), after=2), para(run(d, 13.5, MUTED), line=105)])

tw3 = (rw - 2 * 0.2) / 3
for k, (big, small) in enumerate([("~100", "Nutzer"), ("~8", "parallele Sitzungen"), ("4–6", "Wochen bis Go-live")]):
    s3.shape(rx + k * (tw3 + 0.2), bot - 1.0, tw3, 1.0, fill=TINT, geom="roundRect", radius=9000,
             inset=(0.1, 0.08, 0.1, 0.08), anchor="ctr",
             paras=[para(run(big, 24, RED, b=True), algn="ctr", after=1),
                    para(run(small, 11.5, MUTED), algn="ctr")])

s3.text(M, 6.55, W - 2 * M, 0.55,
        [para(run("Richtpreis Stand September 2026. Kapazitäten sind Schätzungen und werden im Abnahmetest "
                  "bestätigt. Für Organisationen ab ca. 300 Nutzern: GPU-Server-Variante auf Anfrage.",
                  10.5, MUTED), line=105)], anchor="ctr")

out = sys.argv[1] if len(sys.argv) > 1 else "Suisse_Meets_OnPrem_DE.pptx"
write_pptx(out, [s1, s2, s3],
           dict(name="Suisse Meets", dk1=TEXT, dk2=INK, lt2=TINT,
                accents=[RED, "5B6470", "0F1115", "A3ABB6", "8C1C13", "D3D8DF"]),
           title="Suisse Meets On-Premise", author="Suisse Meets")
print("wrote", out)

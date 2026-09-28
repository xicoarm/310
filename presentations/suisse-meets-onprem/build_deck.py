"""Suisse Meets On-Premise — 3-slide proposal deck (16:9, 13.333 x 7.5 in)."""
import sys
from ooxml import Slide, para, run, write_pptx

# ---- Brand tokens (swap these for the official Suisse Meets values) --------
RED = "D52B1E"        # Swiss red accent
INK = "0F1115"        # dominant dark
CARD_D = "1A1E25"     # card on dark
CARD_D2 = "252A33"    # nested card on dark
LINE_D = "343B46"
MUTED_D = "A3ABB6"
SOFT_D = "D3D8DF"
TEXT = "1F2328"
BODY = "3A414B"
MUTED = "5B6470"
TINT = "F3F4F6"
WHITE = "FFFFFF"

W, H, M = 13.333, 7.5, 0.6


def logo(s, x, y, size, dark, tw=4.2):
    """Placeholder mark: red rounded square with white Swiss cross + wordmark."""
    s.shape(x, y, size, size, fill=RED, geom="roundRect", radius=18000, name="Logo mark")
    bar, arm = size * 0.2, size * 0.62
    s.shape(x + (size - bar) / 2, y + (size - arm) / 2, bar, arm, fill=WHITE, name="Logo cross")
    s.shape(x + (size - arm) / 2, y + (size - bar) / 2, arm, bar, fill=WHITE, name="Logo cross")
    fs = size * 40
    s.text(x + size + 0.14, y - 0.05, tw, size + 0.1,
           [para([run("Suisse Meets", fs, WHITE if dark else TEXT, b=True),
                  run("  On-Premise", fs, MUTED_D if dark else MUTED)])],
           anchor="ctr", name="Wordmark")


def header(s, title, subtitle):
    logo(s, W - M - 2.75, 0.5, 0.3, dark=False, tw=2.31)
    s.text(M, 0.42, 8.8, 0.62, [para(run(title, 30, TEXT, b=True))], anchor="t", name="Title")
    s.text(M, 1.04, 11.0, 0.4, [para(run(subtitle, 14, MUTED))], name="Subtitle")


def label(s, x, y, w, text, color=RED):
    s.text(x, y, w, 0.26, [para(run(text, 10, color, b=True, spc=120))], name="Label")


def num_badge(s, x, y, n, d=0.36, fill=RED, color=WHITE):
    s.shape(x, y, d, d, fill=fill, geom="ellipse",
            paras=[para(run(str(n), 12, color, b=True), algn="ctr")], anchor="ctr", name="Badge")


# ============================ Slide 1 ======================================
s1 = Slide(bg=INK)
logo(s1, M, 0.5, 0.44, dark=True)
s1.text(W - M - 4.5, 0.5, 4.5, 0.44,
        [para(run("Solution proposal  ·  September 2026", 11, MUTED_D), algn="r")], anchor="ctr")

LW = 6.0
label(s1, M, 1.5, LW, "ON-PREMISE EDITION")
s1.text(M, 1.82, LW, 1.7,
        [para(run("Meeting intelligence that never leaves your building.", 36, WHITE, b=True), line=92)])
s1.text(M, 3.62, LW - 0.2, 1.1,
        [para(run("The Suisse Meets web app, Swiss-German transcription, speaker recognition and "
                  "AI minutes — installed on your own servers. No cloud. No internet connection required.",
                  15, SOFT_D), line=110)])

# scope cards
cw, cy, ch = 2.95, 4.85, 2.05
for i, (head, items, col) in enumerate([
    ("In scope", ["In-person meetings: live + upload", "Swiss German + 50+ languages",
                  "Speaker recognition", "Summaries, minutes, action items",
                  "SSO, 100 % on-prem storage"], RED),
    ("Out of scope", ["Teams / Zoom / Meet bots", "Media bot", "Mobile and desktop apps",
                      "Any cloud or third-party API"], MUTED_D),
]):
    x = M + i * (cw + 0.2)
    s1.shape(x, cy, cw, ch, fill=CARD_D, geom="roundRect", radius=6000, name="Scope card")
    ps = [para(run(head, 12, WHITE, b=True), after=5)]
    ps += [para(run(t, 10.5, SOFT_D), after=3, bullet="•" if i == 0 else "–", bullet_color=col, indent=0.16)
           for t in items]
    s1.text(x + 0.22, cy + 0.18, cw - 0.4, ch - 0.3, ps)

# architecture diagram (right)
DX, DW = 7.0, W - M - 7.0
cx = DX + DW / 2
s1.shape(DX, 1.5, DW, 0.9, fill=CARD_D, line=LINE_D, geom="roundRect", radius=8000,
         inset=(0.22, 0.1, 0.2, 0.1), anchor="ctr",
         paras=[para(run("MEETING ROOM", 10, RED, b=True, spc=120), after=2),
                para(run("Browser on a laptop or room PC  +  USB conference microphone", 12, WHITE))])
s1.arrow(cx, 2.4, cx, 2.84, color=MUTED_D, w=1.75)
s1.text(cx + 0.15, 2.46, 2.6, 0.3, [para(run("HTTPS · internal network only", 10, MUTED_D))], anchor="ctr")

s1.shape(DX, 2.88, DW, 4.02, line=RED, line_w=1.25, dash="dash", geom="roundRect", radius=3500,
         name="Data centre boundary")
label(s1, DX + 0.25, 3.02, DW - 0.5, "YOUR DATA CENTRE  —  NO INTERNET REQUIRED")
IX, IW = DX + 0.25, DW - 0.5
icx = IX + IW / 2
s1.shape(IX, 3.36, IW, 0.72, fill=CARD_D, geom="roundRect", radius=9000, inset=(0.2, 0.06, 0.2, 0.06),
         anchor="ctr",
         paras=[para([run("Suisse Meets Web", 13, WHITE, b=True),
                      run("   same web app as the cloud, self-hosted", 11, MUTED_D)])])
s1.arrow(icx, 4.08, icx, 4.3, color=MUTED_D, w=1.5)

s1.shape(IX, 4.3, IW, 1.5, fill=CARD_D2, geom="roundRect", radius=6000, name="AI appliance")
s1.text(IX + 0.2, 4.4, IW - 0.4, 0.28,
        [para(run("AI APPLIANCE  ·  1 GPU SERVER, ALL INFERENCE LOCAL", 10, MUTED_D, b=True, spc=80))], anchor="ctr")
gap = 0.12
chip_w = (IW - 0.4 - 2 * gap) / 3
for k, (name, role) in enumerate([("Whisper", "Transcription"), ("pyannote", "Speaker diarization"),
                                  ("Qwen3.8-27B", "Summaries & minutes")]):
    x = IX + 0.2 + k * (chip_w + gap)
    s1.shape(x, 4.8, chip_w, 0.86, fill=LINE_D, geom="roundRect", radius=9000, anchor="ctr",
             inset=(0.08, 0.04, 0.08, 0.04),
             paras=[para([run(f"{k + 1}  ", 12, RED, b=True), run(name, 12, WHITE, b=True)], algn="ctr", after=2),
                    para(run(role, 10, SOFT_D), algn="ctr")])
s1.arrow(icx, 5.8, icx, 6.02, color=MUTED_D, w=1.5)
s1.shape(IX, 6.02, IW, 0.72, fill=CARD_D, geom="roundRect", radius=9000, inset=(0.2, 0.06, 0.2, 0.06),
         anchor="ctr",
         paras=[para([run("On-prem storage", 13, WHITE, b=True),
                      run("   encrypted, on your own SAN / NAS", 11, MUTED_D)])])

# ============================ Slide 2 ======================================
s2 = Slide(bg=WHITE)
header(s2, "AI stack & recommended hardware",
       "Open, commercially usable models — the full pipeline runs locally on a single GPU server.")

label(s2, M, 1.55, 4, "MODELS")
cw = (W - 2 * M - 2 * 0.3) / 3
models = [
    ("TRANSCRIPTION", "Whisper large-v3-turbo",
     "Swiss-German fine-tune → Standard German text, plus 50+ languages. Live and batch via faster-whisper. ≈ 6 GB VRAM."),
    ("SPEAKER DIARIZATION", "pyannote community-1",
     "Who spoke when, with no fixed speaker limit. Fully self-hosted, no API calls. ≈ 2 GB VRAM, 1–2 min per audio hour."),
    ("SUMMARIES & MINUTES", "Qwen3.8-27B (FP8)",
     "Minutes, action items, Q&A on transcripts. Apache 2.0, 262k context, strong German. Served by vLLM, ≈ 28 GB + cache."),
]
for k, (lab, name, desc) in enumerate(models):
    x = M + k * (cw + 0.3)
    y = 1.85
    s2.shape(x, y, cw, 1.6, fill=TINT, geom="roundRect", radius=5000)
    num_badge(s2, x + 0.22, y + 0.22, k + 1, d=0.4)
    s2.text(x + 0.76, y + 0.16, cw - 0.9, 0.56,
            [para(run(lab, 9.5, MUTED, b=True, spc=100), after=1), para(run(name, 14, TEXT, b=True))], anchor="ctr")
    s2.text(x + 0.22, y + 0.82, cw - 0.44, 0.7, [para(run(desc, 11, BODY), line=105)])

label(s2, M, 3.68, 4, "HARDWARE OPTIONS")
tiers = [
    dict(tag="COMPACT", name="Mac Studio M5 Ultra", spec="96 GB unified memory · 2 TB SSD · quiet desktop unit",
         pts=["Up to ~30 users, 2–3 parallel live sessions", "Plug & play, very low power draw",
              "No ECC, no remote management, single PSU → pilots, practices, law firms"],
         price="≈ CHF 6–8k", dark=False),
    dict(tag="RECOMMENDED", name="2U GPU server + RTX PRO 6000",
         spec="NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB · Dell R760xa, HPE DL380a or Supermicro",
         pts=["50–300 users, ~15 parallel live sessions", "1-hour meeting → finished minutes in ~3 min",
              "ECC, iDRAC/iLO, redundant PSUs, 5-year on-site support"],
         price="≈ CHF 25–40k", dark=True),
    dict(tag="ENTERPRISE HA", name="2 GPU servers, active/active",
         spec="Each with 2 × RTX PRO 6000 · load-balanced, no single point of failure",
         pts=["300–1,500 users, 40+ parallel live sessions", "Headroom for larger LLMs (100B+ class)",
              "Rolling updates without downtime"],
         price="≈ CHF 90–130k", dark=False),
]
ty, th = 3.98, 2.72
for k, t in enumerate(tiers):
    x = M + k * (cw + 0.3)
    dk = t["dark"]
    s2.shape(x, ty, cw, th, fill=INK if dk else TINT, geom="roundRect", radius=4000)
    ix, iw = x + 0.25, cw - 0.5
    if dk:
        s2.shape(ix, ty + 0.2, 1.35, 0.27, fill=RED, geom="roundRect", radius=50000,
                 paras=[para(run(t["tag"], 9, WHITE, b=True, spc=100), algn="ctr")], anchor="ctr")
    else:
        s2.text(ix, ty + 0.2, iw, 0.27, [para(run(t["tag"], 9.5, MUTED, b=True, spc=100))], anchor="ctr")
    s2.text(ix, ty + 0.54, iw, 0.36, [para(run(t["name"], 15, WHITE if dk else TEXT, b=True))], anchor="ctr")
    s2.text(ix, ty + 0.92, iw, 0.42, [para(run(t["spec"], 10, MUTED_D if dk else MUTED), line=100)])
    s2.text(ix, ty + 1.4, iw, 0.9,
            [para(run(p, 11, SOFT_D if dk else BODY), after=3, bullet="•", bullet_color=RED, indent=0.16)
             for p in t["pts"]])
    s2.text(ix, ty + th - 0.46, iw, 0.34,
            [para([run(t["price"], 16, WHITE if dk else TEXT, b=True),
                   run("   hardware, indicative", 9.5, MUTED_D if dk else MUTED)])], anchor="ctr")

s2.text(M, 6.8, W - 2 * M, 0.45,
        [para([run("Evaluated, not recommended for production: ", 9.5, MUTED, b=True),
               run("NVIDIA DGX Spark — 128 GB memory, but 273 GB/s bandwidth makes text generation ~6–7× slower "
                   "than an RTX PRO 6000. Prices: hardware only, excl. VAT and Suisse Meets licence, Sept 2026; "
                   "GPU street prices are volatile due to the 2026 memory shortage.", 9.5, MUTED)], line=105)])

# ============================ Slide 3 ======================================
s3 = Slide(bg=WHITE)
header(s3, "Sizing, rollout & operations",
       "Figures for the recommended 1-GPU server. From order to go-live in about 6–8 weeks, driven mainly by GPU lead time.")

top, bot = 1.62, 6.7
# stats panel
sx, sw = M, 3.3
s3.shape(sx, top, sw, bot - top, fill=INK, geom="roundRect", radius=4000)
label(s3, sx + 0.3, top + 0.25, sw - 0.6, "CAPACITY (ESTIMATED)")
stats = [("~15", "parallel live transcriptions on one GPU, while summaries run"),
         ("≈ 3 min", "from the end of a 1-hour meeting to finished, speaker-labelled minutes"),
         ("< 0.5 TB", "storage per year for 200 users (compressed audio + text)")]
for k, (big, small) in enumerate(stats):
    y = top + 0.62 + k * 1.5
    s3.text(sx + 0.3, y, sw - 0.6, 0.7, [para(run(big, 40, RED, b=True))], anchor="b")
    s3.text(sx + 0.3, y + 0.74, sw - 0.6, 0.6, [para(run(small, 11.5, SOFT_D), line=105)])

# rollout timeline
rx, rw = sx + sw + 0.45, 4.25
label(s3, rx, top, rw, "ROLLOUT")
steps = [("Scope & order", "WEEK 1", "Users, rooms, retention rules, SSO. Order hardware (GPU lead time 4–8 weeks)."),
         ("Install", "ON DELIVERY", "Rack the server, install the signed offline bundle (Docker / k3s), internal TLS certificate."),
         ("Integrate & test", "+1 WEEK", "SSO (Entra ID, ADFS, LDAP), storage, backup, SIEM logging. Acceptance test with real Swiss-German meetings."),
         ("Pilot → go-live", "+2–4 WEEKS", "Pilot group, room-microphone check, short training, then roll-out to all users.")]
sy0, step_h, d = top + 0.4, 1.17, 0.4
s3.shape(rx + d / 2 - 0.01, sy0 + d, 0.02, step_h * 3 - d / 2 + 0.05, fill="D5D9DF", name="Timeline")
for k, (t, when, desc) in enumerate(steps):
    y = sy0 + k * step_h
    num_badge(s3, rx, y, k + 1, d=d)
    s3.text(rx + 0.6, y - 0.02, rw - 0.6, 0.44,
            [para([run(t, 13, TEXT, b=True), run("   " + when, 9.5, RED, b=True, spc=80)])], anchor="ctr")
    s3.text(rx + 0.6, y + 0.42, rw - 0.6, 0.7, [para(run(desc, 11, BODY), line=105)])

# operations & security
ox = rx + rw + 0.45
ow = W - M - ox
s3.shape(ox, top, ow, bot - top, fill=TINT, geom="roundRect", radius=4000)
label(s3, ox + 0.3, top + 0.25, ow - 0.6, "OPERATIONS & SECURITY")
ops = [("Air-gap capable. ", "No outbound internet; updates ship as signed offline bundles (quarterly + security fixes)."),
       ("Your storage, your rules. ", "Recordings, transcripts and summaries stay on your SAN/NAS, with configurable retention and deletion."),
       ("Encrypted. ", "AES-256 at rest, TLS 1.3 in transit, role-based access and audit log."),
       ("Support on your terms. ", "Remote access only via your VPN and only on request; SLA options."),
       ("Room audio matters. ", "One USB conference mic per room (e.g. Jabra Speak2 75) is the biggest lever for accuracy.")]
s3.text(ox + 0.3, top + 0.62, ow - 0.6, bot - top - 0.8,
        [para([run(a, 12, TEXT, b=True), run(b, 12, BODY)], after=10, line=105,
              bullet="•", bullet_color=RED, indent=0.18) for a, b in ops])

s3.text(M, 6.82, W - 2 * M, 0.4,
        [para(run("Assumptions: ≤ 15 concurrent meetings, ~10 h of recorded meetings per user per month, audio stored as "
                  "Opus at 32 kbit/s. Throughput figures are engineering estimates, to be confirmed in the acceptance test.",
                  9.5, MUTED), line=105)])

out = sys.argv[1] if len(sys.argv) > 1 else "Suisse_Meets_OnPrem.pptx"
write_pptx(out, [s1, s2, s3],
           dict(name="Suisse Meets", dk1=TEXT, dk2=INK, lt2=TINT,
                accents=[RED, "5B6470", "0F1115", "A3ABB6", "8C1C13", "D3D8DF"]),
           title="Suisse Meets On-Premise", author="Suisse Meets")
print("wrote", out)

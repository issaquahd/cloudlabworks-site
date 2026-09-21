#!/usr/bin/env python3
"""The agents set: six chibi characters, anime-flavoured, one per member of the roster.
Waku the orca and the Salish Sea five: Heron (scout), Raven (courier, the only one with keys),
Salmon (scribe), Osprey (watch), Cormorant (reviewer). Big heads, bigger eyes, one prop each that
says the job. Hand-written SVG, 1024 square, pastel field, name in katakana and romaji at the
foot. Rendered with headless Chrome (text), then watermarked. Run: python3 gen.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1f2a33"; CREAM = "#fbf7ef"; RED = "#d94a3d"; TEAL = "#3f6e6a"; GOLD = "#e0a52a"

def field(colour, sparkle):
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".7"/>' for x, y, r in sparkle)
    stars = "".join(f'<path d="M{x} {y-14} l4 10 l10 4 l-10 4 l-4 10 l-4 -10 l-10 -4 l10 -4z" fill="#fff" opacity=".9"/>' for x, y, _ in sparkle[:3])
    return f'<rect width="1024" height="1024" fill="{CREAM}"/><circle cx="512" cy="470" r="400" fill="{colour}"/>{dots}{stars}'

def eyes(cx, cy, gap, r, iris, look=(0, 0), wink=False):
    out = []
    for i, x in enumerate((cx - gap, cx + gap)):
        if wink and i == 1:
            out.append(f'<path d="M{x-r*.9:.0f} {cy:.0f} q{r*.9:.0f} {r*.8:.0f} {r*1.8:.0f} 0" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>')
            continue
        out.append(f'<ellipse cx="{x}" cy="{cy}" rx="{r}" ry="{r*1.15:.0f}" fill="#fff" stroke="{INK}" stroke-width="8"/>')
        out.append(f'<ellipse cx="{x+look[0]}" cy="{cy+8+look[1]}" rx="{r*.62:.0f}" ry="{r*.78:.0f}" fill="{iris}"/>')
        out.append(f'<ellipse cx="{x+look[0]}" cy="{cy+18+look[1]}" rx="{r*.42:.0f}" ry="{r*.5:.0f}" fill="{INK}"/>')
        out.append(f'<circle cx="{x-r*.25+look[0]:.0f}" cy="{cy-r*.25+look[1]:.0f}" r="{r*.26:.0f}" fill="#fff"/><circle cx="{x+r*.3+look[0]:.0f}" cy="{cy+r*.35+look[1]:.0f}" r="{r*.12:.0f}" fill="#fff"/>')
    return "".join(out)

def blush(cx, cy, gap): return f'<ellipse cx="{cx-gap}" cy="{cy}" rx="34" ry="18" fill="#f4a1a8" opacity=".8"/><ellipse cx="{cx+gap}" cy="{cy}" rx="34" ry="18" fill="#f4a1a8" opacity=".8"/>'
def mouth(cx, cy, w=40, open_=False):
    if open_: return f'<path d="M{cx-w} {cy} q{w} {w*1.6:.0f} {w*2} 0z" fill="{INK}"/><path d="M{cx-w*.5:.0f} {cy+w*.55:.0f} q{w*.5:.0f} {w*.5:.0f} {w} 0z" fill="#f28a9a"/>'
    return f'<path d="M{cx-w} {cy} q{w} {w*.9:.0f} {w*2} 0" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
def caption(kana, romaji, role):
    return (f'<text x="512" y="940" text-anchor="middle" font-family="Hiragino Sans, Hiragino Kaku Gothic ProN, Noto Sans JP, sans-serif" font-size="64" font-weight="700" fill="{INK}">{kana}</text>'
            f'<text x="512" y="998" text-anchor="middle" font-family="Futura, Avenir Next, Helvetica Neue, sans-serif" font-size="30" letter-spacing="6" fill="{INK}" opacity=".8">{romaji} · {role}</text>')
def shadow(): return '<ellipse cx="512" cy="880" rx="230" ry="26" fill="#000" opacity=".12"/>'

CHARS = []
def char(name, kana, romaji, role, title, text):
    def deco(f): CHARS.append(dict(name=name, kana=kana, romaji=romaji, role=role, title=title, text=text, draw=f)); return f
    return deco

@char("waku", "ワク", "WAKU", "the orchestrator", "Waku", "The orca who runs the lab: headset on, wrench cross on the chest, one eyebrow always slightly up. The one voice Alex talks to.")
def _():
    s = field("#cfe6e4", [(180, 200, 6), (840, 180, 5), (860, 640, 7), (150, 620, 4), (700, 800, 5)]) + shadow()
    # body (small) and tail
    s += f'<path d="M420 700 q92 -60 184 0 q30 100 -92 130 q-122 -30 -92 -130z" fill="{INK}"/><path d="M470 760 q42 -30 84 0 q0 60 -42 62 q-42 -2 -42 -62z" fill="#fff"/>'
    s += f'<path d="M600 780 q60 -20 80 20 q-30 6 -50 -4 q-6 24 -30 26z" fill="{INK}"/>'
    # head: black with white face patch, eye patches
    s += f'<circle cx="512" cy="470" r="250" fill="{INK}"/>'
    s += f'<path d="M512 240 q-40 -110 -20 -160 q70 60 80 160z" fill="{INK}"/>'  # dorsal fin
    s += f'<path d="M300 520 q60 190 212 190 q152 0 212 -190 q-60 -60 -212 -60 q-152 0 -212 60z" fill="#fff"/>'
    s += f'<ellipse cx="392" cy="360" rx="56" ry="70" fill="#fff" transform="rotate(-20 392 360)"/><ellipse cx="632" cy="360" rx="56" ry="70" fill="#fff" transform="rotate(20 632 360)"/>'
    s += eyes(512, 470, 110, 62, "#2f5f8f", look=(6, 0))
    s += blush(512, 560, 150) + mouth(512, 600, 44)
    # headset
    s += f'<path d="M270 440 q0 -220 242 -220 q242 0 242 220" fill="none" stroke="{TEAL}" stroke-width="18" stroke-linecap="round"/><rect x="244" y="420" width="52" height="90" rx="20" fill="{TEAL}"/><rect x="728" y="420" width="52" height="90" rx="20" fill="{TEAL}"/><path d="M280 510 q-30 90 60 120" fill="none" stroke="{TEAL}" stroke-width="14" stroke-linecap="round"/><circle cx="352" cy="636" r="16" fill="{RED}"/>'
    # wrench cross badge on the chest
    s += f'<g transform="translate(512 770) scale(.55)"><path d="M-40 -40 l80 80 M40 -40 l-80 80" stroke="{CREAM}" stroke-width="14" stroke-linecap="round"/><circle cx="-40" cy="-40" r="16" fill="none" stroke="{CREAM}" stroke-width="10"/><circle cx="40" cy="-40" r="16" fill="none" stroke="{CREAM}" stroke-width="10"/></g>'
    return s + caption("ワク", "WAKU", "orchestrator")

@char("heron", "ヘロン", "HERON", "scout", "Heron, the scout", "Long legs, longer beak, a brass spyglass and a scarf for the wind. Goes out, looks, comes back with the source and the date. Never with a key.")
def _():
    s = field("#dfe8f2", [(200, 220, 6), (830, 200, 5), (870, 620, 6), (170, 640, 4), (680, 820, 5)]) + shadow()
    # legs
    s += f'<path d="M470 720 v150 M554 720 v150 M440 870 h60 M524 870 h60" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round"/>'
    s += f'<ellipse cx="512" cy="700" rx="120" ry="90" fill="#8fa8bf"/><path d="M420 690 q90 -40 180 0 q-10 70 -90 80 q-80 -10 -90 -80z" fill="#c9d7e4"/>'
    s += f'<circle cx="512" cy="450" r="240" fill="#9fb6cc"/><path d="M340 500 q40 160 172 160 q132 0 172 -160 q-60 -50 -172 -50 q-112 0 -172 50z" fill="#e8eef5"/>'
    s += f'<path d="M560 210 q120 -90 190 -60 q-80 30 -110 90z" fill="{INK}"/>'  # plume
    s += eyes(512, 450, 100, 58, "#4a6f8f", look=(-4, 0))
    s += blush(512, 540, 140)
    s += f'<path d="M512 540 l150 40 l-150 40 z" fill="{GOLD}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M512 580 l150 0" stroke="{INK}" stroke-width="4"/>'  # beak
    # scarf
    s += f'<path d="M400 660 q112 60 224 0 v40 q-112 60 -224 0z" fill="{RED}"/><path d="M600 690 q40 60 20 120 q-30 -40 -60 -60z" fill="{RED}"/>'
    # spyglass held up to the right
    s += f'<g transform="rotate(-30 700 520)"><rect x="700" y="500" width="150" height="44" rx="10" fill="#b5872f" stroke="{INK}" stroke-width="6"/><rect x="840" y="492" width="60" height="60" rx="10" fill="#8a6520" stroke="{INK}" stroke-width="6"/><rect x="660" y="506" width="50" height="32" rx="8" fill="#8a6520" stroke="{INK}" stroke-width="6"/></g>'
    s += f'<path d="M620 650 q60 -40 90 -90" fill="none" stroke="#9fb6cc" stroke-width="26" stroke-linecap="round"/>'
    return s + caption("ヘロン", "HERON", "scout")

@char("raven", "レイヴン", "RAVEN", "courier", "Raven, the courier", "Glossy black with a violet sheen, a satchel with the red seal, and the only key ring in the lab. Runs the fixed script, reports the HTTP code, hands the key back.")
def _():
    s = field("#e3d9ee", [(190, 210, 6), (840, 190, 5), (850, 650, 6), (160, 640, 4), (690, 810, 5)]) + shadow()
    s += f'<ellipse cx="512" cy="700" rx="130" ry="95" fill="{INK}"/><path d="M430 680 q82 -30 164 0 q-6 60 -82 70 q-76 -10 -82 -70z" fill="#4b3d66"/>'
    s += f'<circle cx="512" cy="450" r="245" fill="{INK}"/><path d="M330 400 q60 -130 182 -130 q122 0 182 130 q-100 -40 -182 -40 q-82 0 -182 40z" fill="#4b3d66" opacity=".8"/>'
    s += f'<path d="M420 230 q20 -70 60 -60 q-10 40 10 60z M520 215 q30 -70 70 -50 q-30 30 -20 60z" fill="{INK}"/>'  # ruffled crown
    s += eyes(512, 450, 100, 60, "#7a4fb3", look=(0, 4), wink=True)
    s += blush(512, 545, 140)
    s += f'<path d="M512 535 l140 30 l-140 30 z" fill="#5a5a66" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'  # beak
    # satchel with red seal
    s += f'<path d="M380 640 q-40 20 -30 80" fill="none" stroke="#7a5230" stroke-width="12"/><rect x="330" y="700" width="120" height="96" rx="14" fill="#8a5a32" stroke="{INK}" stroke-width="6"/><rect x="330" y="700" width="120" height="40" rx="14" fill="#a56d3c" stroke="{INK}" stroke-width="6"/><circle cx="390" cy="760" r="16" fill="{RED}"/>'
    # key ring
    s += f'<circle cx="680" cy="720" r="34" fill="none" stroke="{GOLD}" stroke-width="12"/><g transform="rotate(25 680 720)"><rect x="700" y="712" width="80" height="16" rx="6" fill="{GOLD}"/><rect x="760" y="724" width="12" height="18" fill="{GOLD}"/><rect x="740" y="724" width="12" height="14" fill="{GOLD}"/></g><g transform="rotate(-40 680 720)"><rect x="700" y="712" width="70" height="16" rx="6" fill="{GOLD}"/><rect x="752" y="724" width="12" height="16" fill="{GOLD}"/></g>'
    s += f'<path d="M600 660 q60 20 80 60" fill="none" stroke="{INK}" stroke-width="26" stroke-linecap="round"/>'
    return s + caption("レイヴン", "RAVEN", "courier")

@char("salmon", "サーモン", "SALMON", "scribe", "Salmon, the scribe", "Pink, round, a brush in one fin and a scroll in the other, ink on the cheek. Folds the days into memory and never invents a word of it.")
def _():
    s = field("#fbe0d8", [(200, 200, 6), (830, 210, 5), (860, 630, 6), (160, 650, 4), (700, 810, 5)]) + shadow()
    s += f'<path d="M420 720 q92 -40 184 0 q20 80 -92 110 q-112 -30 -92 -110z" fill="#f28c7e"/>'
    s += f'<path d="M600 780 q70 -50 110 10 q-50 0 -70 30 q-10 -30 -40 -40z" fill="#f28c7e" stroke="{INK}" stroke-width="5"/>'  # tail
    s += f'<circle cx="512" cy="460" r="248" fill="#f6a094"/><path d="M330 520 q50 170 182 170 q132 0 182 -170 q-70 -60 -182 -60 q-112 0 -182 60z" fill="#fde3d6"/>'
    s += f'<path d="M512 212 q-30 -70 0 -110 q30 40 0 110z" fill="#e0776b"/>'  # dorsal fin
    for x, y in ((360, 320), (420, 280), (600, 280), (660, 320), (512, 250)): s += f'<circle cx="{x}" cy="{y}" r="10" fill="#e0776b"/>'
    s += eyes(512, 460, 105, 62, "#c2513f", look=(0, 2))
    s += blush(512, 550, 145)
    s += f'<ellipse cx="512" cy="605" rx="40" ry="22" fill="#e07a7a" stroke="{INK}" stroke-width="7"/><path d="M482 605 q30 -18 60 0" fill="none" stroke="{INK}" stroke-width="5"/>'  # fish lips
    s += f'<circle cx="640" cy="590" r="7" fill="{INK}"/><circle cx="656" cy="604" r="4" fill="{INK}"/>'  # ink spots
    # brush (right) and scroll (left)
    s += f'<g transform="rotate(20 700 640)"><rect x="690" y="500" width="22" height="200" rx="8" fill="#8a5a32" stroke="{INK}" stroke-width="5"/><path d="M690 700 q11 50 22 0 q-11 60 -11 80 q0 -20 -11 -80z" fill="{INK}"/></g>'
    s += f'<rect x="290" y="620" width="120" height="150" rx="10" fill="{CREAM}" stroke="{INK}" stroke-width="6"/><rect x="280" y="610" width="140" height="22" rx="11" fill="#c9a06a" stroke="{INK}" stroke-width="5"/><rect x="280" y="760" width="140" height="22" rx="11" fill="#c9a06a" stroke="{INK}" stroke-width="5"/><path d="M320 660 h60 M320 690 h60 M320 720 h40" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    return s + caption("サーモン", "SALMON", "scribe")

@char("osprey", "オスプレイ", "OSPREY", "watch", "Osprey, the watch", "The masked one with the binoculars and the lantern. Runs the night checks, says nothing when all is well, and says it loudly when it is not.")
def _():
    s = field("#e6e2d3", [(200, 210, 6), (840, 200, 5), (860, 640, 6), (150, 640, 4), (700, 815, 5)]) + shadow()
    s += f'<path d="M470 730 v130 M554 730 v130 M440 860 l30 -10 l30 10 M524 860 l30 -10 l30 10" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<ellipse cx="512" cy="700" rx="130" ry="95" fill="#6b4f36"/><ellipse cx="512" cy="740" rx="70" ry="50" fill="#f2ede3"/>'
    s += f'<circle cx="512" cy="450" r="245" fill="#f2ede3"/><path d="M290 420 q80 -170 222 -170 q142 0 222 170 q-100 -60 -222 -60 q-122 0 -222 60z" fill="#6b4f36"/>'
    s += f'<path d="M280 440 q232 -60 464 0 q-40 60 -232 60 q-192 0 -232 -60z" fill="#4a3624" opacity=".85"/>'  # mask stripe
    s += eyes(512, 455, 100, 56, "#d9a22a", look=(0, -2))
    s += blush(512, 545, 140)
    s += f'<path d="M512 545 q40 0 60 30 q-30 20 -60 10 q-30 10 -60 -10 q20 -30 60 -30z" fill="{INK}"/>'  # hooked beak
    # binoculars held up
    s += f'<g transform="translate(600 600)"><rect x="0" y="0" width="60" height="80" rx="14" fill="{INK}"/><rect x="70" y="0" width="60" height="80" rx="14" fill="{INK}"/><rect x="48" y="24" width="34" height="30" rx="6" fill="{INK}"/><circle cx="30" cy="70" r="20" fill="#3f6e8f" stroke="{INK}" stroke-width="6"/><circle cx="100" cy="70" r="20" fill="#3f6e8f" stroke="{INK}" stroke-width="6"/></g>'
    # lantern
    s += f'<path d="M330 600 v40" stroke="{INK}" stroke-width="8"/><rect x="290" y="640" width="80" height="110" rx="12" fill="#fff2b0" stroke="{INK}" stroke-width="7"/><rect x="284" y="632" width="92" height="16" rx="6" fill="{INK}"/><rect x="284" y="742" width="92" height="16" rx="6" fill="{INK}"/><path d="M330 665 q-18 40 0 60 q18 -20 0 -60z" fill="{GOLD}"/>'
    return s + caption("オスプレイ", "OSPREY", "watch")

@char("cormorant", "コーモラント", "CORMORANT", "reviewer", "Cormorant, the reviewer", "Dark green, yellow face, a magnifying glass and a clipboard with exactly two ticks. The second confirmation before anything is called live.")
def _():
    s = field("#d9e8dc", [(190, 200, 6), (840, 190, 5), (860, 640, 6), (160, 640, 4), (690, 820, 5)]) + shadow()
    s += f'<ellipse cx="512" cy="705" rx="130" ry="95" fill="#1e3d34"/><path d="M430 690 q82 -30 164 0 q-6 60 -82 70 q-76 -10 -82 -70z" fill="#2f5a4a"/>'
    s += f'<circle cx="512" cy="455" r="245" fill="#1e3d34"/><path d="M340 505 q50 160 172 160 q122 0 172 -160 q-60 -50 -172 -50 q-112 0 -172 50z" fill="#e8c95a"/>'
    s += f'<path d="M470 230 q20 -50 50 -40 q-10 30 0 50z" fill="#1e3d34"/>'
    s += eyes(512, 455, 100, 58, "#2f7f6f", look=(4, 0))
    s += blush(512, 545, 140)
    s += f'<path d="M512 540 l140 34 q-40 30 -80 20 l-60 -14z" fill="#6b6b6b" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'  # hooked beak
    # magnifying glass (right)
    s += f'<g transform="rotate(-20 690 600)"><circle cx="690" cy="600" r="58" fill="#cfe9f2" stroke="{INK}" stroke-width="10" opacity=".95"/><path d="M670 580 q10 -14 30 -12" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/><rect x="730" y="640" width="26" height="110" rx="10" fill="#8a5a32" stroke="{INK}" stroke-width="6" transform="rotate(-45 743 695)"/></g>'
    # clipboard with two ticks (left)
    s += f'<rect x="290" y="610" width="130" height="160" rx="12" fill="#c9a06a" stroke="{INK}" stroke-width="6"/><rect x="300" y="630" width="110" height="130" rx="6" fill="{CREAM}"/><rect x="330" y="598" width="50" height="24" rx="8" fill="{INK}"/><path d="M318 670 l14 14 l28 -30 M318 715 l14 14 l28 -30" fill="none" stroke="{TEAL}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/><path d="M370 660 h30 M370 705 h30" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    return s + caption("コーモラント", "CORMORANT", "reviewer")

def main():
    out = []
    for c in CHARS:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{c["draw"]()}</svg>'
        open(os.path.join(HERE, f'agent-{c["name"]}.svg'), "w").write(svg)
        out.append({"name": c["name"], "title": c["title"], "text": c["text"], "role": c["role"]})
        print(c["name"])
    json.dump(out, open(os.path.join(HERE, "set.json"), "w"), indent=0, ensure_ascii=False)

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""The lovers set: a subset of the Japanese set drawn around two people (cream field, dark
outline, one red accent, at most one second colour, the same 512 grid). Cute on purpose: round
heads, dot eyes, a blush where the red goes. Hand-written path data; this file is the source,
the SVGs beside it are its output. Run: python3 gen.py
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
CREAM, INK, RED, TEAL, GOLD, PAPER = "#f1e3c3", "#1f3a3a", "#d94a3d", "#3f6e6a", "#e0a52a", "#fbf7ef"
FRAME = f'<circle cx="256" cy="256" r="236" fill="{CREAM}" stroke="{INK}" stroke-width="14"/>\n<circle cx="256" cy="256" r="252" fill="none" stroke="{CREAM}" stroke-width="8" opacity=".9"/>'
S = f'stroke="{INK}" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"'
S8 = f'stroke="{INK}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"'

def face(cx, cy, r=44, fill=PAPER, smile=True, blush=True, wink=False):
    """A round head: two dot eyes, a small smile, a blush on each cheek."""
    eyes = (f'<circle cx="{cx-14}" cy="{cy-6}" r="6" fill="{INK}"/>' +
            (f'<path d="M{cx+6} {cy-6} q8-8 16 0" fill="none" {S8}/>' if wink else f'<circle cx="{cx+14}" cy="{cy-6}" r="6" fill="{INK}"/>'))
    mouth = f'<path d="M{cx-10} {cy+12} q10 10 20 0" fill="none" {S8}/>' if smile else f'<circle cx="{cx}" cy="{cy+14}" r="5" fill="{INK}"/>'
    bl = f'<circle cx="{cx-26}" cy="{cy+8}" r="7" fill="{RED}" opacity=".55"/><circle cx="{cx+26}" cy="{cy+8}" r="7" fill="{RED}" opacity=".55"/>' if blush else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {S}/>' + eyes + mouth + bl

def heart(cx, cy, s=1.0, fill=RED, stroke=True):
    d = f'M0 14 C -18 -2, -30 -14, -18 -26 C -10 -34, 0 -28, 0 -18 C 0 -28, 10 -34, 18 -26 C 30 -14, 18 -2, 0 14 z'
    return f'<path d="{d}" fill="{fill}" {S8 if stroke else ""} transform="translate({cx} {cy}) scale({s})"/>'

M = {}
def m(name, title, text):
    def deco(f): M[name] = (title, text, f); return f
    return deco

@m("aiaigasa", "Ai-ai-gasa", "The love umbrella: the doodle every schoolkid draws, two names under one canopy. Here it is two people, and the canopy is the red thing.")
def _(): return f'''<path d="M256 120 v230" {S}/><path d="M256 350 q0 30 -26 30" fill="none" {S}/>
<path d="M96 236 q160-140 320 0 q-40-20-80 0 q-40-20-80 0 q-40-20-80 0 q-40-20-80 0 z" fill="{RED}" {S}/>
<circle cx="256" cy="110" r="10" fill="{INK}"/>
{face(196, 300, 40)}{face(316, 300, 40, wink=True)}
<path d="M156 380 q40-40 80 0 z" fill="{TEAL}" {S}/><path d="M276 380 q40-40 80 0 z" fill="{PAPER}" {S}/>
<path d="M236 330 q20 20 40 0" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round"/>'''

@m("akai-ito", "Akai ito", "The red string of fate, tied at birth to the little finger of the one you will meet. Two people, one thread, and a bow because nobody said it had to be tidy.")
def _():
    person = lambda cx, body, flip: f'''<g transform="translate({cx} 0) scale({flip} 1)">
<path d="M-44 400 q0-80 44-80 q44 0 44 80 z" fill="{body}" {S}/>
{face(0, 270, 44)}
<path d="M30 340 q40-30 50-90" fill="none" {S}/><circle cx="82" cy="246" r="9" fill="{PAPER}" {S8}/></g>'''
    return (person(150, TEAL, 1) + person(362, RED, -1) +
            f'<path d="M232 246 q24 60 48 0" fill="none" stroke="{RED}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M256 290 q-22-26-30-4 q6 14 30 4 q22-26 30-4 q-6 14-30 4 z" fill="{RED}" {S8}/>'
            f'{heart(256, 170, .9)}')

@m("koi-pair", "Two koi", "Red cap and gold cap, nose to tail, the circle they make is the point. Neither one leads for long.")
def _():
    # one koi drawn head-up around (0,0), body from y=-120 to y=+120
    koi = lambda cap: f'''<path d="M0 -120 C 60 -70, 70 30, 32 90 C 14 118, -14 118, -32 90 C -70 30, -60 -70, 0 -120 z" fill="{PAPER}" {S}/>
<path d="M0 -120 C 44 -80, 50 -20, 36 14 C 14 -2, -14 -2, -36 14 C -50 -20, -44 -80, 0 -120 z" fill="{cap}"/>
<path d="M-32 90 q-30 40-40 80 q40-20 72-8 q32-12 72 8 q-10-40-40-80" fill="{PAPER}" {S}/>
<path d="M44 -10 q40-10 56 26 q-40 8-56-26 z M-44 -10 q-40-10-56 26 q40 8 56-26 z" fill="{PAPER}" {S}/>
<circle cx="-12" cy="-44" r="8" fill="{INK}"/><circle cx="12" cy="-44" r="8" fill="{INK}"/>'''
    return (f'<g transform="translate(196 256) rotate(-30) scale(.78)">{koi(RED)}</g>'
            f'<g transform="translate(316 256) rotate(150) scale(.78)">{koi(GOLD)}</g>'
            f'{heart(256, 256, .75)}')

@m("orizuru-pair", "Two cranes", "Paper cranes mate for life, or so the folding tradition insists. Beaks touching; the red one is hers, the cream one is his, and the heart is what fell out of the folds.")
def _():
    # one crane facing right around (0,0): body diamond, wing up, tail left, neck and beak right
    crane = lambda fill: f'''<path d="M-60 20 l60-40 l60 40 l-60 40 z" fill="{fill}" {S}/>
<path d="M-30 0 l10-90 l50 70" fill="{fill}" {S}/>
<path d="M-60 20 l-50-30 l10 50" fill="{fill}" {S}/>
<path d="M60 20 l30-70 l10 20" fill="{fill}" {S}/><path d="M100 -50 l26-6 l-16 18" fill="{RED if fill != RED else INK}" {S8}/>'''
    return (f'<g transform="translate(150 290) scale(.95)">{crane(RED)}</g>'
            f'<g transform="translate(362 290) scale(-.95 .95)">{crane(PAPER)}</g>'
            f'{heart(256, 180, .9)}')

@m("daifuku-pair", "Two daifuku", "Mochi with faces. The one on the right is leaning; the one on the left is letting it. The strawberry is the red.")
def _(): return f'''<path d="M96 330 q0-90 90-90 q90 0 90 90 q0 30-90 30 q-90 0-90-30 z" fill="{PAPER}" {S}/>
<path d="M236 340 q-6-90 84-98 q90-6 100 84 q2 30-88 36 q-90 4-96-22 z" fill="{PAPER}" {S} transform="rotate(-10 320 300)"/>
<circle cx="170" cy="286" r="6" fill="{INK}"/><circle cx="200" cy="286" r="6" fill="{INK}"/><path d="M176 304 q10 8 20 0" fill="none" {S8}/>
<path d="M300 288 q8-8 16 0 M330 286 q8-8 16 0" fill="none" {S8}/><path d="M312 306 q10 8 20 0" fill="none" {S8}/>
<circle cx="150" cy="302" r="7" fill="{RED}" opacity=".55"/><circle cx="220" cy="302" r="7" fill="{RED}" opacity=".55"/>
<circle cx="292" cy="306" r="7" fill="{RED}" opacity=".55"/><circle cx="356" cy="302" r="7" fill="{RED}" opacity=".55"/>
<path d="M186 240 q-24-40 0-60 q24 20 0 60 z" fill="{RED}" {S8}/><path d="M186 182 q-12-16 0-24 q12 8 0 24" fill="{TEAL}" {S8}/>
<path d="M60 380 h392" {S8} opacity=".4"/>'''

@m("kokeshi-pair", "Two kokeshi", "The wooden dolls from the hot-spring towns, heads tilted together. One flower between them, red, because that is how the painters do it.")
def _():
    doll = lambda cx, fill, tilt: f'''<g transform="rotate({tilt} {cx} 300)">
<rect x="{cx-40}" y="250" width="80" height="150" rx="30" fill="{fill}" {S}/>
<path d="M{cx-40} 300 h80 M{cx-40} 330 h80" fill="none" {S8} opacity=".6"/>
{face(cx, 200, 52)}
<path d="M{cx-52} 186 q52-60 104 0 q-52-14-104 0 z" fill="{INK}"/></g>'''
    return (doll(196, TEAL, 8) + doll(316, PAPER, -8) +
            f'<circle cx="256" cy="174" r="16" fill="{RED}" {S8}/>' + "".join(f'<circle cx="256" cy="150" r="9" fill="{RED}" transform="rotate({a} 256 174)"/>' for a in range(0, 360, 72)))

@m("tsuki-usagi", "Moon rabbits", "Two rabbits on the hill, the full moon behind them. In Japan the rabbit in the moon is pounding mochi; these two have knocked off for the night.")
def _():
    rabbit = lambda cx, flip: f'''<g transform="translate({cx} 0) scale({flip} 1)">
<path d="M-40 300 q0-60 40-60 q40 0 40 60 v40 h-80 z" fill="{PAPER}" {S}/>
<path d="M-24 250 l-12-70 q0-12 12-12 q12 0 12 12 l4 62 M8 250 l-4-62 q0-12 12-12 q12 0 12 12 l-12 70" fill="{PAPER}" {S}/>
<circle cx="-12" cy="272" r="5" fill="{INK}"/><circle cx="12" cy="272" r="5" fill="{INK}"/><path d="M-6 288 q6 6 12 0" fill="none" {S8}/>
<circle cx="-24" cy="286" r="6" fill="{RED}" opacity=".55"/><circle cx="24" cy="286" r="6" fill="{RED}" opacity=".55"/></g>'''
    return (f'<circle cx="256" cy="200" r="110" fill="{GOLD}" {S}/>'
            f'<path d="M40 400 q216-120 432 0 z" fill="{TEAL}" {S}/>'
            + rabbit(206, 1) + rabbit(306, -1) +
            f'<path d="M56 130 l10 10 M420 100 l10 10 M100 90 l8 8" {S8} opacity=".5"/>')

@m("onsen-saru", "Snow monkeys", "Two macaques in the hot spring, steam going up, one with the towel folded on its head the way the regulars do. The red faces are real; the monkeys are like that.")
def _():
    monkey = lambda cx, towel: (f'''<circle cx="{cx}" cy="262" r="56" fill="{TEAL}" {S}/>
<circle cx="{cx-54}" cy="256" r="14" fill="{TEAL}" {S8}/><circle cx="{cx+54}" cy="256" r="14" fill="{TEAL}" {S8}/>
<circle cx="{cx}" cy="272" r="36" fill="{RED}" {S8}/>
<circle cx="{cx-13}" cy="264" r="6" fill="{INK}"/><circle cx="{cx+13}" cy="264" r="6" fill="{INK}"/><path d="M{cx-10} 286 q10 8 20 0" fill="none" {S8}/>'''
        + (f'<path d="M{cx-44} 216 h88 l-6-22 q-38-12-76 0 z" fill="{PAPER}" {S8}/>' if towel else ""))
    return (monkey(196, True) + monkey(316, False) +
            f'<path d="M50 320 q52-22 104 0 q52 22 104 0 q52-22 104 0 q52 22 104 0 v70 h-416 z" fill="{TEAL}" {S} opacity=".8"/>'
            f'<path d="M110 350 q40-14 80 0 M300 350 q40-14 80 0" fill="none" stroke="{PAPER}" stroke-width="8" stroke-linecap="round" opacity=".7"/>'
            f'<path d="M140 180 q-24-30 0-60 M256 160 q-24-30 0-60 M372 180 q-24-30 0-60" fill="none" {S8} opacity=".45"/>')

@m("hanabi-futari", "Fireworks, two of us", "Summer festival, the yukata, the two heads from behind, the one red burst. The point of the fireworks is who you watch them with.")
def _():
    burst = "".join(f'<path d="M256 150 v-70" stroke="{RED}" stroke-width="8" stroke-linecap="round" transform="rotate({a} 256 150)"/><circle cx="256" cy="66" r="9" fill="{RED}" transform="rotate({a} 256 150)"/>' for a in range(0, 360, 30))
    return (burst + f'<circle cx="256" cy="150" r="12" fill="{GOLD}" {S8}/>'
            f'<path d="M150 420 q0-100 60-100 q60 0 60 100 z" fill="{TEAL}" {S}/><path d="M256 420 q0-100 60-100 q60 0 60 100 z" fill="{RED}" {S}/>'
            f'<circle cx="210" cy="296" r="44" fill="{INK}" {S}/><circle cx="316" cy="296" r="44" fill="{INK}" {S}/>'
            f'<path d="M298 260 q20-30 40-10" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M180 296 q-20 40 0 60 M346 296 q20 40 0 60" fill="none" {S8} opacity=".5"/>')

@m("sakura-heart", "Sakura heart", "Five petals, each notched once, arranged until they made a heart instead of a flower. It happens if you leave them alone long enough.")
def _():
    petal = lambda x, y, a: f'<path d="M0 0 q-30-40-20-72 q10-10 20 0 q10-10 20 0 q10 32-20 72 z" fill="{PAPER}" {S} transform="translate({x} {y}) rotate({a})"/>'
    return (f'<path d="M256 380 C 150 300, 100 240, 150 180 C 190 140, 240 160, 256 200 C 272 160, 322 140, 362 180 C 412 240, 362 300, 256 380 z" fill="{RED}" {S}/>'
            + petal(200, 250, -30) + petal(312, 250, 30) + petal(256, 300, 0)
            + f'<circle cx="256" cy="250" r="12" fill="{GOLD}" {S8}/>')

@m("mizuhiki-heart", "Mizuhiki heart", "The red-and-white paper cord tied on a gift envelope, knotted into a heart. The knot that tightens when you pull on it: that one is for weddings.")
def _():
    d = "M256 370 C 140 290, 110 230, 160 180 C 200 140, 246 160, 256 200 C 266 160, 312 140, 352 180 C 402 230, 372 290, 256 370 z"
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="30" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{PAPER}" stroke-width="18" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="18" stroke-linejoin="round" stroke-dasharray="40 40"/>'
            f'<path d="M256 200 q-40 30-50 80 q50-20 50 20 q0-40 50-20 q-10-50-50-80 z" fill="{PAPER}" {S}/>'
            f'<path d="M226 250 l60 40 M286 250 l-60 40" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>')

@m("kanpai", "Kanpai", "Two sake cups meeting over the bottle, the clink drawn as three lines because sound has to be drawn somehow. The red is the lacquer on her cup.")
def _():
    cup = lambda cx, fill, tilt: f'''<g transform="rotate({tilt} {cx} 300)">
<path d="M{cx-46} 270 q6 60 46 60 q40 0 46-60 z" fill="{fill}" {S}/>
<path d="M{cx-46} 270 q46-12 92 0 q-46 12-92 0 z" fill="{PAPER}" {S8}/>
<path d="M{cx-14} 330 h28 v12 q0 8-14 8 q-14 0-14-8 z" fill="{fill}" {S8}/></g>'''
    return (f'<path d="M238 196 h36 v34 q52 18 52 80 q0 70-70 70 q-70 0-70-70 q0-62 52-80 z" fill="{TEAL}" {S}/>'
            f'<path d="M238 196 h36" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
            f'<circle cx="256" cy="316" r="24" fill="{PAPER}" {S8}/><path d="M246 316 h20 M256 306 v20" {S8}/>'
            + cup(150, RED, 14) + cup(362, PAPER, -14) +
            f'<path d="M232 236 l-14-20 M256 226 v-24 M280 236 l14-20" fill="none" {S8}/>'
            f'{heart(256, 150, .9)}')

def svg(inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n{FRAME}\n{inner}\n</svg>\n'

if __name__ == "__main__":
    for name, (title, text, f) in M.items():
        open(os.path.join(HERE, name + ".svg"), "w").write(svg(f()))
    import json
    json.dump([{"name": n, "title": t, "text": x} for n, (t, x, _) in M.items()], open(os.path.join(HERE, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(M), "badges")

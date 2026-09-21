#!/usr/bin/env python3
"""The Japanese set, generated: one badge per motif in the portal's vocabulary (cream field, dark
outline, one red accent, at most one second colour). Each drawing is hand-written path data in a
512 grid; this file is the source, the SVGs beside it are its output. Run: python3 gen.py
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
CREAM, INK, RED, TEAL, GOLD, PAPER = "#f1e3c3", "#1f3a3a", "#d94a3d", "#3f6e6a", "#e0a52a", "#fbf7ef"
FRAME = f'<circle cx="256" cy="256" r="236" fill="{CREAM}" stroke="{INK}" stroke-width="14"/>\n<circle cx="256" cy="256" r="252" fill="none" stroke="{CREAM}" stroke-width="8" opacity=".9"/>'
S = f'stroke="{INK}" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"'
S8 = f'stroke="{INK}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"'

M = {}
def m(name, title, text):
    def deco(f): M[name] = (title, text, f); return f
    return deco

@m("torii", "Torii", "The gate between the ordinary and the sacred. Two posts, two lintels, the one red thing.")
def _(): return f'''<g fill="{RED}" {S}>
<rect x="150" y="150" width="30" height="230"/><rect x="332" y="150" width="30" height="230"/>
<path d="M104 132 q152-30 304 0 v30 q-152-22-304 0 z"/><rect x="142" y="196" width="228" height="24"/></g>
<rect x="244" y="166" width="24" height="30" fill="{INK}"/>'''

@m("fuji", "Fuji", "The mountain with snow on its shoulders and a red sun behind it. Drawn the way the woodblocks draw it: three strokes and a cap.")
def _(): return f'''<circle cx="330" cy="176" r="52" fill="{RED}"/>
<path d="M60 380 L200 150 q56-24 112 0 L452 380 z" fill="{TEAL}" {S}/>
<path d="M200 150 q56-24 112 0 l24 46 q-22 18-44 0 q-22 18-44 0 q-22 18-44 0 q-22 18-44 0 z" fill="{PAPER}" {S}/>
<path d="M110 400 q40-24 80 0 q40-24 80 0 q40-24 80 0 q40-24 80 0" fill="none" {S8}/>'''

@m("wave", "The wave", "Hokusai's claw, redrawn as three curls and a red sun. The foam is the field showing through.")
def _(): return f'''<circle cx="356" cy="170" r="46" fill="{RED}"/>
<path d="M72 360 C 90 260, 170 200, 250 210 C 330 220, 330 300, 280 300 C 250 300, 240 270, 262 258 C 300 240, 330 290, 300 320 C 360 300, 400 330, 440 360 z" fill="{TEAL}" {S}/>
<g fill="{PAPER}"><circle cx="228" cy="232" r="12"/><circle cx="262" cy="222" r="9"/><circle cx="292" cy="238" r="7"/><circle cx="310" cy="272" r="8"/></g>
<path d="M60 392 h392" {S8}/>'''

@m("koi", "Koi", "One carp, going up. The red patch on the head is the whole colour budget.")
def _(): return f'''<path d="M256 96 C 320 150, 330 260, 290 330 C 270 364, 240 364, 222 330 C 182 260, 192 150, 256 96 z" fill="{PAPER}" {S}/>
<path d="M256 96 C 300 140, 306 200, 292 236 C 270 220, 242 220, 220 236 C 206 200, 212 140, 256 96 z" fill="{RED}"/>
<path d="M222 330 q-30 40-40 88 q40-24 74-10 q34-14 74 10 q-10-48-40-88" fill="{PAPER}" {S}/>
<path d="M300 210 q40-10 60 30 q-40 10-60-30 z M212 210 q-40-10-60 30 q40 10 60-30 z" fill="{PAPER}" {S}/>
<circle cx="244" cy="176" r="8" fill="{INK}"/><circle cx="268" cy="176" r="8" fill="{INK}"/>'''

@m("daruma", "Daruma", "Paint one eye when you set the goal, the other when you reach it. This one has one eye.")
def _(): return f'''<path d="M256 110 C 370 110, 420 200, 420 300 C 420 380, 340 420, 256 420 C 172 420, 92 380, 92 300 C 92 200, 142 110, 256 110 z" fill="{RED}" {S}/>
<path d="M256 170 C 320 170, 350 220, 350 280 C 350 330, 310 350, 256 350 C 202 350, 162 330, 162 280 C 162 220, 192 170, 256 170 z" fill="{PAPER}" {S}/>
<path d="M196 236 q30-24 56 0 M260 236 q30-24 56 0" fill="none" {S}/>
<circle cx="224" cy="262" r="18" fill="{PAPER}" {S8}/><circle cx="224" cy="262" r="9" fill="{INK}"/>
<circle cx="288" cy="262" r="18" fill="{PAPER}" {S8}/>
<path d="M236 314 q20 12 40 0" fill="none" {S8}/>'''

@m("maneki", "Maneki-neko", "The beckoning cat, left paw up for customers. The collar is the red.")
def _(): return f'''<path d="M170 210 l-20-80 l70 40 h72 l70-40 l-20 80 q60 60 40 130 q-20 70-126 70 q-106 0-126-70 q-20-70 40-130 z" fill="{PAPER}" {S}/>
<path d="M150 130 l30 40 M362 130 l-30 40" {S8}/>
<circle cx="220" cy="236" r="8" fill="{INK}"/><circle cx="292" cy="236" r="8" fill="{INK}"/>
<path d="M244 266 q12 10 24 0 M236 266 l8 8 M276 266 l-8 8" fill="none" {S8}/>
<path d="M186 320 q70 30 140 0" fill="none" stroke="{RED}" stroke-width="16" stroke-linecap="round"/>
<circle cx="256" cy="330" r="14" fill="{GOLD}" {S8}/>
<path d="M112 200 q-40-60 10-90 q50 10 40 80 q-20 20-50 10 z" fill="{PAPER}" {S}/>'''

@m("sakura", "Sakura", "Five petals, each notched once. The centre is red because the season is short.")
def _():
    petals = "".join(f'<path d="M256 256 q-60-40-60-100 q0-40 40-40 q20 0 20 30 q0-30 20-30 q40 0 40 40 q0 60-60 100 z" fill="{PAPER}" {S} transform="rotate({a} 256 256)"/>' for a in range(0, 360, 72))
    return petals + f'<circle cx="256" cy="256" r="26" fill="{RED}" {S8}/>'

@m("momiji", "Momiji", "The maple leaf in autumn red, the one month Kyoto is unbearable to visit and everyone goes anyway.")
def _():
    lobes = "".join(f'<path d="M256 270 L226 150 L256 90 L286 150 z" fill="{RED}" {S} transform="rotate({a} 256 270)"/>' for a in (-64, -32, 0, 32, 64))
    return lobes + f'<path d="M256 270 v120" {S}/>'

@m("bamboo", "Take", "Bamboo: three culms, the nodes marked, leaves at the top. It bends, it does not break, the proverb writes itself.")
def _(): return f'''<g fill="{TEAL}" {S}><rect x="150" y="110" width="40" height="300" rx="8"/><rect x="236" y="90" width="40" height="320" rx="8"/><rect x="322" y="130" width="40" height="280" rx="8"/></g>
<path d="M146 210 h48 M146 320 h48 M232 190 h48 M232 300 h48 M318 230 h48 M318 340 h48" {S8}/>
<g fill="{TEAL}" {S8}><path d="M276 120 q60-40 90-10 q-50 30-90 10 z"/><path d="M190 140 q-60-40-90-10 q50 30 90 10 z"/><path d="M362 160 q50-40 80 0 q-40 20-80 0 z"/></g>'''

@m("chochin", "Chōchin", "The paper lantern. Ribs drawn as arcs, a character left off on purpose so it can mean any shop.")
def _(): return f'''<rect x="216" y="96" width="80" height="30" rx="6" fill="{INK}"/>
<path d="M170 140 q86-40 172 0 v220 q-86 40-172 0 z" fill="{RED}" {S}/>
<path d="M170 190 q86 20 172 0 M170 240 q86 20 172 0 M170 290 q86 20 172 0 M170 340 q86 20 172 0" fill="none" {S8}/>
<rect x="216" y="380" width="80" height="26" rx="6" fill="{INK}"/><path d="M256 406 v20" {S8}/>'''

@m("kitsune", "Kitsune", "The fox mask from the festival stall. White face, red markings, ears that hear everything.")
def _(): return f'''<path d="M256 110 L160 130 L120 240 Q140 360 256 420 Q372 360 392 240 L352 130 z" fill="{PAPER}" {S}/>
<path d="M160 130 L176 96 L212 138 z M352 130 L336 96 L300 138 z" fill="{RED}" {S}/>
<path d="M196 226 l34 24 l-34 12 z M316 226 l-34 24 l34 12 z" fill="{INK}"/>
<path d="M186 190 q24-10 50 4 M326 190 q-24-10-50 4" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round"/>
<path d="M246 330 q10 12 20 0" fill="none" {S8}/><path d="M226 360 l30 12 l30-12" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>'''

@m("orizuru", "Orizuru", "The folded crane, drawn flat: two wings, a beak, a tail, and the creases that make it a crane and not a paper triangle.")
def _(): return f'''<path d="M256 240 L100 180 L200 260 z" fill="{PAPER}" {S}/>
<path d="M256 240 L412 180 L312 260 z" fill="{PAPER}" {S}/>
<path d="M200 260 L256 240 L312 260 L256 330 z" fill="{RED}" {S}/>
<path d="M256 240 L246 120 L286 150 z" fill="{PAPER}" {S}/><path d="M246 120 l-30 8" {S8}/>
<path d="M256 330 L226 400 L286 400 z" fill="{PAPER}" {S}/>'''

@m("bonsai", "Bonsai", "A pine in a shallow pot, forty years of patience in a shape that fits on a shelf.")
def _(): return f'''<path d="M150 380 h212 l-16 40 h-180 z" fill="{RED}" {S}/>
<path d="M256 380 q-6-80 20-130 q-40-10-60-60" fill="none" {S}/>
<g fill="{TEAL}" {S8}><ellipse cx="200" cy="180" rx="70" ry="30"/><ellipse cx="300" cy="150" rx="80" ry="34"/><ellipse cx="330" cy="240" rx="60" ry="26"/></g>
<path d="M276 250 q20-40 54-10" fill="none" {S}/>'''

@m("pagoda", "Pagoda", "Five stories, each roof a little smaller, the finial the one red line. Wood, no nails.")
def _():
    roofs = "".join(f'<path d="M{256-w} {y} q{w} -40 {2*w} 0 l-16 14 h-{2*w-32} z" fill="{INK}" {S8}/><rect x="{256-w+40}" y="{y+14}" width="{2*w-80}" height="40" fill="{PAPER}" {S8}/>' for w, y in ((60, 130), (76, 190), (92, 250), (108, 310)))
    return f'<path d="M256 70 v60" stroke="{RED}" stroke-width="14" stroke-linecap="round"/>' + roofs + f'<rect x="120" y="380" width="272" height="28" fill="{INK}"/>'

@m("sensu", "Sensu", "The folding fan, open. Nine ribs, a red field, the rivet at the bottom.")
def _():
    ribs = "".join(f'<path d="M256 380 L{256+int(240*__import__("math").cos(__import__("math").radians(a)))} {380-int(240*__import__("math").sin(__import__("math").radians(a)))}" {S8}/>' for a in range(30, 151, 15))
    return f'<path d="M256 380 L48 260 A240 240 0 0 1 464 260 z" fill="{RED}" {S}/><path d="M256 380 L152 320 A120 120 0 0 1 360 320 z" fill="{PAPER}" {S}/>' + ribs + f'<circle cx="256" cy="380" r="14" fill="{INK}"/>'

@m("uchiwa", "Uchiwa", "The flat fan for summer festivals. Round, a handle, a red circle: the cheapest good design in Japan.")
def _(): return f'''<circle cx="256" cy="220" r="130" fill="{PAPER}" {S}/><circle cx="256" cy="220" r="60" fill="{RED}"/>
<path d="M256 90 v260 M156 140 l200 160 M356 140 l-200 160 M126 220 h260" fill="none" {S8} opacity=".5"/>
<rect x="240" y="350" width="32" height="90" rx="10" fill="{INK}"/>'''

@m("geta", "Geta", "Wooden sandals, two teeth each, the red thong. The sound of a summer street.")
def _(): return f'''<g transform="rotate(-12 200 260)"><path d="M120 200 q80-30 160 0 v70 q-80 30-160 0 z" fill="{PAPER}" {S}/><rect x="140" y="272" width="24" height="40" fill="{INK}"/><rect x="236" y="272" width="24" height="40" fill="{INK}"/><path d="M200 214 v-24 M200 190 l-50 40 M200 190 l50 40" fill="none" stroke="{RED}" stroke-width="12" stroke-linecap="round"/></g>
<g transform="rotate(8 320 300)"><path d="M240 240 q80-30 160 0 v70 q-80 30-160 0 z" fill="{PAPER}" {S}/><rect x="260" y="312" width="24" height="40" fill="{INK}"/><rect x="356" y="312" width="24" height="40" fill="{INK}"/><path d="M320 254 v-24 M320 230 l-50 40 M320 230 l50 40" fill="none" stroke="{RED}" stroke-width="12" stroke-linecap="round"/></g>'''

@m("kimono", "Kimono", "The garment, hung flat as a T. The obi is the red band; the sleeves tell you it is a woman's.")
def _(): return f'''<path d="M96 150 L200 110 q56 40 112 0 L416 150 L392 250 L340 232 V410 H172 V232 L120 250 z" fill="{TEAL}" {S}/>
<path d="M200 110 q56 40 112 0 L280 260 H232 z" fill="{PAPER}" {S}/>
<rect x="172" y="280" width="168" height="44" fill="{RED}" {S8}/>
<path d="M172 232 v100 M340 232 v100" {S8}/>'''

@m("obi", "Obi knot", "The taiko musubi, the drum knot on the back of a kimono. Drawn from behind, which is the only way to see it.")
def _(): return f'''<rect x="96" y="220" width="320" height="70" fill="{RED}" {S}/>
<path d="M176 190 h160 v130 h-160 z" fill="{RED}" {S}/>
<path d="M176 190 q-40 60 0 130 M336 190 q40 60 0 130" fill="none" {S}/>
<rect x="216" y="236" width="80" height="40" rx="6" fill="{GOLD}" {S8}/>
<path d="M120 290 v60 M392 290 v60" {S8}/>'''

@m("onigiri", "Onigiri", "Rice, a strip of nori, one umeboshi. Lunch, drawn in three shapes.")
def _(): return f'''<path d="M256 120 q40 0 70 50 l70 120 q30 50-30 60 h-220 q-60-10-30-60 l70-120 q30-50 70-50 z" fill="{PAPER}" {S}/>
<rect x="196" y="270" width="120" height="80" rx="8" fill="{INK}"/>
<circle cx="256" cy="200" r="22" fill="{RED}"/>'''

@m("ramen", "Ramen", "A bowl with the red double line, noodles, two chopsticks, and steam. Drawn at 1 a.m.")
def _(): return f'''<path d="M96 240 h320 q-10 120-160 140 q-150-20-160-140 z" fill="{PAPER}" {S}/>
<path d="M110 270 h292 M118 290 h276" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>
<path d="M140 240 q40-40 80-10 q40-30 80 0 q40-30 80 10" fill="none" {S8}/>
<path d="M300 100 l-60 140 M340 110 l-60 130" {S8}/>
<path d="M180 130 q-20 30 0 60 M220 110 q-20 30 0 60" fill="none" {S8} opacity=".6"/>'''

@m("chawan", "Chawan", "The tea bowl, with a kintsugi seam. The break is the red line; the repair is the point.")
def _(): return f'''<path d="M120 190 h272 q-6 130-136 160 q-130-30-136-160 z" fill="{TEAL}" {S}/>
<ellipse cx="256" cy="190" rx="136" ry="26" fill="{PAPER}" {S}/>
<path d="M330 210 l-30 50 l20 40 l-30 46" fill="none" stroke="{GOLD}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="256" cy="186" r="30" fill="{RED}" opacity=".9"/>'''

@m("chasen", "Chasen", "The bamboo whisk, eighty tines from one piece of bamboo, and the matcha it is for.")
def _():
    tines = "".join(f'<path d="M256 250 L{256+int(110*__import__("math").cos(__import__("math").radians(a)))} {250-int(110*__import__("math").sin(__import__("math").radians(a)))}" {S8}/>' for a in range(20, 161, 10))
    return f'<rect x="230" y="250" width="52" height="150" rx="14" fill="{PAPER}" {S}/>' + tines + f'<path d="M180 250 q76 30 152 0" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round"/>'

@m("sake", "Tokkuri and ochoko", "The flask and the cup. Warm in winter, cold in summer, the same drawing either way.")
def _(): return f'''<path d="M170 130 h60 v50 q50 30 50 100 v120 h-160 v-120 q0-70 50-100 z" fill="{PAPER}" {S}/>
<path d="M136 300 h144" stroke="{RED}" stroke-width="12" stroke-linecap="round"/>
<path d="M310 300 h100 q0 90-50 100 q-50-10-50-100 z" fill="{PAPER}" {S}/>
<ellipse cx="360" cy="300" rx="50" ry="12" fill="{RED}"/>'''

@m("kokeshi", "Kokeshi", "The wooden doll from Tōhoku: a head, a body, no arms, and a red flower on the kimono.")
def _(): return f'''<circle cx="256" cy="150" r="70" fill="{PAPER}" {S}/>
<path d="M186 140 q70-60 140 0 q-10-40-70-50 q-60 10-70 50 z" fill="{INK}"/>
<circle cx="234" cy="156" r="6" fill="{INK}"/><circle cx="278" cy="156" r="6" fill="{INK}"/><path d="M246 180 q10 8 20 0" fill="none" {S8}/>
<path d="M206 220 h100 q30 100 20 200 h-140 q-10-100 20-200 z" fill="{TEAL}" {S}/>
<circle cx="256" cy="300" r="22" fill="{RED}"/><circle cx="256" cy="300" r="8" fill="{GOLD}"/>'''

@m("kabuto", "Kabuto", "The samurai helmet with its crescent crest. Drawn front-on, the crest the only red.")
def _(): return f'''<path d="M136 260 q0-120 120-130 q120 10 120 130 v40 h-240 z" fill="{INK}" {S}/>
<path d="M256 130 q-40-60-90-40 q40 20 60 60 M256 130 q40-60 90-40 q-40 20-60 60" fill="{RED}" {S}/>
<path d="M120 300 h272 l-20 60 h-232 z" fill="{INK}" {S}/>
<path d="M150 320 h212 M160 340 h192" stroke="{CREAM}" stroke-width="8" stroke-linecap="round"/>
<circle cx="256" cy="230" r="18" fill="{GOLD}" {S8}/>'''

@m("katana", "Katana", "The sword, sheathed. A single curve, the guard, and the red cord on the grip.")
def _(): return f'''<g transform="rotate(-35 256 256)">
<path d="M90 256 q166-40 332 0 q-166 24-332 0 z" fill="{PAPER}" {S}/>
<rect x="290" y="230" width="20" height="52" rx="4" fill="{GOLD}" {S8}/>
<path d="M310 244 h100 v24 h-100 z" fill="{INK}"/>
<path d="M318 244 l16 24 l16-24 l16 24 l16-24 l16 24" fill="none" stroke="{RED}" stroke-width="6"/></g>'''

@m("kendama", "Kendama", "The cup-and-ball. Red ball, string, three cups. Harder than it looks, like most things here.")
def _(): return f'''<rect x="236" y="200" width="40" height="200" rx="10" fill="{PAPER}" {S}/>
<path d="M176 240 h60 v40 h-60 q-20-20 0-40 z M276 240 h60 q20 20 0 40 h-60 z" fill="{PAPER}" {S}/>
<path d="M226 400 h60 q10 30-30 30 q-40 0-30-30 z" fill="{PAPER}" {S}/>
<path d="M256 200 v-30" {S8}/><circle cx="256" cy="130" r="50" fill="{RED}" {S}/><circle cx="256" cy="130" r="8" fill="{PAPER}"/>'''

@m("koinobori", "Koinobori", "Carp streamers for Children's Day, three on a pole, the red one for the mother.")
def _():
    def carp(y, col): return f'<path d="M150 {y} q120-30 220 0 l-30 26 l30 26 q-100 30-220 0 z" fill="{col}" {S}/><circle cx="184" cy="{y+22}" r="10" fill="{PAPER}" {S8}/><path d="M220 {y+4} q20 20 0 44 M250 {y+2} q20 22 0 48" fill="none" {S8}/>'
    return f'<rect x="96" y="90" width="14" height="330" fill="{INK}"/><circle cx="103" cy="86" r="14" fill="{GOLD}"/>' + carp(150, INK) + carp(240, RED) + carp(330, TEAL)

@m("tombo", "Tombo", "The dragonfly, the samurai's insect because it never flies backward. Four wings, a red body.")
def _(): return f'''<path d="M256 120 v260" stroke="{RED}" stroke-width="20" stroke-linecap="round"/>
<circle cx="256" cy="120" r="24" fill="{INK}"/>
<g fill="{PAPER}" {S}><path d="M246 190 q-120-70-160 0 q40 60 160 20 z"/><path d="M266 190 q120-70 160 0 q-40 60-160 20 z"/><path d="M246 240 q-100-30-140 30 q60 40 140 0 z"/><path d="M266 240 q100-30 140 30 q-60 40-140 0 z"/></g>'''

@m("tsuki", "Tsuki to usagi", "The moon and the rabbit pounding mochi in it. Every child in Japan sees the rabbit; the west sees a face.")
def _(): return f'''<circle cx="256" cy="256" r="150" fill="{GOLD}" {S}/>
<g fill="{PAPER}" {S8}><ellipse cx="240" cy="290" rx="60" ry="46"/><circle cx="196" cy="250" r="30"/><path d="M186 226 l-10-60 l30 10 z M206 226 l10-60 l-30 10 z"/></g>
<circle cx="188" cy="248" r="5" fill="{RED}"/>
<rect x="296" y="200" width="16" height="100" rx="6" fill="{INK}" transform="rotate(20 304 250)"/><rect x="290" y="300" width="60" height="30" rx="8" fill="{INK}"/>'''

@m("hanabi", "Hanabi", "Fireworks over the river. A chrysanthemum burst, red at the centre, and the trail it rode up on.")
def _():
    rays = "".join(f'<path d="M256 200 L{256+int(130*__import__("math").cos(__import__("math").radians(a)))} {200-int(130*__import__("math").sin(__import__("math").radians(a)))}" {S8}/>' for a in range(0, 360, 30))
    dots = "".join(f'<circle cx="{256+int(130*__import__("math").cos(__import__("math").radians(a)))}" cy="{200-int(130*__import__("math").sin(__import__("math").radians(a)))}" r="12" fill="{TEAL}"/>' for a in range(0, 360, 30))
    return rays + dots + f'<circle cx="256" cy="200" r="34" fill="{RED}"/><path d="M256 340 q-20 40 0 80" fill="none" {S8} stroke-dasharray="14 12"/>'

@m("temari", "Temari", "The embroidered thread ball. Bands of red and teal over a paper sphere; a gift, never a toy.")
def _(): return f'''<circle cx="256" cy="256" r="150" fill="{PAPER}" {S}/>
<path d="M106 256 h300 M256 106 v300" stroke="{RED}" stroke-width="14"/>
<ellipse cx="256" cy="256" rx="150" ry="60" fill="none" stroke="{TEAL}" stroke-width="12"/><ellipse cx="256" cy="256" rx="60" ry="150" fill="none" stroke="{TEAL}" stroke-width="12"/>
<circle cx="256" cy="256" r="24" fill="{RED}" {S8}/>'''

@m("ema", "Ema", "The wooden wish plaque from the shrine rack, the string through the hole, a red horse where the wish goes.")
def _(): return f'''<path d="M256 120 l150 60 v190 h-300 v-190 z" fill="{GOLD}" {S}/>
<path d="M256 120 l150 60 h-300 z" fill="{INK}" {S}/>
<circle cx="256" cy="150" r="8" fill="{CREAM}"/><path d="M256 142 q0-50 30-60" fill="none" {S8}/>
<path d="M200 300 l30-50 l60 10 l26-30 l10 40 l-16 60 h-24 v-30 h-40 v30 h-24 z" fill="{RED}"/>'''

@m("omamori", "Omamori", "The amulet in its brocade pouch, knotted with the red cord. Not opened, ever; that is the rule.")
def _(): return f'''<path d="M186 180 h140 v190 q-70 40-140 0 z" fill="{TEAL}" {S}/>
<path d="M186 180 l70-40 l70 40 z" fill="{TEAL}" {S}/>
<path d="M256 140 v-30 q-40-10-40 20 q40 10 40 10 q0-30 40-20 q0 30-40 20" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="226" y="220" width="60" height="110" rx="6" fill="{GOLD}" {S8}/>'''

@m("shishiodoshi", "Shishi-odoshi", "The bamboo tube in the garden that fills, tips, and knocks the rock. Meant to scare deer; keeps time instead.")
def _(): return f'''<path d="M100 400 h312" {S}/>
<path d="M170 400 v-120 M200 400 v-120" {S}/>
<g transform="rotate(-18 185 280)"><rect x="90" y="262" width="190" height="36" rx="10" fill="{TEAL}" {S}/><path d="M150 262 v36 M210 262 v36" {S8}/></g>
<path d="M300 310 q40-40 90 0 v90 h-90 z" fill="{PAPER}" {S}/>
<path d="M360 140 q-40 60 0 120" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round" stroke-dasharray="4 14"/>'''

@m("ikebana", "Ikebana", "Three stems, heaven, earth and human, in a shallow dish. The red bloom is heaven.")
def _(): return f'''<path d="M120 360 h272 q-20 40-136 40 q-116 0-136-40 z" fill="{INK}" {S}/>
<path d="M256 360 q-10-120 40-220 M256 360 q-60-60-120-80 M256 360 q30-40 100-50" fill="none" {S}/>
<circle cx="296" cy="140" r="34" fill="{RED}" {S8}/>
<g fill="{TEAL}" {S8}><path d="M136 280 q-30-40 10-60 q30 30-10 60 z"/><path d="M356 310 q40-30 30-70 q-40 20-30 70 z"/></g>'''

@m("noren", "Noren", "The split curtain over a shop door. Two panels, a red circle across the gap, the rod above.")
def _(): return f'''<rect x="96" y="120" width="320" height="16" rx="8" fill="{INK}"/>
<path d="M120 136 h130 v250 h-130 z M262 136 h130 v250 h-130 z" fill="{TEAL}" {S}/>
<path d="M186 136 v-12 M256 136 v-12 M326 136 v-12" {S8}/>
<path d="M250 260 a60 60 0 1 1 0 0.1 z" fill="{RED}" clip-path="inset(0 0 0 0)"/>
<circle cx="256" cy="260" r="60" fill="{RED}"/><rect x="250" y="136" width="12" height="250" fill="{CREAM}"/>'''

@m("shoji", "Shōji", "The paper screen, the grid of lath, and a red sun through the paper from the garden side.")
def _(): return f'''<rect x="120" y="110" width="272" height="292" fill="{PAPER}" {S}/>
<path d="M188 110 v292 M256 110 v292 M324 110 v292 M120 183 h272 M120 256 h272 M120 329 h272" {S8}/>
<circle cx="324" cy="183" r="40" fill="{RED}" opacity=".85"/>'''

@m("taiko", "Taiko", "The drum, on its side, two bachi crossed above it. Loud enough to feel in the ribs.")
def _(): return f'''<path d="M126 200 h260 v130 h-260 z" fill="{RED}" {S}/>
<ellipse cx="126" cy="265" rx="30" ry="65" fill="{PAPER}" {S}/><ellipse cx="386" cy="265" rx="30" ry="65" fill="{PAPER}" {S}/>
<g fill="{INK}"><circle cx="170" cy="215" r="8"/><circle cx="170" cy="315" r="8"/><circle cx="342" cy="215" r="8"/><circle cx="342" cy="315" r="8"/></g>
<path d="M190 150 l130-90 M322 150 l-130-90" stroke="{PAPER}" stroke-width="14" stroke-linecap="round"/><path d="M190 150 l130-90 M322 150 l-130-90" {S8}/>'''

@m("shamisen", "Shamisen", "Three strings, a square body, a long neck, and the bachi that plays it. Red for the body's edge.")
def _(): return f'''<g transform="rotate(-40 256 256)">
<rect x="196" y="270" width="120" height="120" rx="14" fill="{PAPER}" {S}/><rect x="196" y="270" width="120" height="120" rx="14" fill="none" stroke="{RED}" stroke-width="6"/>
<rect x="246" y="60" width="20" height="220" fill="{INK}"/>
<path d="M240 90 h-20 M240 110 h-20 M272 100 h20" {S8}/>
<path d="M250 100 v260 M256 100 v260 M262 100 v260" stroke="{GOLD}" stroke-width="2"/></g>
<path d="M340 380 l40-60 l16 10 l-40 60 z" fill="{PAPER}" {S8}/>'''

@m("mizuhiki", "Mizuhiki", "The paper cord knot on a gift envelope: red and white, tied once, not meant to be untied.")
def _(): return f'''<rect x="150" y="100" width="212" height="312" fill="{PAPER}" {S}/>
<path d="M150 256 c40-60 100-60 106 0 c6 60 66 60 106 0" fill="none" stroke="{RED}" stroke-width="10"/>
<path d="M150 276 c40-60 100-60 106 0 c6 60 66 60 106 0" fill="none" {S8}/>
<path d="M150 236 c40-60 100-60 106 0 c6 60 66 60 106 0" fill="none" {S8}/>
<circle cx="256" cy="256" r="16" fill="{RED}" {S8}/>'''

@m("hinomaru", "Hinomaru", "The sun on the field. The simplest flag there is, and the reason one red accent works in every badge above.")
def _(): return f'''<rect x="106" y="156" width="300" height="200" fill="{PAPER}" {S}/><circle cx="256" cy="256" r="60" fill="{RED}"/>'''

@m("sushi", "Nigiri", "Two pieces: tuna and salmon, the rice underneath, the wasabi nobody sees.")
def _(): return f'''<path d="M110 300 h150 q0 50-75 50 q-75 0-75-50 z" fill="{PAPER}" {S}/><path d="M100 300 q80-50 170 0 q-85 20-170 0 z" fill="{RED}" {S}/>
<path d="M252 300 h150 q0 50-75 50 q-75 0-75-50 z" fill="{PAPER}" {S}/><path d="M242 300 q80-50 170 0 q-85 20-170 0 z" fill="{GOLD}" {S}/>
<path d="M262 276 h40 M280 268 h40 M298 282 h40" stroke="{PAPER}" stroke-width="6" stroke-linecap="round"/>
<path d="M120 200 q136-60 272 0" fill="none" {S8} opacity=".5"/>'''

@m("furoshiki", "Furoshiki", "The wrapping cloth, tied over a box. The knot on top is the handle; the cloth is the gift's second gift.")
def _(): return f'''<path d="M120 280 l136-70 l136 70 l-136 70 z" fill="{TEAL}" {S}/>
<path d="M120 280 v60 l136 70 v-60 z M392 280 v60 l-136 70 v-60 z" fill="{TEAL}" {S}/>
<path d="M256 210 q-40-60-20-100 q30 20 30 60 M256 210 q40-60 20-100 q-30 20-30 60" fill="{TEAL}" {S}/>
<circle cx="256" cy="212" r="16" fill="{RED}" {S8}/>'''

@m("ume", "Ume", "The plum blossom, five round petals, out in February when nothing else is. Red centre, as before.")
def _():
    petals = "".join(f'<circle cx="256" cy="176" r="50" fill="{PAPER}" {S} transform="rotate({a} 256 256)"/>' for a in range(0, 360, 72))
    return petals + f'<circle cx="256" cy="256" r="30" fill="{RED}" {S8}/>' + "".join(f'<circle cx="256" cy="210" r="6" fill="{INK}" transform="rotate({a} 256 256)"/>' for a in range(36, 360, 72))

def svg(inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n{FRAME}\n{inner}\n</svg>\n'

if __name__ == "__main__":
    for name, (title, text, f) in M.items():
        open(os.path.join(HERE, name + ".svg"), "w").write(svg(f()))
    import json
    json.dump([{"name": n, "title": t, "text": x} for n, (t, x, _) in M.items()], open(os.path.join(HERE, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(M), "badges")

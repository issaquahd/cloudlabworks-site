#!/usr/bin/env python3
"""Friends and family: thirty more chibi characters around the roster. Offspring, cousins, aunts,
old friends of Waku and the Salish Sea five, every one a creature of the same sea and the same
shore, named the same way (the creature is the name) with the katakana at the foot.

One parametric chibi (field, body, head, face patch, eyes, mouth) plus a box of parts (ears,
crests, beaks, fins, whiskers, tentacles) and a box of props (bow, ball, book, kite, scarf,
glasses, headphones, pacifier, backpack, fish, flower, shell, mug, bucket, pencil, lantern). Each
character is one spec; the drawing is shared. Same 1024 square, same caption, rendered by headless
Chrome (text) and watermarked by build-art.sh. Run: python3 family.py
"""
import json, os
from gen import INK, CREAM, RED, TEAL, GOLD, field, eyes, blush, mouth, caption, shadow
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- parts ----------
def body(colour, belly=None, w=120, h=90, cy=705):
    s = f'<ellipse cx="512" cy="{cy}" rx="{w}" ry="{h}" fill="{colour}"/>'
    if belly: s += f'<path d="M{512-w*.7:.0f} {cy-15} q{w*.7:.0f} -30 {w*1.4:.0f} 0 q-6 60 -{w*.7:.0f} 70 q-{w*.7-6:.0f} -10 -{w*.7:.0f} -70z" fill="{belly}"/>'
    return s
def head(colour, r=245, cy=455): return f'<circle cx="512" cy="{cy}" r="{r}" fill="{colour}"/>'
def bib(colour, cy=455): return f'<path d="M340 {cy+50} q50 160 172 160 q122 0 172 -160 q-60 -50 -172 -50 q-112 0 -172 50z" fill="{colour}"/>'
def mask(colour, cy=455): return f'<path d="M300 {cy+65} q60 190 212 190 q152 0 212 -190 q-60 -60 -212 -60 q-152 0 -212 60z" fill="{colour}"/>'
def eyepatches(colour, cy=455): return f'<ellipse cx="392" cy="{cy-95}" rx="56" ry="70" fill="{colour}" transform="rotate(-20 392 {cy-95})"/><ellipse cx="632" cy="{cy-95}" rx="56" ry="70" fill="{colour}" transform="rotate(20 632 {cy-95})"/>'
def ears_round(colour, inner, r=70, cy=250): return f'<circle cx="330" cy="{cy}" r="{r}" fill="{colour}"/><circle cx="694" cy="{cy}" r="{r}" fill="{colour}"/><circle cx="330" cy="{cy}" r="{r*.55:.0f}" fill="{inner}"/><circle cx="694" cy="{cy}" r="{r*.55:.0f}" fill="{inner}"/>'
def ears_point(colour, inner): return f'<path d="M300 300 l-20 -150 l120 90z M724 300 l20 -150 l-120 90z" fill="{colour}"/><path d="M320 280 l-8 -90 l70 60z M704 280 l8 -90 l-70 60z" fill="{inner}"/>'
def ears_long(colour, inner): return f'<ellipse cx="400" cy="200" rx="46" ry="120" fill="{colour}" transform="rotate(-15 400 200)"/><ellipse cx="624" cy="200" rx="46" ry="120" fill="{colour}" transform="rotate(15 624 200)"/><ellipse cx="400" cy="205" rx="22" ry="80" fill="{inner}" transform="rotate(-15 400 205)"/><ellipse cx="624" cy="205" rx="22" ry="80" fill="{inner}" transform="rotate(15 624 205)"/>'
def crest(colour, n=3): return "".join(f'<path d="M{512+(i-(n-1)/2)*40:.0f} 230 q{-20+i*10} -110 {30+i*6} -90 q-10 40 -10 90z" fill="{colour}"/>' for i in range(n))
def tuft(colour): return f'<path d="M470 225 q10 -70 60 -60 q-20 30 -10 60z" fill="{colour}"/>'
def dorsal(colour): return f'<path d="M512 240 q-40 -110 -20 -160 q70 60 80 160z" fill="{colour}"/>'
def horns(colour): return f'<path d="M380 250 q-60 -80 -10 -140 q20 70 60 110z M644 250 q60 -80 10 -140 q-20 70 -60 110z" fill="{colour}"/>'
def antlers(colour): return f'<path d="M400 240 l-40 -140 l-40 20 M360 100 l30 -60 M390 180 l-50 -30 M624 240 l40 -140 l40 20 M664 100 l-30 -60 M634 180 l50 -30" fill="none" stroke="{colour}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
def beak(colour, size=1.0, cy=545): return f'<path d="M512 {cy} l{140*size:.0f} {34*size:.0f} q{-40*size:.0f} {30*size:.0f} {-80*size:.0f} {20*size:.0f} l{-60*size:.0f} {-14*size:.0f}z" fill="{colour}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
def beak_small(colour, cy=550): return f'<path d="M482 {cy} l60 0 l-30 34z" fill="{colour}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
def beak_puffin(cy=540): return f'<path d="M512 {cy-20} l150 40 l-150 60 z" fill="{GOLD}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M600 {cy+4} l62 16 l-62 24z" fill="{RED}"/><path d="M512 {cy+20} l150 0" stroke="{INK}" stroke-width="4"/>'
def snout(colour, cy=560): return f'<ellipse cx="512" cy="{cy}" rx="70" ry="44" fill="{colour}"/><ellipse cx="512" cy="{cy-14}" rx="22" ry="14" fill="{INK}"/>'
def whiskers(cy=560): return f'<path d="M430 {cy} l-90 -16 M430 {cy+16} l-90 10 M594 {cy} l90 -16 M594 {cy+16} l90 10" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
def flippers(colour, cy=700): return f'<ellipse cx="380" cy="{cy}" rx="70" ry="30" fill="{colour}" transform="rotate(-30 380 {cy})"/><ellipse cx="644" cy="{cy}" rx="70" ry="30" fill="{colour}" transform="rotate(30 644 {cy})"/>'
def wings(colour, cy=690): return f'<path d="M400 {cy} q-120 -20 -140 60 q80 30 150 -10z M624 {cy} q120 -20 140 60 q-80 30 -150 -10z" fill="{colour}"/>'
def legs(colour, cy=790): return f'<path d="M470 {cy-70} v{70} M554 {cy-70} v{70} M440 {cy} h60 M524 {cy} h60" fill="none" stroke="{colour}" stroke-width="12" stroke-linecap="round"/>'
def tail_fish(colour, cy=720): return f'<path d="M620 {cy} q70 -50 90 -10 q-30 10 -40 40 q-20 -20 -50 -30z" fill="{colour}"/>'
def fins(colour, cy=700): return f'<path d="M400 {cy} q-90 -30 -110 40 q70 10 110 -10z M624 {cy} q90 -30 110 40 q-70 10 -110 -10z" fill="{colour}"/>'
def tentacles(colour, cy=720): return "".join(f'<path d="M{380+i*44} {cy} q{-30+i*10} 90 {-10+i*8} 150" fill="none" stroke="{colour}" stroke-width="26" stroke-linecap="round"/>' for i in range(7))
def arms_star(colour): return "".join(f'<path d="M512 470 l-90 -40 l-330 {-60+i*12} l330 140z" fill="{colour}" transform="rotate({72*i} 512 470)"/>' for i in range(5))
def spines(colour): return "".join(f'<path d="M512 455 l-14 0 l14 -300 l14 300z" fill="{colour}" transform="rotate({i*22.5} 512 455)"/>' for i in range(16))
def shell_dome(colour, stripe): return f'<path d="M262 700 a250 250 0 0 1 500 0z" fill="{colour}"/>' + "".join(f'<path d="M{262+i*100} 700 q{50} -{200-abs(2-i)*40} {100} 0" fill="none" stroke="{stripe}" stroke-width="10"/>' for i in range(5))
def claws(colour): return f'<path d="M330 640 q-110 -40 -140 20 q40 40 90 20 l-30 40 q60 20 90 -30z M694 640 q110 -40 140 20 q-40 40 -90 20 l30 40 q-60 20 -90 -30z" fill="{colour}"/>'
def bell(colour): return f'<path d="M262 520 a250 200 0 0 1 500 0 q-250 40 -500 0z" fill="{colour}" opacity=".85"/>' + "".join(f'<path d="M{360+i*60} 560 q{-20+i*8} 120 {10} 220" fill="none" stroke="{colour}" stroke-width="14" stroke-linecap="round" opacity=".8"/>' for i in range(6))
def teeth(): return f'<rect x="490" y="596" width="20" height="22" rx="4" fill="#fff" stroke="{INK}" stroke-width="4"/><rect x="514" y="596" width="20" height="22" rx="4" fill="#fff" stroke="{INK}" stroke-width="4"/>'
def tail_flat(colour): return f'<path d="M560 740 q140 0 170 80 q-90 30 -190 -20z" fill="{colour}"/>' + "".join(f'<path d="M{600+i*30} {760+i*10} l20 30" stroke="{INK}" stroke-width="4" opacity=".4"/>' for i in range(4))
def antennae(colour): return f'<path d="M470 240 q-30 -120 -90 -140 M554 240 q30 -120 90 -140" fill="none" stroke="{colour}" stroke-width="12" stroke-linecap="round"/><circle cx="380" cy="100" r="16" fill="{colour}"/><circle cx="644" cy="100" r="16" fill="{colour}"/>'

# ---------- props ----------
def bow(colour, x=640, y=250): return f'<g transform="translate({x} {y})"><path d="M0 0 q-60 -50 -70 0 q10 50 70 0 q60 -50 70 0 q-10 50 -70 0z" fill="{colour}" stroke="{INK}" stroke-width="6"/><circle r="14" fill="{colour}" stroke="{INK}" stroke-width="6"/></g>'
def ball(): return f'<circle cx="330" cy="760" r="60" fill="{RED}" stroke="{INK}" stroke-width="6"/><path d="M270 760 h120 M330 700 v120" stroke="#fff" stroke-width="8"/>'
def book(colour): return f'<g transform="rotate(-10 700 720)"><rect x="640" y="660" width="120" height="140" rx="8" fill="{colour}" stroke="{INK}" stroke-width="6"/><rect x="652" y="672" width="96" height="116" rx="4" fill="{CREAM}"/><path d="M668 700 h64 M668 725 h64 M668 750 h40" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g>'
def kite(colour): return f'<path d="M760 250 l60 90 l-60 90 l-60 -90z" fill="{colour}" stroke="{INK}" stroke-width="6"/><path d="M760 430 q-20 60 10 90 q-30 40 0 80" fill="none" stroke="{INK}" stroke-width="5"/><path d="M760 430 q-100 200 -160 260" fill="none" stroke="{INK}" stroke-width="4" stroke-dasharray="8 8"/>'
def scarf(colour): return f'<path d="M400 660 q112 60 224 0 v40 q-112 60 -224 0z" fill="{colour}"/><path d="M600 690 q40 60 20 120 q-30 -40 -60 -60z" fill="{colour}"/>'
def glasses(): return f'<circle cx="412" cy="455" r="74" fill="none" stroke="{INK}" stroke-width="10"/><circle cx="612" cy="455" r="74" fill="none" stroke="{INK}" stroke-width="10"/><path d="M486 455 h52" stroke="{INK}" stroke-width="10"/>'
def headphones(colour): return f'<path d="M270 440 q0 -220 242 -220 q242 0 242 220" fill="none" stroke="{colour}" stroke-width="18" stroke-linecap="round"/><rect x="244" y="420" width="52" height="90" rx="20" fill="{colour}"/><rect x="728" y="420" width="52" height="90" rx="20" fill="{colour}"/>'
def pacifier(): return f'<ellipse cx="512" cy="600" rx="50" ry="24" fill="{TEAL}" stroke="{INK}" stroke-width="6"/><circle cx="512" cy="600" r="16" fill="{GOLD}" stroke="{INK}" stroke-width="5"/>'
def backpack(colour): return f'<rect x="300" y="640" width="110" height="140" rx="22" fill="{colour}" stroke="{INK}" stroke-width="6"/><rect x="320" y="700" width="70" height="50" rx="10" fill="{CREAM}" stroke="{INK}" stroke-width="5"/><path d="M330 640 q25 -40 50 0" fill="none" stroke="{INK}" stroke-width="8"/>'
def fish_prop(): return f'<g transform="rotate(20 700 720)"><path d="M640 720 q60 -50 120 0 q-60 50 -120 0z" fill="#8fb5c9" stroke="{INK}" stroke-width="6"/><path d="M760 720 l40 -30 v60z" fill="#8fb5c9" stroke="{INK}" stroke-width="6"/><circle cx="668" cy="712" r="6" fill="{INK}"/></g>'
def flower(colour, x=350, y=260): return f'<g transform="translate({x} {y})">' + "".join(f'<ellipse cx="0" cy="-34" rx="16" ry="30" fill="{colour}" stroke="{INK}" stroke-width="4" transform="rotate({a})"/>' for a in range(0, 360, 60)) + f'<circle r="16" fill="{GOLD}" stroke="{INK}" stroke-width="4"/></g>'
def shell(): return f'<g transform="translate(330 740) rotate(-15)"><path d="M0 40 a70 70 0 0 1 140 0z" fill="#f3d6c1" stroke="{INK}" stroke-width="6"/>' + "".join(f'<path d="M70 40 l{-60+i*30} -60" stroke="{INK}" stroke-width="4"/>' for i in range(5)) + '</g>'
def mug(): return f'<rect x="640" y="700" width="90" height="100" rx="14" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M730 730 q50 0 50 35 q0 35 -50 35" fill="none" stroke="{INK}" stroke-width="8"/><path d="M660 690 q10 -30 0 -50 M700 690 q10 -30 0 -50" fill="none" stroke="{INK}" stroke-width="5" opacity=".5"/>'
def bucket(): return f'<path d="M290 700 h120 l-14 110 h-92z" fill="{TEAL}" stroke="{INK}" stroke-width="6"/><path d="M290 700 q60 -80 120 0" fill="none" stroke="{INK}" stroke-width="8"/><path d="M300 720 h100" stroke="#fff" stroke-width="6" opacity=".6"/>'
def pencil(): return f'<g transform="rotate(-40 700 720)"><rect x="640" y="700" width="160" height="34" rx="6" fill="{GOLD}" stroke="{INK}" stroke-width="6"/><path d="M800 700 l40 17 l-40 17z" fill="#f3d6c1" stroke="{INK}" stroke-width="6"/><rect x="640" y="700" width="30" height="34" fill="{RED}" stroke="{INK}" stroke-width="6"/></g>'
def lantern_small(): return f'<path d="M330 600 v40" stroke="{INK}" stroke-width="8"/><rect x="290" y="640" width="80" height="110" rx="12" fill="#fff2b0" stroke="{INK}" stroke-width="7"/><rect x="284" y="632" width="92" height="16" rx="6" fill="{INK}"/><rect x="284" y="742" width="92" height="16" rx="6" fill="{INK}"/>'
def cap(colour): return f'<path d="M290 330 a222 222 0 0 1 444 0z" fill="{colour}" stroke="{INK}" stroke-width="6"/><path d="M734 330 h110 q10 20 -10 30 h-100z" fill="{colour}" stroke="{INK}" stroke-width="6"/>'
def beanie(colour): return f'<path d="M290 330 a222 222 0 0 1 444 0 q-222 -30 -444 0z" fill="{colour}" stroke="{INK}" stroke-width="6"/><circle cx="512" cy="120" r="34" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>'
def bandana(colour): return f'<path d="M280 330 q232 -60 464 0 q-40 40 -232 40 q-192 0 -232 -40z" fill="{colour}"/><path d="M280 330 l-60 40 l70 10z" fill="{colour}"/>'
def sparkles(): return f'<path d="M780 700 l6 16 l16 6 l-16 6 l-6 16 l-6 -16 l-16 -6 l16 -6z M820 640 l4 10 l10 4 l-10 4 l-4 10 l-4 -10 l-10 -4 l10 -4z" fill="{GOLD}"/>'
def balloon(colour): return f'<ellipse cx="800" cy="300" rx="70" ry="86" fill="{colour}" stroke="{INK}" stroke-width="6"/><path d="M800 386 l-10 16 h20z" fill="{colour}" stroke="{INK}" stroke-width="5"/><path d="M800 402 q-40 150 -180 250" fill="none" stroke="{INK}" stroke-width="4"/>'
def crown(): return f'<path d="M400 250 l20 -110 l60 60 l32 -90 l32 90 l60 -60 l20 110z" fill="{GOLD}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
def bowtie(colour): return f'<path d="M472 640 l-50 -26 v52z M552 640 l50 -26 v52z" fill="{colour}" stroke="{INK}" stroke-width="5"/><circle cx="512" cy="640" r="12" fill="{colour}" stroke="{INK}" stroke-width="5"/>'

# ---------- the shared chibi ----------
def chibi(spec):
    s = field(spec["field"], spec.get("sparkle", [(190, 200, 6), (840, 190, 5), (860, 640, 6), (160, 640, 4), (690, 820, 5)])) + shadow()
    for part in spec.get("behind", []): s += part
    s += body(spec["body"], spec.get("belly"))
    for part in spec.get("mid", []): s += part
    s += head(spec.get("head", spec["body"]))
    if spec.get("bib"): s += bib(spec["bib"])
    if spec.get("mask"): s += mask(spec["mask"])
    for part in spec.get("face", []): s += part
    s += eyes(512, 455, spec.get("gap", 100), spec.get("eye", 58), spec["iris"], look=spec.get("look", (0, 0)), wink=spec.get("wink", False))
    s += blush(512, 545, 140)
    s += spec.get("mouth", mouth(512, 590, 40))
    for part in spec.get("front", []): s += part
    return s + caption(spec["kana"], spec["romaji"], spec["role"])

CHARS = [
 # Waku's pod
 dict(name="minke", kana="ミンク", romaji="MINKE", role="little cousin", title="Minke, the little cousin", text="Waku's little cousin, half the size and twice the questions. Ball under one flipper, always.", field="#cfe6e4", body="#4a5a66", belly="#e8eef2", head="#4a5a66", mask="#e8eef2", iris="#2f5f8f", eye=64, behind=[dorsal("#4a5a66")], mid=[flippers("#4a5a66")], front=[ball()]),
 dict(name="humpback", kana="ザトウ", romaji="HUMPBACK", role="uncle", title="Humpback, the uncle", text="The big uncle who sings at the family dinner whether anyone asked. Bumps on the chin, barnacles he calls character.", field="#d6e3ec", body="#3d4f5c", belly="#dfe7ee", head="#3d4f5c", mask="#dfe7ee", iris="#3f6e8f", face=[f'<circle cx="420" cy="380" r="9" fill="#9aa8b0"/><circle cx="600" cy="370" r="9" fill="#9aa8b0"/><circle cx="512" cy="330" r="9" fill="#9aa8b0"/>'], mid=[flippers("#3d4f5c")], front=[headphones(TEAL)]),
 dict(name="porpoise", kana="ネズミイルカ", romaji="PORPOISE", role="old friend", title="Porpoise, the old friend", text="Waku's friend from the harbour days. Shy, quick, gone before the photo. Wears the scarf Heron knitted.", field="#dfe8f2", body="#6f7f8a", belly="#e9eef2", head="#6f7f8a", mask="#e9eef2", iris="#4a6f8f", look=(-6, 0), mid=[flippers("#6f7f8a")], front=[scarf(RED)]),
 dict(name="dolphin", kana="イルカ", romaji="DOLPHIN", role="friend", title="Dolphin, the friend", text="Talks fast, jumps for no reason, keeps the pod laughing. Balloon from the last birthday, still up.", field="#d9ecf2", body="#8fb5c9", belly="#eef5f8", head="#8fb5c9", mask="#eef5f8", iris="#2f6f8f", mouth=mouth(512, 590, 44, open_=True), behind=[dorsal("#8fb5c9"), balloon(GOLD)], mid=[flippers("#8fb5c9")]),
 dict(name="sealion", kana="アシカ", romaji="SEA LION", role="neighbour", title="Sea Lion, the neighbour", text="Barks from the dock, mostly at nothing. Bandana, whiskers, a mug of something hot.", field="#eadfcf", body="#8a6a48", belly="#c9a882", head="#8a6a48", iris="#5a3f2a", face=[snout("#a88664"), whiskers()], mouth="", mid=[flippers("#8a6a48")], front=[bandana(RED), mug()]),
 dict(name="otter", kana="ラッコ", romaji="OTTER", role="friend", title="Otter, the friend", text="Floats on her back holding a shell she is not going to open yet. Everyone's favourite; she knows.", field="#e6e2d6", body="#6b5238", belly="#c7b08f", head="#6b5238", bib="#d9c5a5", iris="#3b2a1c", face=[ears_round("#6b5238", "#c7b08f", 40, 290), snout("#d9c5a5", 570), whiskers(570)], mouth="", front=[shell()]),
 dict(name="seal", kana="アザラシ", romaji="SEAL", role="friend", title="Seal, the friend", text="Harbour seal, spotted, round, asleep on the ramp until something interesting happens. Pacifier is a joke that stuck.", field="#e3e6ea", body="#9aa3ad", belly="#d7dce2", head="#9aa3ad", iris="#2a2a2a", eye=66, face=[f'<circle cx="400" cy="380" r="10" fill="#6f7882"/><circle cx="640" cy="400" r="8" fill="#6f7882"/><circle cx="560" cy="340" r="7" fill="#6f7882"/>', snout("#c9ced4", 566), whiskers(566)], mouth="", front=[pacifier()]),
 # Heron's family
 dict(name="puffin", kana="パフィン", romaji="PUFFIN", role="Heron's nephew", title="Puffin, the nephew", text="Heron's nephew, apprentice scout. The beak is bigger than the plan. Backpack packed for a trip nobody has announced.", field="#dfe8f2", body="#2a2f38", belly="#f2f2f2", head="#2a2f38", bib="#f2f2f2", iris="#3f3f3f", eye=60, face=[beak_puffin()], mouth="", mid=[wings("#2a2f38")], front=[backpack(RED)]),
 dict(name="kingfisher", kana="カワセミ", romaji="KINGFISHER", role="Heron's sister", title="Kingfisher, the sister", text="Heron's sister, faster and louder. Turquoise back, rust front, one fish, no comment.", field="#d9ecf2", body="#2a8fa8", belly="#d8804f", head="#2a8fa8", bib="#e9c39a", iris="#1f3f4f", face=[crest("#2a8fa8", 2), beak("#3a3a3a", .9)], mouth="", mid=[wings("#2a8fa8")], front=[fish_prop()]),
 dict(name="sandpiper", kana="シギ", romaji="SANDPIPER", role="Heron's little one", title="Sandpiper, the little one", text="Heron's youngest, runs the tide line back and forth for the joy of it. Bucket, no plan for the bucket.", field="#efe6d3", body="#b89a72", belly="#f3ebdc", head="#b89a72", bib="#f3ebdc", iris="#4a3a28", eye=66, face=[beak_small("#4a4a4a")], mouth="", mid=[legs(GOLD)], front=[bucket()]),
 dict(name="egret", kana="サギ", romaji="EGRET", role="Heron's grandmother", title="Egret, the grandmother", text="Heron's grandmother, all white, all patience. Glasses for the reading, not the looking.", field="#eef0e8", body="#f5f5f0", belly=None, head="#f5f5f0", iris="#6b7f8f", face=[tuft("#f5f5f0"), beak(GOLD, .9)], mouth="", mid=[legs("#3a3a3a")], front=[glasses(), book("#8a5a32")]),
 # Raven's family
 dict(name="crow", kana="カラス", romaji="CROW", role="Raven's brother", title="Crow, the brother", text="Raven's brother, the one without the keys and fine with it. Collects shiny things; the crown was on sale.", field="#e4e2ea", body="#23252b", belly="#3a3d45", head="#23252b", iris="#7a8b99", face=[beak("#2f2f2f", .8)], mouth="", mid=[wings("#23252b")], front=[crown()]),
 dict(name="jay", kana="カケス", romaji="JAY", role="Raven's kid", title="Jay, the kid", text="Steller's jay, Raven's kid, blue as a gas flame with a black crest that will not stay down. Kite weather is every weather.", field="#dbe3f2", body="#2a5fb8", belly="#3b74d1", head="#1e1e28", bib="#2a5fb8", iris="#1a2a3a", eye=64, face=[crest("#1e1e28", 3), beak("#2f2f2f", .7)], mouth="", mid=[wings("#2a5fb8")], behind=[kite(RED)]),
 dict(name="magpie", kana="カササギ", romaji="MAGPIE", role="Raven's cousin", title="Magpie, the cousin", text="Raven's cousin from the other side of the mountains. Black and white and a green sheen when the light is right. Bow tie for no occasion.", field="#e6e6e6", body="#1f2228", belly="#f2f2f2", head="#1f2228", bib="#f2f2f2", iris="#3f5f4f", face=[beak("#2f2f2f", .8)], mouth="", mid=[wings("#1f2228")], front=[bowtie(RED)]),
 dict(name="nutcracker", kana="ホシガラス", romaji="NUTCRACKER", role="Raven's aunt", title="Nutcracker, the aunt", text="Clark's nutcracker, Raven's aunt from the high passes. Remembers where every seed is buried. Pencil behind the wing, a list in the head.", field="#e8e4dc", body="#9a9a9a", belly="#d5d5d5", head="#9a9a9a", bib="#d5d5d5", iris="#3a3a3a", face=[beak("#2f2f2f", 1.0)], mouth="", mid=[wings("#1f2228")], front=[pencil()]),
 # Salmon's family
 dict(name="trout", kana="マス", romaji="TROUT", role="Salmon's cousin", title="Trout, the cousin", text="Salmon's freshwater cousin who never went to sea and doesn't see the point. Speckled, content, reading.", field="#dfe9dc", body="#7a9a6a", belly="#e8efd8", head="#7a9a6a", bib="#e8efd8", iris="#2f4f2f", face=[f'<circle cx="400" cy="370" r="8" fill="#3f5f3f"/><circle cx="620" cy="360" r="8" fill="#3f5f3f"/><circle cx="520" cy="320" r="7" fill="#3f5f3f"/><circle cx="450" cy="300" r="6" fill="#3f5f3f"/>'], behind=[tail_fish("#7a9a6a")], mid=[fins("#7a9a6a")], front=[book(TEAL)]),
 dict(name="steelhead", kana="スチールヘッド", romaji="STEELHEAD", role="Salmon's big sister", title="Steelhead, the big sister", text="Salmon's big sister: went to sea, came back, went again. Silver, a rose stripe, headphones for the long swims.", field="#e2e6ea", body="#a9b3bd", belly="#eef0f2", head="#a9b3bd", bib="#eef0f2", iris="#3f4f5f", face=[f'<path d="M290 520 q222 -30 444 0 q-222 40 -444 0z" fill="#e3a0a8" opacity=".7"/>'], behind=[tail_fish("#a9b3bd")], mid=[fins("#a9b3bd")], front=[headphones(RED)]),
 dict(name="herring", kana="ニシン", romaji="HERRING", role="Salmon's little one", title="Herring, the little one", text="Salmon's littlest, one of ten thousand, and the only one with a name. Sparkles because the light does that on herring.", field="#e6eef4", body="#b8c8d6", belly="#f2f6f8", head="#b8c8d6", bib="#f2f6f8", iris="#2f4f6f", eye=68, behind=[tail_fish("#b8c8d6")], mid=[fins("#b8c8d6")], front=[sparkles()]),
 dict(name="sturgeon", kana="チョウザメ", romaji="STURGEON", role="Salmon's great-uncle", title="Sturgeon, the great-uncle", text="Salmon's great-uncle, older than the bridge, armoured, unhurried. Cap from a boat that no longer exists.", field="#e3e0d8", body="#6f6a5e", belly="#c9c2b2", head="#6f6a5e", bib="#c9c2b2", iris="#3a3a2a", face=[whiskers(600)], behind=[tail_fish("#6f6a5e")], mid=[fins("#6f6a5e")], front=[cap(TEAL)]),
 # Osprey's family
 dict(name="eagle", kana="ワシ", romaji="EAGLE", role="Osprey's grandfather", title="Eagle, the grandfather", text="Bald eagle, Osprey's grandfather, sits in the same snag every morning judging the harbour. White head, gold beak, no jokes.", field="#e6e2d8", body="#4a3624", belly="#5a4530", head="#f2f2f2", iris="#c98a1e", face=[beak(GOLD, 1.0)], mouth="", mid=[wings("#4a3624")], front=[glasses()]),
 dict(name="owl", kana="フクロウ", romaji="OWL", role="Osprey's aunt", title="Owl, the aunt", text="Barred owl, Osprey's aunt, runs the night shift and says so. Lantern, ear tufts, the look.", field="#e2dfe8", body="#8a7a66", belly="#d8ccb8", head="#8a7a66", bib="#d8ccb8", iris="#2a2a2a", eye=70, gap=104, face=[ears_point("#8a7a66", "#d8ccb8"), beak_small("#3f3f3f", 556)], mouth="", mid=[wings("#8a7a66")], front=[lantern_small()]),
 dict(name="hawk", kana="タカ", romaji="HAWK", role="Osprey's kid", title="Hawk, the kid", text="Red-tailed hawk, Osprey's kid, learning the watch by doing it wrong first. Beanie because the wind is real.", field="#eadfcf", body="#9a6a44", belly="#e8d3b8", head="#9a6a44", bib="#e8d3b8", iris="#5a3a1a", eye=62, face=[beak("#3f3f3f", .8)], mouth="", mid=[wings("#9a6a44")], front=[beanie(RED)]),
 dict(name="falcon", kana="ハヤブサ", romaji="FALCON", role="Osprey's friend", title="Falcon, the friend", text="Peregrine, Osprey's friend from the cliffs, fastest thing on the coast and quiet about it. Bandana, no other equipment.", field="#dfe3ea", body="#3f4a58", belly="#e3e6ea", head="#3f4a58", bib="#e3e6ea", iris="#2a2a2a", face=[f'<path d="M420 470 q-30 60 0 110 M604 470 q30 60 0 110" fill="none" stroke="#3f4a58" stroke-width="22" stroke-linecap="round"/>', beak("#3f3f3f", .8)], mouth="", mid=[wings("#3f4a58")], front=[bandana(TEAL)]),
 # Cormorant's family and the shore
 dict(name="loon", kana="アビ", romaji="LOON", role="Cormorant's friend", title="Loon, the friend", text="Cormorant's friend from the lake. Checkerboard back, a red eye, a call that empties the campground. Flower behind the ear, always.", field="#dfe9ec", body="#1f2a30", belly="#eef2f4", head="#1f2a30", bib="#eef2f4", iris="#c8323a", face=[f'<path d="M290 700 h444" stroke="#eef2f4" stroke-width="8" stroke-dasharray="14 14"/>', beak("#2f2f2f", .9)], mouth="", mid=[wings("#1f2a30")], front=[flower(RED)]),
 dict(name="grebe", kana="カイツブリ", romaji="GREBE", role="Cormorant's cousin", title="Grebe, the cousin", text="Cormorant's cousin, dives before you've finished the sentence. Rust neck, a crest that has opinions.", field="#e6e2da", body="#8a4a3a", belly="#e8d8c8", head="#2a2a2a", bib="#e8d8c8", iris="#c8323a", face=[crest("#2a2a2a", 3), beak(GOLD, .8)], mouth="", mid=[wings("#8a4a3a")], front=[bowtie(GOLD)]),
 dict(name="murre", kana="ウミガラス", romaji="MURRE", role="Cormorant's kid", title="Murre, the kid", text="Cormorant's kid, black and white like a small waiter, stands on the ledge with a thousand others and still thinks it is a solo act.", field="#e4e6ea", body="#23252b", belly="#f2f2f2", head="#23252b", bib="#f2f2f2", iris="#3f3f3f", eye=64, face=[beak("#2f2f2f", .8)], mouth="", mid=[wings("#23252b")], front=[bow(RED, 640, 260)]),
 dict(name="crab", kana="カニ", romaji="CRAB", role="the reviewer's reviewer", title="Crab, the reviewer's reviewer", text="Dungeness, Cormorant's oldest friend, reviews the reviewer. Sideways is a choice. The claws are for emphasis.", field="#f2e2d8", body="#c8623a", belly="#e8a888", head="#c8623a", iris="#2a2a2a", eye=52, gap=96, face=[antennae("#c8623a")], mid=[claws("#c8623a")], front=[glasses()]),
 dict(name="octopus", kana="タコ", romaji="OCTOPUS", role="the fixer", title="Octopus, the fixer", text="Giant Pacific octopus, everybody's friend, eight things at once and a ninth in mind. Escapes anything, returns the key.", field="#eadfe8", body="#a85a6a", belly=None, head="#a85a6a", iris="#3f2f4f", eye=60, behind=[tentacles("#a85a6a")], face=[f'<circle cx="380" cy="360" r="10" fill="#d89aa8"/><circle cx="640" cy="350" r="12" fill="#d89aa8"/><circle cx="512" cy="300" r="8" fill="#d89aa8"/>'], front=[headphones(GOLD)]),
 dict(name="seastar", kana="ヒトデ", romaji="SEA STAR", role="the youngest", title="Sea Star, the youngest", text="Ochre star from the tide pools, the youngest in the whole set, five arms and no idea which is the front. Sparkles, obviously.", field="#f5e6d6", body="#d97a3a", belly=None, head="#d97a3a", iris="#3f2a1a", eye=66, gap=90, behind=[arms_star("#d97a3a")], face=[f'<circle cx="440" cy="340" r="7" fill="#f2b890"/><circle cx="590" cy="330" r="7" fill="#f2b890"/><circle cx="512" cy="290" r="7" fill="#f2b890"/>'], front=[sparkles()]),
 dict(name="jellyfish", kana="クラゲ", romaji="JELLYFISH", role="the dreamer", title="Jellyfish, the dreamer", text="Moon jelly, drifts in on the tide and drifts out, never in a hurry, never lost. Nobody knows what she does; she does it well.", field="#e3e8f2", body="#c9d8ee", belly=None, head="#dbe6f4", iris="#6f8fbf", eye=60, look=(0, -4), behind=[bell("#c9d8ee")], front=[bow("#f4a1a8", 640, 250)]),
 dict(name="beaver", kana="ビーバー", romaji="BEAVER", role="the builder", title="Beaver, the builder", text="Lives up the creek, builds the thing before the meeting about the thing. Teeth, tail, pencil; the plan is in the wood.", field="#e8e0d0", body="#6b4a2e", belly="#a88660", head="#6b4a2e", bib="#a88660", iris="#3a2a1a", face=[ears_round("#6b4a2e", "#a88660", 44, 280), snout("#c9a882", 560), teeth()], mouth="", behind=[tail_flat("#4a3a2a")], front=[pencil()]),
]

def main():
    out = []
    for c in CHARS:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{chibi(c)}</svg>'
        open(os.path.join(HERE, f'family-{c["name"]}.svg'), "w").write(svg)
        out.append({"name": c["name"], "title": c["title"], "text": c["text"], "role": c["role"]})
    json.dump(out, open(os.path.join(HERE, "family.json"), "w"), indent=0, ensure_ascii=False)
    print(len(out), "characters")

if __name__ == "__main__": main()

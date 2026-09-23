#!/usr/bin/env python3
"""Diagram as code, diagram as art: the sources for /diagrams.

ART: Japanese motifs drawn in ASCII, hand-composed, width-checked.
BLUEPRINTS: the lab's own architecture, scrubbed of personal data (no addresses, hostnames,
people, account ids), each as an ASCII box map and a Mermaid flowchart of the same thing.
tools/build-diagrams.sh renders every entry to a watermarked JPEG; this file is the source.
"""

ART = [
("torii", "Torii", "The gate, in eleven lines of pipe and underscore. Two lintels, two posts, the space between them is the point.", r"""
        ________________________________
       /________________________________\
           |                        |
         __|________________________|__
           |                        |
           |                        |
           |                        |
           |                        |
           |                        |
         __|__                    __|__
"""),
("fuji", "Fuji", "Snow on the shoulders as a zigzag, the sun as a period. Every woodblock does the same three things.", r"""
                                              .-.
                                             ( o )
                                              `-'
                        /\
                       /  \
                      / /\ \
                     / /  \ \
                    /_/ /\ \_\
                   /   /  \   \
                  /   /    \   \
                 /   /      \   \
                /___/        \___\
               /                  \
              /                    \
     ~~~~~~~~/~~~~~~~~~~~~~~~~~~~~~~\~~~~~~~~~~
"""),
("wave", "The wave", "Hokusai's claw as one long curl rising from the left, the spray as periods. The boat is not in this one; the boat never had a chance.", r"""
                                     _
                                  ,-' `-.
                               ,-'  ,--.  `.
                             ,'   ,'    `.  \
                           ,'   ,'   ,-.  \  \
                         ,'   ,'   ,'  `. |  |
                       ,'   ,'   ,'      ||  |       .  .
                     ,'   ,'   ,'   ,-.  ||  |     .  .  .
                   ,'   ,'   ,'   ,'   `.||  |   .  .
                 ,'   ,'   ,'   ,'      `-'  |
       ~~~~~~~~,'~~~,'~~~~,'~~~~,'~~~~~~~~~~~`~~~~~~~~~~~~~~
"""),
("crane", "Tsuru", "The crane, standing. The head is three characters; the legs are the same pipe as the torii posts.", r"""
                        __
                       (o >
                        \ \
                         \ \
            ___________   \ \___________
           /           \___\____________\
          /                              \
         /                                \
        /__________________________________\
                  |  |        |  |
                  |  |        |  |
                 _|  |_      _|  |_
"""),
("chochin", "Chōchin", "The paper lantern: a hood, six ribs, a tassel. The ribs are underscores because that is what ribs are.", r"""
                   _________
                  |_________|
               .-'           '-.
              /  _____________  \
             |  |_____________|  |
             |  |_____________|  |
             |  |_____________|  |
             |  |_____________|  |
             |  |_____________|  |
              \ _______________ /
               '-._____________.-'
                  |_________|
                      | |
                      | |
                     (___)
"""),
("pagoda", "Pagoda", "Three stories of roof and lath. Each roof is one line wider than the one above, which is the whole trick of a pagoda.", r"""
                          _|_
                         /___\
                 _______/_____\_______
                '---------------------'
                     |  []   []  |
            ________/_____________\________
           '-------------------------------'
                 |  []   []   []   []  |
       _________/_________________________\_________
      '-------------------------------------------'
            |   []   []   []   []   []   []   |
      ______|___________________________________|______
"""),
("daruma", "Daruma", "One eye painted. The other waits for the goal. Round, weighted, gets back up: the whole doll is a proverb.", r"""
                    .-''''''''''-.
                  ,'              `.
                 /   ___      ___   \
                |   (   )    (   )   |
                |    \_/      ` '    |
                |                    |
                |       \____/       |
                 \                  /
                  \                /
                   `-.__________.-'
"""),
("bamboo", "Take", "Three culms, the nodes as double bars, leaves as slashes. Bends in wind; drawn straight because ASCII does not bend.", r"""
              \\        //
             \\\\      ////     \\
            ||  ||    ||  ||    \\\\
            ||  ||    ||  ||   ||  ||
            ||==||    ||==||   ||  ||
            ||  ||    ||  ||   ||==||
            ||  ||    ||==||   ||  ||
            ||==||    ||  ||   ||  ||
            ||  ||    ||  ||   ||==||
            ||  ||    ||==||   ||  ||
            ||==||    ||  ||   ||  ||
            ||  ||    ||  ||   ||  ||
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""),
]

# Orca set (Alex, 2026-09-23: "Japanese and orca inspired ascii art ... and the mermaid diagram
# equivalent too"). Each of these carries a Mermaid version of the same subject, so the piece is
# drawn twice: once as a picture, once as a graph. ART entries below are 5-tuples; the eight above
# are 4-tuples and render as a single image, as they always have.
ART_MMD = [
("shachi", "Shachi", "An orca surfacing: the back breaks first, then the fin, and that is the whole of what the water gives you. Japanese writes the animal 鯱, the fish radical beside the tiger, a tiger being the nearest thing they had to compare it to.", r"""
                                     /|
                                    / |
                                   /  |
                                  /   |
                                 /    |
                                /     |
                               /      |
                  ____________/       |___________
             ____/                                \____
        ____/                                          \____
   ,.--'                                                     `--.,
  '                                                               `
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""", r"""
flowchart TD
  A["breach<br/>fin clears first"] --> B["arc<br/>the whole body leaves"]
  B --> C["fall<br/>flank meets water"]
  C --> D["report<br/>heard a mile down the channel"]
  D --> E["dive<br/>five to fifteen minutes"]
  E --> A
"""),
("pod", "The pod", "Four dorsal fins at the surface and nothing else showing. Tallest is a bull, the straight blades are cows and a calf tucked beside one of them. This is the whole of what you see from a beach.", r"""
                 /|
                / |
               /  |                /|
              /   |               / |            /|
             /    |              /  |           / |        /|
            /     |             /   |          /  |       / |
       ____/      |________ ___/    |______ __/   |_____ /  |____
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""", r"""
flowchart TD
  G["grandmother<br/>post-reproductive, leads"] --> M1["daughter"]
  G --> M2["daughter"]
  G --> S["son<br/>stays in the matriline for life"]
  M1 --> C1["calf"]
  M1 --> C2["calf"]
  M2 --> C3["calf"]
"""),
("seigaiha", "Seigaiha", "Blue sea waves. Concentric arcs, each rank offset by half a wave, repeating until the eye gives up and reads it as water. The oldest pattern here and the only one that tiles.", r"""
     .-""-.     .-""-.     .-""-.     .-""-.     .-""-.     .-""-.
    /  .-. \   /  .-. \   /  .-. \   /  .-. \   /  .-. \   /  .-. \
   |  /   \ | |  /   \ | |  /   \ | |  /   \ | |  /   \ | |  /   \ |
  .-""-.   .-""-.   .-""-.   .-""-.   .-""-.   .-""-.   .-""-.
 /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \
|  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |
 \ .-""-. \ .-""-. \ .-""-. \ .-""-. \ .-""-. \ .-""-. \ .-""-.
  /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \ /  .-. \
 |  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |  /   \ |
""", r"""
flowchart LR
  A["one arc"] --> B["rank of arcs<br/>drawn edge to edge"]
  B --> C["next rank<br/>offset by half a wave"]
  C --> D["overlap<br/>each arc covers the joins below"]
  D --> B
"""),
]

MERMAID_INIT ="%%{init: {'theme':'base','themeVariables':{'primaryColor':'#fbf7ef','primaryTextColor':'#1f3a3a','primaryBorderColor':'#1f3a3a','lineColor':'#1f3a3a','secondaryColor':'#f1e3c3','tertiaryColor':'#f1e3c3','fontFamily':'sans-serif','fontSize':'16px'}}}%%"

BLUEPRINTS = [
("estate", "The estate", "Public site at the edge, a private portal behind an identity gate, the lab at home behind a tunnel. Nothing at home listens to the internet.", r"""
 ┌─ Internet ────────────────────────────────────────────────────────┐
 │                                                                   │
 │   ┌─ Cloudflare edge ───────────────────────────────────────────┐ │
 │   │  DNS · TLS · WAF                                            │ │
 │   │  ┌─────────────────┐   ┌──────────────────┐  ┌───────────┐ │ │
 │   │  │ Public site     │   │ Private portal   │  │ Access    │ │ │
 │   │  │ Worker + assets │   │ Worker, D1, mail │◀─│ identity  │ │ │
 │   │  └─────────────────┘   └──────────────────┘  │ gate      │ │ │
 │   │                                              └─────┬─────┘ │ │
 │   └────────────────────────────────────────────────────┼───────┘ │
 └────────────────────────────────────────────────────────┼─────────┘
                                                          │ tunnel (outbound only)
 ┌─ Home lab ───────────────────────────────────────────┐ │
 │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │ │
 │  │ Inference    │  │ Sandbox tier │  │ Subnet     │◀─┘
 │  │ host         │  │ (hypervisor) │  │ router     │
 │  └──────────────┘  └──────────────┘  └────────────┘
 │  ┌──────────────┐  ┌──────────────┐
 │  │ Orchestrator │  │ KVM console  │   no inbound ports; remote
 │  │ (agents)     │  │ (out-of-band)│   access via the mesh only
 │  └──────────────┘  └──────────────┘
 └──────────────────────────────────────────────────────┘
""", MERMAID_INIT + r"""
flowchart TB
  subgraph EDGE["Cloudflare edge: DNS · TLS · WAF"]
    SITE["Public site<br/>Worker + static assets"]
    PORTAL["Private portal<br/>Worker + D1 + mail"]
    ACCESS["Access<br/>identity gate"]
    ACCESS --> PORTAL
  end
  subgraph LAB["Home lab: no inbound ports"]
    INF["Inference host"]
    SBX["Sandbox tier<br/>hypervisor"]
    RTR["Subnet router"]
    ORCH["Orchestrator<br/>agents"]
    KVM["KVM console<br/>out-of-band"]
  end
  Internet((Internet)) --> EDGE
  EDGE -. "tunnel, outbound only" .-> RTR
  RTR --- INF
  RTR --- SBX
  RTR --- ORCH
  RTR --- KVM
"""),
("agents", "The agent roster", "One voice, five roles, three model lanes. Fetch, act, verify: a claim of \"live\" without the verifier's pass is an open step.", r"""
 ┌─ Orchestrator (the one voice) ─────────────────────────────────────┐
 │                                                                    │
 │   Heron ──▶ Raven ──▶ Cormorant          Salmon        Osprey      │
 │   scout     courier   reviewer           scribe        watch       │
 │   fetches   the only  second             memory        scheduled   │
 │   outside   one with  confirmation       folds,        health,     │
 │   context   keys      before "live"      digests       silent on ok│
 │      │         │          │                 │             │        │
 └──────┼─────────┼──────────┼─────────────────┼─────────────┼────────┘
        ▼         ▼          ▼                 ▼             ▼
 ┌─ Model lanes ────────────────────────────────────────────────────┐
 │  subscription (judgement) │ metered API (secret + judgement,     │
 │  local model (pattern)    │ justified in writing)                │
 └──────────────────────────────────────────────────────────────────┘
 ┌─ Rules ──────────────────────────────────────────────────────────┐
 │  fetch → act → verify · two roles never share a spawn ·          │
 │  a courier argument is never sourced from scout output unread    │
 └──────────────────────────────────────────────────────────────────┘
""", MERMAID_INIT + r"""
flowchart LR
  ORCH["Orchestrator<br/>the one voice"]
  ORCH --> H["Heron · scout<br/>fetches outside context"]
  ORCH --> S["Salmon · scribe<br/>memory folds, digests"]
  ORCH --> O["Osprey · watch<br/>scheduled health"]
  H --> R["Raven · courier<br/>the only one with keys"]
  R --> C["Cormorant · reviewer<br/>second confirmation"]
  C -->|"live"| ORCH
  subgraph LANES["Model lanes"]
    L1["subscription: judgement"]
    L2["metered API: secret + judgement, justified"]
    L3["local model: pattern matching"]
  end
  H -.-> L2
  R -.-> L2
  S -.-> L1
  O -.-> L3
"""),
("publish", "The publish path", "A post is a markdown file. Everything after the commit is a machine: build, deploy, verify, mail. The human approves the draft, never the button.", r"""
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ draft.md │──▶│ build    │──▶│ Worker   │──▶│ verify   │──▶│ mail the │
 │ front-   │   │ one JS   │   │ upload   │   │ curl 200 │   │ list     │
 │ matter   │   │ bundle   │   │ + assets │   │ + diff   │   │ once     │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
      ▲              │                              │              │
      │              ▼                              ▼              ▼
 ┌──────────┐   ┌──────────┐                  ┌──────────┐   ┌──────────┐
 │ approve  │   │ feed.xml │                  │ receipt  │   │ sent-list│
 │ (human)  │   │ vCard    │                  │ logged   │   │ in git   │
 └──────────┘   └──────────┘                  └──────────┘   └──────────┘
   the only gate      every deploy is idempotent; a rerun never re-sends
""", MERMAID_INIT + r"""
flowchart LR
  A["approve<br/>(the human's only gate)"] --> D["draft.md<br/>front-matter"]
  D --> B["build<br/>one JS bundle"]
  B --> F["feed.xml · vCard"]
  B --> W["Worker upload<br/>+ assets"]
  W --> V["verify<br/>curl 200 + diff"]
  V --> M["mail the list<br/>exactly once"]
  V --> RC["receipt logged"]
  M --> SL["sent-list in git"]
"""),
("nightly", "Infrastructure as Music, nightly", "The lab plays its own state. Every night the recording is cut, measured, drawn and written, then published with the music.", r"""
 ┌─ every 15 min ─────────┐      ┌─ nightly ────────────────────────────┐
 │ health probe           │      │ cut episodes (song length)           │
 │  ok / fault / recover  │──┐   │   │                                  │
 └────────────────────────┘  │   │   ├─▶ measure: loudness, brightness, │
 ┌─ on change ────────────┐  │   │   │   events per bin                 │
 │ play a phrase          │◀─┘   │   ├─▶ draw one piece (SVG)           │
 │  deploy · fault · hello│──┐   │   ├─▶ write one haiku (same numbers) │
 └────────────────────────┘  │   │   └─▶ watermark · feed.json          │
 ┌─ recorder ─────────────┐  │   └──────────────────┬───────────────────┘
 │ 4-minute takes         │◀─┘                      ▼
 └────────────────────────┘             ┌─ publish ──────────────────┐
                                        │ /live · /art · RSS         │
   same night, same numbers, same       │ deterministic: rerun = same│
   drawing, forever                     └────────────────────────────┘
""", MERMAID_INIT + r"""
flowchart TB
  P["health probe<br/>every 15 min"] -->|"ok / fault / recover"| PH["play a phrase<br/>deploy · fault · hello"]
  PH --> REC["recorder<br/>4-minute takes"]
  REC --> CUT["nightly: cut episodes"]
  CUT --> MEAS["measure<br/>loudness · brightness · events"]
  MEAS --> DRAW["draw one piece (SVG)"]
  MEAS --> HAIKU["write one haiku"]
  DRAW --> WM["watermark"]
  HAIKU --> FEED["feed.json"]
  WM --> FEED
  FEED --> PUB["/live · /art · RSS"]
"""),
("secrets", "Where a secret can go", "The model never sees a credential. Names go in, a proxy swaps the value at the edge of the box, and the receipt comes back without it.", r"""
 ┌─ vault ─────────┐        ┌─ gateway host ─────────────────────────────┐
 │ password store  │        │                                            │
 │ + age keys      │───────▶│  env: TOKEN_X = <opaque sentinel>          │
 └─────────────────┘        │            │                               │
                            │            ▼                               │
 ┌─ model / agent ─┐        │  ┌──────────────────┐   ┌───────────────┐  │
 │ sees only the   │───────▶│  │ script or curl   │──▶│ egress proxy  │──┼─▶ api.vendor
 │ NAME, never the │  exec  │  │ (sentinel in hdr)│   │ swaps sentinel│  │
 │ value           │        │  └──────────────────┘   │ for the value │  │
 └─────────────────┘        │            ▲            └───────────────┘  │
        ▲                   │            │ allow-list of hosts only      │
        │ receipt: status,  └────────────┼───────────────────────────────┘
        │ never the header               │
        └────────────────────────────────┘
   interactive sessions never get the sentinel; scheduled jobs do, headless
""", MERMAID_INIT + r"""
flowchart LR
  V["vault<br/>password store + age keys"] --> ENV["gateway env<br/>TOKEN_X = opaque sentinel"]
  M["model / agent<br/>sees only the NAME"] -->|exec| SC["script or curl<br/>sentinel in header"]
  ENV --> SC
  SC --> PX["egress proxy<br/>swaps sentinel for value<br/>allow-listed hosts only"]
  PX --> API["vendor API"]
  SC -->|"receipt: status, never the header"| M
"""),
("request", "One request, edge to byte", "What happens to a URL on the public site: redirects, then the Worker, then either a built page from memory or a ranged asset from the edge store.", r"""
   client ──▶ edge ──▶ www → apex 301 ──▶ Worker fetch()
                                            │
              ┌─────────────────────────────┼───────────────────────┐
              ▼                             ▼                       ▼
        /media/*  (assets)          /inquire (POST)           everything else
        Range → 206 slices          validate → mail           PAGES[path] from
        (video seeks, audio         → 303 to /thanks          the build; 404 if
        loops on WebKit)                                      not in the map
              │                             │                       │
              └──────────────┬──────────────┘                       │
                             ▼                                      │
                  headers: CSP default-src 'none', HSTS,            │
                  no-store on forms, immutable on assets ◀──────────┘
""", MERMAID_INIT + r"""
flowchart TB
  C((client)) --> E["edge: DNS · TLS"]
  E --> R{"www?"}
  R -->|"301 to apex"| W
  R -->|no| W["Worker fetch()"]
  W --> A["/media/*<br/>ranged 206 slices"]
  W --> I["/inquire POST<br/>validate → mail → 303"]
  W --> P["PAGES[path]<br/>built HTML from memory"]
  P --> N["404 if not in the map"]
  A --> H["headers: strict CSP · HSTS<br/>no-store forms · immutable assets"]
  I --> H
  P --> H
"""),
]

def check_widths(limit=90):
    bad = []
    for name, _, _, body in ART:
        w = max(len(l) for l in body.splitlines())
        if w > limit: bad.append((name, w))
    for name, _, _, body, _ in ART_MMD:
        w = max(len(l) for l in body.splitlines())
        if w > limit: bad.append((name, w))
    for name, _, _, ascii_, _ in BLUEPRINTS:
        w = max(len(l) for l in ascii_.splitlines())
        if w > limit: bad.append((name, w))
    return bad

if __name__ == "__main__":
    import json, os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    bad = check_widths()
    if bad: sys.exit("too wide: " + str(bad))
    for name, title, text, body in ART:
        open(os.path.join(here, f"art-{name}.txt"), "w").write(body.strip("\n") + "\n")
    for name, title, text, body, mmd in ART_MMD:
        open(os.path.join(here, f"art-{name}.txt"), "w").write(body.strip("\n") + "\n")
        open(os.path.join(here, f"art-{name}.mmd"), "w").write(MERMAID_INIT + "\n" + mmd.strip("\n") + "\n")
    for name, title, text, ascii_, mmd in BLUEPRINTS:
        open(os.path.join(here, f"bp-{name}.txt"), "w").write(ascii_.strip("\n") + "\n")
        open(os.path.join(here, f"bp-{name}.mmd"), "w").write(mmd.strip("\n") + "\n")
    json.dump({"art": [{"name": n, "title": t, "text": x} for n, t, x, _ in ART]
                      + [{"name": n, "title": t, "text": x, "mermaid": True} for n, t, x, _, _ in ART_MMD],
               "blueprints": [{"name": n, "title": t, "text": x} for n, t, x, _, _ in BLUEPRINTS]},
              open(os.path.join(here, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(ART) + len(ART_MMD), "art (", len(ART_MMD), "with mermaid ),", len(BLUEPRINTS), "blueprints")

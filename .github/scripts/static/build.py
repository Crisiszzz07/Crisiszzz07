"""Genera los SVG estáticos del perfil (portada, consola, stack, entorno,
separador y botones de idioma) en español e inglés.

    python3 .github/scripts/static/build.py
"""

import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets"
ICONS = Path(__file__).parent / "icons"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

BG = """<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#240046"/></linearGradient>
  <linearGradient id="ico" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3e8ff"/><stop offset="1" stop-color="#c77dff"/></linearGradient>
  <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9d4edd"/><stop offset="1" stop-color="#ff6ec7"/></linearGradient>"""

STR = {
    "es": {
        "whoami": "Cristy · Ing. de Sistemas, 8vo semestre · Cartagena, CO",
        "focus": "DevSecOps · arquitectura de software · Linux · open source",
        "mixer": "controles de seguridad en cada etapa del pipeline",
        "main": "// lenguajes principales",
        "also": "// también he trabajado con",
        "learning": "// aprendiendo ahora",
        "setup": [
            ("fedora", "OS", "Fedora Linux · mi sistema del día a día"),
            ("kalilinux", "Distros", "Ubuntu · Kali Linux (en VM para labs)"),
            ("podman", "Contenedores", "Podman · Docker"),
            ("qemu", "Virtualización", "virt-manager (KVM/QEMU)"),
            ("gnubash", "Shell", "bash"),
            ("pnpm", "Paquetes JS", "pnpm"),
            ("git", "Versiones", "git · GitHub CLI"),
        ],
    },
    "en": {
        "whoami": "Cristy · Systems Engineering, 8th semester · Cartagena, CO",
        "focus": "DevSecOps · software architecture · Linux · open source",
        "mixer": "security checks at every stage of the pipeline",
        "main": "// main languages",
        "also": "// also worked with",
        "learning": "// currently learning",
        "setup": [
            ("fedora", "OS", "Fedora Linux · my daily driver"),
            ("kalilinux", "Distros", "Ubuntu · Kali Linux (VM for labs)"),
            ("podman", "Containers", "Podman · Docker"),
            ("qemu", "Virtualization", "virt-manager (KVM/QEMU)"),
            ("gnubash", "Shell", "bash"),
            ("pnpm", "JS packages", "pnpm"),
            ("git", "VCS", "git · GitHub CLI"),
        ],
    },
}


def icon(name, x, y, size, fill="url(#ico)"):
    d = (ICONS / f"{name}.path").read_text().strip()
    return f'<path transform="translate({x:.1f},{y:.1f}) scale({size / 24:.3f})" fill="{fill}" fill-rule="evenodd" d="{d}"/>'


def svg(w, h, body, style="", defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<defs>
  {BG}
  {defs}
</defs>
<style>{style}</style>
{body}
</svg>'''


def frame(w, h, rx=16):
    return (f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#bg)"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" stroke="#5a189a" stroke-opacity=".7"/>')


# ---------------- portada ----------------
def hero(t):
    rnd = random.Random(7)
    grooves = "".join(f'<circle cx="170" cy="165" r="{r}" fill="none" stroke="#2a1a3d" stroke-width="0.8" opacity="{0.35 + 0.5 * ((r // 6) % 2)}"/>' for r in range(48, 124, 5))
    eq = "".join(
        f'<rect class="bar" x="{860 + i * 11}" y="34" width="7" height="44" rx="2" fill="url(#eq)" style="animation-duration:{rnd.uniform(.5, 1.3):.2f}s;animation-delay:-{rnd.uniform(0, 1):.2f}s"/>'
        for i in range(10))
    lines = [("prompt", "whoami"), ("out", t["whoami"]), ("prompt", "cat focus.txt"), ("out", t["focus"]), ("prompt", "")]
    term, clips, tm = [], [], 0.6
    for i, (kind, txt) in enumerate(lines):
        y = 180 + i * 26
        w = (len(txt) + (17 if kind == "prompt" else 2)) * 8.5 + 10
        dur = 0.25 if kind == "out" else max(0.5, len(txt) * 0.035)
        clips.append(f'<clipPath id="c{i}"><rect x="360" y="{y - 16}" height="22" width="0"><animate attributeName="width" from="0" to="{w:.0f}" begin="{tm:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        if kind == "prompt":
            body = f'<tspan fill="#c77dff">cristy</tspan><tspan fill="#7b6a8f">@</tspan><tspan fill="#ff6ec7">fedora</tspan><tspan fill="#7b6a8f">:~$ </tspan><tspan fill="#f3e8ff">{txt}</tspan>'
        else:
            body = f'<tspan fill="#9d8bb0">› </tspan><tspan fill="#e0aaff">{txt}</tspan>'
        term.append(f'<text x="364" y="{y}" clip-path="url(#c{i})">{body}</text>')
        tm += dur + 0.25
    last_y = 180 + (len(lines) - 1) * 26
    cursor = f'<rect class="cursor" x="508" y="{last_y - 13}" width="8" height="16" fill="#c77dff" opacity="0"><set attributeName="opacity" to="1" begin="{tm:.2f}s"/></rect>'

    defs = f'''<linearGradient id="hbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset=".55" stop-color="#1b0638"/><stop offset="1" stop-color="#3c096c"/></linearGradient>
  <linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#7b2cbf"/><stop offset=".6" stop-color="#c77dff"/><stop offset="1" stop-color="#ff6ec7"/></linearGradient>
  <radialGradient id="disc"><stop offset="0" stop-color="#1c1026"/><stop offset=".7" stop-color="#0b0612"/><stop offset="1" stop-color="#150a22"/></radialGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="#9d4edd" stop-opacity=".55"/><stop offset="1" stop-color="#9d4edd" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#c77dff" stroke-opacity=".06"/></pattern>
  <clipPath id="frame"><rect width="1000" height="330" rx="18"/></clipPath>
  {"".join(clips)}'''
    style = '''
  .spin{animation:spin 3.2s linear infinite;transform-box:fill-box;transform-origin:center}
  @keyframes spin{to{transform:rotate(360deg)}}
  .bar{animation:eq 1s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 100%}
  @keyframes eq{0%{transform:scaleY(.15)}100%{transform:scaleY(1)}}
  .cursor{animation:blink 1s steps(1) infinite}
  @keyframes blink{50%{opacity:0}}
  .scan{animation:scan 5s linear infinite}
  @keyframes scan{0%{transform:translateY(0);opacity:0}10%{opacity:.6}90%{opacity:.6}100%{transform:translateY(150px);opacity:0}}
  .g1{animation:g1 4s steps(1) infinite} .g2{animation:g2 4s steps(1) infinite}
  @keyframes g1{0%,88%,100%{transform:translate(0,0);opacity:0}90%{transform:translate(-3px,1px);opacity:.8}93%{transform:translate(2px,-1px);opacity:.8}96%{transform:translate(-1px,0);opacity:.6}}
  @keyframes g2{0%,88%,100%{transform:translate(0,0);opacity:0}90%{transform:translate(3px,-1px);opacity:.8}93%{transform:translate(-2px,1px);opacity:.8}96%{transform:translate(1px,0);opacity:.6}}
  .note{animation:float 4s ease-in infinite;opacity:0}
  @keyframes float{0%{transform:translate(0,0);opacity:0}15%{opacity:.9}100%{transform:translate(18px,-70px);opacity:0}}
'''
    body = f'''<g clip-path="url(#frame)">
  <rect width="1000" height="330" fill="url(#hbg)"/>
  <rect width="1000" height="330" fill="url(#grid)"/>
  <circle cx="170" cy="165" r="170" fill="url(#glow)"/>
  <g class="spin">
    <circle cx="170" cy="165" r="125" fill="url(#disc)" stroke="#3c096c" stroke-width="2"/>
    {grooves}
    <path d="M170 45 A120 120 0 0 1 280 110" stroke="#e0aaff" stroke-opacity=".25" stroke-width="6" fill="none" stroke-linecap="round"/>
    <circle cx="170" cy="165" r="42" fill="url(#neon)"/>
    <text x="170" y="160" text-anchor="middle" font-size="11" font-weight="700" fill="#10002b" letter-spacing="2">SIDE A</text>
    <text x="170" y="176" text-anchor="middle" font-size="8" fill="#240046">33⅓ RPM</text>
    <circle cx="170" cy="165" r="4" fill="#0d0221"/>
  </g>
  <g stroke-linecap="round">
    <circle cx="308" cy="42" r="14" fill="#240046" stroke="#9d4edd" stroke-width="2"/>
    <path d="M308 42 L292 150 L262 190" stroke="#c77dff" stroke-width="5" fill="none"/>
    <rect x="248" y="184" width="20" height="12" rx="3" transform="rotate(-35 258 190)" fill="#ff6ec7"/>
  </g>
  <text class="note" x="60" y="80" font-size="22" fill="#e0aaff">♪</text>
  <text class="note" x="275" y="270" font-size="18" fill="#ff6ec7" style="animation-delay:1.6s">♫</text>
  <text class="note" x="40" y="250" font-size="16" fill="#c77dff" style="animation-delay:2.8s">♩</text>
  <g font-size="54" font-weight="800" letter-spacing="3">
    <text class="g1" x="360" y="84" fill="#ff6ec7">CRISTY</text>
    <text class="g2" x="360" y="84" fill="#5ee7ff">CRISTY</text>
    <text x="360" y="84" fill="#f3e8ff">CRISTY</text>
  </g>
  <text x="362" y="112" font-size="14" fill="#c77dff" letter-spacing="1">DevSecOps · Software Architecture · Linux · Open Source</text>
  {eq}
  <rect x="350" y="128" width="620" height="188" rx="10" fill="#0a0118" fill-opacity=".85" stroke="#5a189a"/>
  <circle cx="366" cy="142" r="4" fill="#ff6ec7"/><circle cx="380" cy="142" r="4" fill="#c77dff"/><circle cx="394" cy="142" r="4" fill="#7b2cbf"/>
  <text x="960" y="146" text-anchor="end" font-size="10" fill="#7b6a8f">bash — fedora</text>
  <g font-size="14">{"".join(term)}{cursor}</g>
  <rect class="scan" x="351" y="152" width="618" height="2" fill="#c77dff" opacity="0"/>
</g>
<rect x="1" y="1" width="998" height="328" rx="18" fill="none" stroke="#5a189a" stroke-opacity=".6"/>'''
    return svg(1000, 330, body, style, defs)


# ---------------- consola DevSecOps ----------------
def mixer(t):
    rnd = random.Random(7)
    chans = [("PLAN", "threat model"), ("CODE", "SAST"), ("DEPS", "SCA / SBOM"), ("SECRETS", "gitleaks"),
             ("BUILD", "image scan"), ("IaC", "policy"), ("DEPLOY", "signing"), ("MONITOR", "SIEM")]
    x0, cw, strips = 40, 116, []
    for i, (name, sub) in enumerate(chans):
        x = x0 + i * cw
        cx = x + cw / 2 - 8
        d, dl = rnd.uniform(.6, 1.4), rnd.uniform(0, 1)
        fy = rnd.randint(215, 265)
        leds = "".join(
            f'<rect x="{cx - 26}" y="{252 - j * 10}" width="14" height="7" rx="2" fill="{"#ff6ec7" if j >= 9 else "#c77dff" if j >= 6 else "#7b2cbf"}" class="led" style="animation-delay:{j * 0.09 + dl:.2f}s;animation-duration:{d:.2f}s"/>'
            for j in range(11))
        strips.append(f'''<g>
  <rect x="{x}" y="70" width="{cw - 16}" height="270" rx="10" fill="#12032a" stroke="#3c096c"/>
  <text x="{cx}" y="92" text-anchor="middle" font-size="12" font-weight="700" fill="#f3e8ff" letter-spacing="1">{name}</text>
  <text x="{cx}" y="108" text-anchor="middle" font-size="9.5" fill="#9d8bb0">{sub}</text>
  <g class="knob" style="animation-duration:{rnd.uniform(3, 6):.1f}s;animation-delay:-{rnd.uniform(0, 3):.1f}s"><circle cx="{cx}" cy="128" r="10" fill="#240046" stroke="#9d4edd"/><line x1="{cx}" y1="128" x2="{cx}" y2="119" stroke="#ff6ec7" stroke-width="2" stroke-linecap="round"/></g>
  {leds}
  <rect x="{cx + 10}" y="150" width="4" height="110" rx="2" fill="#2a1446"/>
  <rect class="fader" x="{cx + 2}" y="{fy}" width="20" height="10" rx="2" fill="#e0aaff" style="animation-duration:{rnd.uniform(3, 5):.1f}s;animation-delay:-{rnd.uniform(0, 3):.1f}s"/>
  <g transform="translate({cx - 6},292)"><rect y="6" width="12" height="10" rx="2" fill="none" stroke="#c77dff" stroke-width="1.6"/><path d="M2.5 6V3.5a3.5 3.5 0 0 1 7 0V6" fill="none" stroke="#c77dff" stroke-width="1.6"/></g>
  <text x="{cx}" y="328" text-anchor="middle" font-size="9" fill="#5ee7ff" class="ok" style="animation-delay:{i * 0.35:.2f}s">PASS</text>
</g>''')
    style = '''
  .led{animation:led 1s ease-in-out infinite alternate;opacity:.15}
  @keyframes led{0%{opacity:.12}100%{opacity:1}}
  .fader{animation:fad 4s ease-in-out infinite alternate}
  @keyframes fad{0%{transform:translateY(-40px)}100%{transform:translateY(8px)}}
  .knob{animation:knob 4s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
  @keyframes knob{0%{transform:rotate(-120deg)}100%{transform:rotate(120deg)}}
  .head{animation:head 8s linear infinite}
  @keyframes head{0%{transform:translateX(0)}100%{transform:translateX(870px)}}
  .ok{animation:ok 2.8s ease-in-out infinite}
  @keyframes ok{0%,100%{opacity:.35}50%{opacity:1}}
'''
    defs = '<linearGradient id="ph" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff6ec7" stop-opacity="0"/><stop offset="1" stop-color="#ff6ec7"/></linearGradient>'
    body = f'''{frame(1000, 380, 18)}
<text x="40" y="36" font-size="15" font-weight="800" fill="#f3e8ff" letter-spacing="2">DEVSECOPS MIXING CONSOLE</text>
<text x="40" y="56" font-size="11" fill="#9d8bb0">{t["mixer"]}</text>
<g transform="translate(866,26)"><rect width="94" height="26" rx="13" fill="#240046" stroke="#c77dff"/><circle cx="16" cy="13" r="5" fill="#5ee7ff" class="ok"/><text x="28" y="17" font-size="11" fill="#e0aaff" letter-spacing="1">PASSING</text></g>
{"".join(strips)}
<g class="head"><rect x="{x0}" y="66" width="60" height="3" fill="url(#ph)"/><rect x="{x0 + 58}" y="62" width="3" height="282" fill="#ff6ec7" opacity=".35"/></g>
<text x="500" y="364" text-anchor="middle" font-size="10" fill="#7b6a8f">plan → code → build → test → release → deploy → operate → monitor ↺</text>'''
    return svg(1000, 380, body, style, defs)


# ---------------- stack ----------------
def stack(t):
    main = [("go", "Go"), ("typescript", "TypeScript"), ("gnubash", "Bash"), ("python", "Python")]
    also = [("dart", "Dart"), ("flutter", "Flutter"), ("c", "C"), ("cplusplus", "C++"), ("openjdk", "Java"), ("rust", "Rust")]
    learning = [("kalilinux", "Kali Linux"), ("go", "Go"), ("wazuh", "Wazuh"), ("mitre", "MITRE ATT&amp;CK"), ("ebpf", "eBPF"), ("kubernetes", "Kubernetes")]
    b = [frame(1000, 284)]
    b.append(f'<text x="40" y="44" font-size="11" fill="#9d8bb0">{t["main"]}</text>')
    b.append(f'<text x="560" y="44" font-size="11" fill="#9d8bb0">{t["also"]}</text>')
    k = 0
    for i, (ic, name) in enumerate(main):
        x, y = 40 + i * 124, 58
        b.append(f'<rect x="{x}" y="{y}" width="112" height="104" rx="12" fill="#12032a" stroke="#3c096c"/>'
                 f'<rect class="glow" x="{x}" y="{y}" width="112" height="104" rx="12" fill="none" stroke="#c77dff" style="animation-delay:{k * 0.35:.2f}s"/>'
                 f'{icon(ic, x + 36, y + 18, 40)}'
                 f'<text x="{x + 56}" y="{y + 88}" text-anchor="middle" font-size="13" fill="#f3e8ff">{name}</text>')
        k += 1
    for i, (ic, name) in enumerate(also):
        x, y = 560 + i * 68, 58
        b.append(f'<rect x="{x}" y="{y}" width="60" height="104" rx="12" fill="#12032a" stroke="#3c096c"/>'
                 f'<rect class="glow" x="{x}" y="{y}" width="60" height="104" rx="12" fill="none" stroke="#c77dff" style="animation-delay:{k * 0.35:.2f}s"/>'
                 f'{icon(ic, x + 17, y + 26, 26)}'
                 f'<text x="{x + 30}" y="{y + 88}" text-anchor="middle" font-size="11" fill="#e0aaff">{name}</text>')
        k += 1

    b.append(f'<text x="40" y="200" font-size="11" fill="#9d8bb0">{t["learning"]}</text>')
    x = 40
    for i, (ic, name) in enumerate(learning):
        chars = len(name.replace("&amp;", "&"))
        w = 72 + chars * 8.3
        b.append(f'<g><rect x="{x}" y="214" width="{w:.0f}" height="46" rx="23" fill="#12032a" stroke="#5a189a"/>'
                 f'{icon(ic, x + 16, 228, 18)}'
                 f'<text x="{x + 42}" y="242" font-size="13" fill="#f3e8ff">{name}</text>'
                 f'<circle class="dot" cx="{x + w - 16:.0f}" cy="237" r="3.5" fill="#ff6ec7" style="animation-delay:{i * 0.3:.1f}s"/>'
                 f'<rect class="load" x="{x + 22}" y="257" width="{w - 44:.0f}" height="2" rx="1" fill="url(#neon)" style="animation-delay:{i * 0.4:.1f}s"/></g>')
        x += w + 12
    style = '''
  .glow{opacity:0;animation:glow 3.5s ease-in-out infinite}
  @keyframes glow{0%,100%{opacity:0}15%{opacity:.9}35%{opacity:0}}
  .dot{animation:dot 1.8s ease-in-out infinite}
  @keyframes dot{50%{opacity:.2}}
  .load{animation:load 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:left}
  @keyframes load{0%{transform:scaleX(0);opacity:1}70%{transform:scaleX(1);opacity:1}100%{transform:scaleX(1);opacity:0}}
'''
    return svg(1000, 284, "\n".join(b), style)


# ---------------- entorno (estilo neofetch) ----------------
def setup(t):
    b = [frame(1000, 320)]
    b.append('<circle cx="160" cy="160" r="115" fill="url(#halo)"/>')
    b.append(f'<g class="float">{icon("fedora", 85, 85, 150, "url(#logo)")}</g>')
    b.append('<text x="330" y="52" font-size="16" font-weight="700"><tspan fill="#c77dff">cristy</tspan><tspan fill="#7b6a8f">@</tspan><tspan fill="#ff6ec7">fedora</tspan></text>')
    b.append('<text x="330" y="70" font-size="14" fill="#5a189a">──────────────</text>')
    for i, (ic, key, val) in enumerate(t["setup"]):
        y = 100 + i * 26
        b.append(f'<g class="ln" style="animation-delay:{0.3 + i * 0.18:.2f}s">{icon(ic, 330, y - 13, 15, "#9d4edd")}'
                 f'<text x="356" y="{y}" font-size="14"><tspan fill="#c77dff" font-weight="700">{key}</tspan><tspan fill="#7b6a8f">: </tspan><tspan fill="#f3e8ff">{val}</tspan></text></g>')
    palette = ["#10002b", "#240046", "#3c096c", "#5a189a", "#7b2cbf", "#9d4edd", "#c77dff", "#e0aaff", "#ff6ec7"]
    for i, c in enumerate(palette):
        b.append(f'<rect class="ln" x="{330 + i * 30}" y="{100 + len(t["setup"]) * 26 + 2}" width="26" height="14" fill="{c}" style="animation-delay:{1.7 + i * 0.05:.2f}s"/>')
    defs = '''<linearGradient id="logo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e0aaff"/><stop offset="1" stop-color="#7b2cbf"/></linearGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="#9d4edd" stop-opacity=".35"/><stop offset="1" stop-color="#9d4edd" stop-opacity="0"/></radialGradient>'''
    style = '''
  .ln{animation:ln .5s ease-out both}
  @keyframes ln{from{opacity:0;transform:translateX(-8px)}}
  .float{animation:float 5s ease-in-out infinite}
  @keyframes float{50%{transform:translateY(-6px)}}
'''
    return svg(1000, 320, "\n".join(b), style, defs)


# ---------------- separador ----------------
def divider():
    rnd = random.Random(7)
    bars = []
    for i in range(100):
        env = 0.35 + 0.65 * math.sin(math.pi * i / 99)
        h = max(4, env * 30 * rnd.uniform(.4, 1))
        bars.append(f'<rect class="w" x="{i * 10 + 3}" y="{20 - h / 2:.1f}" width="4" height="{h:.1f}" rx="2" style="animation-delay:-{rnd.uniform(0, 1.6):.2f}s;animation-duration:{rnd.uniform(.9, 1.8):.2f}s"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="40" viewBox="0 0 1000 40">
<defs><linearGradient id="n" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7b2cbf" stop-opacity=".2"/><stop offset=".5" stop-color="#c77dff"/><stop offset=".8" stop-color="#ff6ec7"/><stop offset="1" stop-color="#7b2cbf" stop-opacity=".2"/></linearGradient></defs>
<style>.w{{fill:url(#n);animation:w 1.2s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}@keyframes w{{0%{{transform:scaleY(.25)}}100%{{transform:scaleY(1)}}}}</style>
{"".join(bars)}</svg>'''


# ---------------- botones de idioma ----------------
def button(code, label, active):
    fill, stroke, text, sub = ("url(#neon)", "none", "#10002b", "#240046") if active else ("#12032a", "#5a189a", "#e0aaff", "#9d8bb0")
    body = (f'<rect x=".5" y=".5" width="139" height="39" rx="20" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="24" y="25" font-size="12" font-weight="800" fill="{sub}">{code}</text>'
            f'<text x="52" y="25" font-size="13" font-weight="700" fill="{text}">{label}</text>')
    return svg(140, 40, body)


def main():
    (ASSETS / "lang").mkdir(parents=True, exist_ok=True)
    (ASSETS / "divider.svg").write_text(divider())
    for lang, t in STR.items():
        (ASSETS / f"hero.{lang}.svg").write_text(hero(t))
        (ASSETS / f"mixer.{lang}.svg").write_text(mixer(t))
        (ASSETS / f"stack.{lang}.svg").write_text(stack(t))
        (ASSETS / f"setup.{lang}.svg").write_text(setup(t))
    for code, label in (("ES", "Español"), ("EN", "English")):
        for active in (True, False):
            (ASSETS / "lang" / f"{code.lower()}-{'on' if active else 'off'}.svg").write_text(button(code, label, active))


if __name__ == "__main__":
    main()

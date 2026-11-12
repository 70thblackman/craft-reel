// Deterministic reel engine: every element is a pure function of film time t.
// window.seek(t) fully redraws a frame; the renderer captures it. No retained timelines.
const FPS = 30;
const DURATION = window.FILM_DURATION || 60;
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, p) => a + (b - a) * p;
const P = (t, a, b) => clamp((t - a) / (b - a));
const E = {
  out: (p) => 1 - Math.pow(1 - p, 3),
  out5: (p) => 1 - Math.pow(1 - p, 5),
  in: (p) => p * p * p,
  io: (p) => (p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  back: (p) => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); },
  sine: (p) => .5 - .5 * Math.cos(Math.PI * p),
};
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const WORLD = $("#world"), TEAR = $("#fx .tear"), FLASH = $("#fx .flash"), CAP = $("#cap .pill");

// narration words in film time: W(i) = start of word i, WE(i) = its end
const W = (i) => window.WORDS[i][1];
const WE = (i) => window.WORDS[i][2];

function mk(html, parent = WORLD) {
  const d = document.createElement("div");
  d.innerHTML = html.trim();
  const n = d.firstElementChild;
  parent.appendChild(n);
  return n;
}
const at = (root, html) => mk(html, root);
// transform + opacity in one call; hidden elements are display:none
function tf(n, o = 1, x = 0, y = 0, s = 1, r = 0, extra = "") {
  if (o <= .002) { n.classList.add("hide"); return false; }
  n.classList.remove("hide");
  n.style.opacity = o >= .999 ? "" : o.toFixed(3);
  n.style.transform = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) scale(${s.toFixed(4)}) rotate(${r.toFixed(2)}deg) ${extra}`;
  return true;
}
// split text into words; a leading * makes a word brand coloured
function words(n, text) {
  n.innerHTML = text.split(" ").map((w) => w.startsWith("*")
    ? `<span class="wd"><span class="brand">${w.slice(1)}</span></span>`
    : `<span class="wd"><span>${w}</span></span>`).join(" ");
  return [...n.querySelectorAll(".wd > span")];
}
// a centred line of words: { n, w }
function line(root, cls, top, size, text, style = "") {
  const n = at(root, `<div class="a c ${cls}" style="top:${top}px;font-size:${size}px;${style}"></div>`);
  return { n, w: words(n, text) };
}
const when = (w, i) => Array.isArray(w) ? w[Math.min(i, w.length - 1)] : w + i * .07;
// words rise out of a mask, fast
function reveal(spans, t, w, dur = .2) {
  spans.forEach((s, i) => {
    const p = E.out(P(t, when(w, i) - .05, when(w, i) - .05 + dur));
    s.style.transform = `translateY(${((1 - p) * 110).toFixed(1)}%)`;
    s.style.opacity = p.toFixed(3);
  });
}
// words slam in: big, blurred, then sharp
function pop(spans, t, w, dur = .14) {
  spans.forEach((s, i) => {
    const q = P(t, when(w, i) - .04, when(w, i) - .04 + dur), p = E.out(q);
    s.style.transform = `scale(${(1.45 - .45 * p).toFixed(3)})`;
    s.style.opacity = q > 0 ? Math.min(1, q * 3).toFixed(3) : "0";
    s.style.filter = q < 1 ? `blur(${((1 - p) * 6).toFixed(1)}px)` : "";
  });
}
const fa = (n) => String(n).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);
const faNum = (n) => fa(Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, "٬"));
// draw-on for svg strokes that use pathLength="1"
function draw(el, p) {
  el.style.strokeDasharray = "1 1";
  el.style.strokeDashoffset = (1 - clamp(p)).toFixed(4);
  el.style.opacity = p <= 0 ? 0 : 1;
}
const hash = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// a slam: scale from `from` to 1 in .12 s
const slam = (t, t0, from = 1.6, d = .12) => { const p = P(t, t0, t0 + d); return { o: p > 0 ? 1 : 0, s: lerp(from, 1, E.out(p)) }; };
// drop onto the desk: falls from above with a bounce
const drop = (t, t0, d = .32) => { const p = P(t, t0, t0 + d); return { o: p > 0 ? 1 : 0, y: (1 - E.back(p)) * -220, s: lerp(1.25, 1, E.out(p)) }; };

// extruded type: `depth` px of side in `side`, optional ring outline, soft cast shadow
function ext(side = "#0753a8", depth = 14, ring = "", ringW = 0, cast = "rgba(0,20,60,.45)") {
  const s = [];
  if (ringW) for (let a = 0; a < 16; a++) {
    const r = a * Math.PI / 8;
    s.push(`${(Math.cos(r) * ringW).toFixed(1)}px ${(Math.sin(r) * ringW).toFixed(1)}px 0 ${ring}`);
  }
  for (let k = 1; k <= depth; k++) s.push(`${(k * .55).toFixed(1)}px ${k}px 0 ${side}`);
  s.push(`${depth * .55 + 6}px ${depth + 14}px 26px ${cast}`);
  return `text-shadow:${s.join(",")};`;
}

/* ---------- scenes ---------- */
const SCENES = [];
const SFX = [];
const sfx = (t, kind, g = 1) => SFX.push([+t.toFixed(3), kind, g]);
// scene(a, b, bg, build, opts): build(cam, root) returns update(t, p)
//   tr: how it comes in: whip | whipL | punch | up | down | flash | cut ; hits: times that shake the camera
function scene(a, b, bg, build, { push = .05, tr = "whip", hits = [], quiet = false } = {}) {
  const root = mk(`<div class="scene bg-${bg} vig hide"><div class="cam"></div></div>`);
  const cam = root.firstElementChild;
  const update = build(cam, root);
  SCENES.push({ a, b, root, cam, update, push, tr, hits });
  if (a > 0 && !quiet) sfx(a, tr === "punch" || tr === "flash" ? "hit" : "whoosh", 1);
}

// captions: [film time, text]; each shows until the next one (an empty text hides the pill)
const CAPS = [];
const cap = (t, text) => CAPS.push([t, text]);

function frame(t) {
  let cur = null;
  for (const s of SCENES) {
    const on = t >= s.a - .0001 && t < s.b;
    s.root.classList.toggle("hide", !on);
    if (on) {
      cur = s;
      let sx = 0, sy = 0;
      for (const h of s.hits) {
        const d = t - h;
        if (d >= 0 && d < .35) {
          const k = Math.floor(t * FPS), amp = 24 * (1 - d / .35);
          sx += (hash(k) - .5) * 2 * amp; sy += (hash(k + 11) - .5) * 2 * amp;
        }
      }
      const p = P(t, s.a, s.b);
      s.cam.style.transform = `translate(${sx.toFixed(1)}px,${sy.toFixed(1)}px) scale(${(1 + s.push * E.sine(p)).toFixed(4)})`;
      s.update(t, p);
    }
  }
  // the way in: a fast move with motion blur, an accent/white split and a tracking tear
  const since = cur ? t - cur.a : 9;
  let tfm = "", flt = "", fl = 0;
  if (cur && cur.a > 0 && since < .2) {
    const q = E.out(P(since, 0, .16)), g = 1 - P(since, 0, .12);
    const k = Math.floor(t * FPS);
    if (cur.tr === "whip" || cur.tr === "whipL") tfm = `translateX(${((cur.tr === "whip" ? 1 : -1) * (1 - q) * 760).toFixed(1)}px)`;
    if (cur.tr === "up") tfm = `translateY(${((1 - q) * 900).toFixed(1)}px)`;
    if (cur.tr === "down") tfm = `translateY(${(-(1 - q) * 900).toFixed(1)}px)`;
    if (cur.tr === "punch") tfm = `scale(${(1 + .28 * (1 - q)).toFixed(3)})`;
    if (cur.tr === "flash") fl = 1 - P(since, 0, .14);
    const blur = cur.tr === "cut" || cur.tr === "flash" ? 0 : (1 - q) * 16;
    flt = `${blur > .3 ? `blur(${blur.toFixed(1)}px) ` : ""}drop-shadow(${(10 * g).toFixed(1)}px 0 0 rgba(0,142,250,.6)) drop-shadow(${(-10 * g).toFixed(1)}px 0 0 rgba(255,255,255,.5))`;
    if (g > 0) { TEAR.style.top = (hash(k + 3) * 1700).toFixed(0) + "px"; TEAR.style.height = (40 + hash(k + 5) * 140).toFixed(0) + "px"; }
    else TEAR.style.height = "0";
  } else TEAR.style.height = "0";
  WORLD.style.transform = tfm; WORLD.style.filter = flt;
  FLASH.style.opacity = fl.toFixed(3);
  // caption
  let txt = "";
  for (const [ct, tx] of CAPS) if (t >= ct - .02) txt = tx;
  if (CAP.dataset.t !== txt) { CAP.innerHTML = txt; CAP.dataset.t = txt; }
}

window.seek = async (t) => {
  frame(t);
  await document.fonts.ready;
};
window.ready = new Promise((res) => addEventListener("load", async () => {
  await Promise.all([100, 300, 400, 500, 700, 800, 900, 950].map((w) => document.fonts.load(`${w} 40px Y`, "سلام ۱۲۳ abc")));
  await Promise.all([...document.images].map((im) => im.decode().catch(() => {})));
  res();
}));
// clean data for the build scripts: cuts, transition types and the SFX cue list
window.cues = () => ({
  fps: FPS,
  duration: DURATION,
  scenes: SCENES.map((s) => ({ a: +s.a.toFixed(3), b: +s.b.toFixed(3), tr: s.tr, push: s.push })),
  sfx: SFX,
  caps: CAPS,
});
window.DURATION = DURATION;
window.FPS = FPS;
window.SFX = SFX;

// Demo film: 3 scenes / 12.5 s showing the house grammar.
// Replace with the real script. Cuts land on word starts: S0(i) = W(i) - .04.
const S0 = (i) => W(i) - .04;
const PH = { left: 290, top: 380, w: 500, h: 960 };     // one phone position for every phone scene
function phone(root, inner = "", ph = PH) {
  return at(root, `<div class="phone" style="left:${ph.left}px;top:${ph.top}px;width:${ph.w}px;height:${ph.h}px"><div class="scr"><div class="isl"></div>${inner}</div></div>`);
}
// big extruded figure: white face + deep side on dark, accent face + white ring on light
const BIG = (size, light = false) => light
  ? `font-weight:950;font-size:${size}px;line-height:1.2;color:#008efa;${ext("#06386f", Math.round(size / 16), "#fff", Math.max(6, size / 30))}`
  : `font-weight:950;font-size:${size}px;line-height:1.2;color:#fff;${ext("#06386f", Math.round(size / 16))}`;
// props scattered on a desk: [html, x, y, rot, delay]
function props(root, list, A, step = .05) {
  return list.map(([html, x, y, r, dl = 0], i) => ({ n: at(root, `<div class="a shd" style="left:${x}px;top:${y}px">${html}</div>`), r, d: A + dl + i * step }));
}
const propsIn = (ps, t, drift = 1) => ps.forEach((p, i) => {
  const d = drop(t, p.d);
  tf(p.n, d.o, Math.sin(t * .9 + i) * 6 * drift, d.y + Math.cos(t * .8 + i * 2) * 6 * drift, d.s, p.r + Math.sin(t * .7 + i) * 1.2 * drift);
});

/* =============== 1  hook: the month got away =============== */
scene(0, S0(10), "desk", (cam) => {
  const ps = props(cam, [
    [ART.coin(130), 110, 1250, -10], [ART.coin(100), 850, 300, 20], [ART.note(380), 590, 1280, 14],
    [ART.clip(60), 150, 320, -30], [ART.pencil(420), 600, 1640, -8],
  ], 0.02, .04);
  const w = at(cam, `<div class="a shd" style="left:290px;top:350px">${ART.wallet(480)}</div>`);
  const flap = w.querySelector(".flap");
  const sub = line(cam, "m", 790, 64, "این ماه هم", "color:#b9dcff");
  const big = at(cam, `<div class="a c" style="top:875px;${BIG(240)}">دیر شد!</div>`);
  return (t) => {
    propsIn(ps, t);
    const d = drop(t, .02, .3);
    tf(w, d.o, 0, d.y, d.s, -4);
    flap.setAttribute("transform", `rotate(${f1(-26 * E.back(P(t, .25, .6)))} 30 150)`);
    reveal(sub.w, t, [W(0), W(1), W(2)]);
    const s = slam(t, W(3) - .1, 1.8);
    tf(big, s.o, 0, 0, s.s, -3);
  };
}, { hits: [W(3) - .1] });
sfx(0.02, "impact", .9); sfx(W(3) - .1, "hit", .9);

/* =============== 2  proof: the number and the crowd =============== */
scene(S0(10), S0(18), "grid", (cam) => {
  const A = S0(10);
  const G = at(cam, `<div class="a" style="left:115px;top:610px;width:850px;height:830px"></div>`);
  const cells = [];
  const on = "#008efa", off = "rgba(11,27,51,.14)";
  for (let k = 0; k < 100; k++) {
    cells.push(at(G, `<div class="a" style="left:${(9 - k % 10) * 85 + 12}px;top:${Math.floor(k / 10) * 78}px">${ART.person(off, 60)}</div>`));
  }
  const setCell = (k, c) => { const p = cells[k].querySelector("path"); if (p.getAttribute("fill") !== c) p.setAttribute("fill", c); };
  const big = at(cam, `<div class="a c" style="top:150px;${BIG(280, true)}"></div>`);
  const sub = line(cam, "hx", 500, 56, "از کاربرا گفتن…", "color:#0b1b33");
  const tag = at(cam, `<div class="tag" style="left:240px;top:1400px;font-size:56px;transform-origin:50% 50%">خرید قسطی کمک می‌کنه</div>`);
  return (t) => {
    const f = E.out(P(t, W(11), W(14) + .2));
    const n = Math.round(42 * f);
    big.textContent = fa(n) + "٪";
    const s = slam(t, W(11) - .02, 1.5);
    tf(big, s.o, 0, 0, s.s);
    cells.forEach((c, k) => {
      const p = E.out(P(t, A + k * .004, A + .2 + k * .004));
      tf(c, p, 0, (1 - p) * 30, 1);
      setCell(k, k < n ? on : off);
    });
    reveal(sub.w, t, [W(10), W(11), W(12)]);
    const s2 = slam(t, W(15), 1.7);
    tf(tag, s2.o, 0, 0, s2.s, -3);
  };
}, { tr: "punch", hits: [W(11)] });
for (let k = 0; k < 10; k++) sfx(W(11) + k * .09, "tick", .7);
sfx(W(11) - .02, "impact", .8); sfx(W(15), "hit", .7);

/* =============== 3  CTA: you tell us =============== */
scene(S0(18), DURATION + .5, "brand", (cam) => {
  const A = S0(18);
  const kick = at(cam, `<div class="a c lat b" style="top:330px;font-size:40px;color:rgba(255,255,255,.8);letter-spacing:.16em">YOUR TURN</div>`);
  const l1 = at(cam, `<div class="a c" style="top:430px;${BIG(220).replace("#06386f", "#0753a8")}">شما بگین</div>`);
  const box = at(cam, `<div class="a" style="left:110px;top:900px;width:860px;height:130px;border-radius:65px;background:#fff;display:flex;align-items:center;padding:0 46px;box-sizing:border-box;gap:20px;box-shadow:0 24px 40px rgba(0,30,80,.3)">
    <span class="md tx" style="font-size:42px;color:#101828;flex:1;white-space:nowrap;overflow:hidden"></span>
    <span style="width:84px;height:84px;border-radius:50%;background:#008efa;flex:none;display:flex;align-items:center;justify-content:center">
      <svg viewBox="0 0 24 24" width="44" height="44" style="direction:ltr"><path d="M3 12l18-9-6 18-3-7z" fill="#fff"/></svg></span></div>`);
  const tx = box.querySelector(".tx");
  const msg = Array.from("نظرتون چیه؟");
  const arrow = at(cam, `<div class="a c h" style="top:1100px;font-size:120px;color:#fff">↓</div>`);
  return (t) => {
    const s = slam(t, W(18), 1.8);
    tf(kick, s.o, 0, 0, s.s);
    tf(l1, s.o, 0, 0, s.s, -2);
    const b = E.out(P(t, A + .1, A + .35));
    tf(box, b, 0, (1 - b) * 400);
    const k = Math.round(msg.length * clamp((t - A - .25) / .45));
    tx.innerHTML = msg.slice(0, k).join("") + `<span style="color:#008efa;opacity:${Math.floor(t * 4) % 2 ? 1 : 0}">|</span>`;
    tf(arrow, E.out(P(t, A + .3, A + .5)), 0, Math.abs(Math.sin(t * 7)) * 30);
  };
}, { tr: "whip", hits: [W(18)] });
sfx(W(18), "hit", .8);
for (let k = 0; k < 10; k++) sfx(S0(18) + .3 + k * .05, "key", .5);
sfx(DURATION - .3, "notif", .7);

// Drawn props, part 1: money and paperwork. Each returns an SVG string sized by `w`.
// Recolour with build/rebrand.py; geometry is brand-neutral.
const f1 = (v) => v.toFixed(1);
const ART = {};
const sv = (vb, w, body, cls = "") => {
  const [, , vw, vh] = vb.split(" ").map(Number);
  // direction:ltr keeps text-anchor physical (start = left); Persian runs still shape right to left
  return `<svg class="${cls}" style="direction:ltr" viewBox="${vb}" width="${w}" height="${f1(w * vh / vw)}">${body}</svg>`;
};

/* ---------- person glyph (unit box 100 x 130) ---------- */
ART.personPath = "M50 8a22 22 0 1 1 0 44a22 22 0 1 1 0-44zM6 130C6 84 25 62 50 62s44 22 44 68z";
ART.person = (fill = "#0b1b33", w = 100) => sv("0 0 100 130", w, `<path d="${ART.personPath}" fill="${fill}"/>`);

/* ---------- coin ---------- */
ART.coin = (w = 120) => sv("0 0 100 100", w, `
  <circle cx="50" cy="54" r="44" fill="#c98a12"/>
  <circle cx="50" cy="50" r="44" fill="#ffc23d"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="#e5a21c" stroke-width="5"/>
  <path d="M30 30a30 30 0 0 1 30-8" stroke="#fff3c4" stroke-width="6" fill="none" stroke-linecap="round" opacity=".8"/>
  <text x="50" y="64" text-anchor="middle" font-family="Y" font-weight="950" font-size="40" fill="#c98a12">ت</text>`);

/* ---------- banknote (generic, brand tinted) ---------- */
ART.note = (w = 360) => sv("0 0 360 170", w, `
  <rect x="0" y="0" width="360" height="170" rx="10" fill="#7fc3ff"/>
  <rect x="12" y="12" width="336" height="146" rx="6" fill="none" stroke="#2a8de0" stroke-width="3"/>
  <circle cx="250" cy="85" r="46" fill="#cfe8ff" stroke="#2a8de0" stroke-width="3"/>
  <path d="M232 85a18 18 0 1 0 36 0a18 18 0 1 0-36 0" fill="#2a8de0" opacity=".45"/>
  <path d="M30 40h120M30 58h90M30 130h70" stroke="#2a8de0" stroke-width="5" stroke-linecap="round" opacity=".6"/>
  <text x="96" y="112" text-anchor="middle" font-family="Y" font-weight="950" font-size="40" fill="#0753a8">۱۰۰٬۰۰۰</text>`);

/* ---------- wallet, open, empty (opening 0..1 lifts the flap) ---------- */
ART.wallet = (w = 520) => sv("0 0 520 400", w, `
  <g class="flap"><path d="M30 150 Q30 40 140 40 H470 Q500 40 500 70 V150Z" fill="#0d2f5c"/>
    <path d="M60 140 Q62 66 140 66 H470" fill="none" stroke="#3d7fd1" stroke-width="4" stroke-dasharray="12 10"/></g>
  <rect x="20" y="130" width="490" height="260" rx="40" fill="#123a6e"/>
  <rect x="20" y="130" width="490" height="60" rx="30" fill="#0a2a52"/>
  <rect x="44" y="160" width="442" height="206" rx="28" fill="none" stroke="#3d7fd1" stroke-width="4" stroke-dasharray="12 10"/>
  <rect x="360" y="218" width="170" height="100" rx="26" fill="#0d2f5c"/>
  <circle cx="420" cy="268" r="18" fill="#ffc23d"/><circle cx="420" cy="268" r="8" fill="#c98a12"/>`);

/* ---------- calendar page: month title, 5x7 grid, `mark` = circled day ---------- */
ART.calendar = (w = 560, month = "آبان", mark = 30, today = 24) => {
  let cells = "";
  for (let d = 1; d <= 30; d++) {
    const i = d - 1, cx = 470 - (i % 7) * 70, cy = 250 + Math.floor(i / 7) * 66;
    const past = d < today;
    cells += `<text class="d d${d}" x="${cx}" y="${cy}" text-anchor="middle" font-family="Y" font-weight="${d === today ? 950 : 700}" font-size="32"
      fill="${d === today ? "#008efa" : past ? "#b7c2d0" : "#101828"}">${fa(d)}</text>`;
    if (past) cells += `<path d="M${cx - 18} ${cy - 22}L${cx + 18} ${cy + 4}" stroke="#ff5b5b" stroke-width="4" stroke-linecap="round" opacity=".55"/>`;
  }
  const mi = mark - 1, mx = 470 - (mi % 7) * 70, my = 250 + Math.floor(mi / 7) * 66 - 12;
  return sv("0 0 560 600", w, `
    <rect x="0" y="20" width="560" height="580" rx="34" fill="#fff"/>
    <rect x="0" y="20" width="560" height="120" rx="34" fill="#008efa"/><rect x="0" y="100" width="560" height="40" fill="#008efa"/>
    <circle cx="140" cy="22" r="16" fill="#0b1b33"/><circle cx="420" cy="22" r="16" fill="#0b1b33"/>
    <rect x="132" y="-10" width="16" height="44" rx="8" fill="#9aa8bb"/><rect x="412" y="-10" width="16" height="44" rx="8" fill="#9aa8bb"/>
    <text x="280" y="105" text-anchor="middle" font-family="Y" font-weight="950" font-size="60" fill="#fff">${month}</text>
    ${cells}
    <path class="ring" pathLength="1" d="M${mx - 40} ${my}a40 34 0 1 0 80 0a40 34 0 1 0-80 0" fill="none" stroke="#008efa" stroke-width="7" stroke-linecap="round"/>`);
};

/* ---------- receipt: long paper with a torn bottom; rows = [[label, price]] ---------- */
ART.receipt = (w = 420, rows = [], title = "رسید خرید") => {
  const h = 200 + rows.length * 62;
  let zig = "";
  for (let k = 0; k <= 20; k++) zig += `L${420 - k * 21} ${h + (k % 2 ? 16 : 0)}`;
  const body = rows.map(([l, p], i) => `<g class="row" data-i="${i}">
      <text x="388" y="${170 + i * 62}" text-anchor="end" font-family="Y" font-weight="700" font-size="30" fill="#101828">${l}</text>
      <text x="32" y="${170 + i * 62}" font-family="Y" font-weight="800" font-size="28" fill="#0a6fd8" text-anchor="start">${p}</text>
      <path d="M32 ${186 + i * 62}H388" stroke="#d0d7e2" stroke-width="2" stroke-dasharray="6 6"/></g>`).join("");
  return sv(`0 0 420 ${h + 16}`, w, `
    <path d="M0 0H420V${h}${zig}Z" fill="#fff"/>
    <text x="210" y="70" text-anchor="middle" font-family="Y" font-weight="950" font-size="36" fill="#101828">${title}</text>
    <path d="M32 100H388" stroke="#101828" stroke-width="3"/>
    ${body}`);
};

/* ---------- calculator showing `txt` ---------- */
ART.calc = (w = 300, txt = "-۴٬۲۰۰٬۰۰۰") => {
  let keys = "";
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++)
    keys += `<rect x="${24 + c * 64}" y="${170 + r * 64}" width="52" height="52" rx="12" fill="${c === 3 ? "#008efa" : "#26344a"}"/>`;
  return sv("0 0 300 440", w, `
    <rect x="0" y="0" width="300" height="440" rx="36" fill="#0f1a2c"/>
    <rect x="22" y="26" width="256" height="110" rx="16" fill="#cfe5d0"/>
    <text class="scr" x="262" y="104" text-anchor="end" font-family="Y" font-weight="900" font-size="46" fill="#ff3b3b" direction="ltr">${txt}</text>
    ${keys}`);
};

/* ---------- salary envelope ---------- */
ART.envelope = (w = 520, label = "حقوق ماه بعد") => sv("0 0 520 340", w, `
  <rect x="0" y="0" width="520" height="340" rx="22" fill="#f0e2c4"/>
  <path class="flap" d="M0 22 L260 200 L520 22 V0 H0Z" fill="#e2cfa6"/>
  <path d="M0 340 L210 170 M520 340 L310 170" stroke="#d6c091" stroke-width="4"/>
  <rect x="120" y="226" width="280" height="66" rx="14" fill="#fff" opacity=".85"/>
  <text x="260" y="272" text-anchor="middle" font-family="Y" font-weight="900" font-size="34" fill="#0b1b33">${label}</text>`);

/* ---------- balance scale: `tilt` in degrees, plates labelled ---------- */
ART.scale = (w = 760, l = "دخل", r = "خرج") => sv("0 0 760 600", w, `
  <rect x="300" y="540" width="160" height="40" rx="14" fill="#0b1b33"/>
  <rect x="368" y="140" width="24" height="410" rx="12" fill="#0b1b33"/>
  <g class="beam">
    <rect x="80" y="126" width="600" height="26" rx="13" fill="#0a6fd8"/>
    <circle cx="380" cy="139" r="26" fill="#ffc23d"/>
    <g class="pl"><path d="M110 139 L50 330 M110 139 L170 330" stroke="#0b1b33" stroke-width="5"/>
      <path d="M20 330 H200 Q190 380 110 384 Q30 380 20 330Z" fill="#008efa"/>
      <text x="110" y="440" text-anchor="middle" font-family="Y" font-weight="950" font-size="48" fill="#0b1b33">${l}</text></g>
    <g class="pr"><path d="M650 139 L590 330 M650 139 L710 330" stroke="#0b1b33" stroke-width="5"/>
      <path d="M560 330 H740 Q730 380 650 384 Q570 380 560 330Z" fill="#008efa"/>
      <text x="650" y="440" text-anchor="middle" font-family="Y" font-weight="950" font-size="48" fill="#0b1b33">${r}</text></g>
  </g>`);

/* ---------- chat bubble with text ---------- */
ART.bubble = (txt, { bg = "#fff", fg = "#101828", size = 36 } = {}) =>
  `<div class="a" style="padding:14px 30px 22px;border-radius:30px 30px 8px 30px;background:${bg};color:${fg};font-weight:800;font-size:${size}px;line-height:1.5;white-space:nowrap;box-shadow:0 14px 28px rgba(3,30,70,.22)">${txt}</div>`;

/* ---------- magnifier, pencil, paper clip, push pin ---------- */
ART.magnifier = (w = 300) => sv("0 0 300 300", w, `
  <rect x="190" y="180" width="40" height="140" rx="18" fill="#0b1b33" transform="rotate(-45 210 250)"/>
  <circle cx="120" cy="120" r="96" fill="rgba(200,230,255,.28)" stroke="#26344a" stroke-width="18"/>
  <path d="M70 80a66 66 0 0 1 50-26" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".8"/>`);
ART.pencil = (w = 420) => sv("0 0 420 50", w, `
  <path d="M0 25 L44 5 V45Z" fill="#f2c79a"/><path d="M0 25 L15 18 V32Z" fill="#26344a"/>
  <rect x="44" y="5" width="300" height="40" fill="#008efa"/><rect x="44" y="5" width="300" height="13" fill="#4db0ff"/>
  <rect x="344" y="5" width="30" height="40" fill="#c9d3df"/><rect x="374" y="5" width="44" height="40" rx="8" fill="#ff8aa0"/>`);
ART.clip = (w = 60) => sv("0 0 60 150", w, `<path d="M15 120 V30 a15 15 0 0 1 30 0 V130 a22 22 0 0 1-44 0 V40" fill="none" stroke="#9aa8bb" stroke-width="7" stroke-linecap="round"/>`);
ART.pin = (w = 70, c = "#008efa") => sv("0 0 70 90", w, `<path d="M35 50 L35 88" stroke="#7d8896" stroke-width="5"/><circle cx="35" cy="32" r="30" fill="${c}"/><circle cx="26" cy="22" r="9" fill="#fff" opacity=".5"/>`);

/* ---------- check mark and cross, drawn on ---------- */
ART.check = (w = 140, c = "#008efa") => sv("0 0 140 140", w, `<path class="k" pathLength="1" d="M20 76 L56 112 L124 30" fill="none" stroke="${c}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>`);
ART.cross = (w = 140, c = "#ff4d4d") => sv("0 0 140 140", w, `<path class="k" pathLength="1" d="M24 24 L116 116 M116 24 L24 116" fill="none" stroke="${c}" stroke-width="20" stroke-linecap="round"/>`);

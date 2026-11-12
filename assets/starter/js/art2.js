// Drawn props, part 2: groceries, luxury goods, report, cart, charts, head, hand.

/* ---------- groceries ---------- */
ART.bread = (w = 320) => sv("0 0 320 150", w, `
  <path d="M10 90 Q20 20 160 18 Q300 20 310 90 Q300 140 160 140 Q20 140 10 90Z" fill="#d9913f"/>
  <path d="M10 90 Q20 20 160 18 Q300 20 310 90 Q240 70 160 72 Q80 70 10 90Z" fill="#eaa95a"/>
  ${[70, 120, 170, 220, 260].map((x) => `<path d="M${x} 40 q14 30 0 70" stroke="#b56d23" stroke-width="7" fill="none" stroke-linecap="round"/>`).join("")}`);
ART.milk = (w = 170) => sv("0 0 170 300", w, `
  <path d="M20 70 L50 20 H120 L150 70Z" fill="#dfe8f3"/><rect x="60" y="0" width="50" height="26" rx="6" fill="#008efa"/>
  <rect x="20" y="70" width="130" height="225" rx="10" fill="#fff"/>
  <path d="M20 170 Q60 150 85 170 T150 165 V295 H20Z" fill="#008efa"/>
  <text x="85" y="140" text-anchor="middle" font-family="Y" font-weight="950" font-size="44" fill="#0b1b33">شیر</text>`);
ART.eggs = (w = 340) => sv("0 0 340 170", w, `
  <path d="M0 80 H340 L320 165 H20Z" fill="#c9b79a"/>
  ${[40, 105, 170, 235, 300].map((x) => `<ellipse cx="${x}" cy="70" rx="30" ry="40" fill="#fbf1e2"/><ellipse cx="${x - 9}" cy="56" rx="8" ry="12" fill="#fff"/>`).join("")}
  <path d="M0 80 H340 L330 110 H10Z" fill="#b8a585"/>`);
ART.rice = (w = 230) => sv("0 0 230 300", w, `
  <path d="M30 40 Q115 0 200 40 L215 280 Q115 310 15 280Z" fill="#f5efe2"/>
  <path d="M30 40 Q115 0 200 40 L198 70 Q115 40 32 70Z" fill="#e3d8c0"/>
  <rect x="40" y="120" width="150" height="110" rx="16" fill="#0a6fd8"/>
  <text x="115" y="190" text-anchor="middle" font-family="Y" font-weight="950" font-size="44" fill="#fff">برنج</text>`);
ART.tomato = (w = 130) => sv("0 0 130 120", w, `
  <ellipse cx="65" cy="68" rx="60" ry="50" fill="#ff4d3d"/><ellipse cx="45" cy="50" rx="16" ry="10" fill="#ff9b8f" opacity=".7"/>
  <path d="M65 22 l-22 -6 l14 14 l-18 8 l26 0 l0 0 l26 0 l-18-8 l14-14z" fill="#2fa84f"/>`);
ART.oil = (w = 150) => sv("0 0 150 330", w, `
  <rect x="55" y="0" width="40" height="40" rx="8" fill="#008efa"/>
  <path d="M50 40 H100 L125 100 V310 Q125 328 107 328 H43 Q25 328 25 310 V100Z" fill="#ffd34d" opacity=".95"/>
  <rect x="30" y="160" width="90" height="90" rx="12" fill="#fff"/>
  <text x="75" y="220" text-anchor="middle" font-family="Y" font-weight="950" font-size="36" fill="#0a6fd8">روغن</text>`);
ART.soap = (w = 170) => sv("0 0 170 300", w, `
  <rect x="60" y="0" width="60" height="50" rx="10" fill="#0b1b33"/><rect x="70" y="40" width="40" height="30" fill="#0b1b33"/>
  <rect x="20" y="66" width="130" height="230" rx="40" fill="#5cc0ff"/>
  <rect x="40" y="130" width="90" height="100" rx="18" fill="#fff"/>
  <path d="M85 150 q24 30 0 54 q-24-24 0-54z" fill="#008efa"/>`);

/* ---------- luxury goods ---------- */
ART.watch = (w = 220) => sv("0 0 220 340", w, `
  <rect x="70" y="0" width="80" height="340" rx="24" fill="#26344a"/>
  <circle cx="110" cy="170" r="92" fill="#ffc23d"/><circle cx="110" cy="170" r="76" fill="#0b1b33"/>
  <path d="M110 170 V118 M110 170 L146 186" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
  <circle cx="110" cy="170" r="8" fill="#ffc23d"/><rect x="198" y="158" width="18" height="26" rx="5" fill="#ffc23d"/>`);
ART.sneaker = (w = 380) => sv("0 0 380 200", w, `
  <path d="M20 150 Q10 60 80 60 L150 40 Q200 100 260 110 Q360 120 370 160 V176 H20Z" fill="#fff"/>
  <path d="M20 162 H370 V186 Q370 196 360 196 H30 Q20 196 20 186Z" fill="#008efa"/>
  <path d="M110 90 L250 140" stroke="#008efa" stroke-width="16" stroke-linecap="round"/>
  ${[0, 1, 2].map((k) => `<path d="M${120 + k * 26} 64 l20 12" stroke="#0b1b33" stroke-width="6" stroke-linecap="round"/>`).join("")}`);
ART.headphones = (w = 300) => sv("0 0 300 300", w, `
  <path d="M40 180 Q40 30 150 30 Q260 30 260 180" fill="none" stroke="#26344a" stroke-width="24"/>
  <rect x="14" y="160" width="70" height="120" rx="30" fill="#0a6fd8"/><rect x="216" y="160" width="70" height="120" rx="30" fill="#0a6fd8"/>
  <rect x="34" y="176" width="20" height="90" rx="10" fill="#4db0ff" opacity=".6"/>`);
ART.ring = (w = 200) => sv("0 0 200 220", w, `
  <circle cx="100" cy="150" r="60" fill="none" stroke="#ffc23d" stroke-width="18"/>
  <path d="M60 40 L80 10 H120 L140 40 L100 90Z" fill="#bfe5ff"/><path d="M60 40 H140 L100 90Z" fill="#7cc4ff"/><path d="M80 10 L100 40 L120 10Z" fill="#fff"/>`);
ART.bag = (w = 280) => sv("0 0 280 300", w, `
  <path d="M80 90 Q80 20 140 20 Q200 20 200 90" fill="none" stroke="#0b1b33" stroke-width="14"/>
  <path d="M30 90 H250 L270 290 H10Z" fill="#008efa"/><path d="M30 90 H250 L254 130 H26Z" fill="#0a6fd8"/>
  <text x="140" y="230" text-anchor="middle" font-family="Y" font-weight="950" font-size="56" fill="#fff">!</text>`);

/* ---------- the BNPL report: a magazine-style cover ---------- */
ART.report = (w = 640) => sv("0 0 640 860", w, `
  <rect x="14" y="14" width="640" height="860" rx="10" fill="#c5d3e4"/>
  <rect x="0" y="0" width="640" height="860" rx="10" fill="#fff"/>
  <rect x="0" y="0" width="640" height="300" rx="10" fill="#008efa"/><rect x="0" y="280" width="640" height="20" fill="#008efa"/>
  <text x="590" y="250" text-anchor="end" font-family="Y" font-weight="950" font-size="54" fill="#fff">گزارش صنعت</text>
  <text x="50" y="250" text-anchor="start" font-family="Y" font-weight="950" font-size="66" fill="#fff" direction="ltr">BNPL</text>
  <text x="590" y="370" text-anchor="end" font-family="Y" font-weight="800" font-size="40" fill="#0b1b33">گزارش نمونه · داده‌های فرضی</text>
  <path d="M50 400 H590" stroke="#0b1b33" stroke-width="4"/>
  ${[0, 1, 2, 3, 4].map((k) => `<rect class="bar" x="${80 + k * 100}" y="${770 - (90 + k * 60)}" width="64" height="${90 + k * 60}" rx="8" fill="${k === 4 ? "#008efa" : "#b9dcff"}"/>`).join("")}
  <path d="M50 772 H590" stroke="#9aa8bb" stroke-width="3"/>
  ${[0, 1, 2].map((k) => `<rect x="${330}" y="${440 + k * 34}" width="${260 - k * 60}" height="14" rx="7" fill="#d0d7e2"/>`).join("")}
  <text x="50" y="830" text-anchor="start" font-family="Y" font-weight="700" font-size="26" fill="#667085">۱۴۰۵</text>`);

/* ---------- shopping cart ---------- */
ART.cart = (w = 420) => sv("0 0 420 340", w, `
  <path d="M10 30 H80 L130 250 H360" fill="none" stroke="#0b1b33" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M90 70 H400 L370 200 H120Z" fill="#008efa" stroke="#0b1b33" stroke-width="12" stroke-linejoin="round"/>
  <path d="M170 70 L180 200 M250 70 L250 200 M330 70 L315 200 M100 135 H385" stroke="#0b1b33" stroke-width="6" opacity=".35"/>
  <circle cx="160" cy="300" r="30" fill="#0b1b33"/><circle cx="330" cy="300" r="30" fill="#0b1b33"/>
  <circle cx="160" cy="300" r="10" fill="#9aa8bb"/><circle cx="330" cy="300" r="10" fill="#9aa8bb"/>`);

/* ---------- donut: fraction 0..1 drawn with `p` (call ART.donutSet) ---------- */
ART.donut = (w = 520, c = "#008efa", track = "rgba(255,255,255,.18)") => sv("0 0 520 520", w, `
  <circle cx="260" cy="260" r="200" fill="none" stroke="${track}" stroke-width="80"/>
  <circle class="arc" cx="260" cy="260" r="200" fill="none" stroke="${c}" stroke-width="80" pathLength="100"
    stroke-dasharray="0 100" transform="rotate(-90 260 260)"/>`);
ART.donutSet = (svgEl, f) => { svgEl.querySelector(".arc").setAttribute("stroke-dasharray", `${(f * 100).toFixed(2)} 100`); };

/* ---------- pie with one slice pulled out (fraction f) ---------- */
ART.pie = (w = 600, f = .17) => {
  const R = 250, a1 = -Math.PI / 2, a2 = a1 + f * 2 * Math.PI, mid = (a1 + a2) / 2;
  const pt = (a, r = R) => `${f1(300 + Math.cos(a) * r)} ${f1(300 + Math.sin(a) * r)}`;
  return sv("0 0 600 600", w, `
    <path d="M300 300 L${pt(a2)} A${R} ${R} 0 1 1 ${pt(a1)}Z" fill="#dbe7f5"/>
    <g class="slice" data-dx="${f1(Math.cos(mid) * 50)}" data-dy="${f1(Math.sin(mid) * 50)}">
      <path d="M300 300 L${pt(a1)} A${R} ${R} 0 0 1 ${pt(a2)}Z" fill="#008efa" stroke="#fff" stroke-width="6"/></g>
    <circle cx="300" cy="300" r="${R}" fill="none" stroke="#fff" stroke-width="6"/>`);
};

/* ---------- loop arrow (circle with a head) ---------- */
ART.loop = (w = 600, c = "#008efa") => sv("0 0 600 600", w, `
  <path class="lp" pathLength="1" d="M300 70 A230 230 0 1 1 90 205" fill="none" stroke="${c}" stroke-width="34" stroke-linecap="round"/>
  <path class="hd" d="M40 170 L120 160 L100 250Z" fill="${c}"/>`);

/* ---------- head in profile, facing right, with a scribble inside ---------- */
ART.head = (w = 640) => {
  let d = "M330 300";
  for (let k = 0; k < 26; k++) {
    const a = k * 2.3, r = 40 + (k * 37 % 90);
    d += ` Q${f1(330 + Math.cos(a) * r * 1.3)} ${f1(300 + Math.sin(a * 1.3) * r)} ${f1(330 + Math.cos(a + 1) * r)} ${f1(300 + Math.sin(a + 1) * r * .9)}`;
  }
  return sv("0 0 640 760", w, `
    <path d="M200 740 V600 Q120 560 120 430 Q100 330 150 230 Q230 90 380 100 Q520 110 560 240 Q580 300 560 360 L610 450 Q620 470 590 476 L560 480 L566 560 Q568 600 520 604 L440 600 V740Z" fill="rgba(255,255,255,.08)" stroke="#7cc4ff" stroke-width="6"/>
    <path class="sc" pathLength="1" d="${d}" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>`);
};

/* ---------- tapping hand cursor ---------- */
ART.hand = (w = 160) => sv("0 0 160 200", w, `
  <path d="M60 110 V24 a16 16 0 0 1 32 0 V90 l2-14 a15 15 0 0 1 30 4 v14 a14 14 0 0 1 28 6 V150 Q152 196 100 196 H82 Q50 196 34 166 L8 120 a15 15 0 0 1 24-16 Z" fill="#fff" stroke="#0b1b33" stroke-width="7" stroke-linejoin="round"/>`);

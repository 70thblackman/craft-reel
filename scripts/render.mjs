// Deterministic frame renderer for the reel engine.
//   node build/render.mjs [from] [to]     render 30 fps JPEG frames into build/frames
//   node build/render.mjs shot 1.2 3.4    single frames into build/shots
//   node build/render.mjs sfx             dump scene + SFX cues to build/cues.json
//   node build/render.mjs cover           screenshot cover.html to out/cover.png
// Run from the project root. Browser is recycled every CHUNK frames; existing frames are skipped.
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const CHUNK = 200;
const FPS = 30;
const W = 1080, H = 1920;

function chromePath() {
  const candidates = [
    process.env.CHROME_PATH,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files/Google/Chrome Beta/Application/chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ].filter(Boolean);
  for (const p of candidates) if (fs.existsSync(p)) return p;
  return "chrome";
}

const closeHard = async (b) => {
  await Promise.race([b.close().catch(() => {}), new Promise((r) => setTimeout(r, 5000))]);
  try { b.process()?.kill("SIGKILL"); } catch {}
};

const urlFor = (file) => pathToFileURL(path.resolve(file)).href + "?render";
const launch = () => puppeteer.launch({
  executablePath: chromePath(),
  headless: "new",
  timeout: 120000,
  protocolTimeout: 120000,
  args: [
    "--allow-file-access-from-files", "--disable-extensions", "--disable-gpu",
    "--js-flags=--max-old-space-size=500", "--disable-background-timer-throttling",
    "--font-render-hinting=none", "--hide-scrollbars",
  ],
});

async function open(pageFile = "index.html") {
  for (let k = 0; ; k++) {
    try { return await open1(pageFile); } catch (e) {
      console.log("open failed:", e.message);
      if (k >= 4) throw e;
      await new Promise((r) => setTimeout(r, 5000));
    }
  }
}
async function open1(pageFile) {
  const browser = await launch();
  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(180000);
  page.setDefaultTimeout(180000);
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.log("[pageerror]", e.message));
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") console.log("[console]", m.text()); });
  try {
    await page.goto(urlFor(pageFile), { waitUntil: "load" });
    await page.evaluate(() => window.ready);
  } catch (e) { await closeHard(browser); throw e; }
  return { browser, page };
}

const mode = process.argv[2];
fs.mkdirSync("build", { recursive: true });

if (mode === "sfx") {
  const { page, browser } = await open();
  const cues = await page.evaluate(() => window.cues());
  fs.writeFileSync("build/cues.json", JSON.stringify(cues, null, 1));
  console.log(`${cues.scenes.length} scenes, ${cues.sfx.length} cues, ${cues.duration}s -> build/cues.json`);
  await closeHard(browser);
  process.exit(0);
}

if (mode === "cover") {
  const { page, browser } = await open("cover.html");
  fs.mkdirSync("out", { recursive: true });
  await page.evaluate(() => window.seek(0));
  await page.screenshot({ path: "out/cover.png", type: "png" });
  console.log("wrote out/cover.png");
  await closeHard(browser);
  process.exit(0);
}

if (mode === "shot") {
  const { page, browser } = await open();
  fs.mkdirSync("build/shots", { recursive: true });
  for (const a of process.argv.slice(3)) {
    await page.evaluate((t) => window.seek(t), +a);
    await page.screenshot({ path: `build/shots/s_${(+a).toFixed(2)}.jpg`, type: "jpeg", quality: 88 });
    console.log("shot", a);
  }
  await closeHard(browser);
  process.exit(0);
}

// ---- full render ----
const outDir = path.resolve("build/frames");
fs.mkdirSync(outDir, { recursive: true });
const file = (f) => path.join(outDir, `f_${String(f).padStart(5, "0")}.jpg`);
const args = process.argv.slice(2).filter((a) => !isNaN(+a));
let { browser, page } = await open();
const DUR = await page.evaluate(() => window.DURATION);
const total = Math.round(DUR * FPS);
const from = Math.max(0, +(args[0] || 0));
const to = Math.min(total, +(args[1] || total));
const todo = [];
for (let f = from; f < to; f++) {
  if (!fs.existsSync(file(f)) || fs.statSync(file(f)).size < 2000) todo.push(f);
}
console.log(`${todo.length} frames to render (${from}-${to} of ${total})`);
const t0 = Date.now();
let done = 0;
for (let c = 0; c < todo.length; c += CHUNK) {
  const batch = todo.slice(c, c + CHUNK);
  try {
    if (!browser.connected) ({ browser, page } = await open());
    for (const f of batch) {
      await page.evaluate((t) => window.seek(t), f / FPS);
      await page.screenshot({ path: file(f), type: "jpeg", quality: 94, optimizeForSpeed: true });
      done++;
    }
  } catch (e) {
    console.log("chunk failed, rerun to resume:", e.message);
    break;
  } finally {
    await closeHard(browser);
  }
  const el = (Date.now() - t0) / 1000;
  console.log(`${done}/${todo.length}  ${el.toFixed(0)}s  ${(done / el).toFixed(2)} fps  eta ${((todo.length - done) / (done / el) / 60).toFixed(1)} min`);
}
process.exit(0);

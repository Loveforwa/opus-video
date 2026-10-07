// Frame-exact render: drives window.renderAt(t) in Chromium, grabs each frame, muxes with the BGM via ffmpeg.
//   node scripts/render.mjs                      full 60s @30fps → renders/game-theory.mp4
//   node scripts/render.mjs --from 17 --to 26    partial range
//   node scripts/render.mjs --stills 3.3,17.2    just PNG/JPEG stills into renders/stills/
// options: --fps 30  --rs 1 (3D render scale)  --workers 2  --headed  --chrome /path/to/chrome
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { serve } from './serve.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]);
  return acc;
}, []));
const FPS = Number(args.fps || 30), RS = Number(args.rs || 1), WORKERS = Number(args.workers || 1);
const OUT = path.join(ROOT, 'renders');
const FRAMES = path.join(OUT, 'frames');
fs.mkdirSync(FRAMES, { recursive: true });

const port = 8123 + Math.floor(Math.random() * 500);
const srv = await serve(port);
const launchOpts = {
  headless: !args.headed,
  args: ['--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--use-angle=default', '--enable-unsafe-swiftshader'],
};
if (args.chrome) launchOpts.executablePath = args.chrome;
else if (process.env.CHROME_PATH) launchOpts.executablePath = process.env.CHROME_PATH;
const browser = await chromium.launch(launchOpts);

async function openPage() {
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  page.on('pageerror', e => console.error('[page error]', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
  await page.goto(`http://localhost:${port}/index.html?rs=${RS}`);
  await page.waitForFunction('window.ready === true', null, { timeout: 120000 });
  return page;
}

async function renderFrame(page, t, file, q = .95) {
  const b64 = await page.evaluate(async ([t, q]) => { window.renderAt(t); return await window.grab(q); }, [t, q]);
  fs.writeFileSync(file, Buffer.from(b64, 'base64'));
}

const first = await openPage();
console.log('WebGL renderer:', await first.evaluate(() => window.glInfo()));

if (args.stills) {
  const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
  for (const s of String(args.stills).split(',')) {
    const t = Number(s); const f = path.join(dir, `t${t.toFixed(2)}.jpg`);
    await renderFrame(first, t, f, .9); console.log('still', f);
  }
} else {
  const dur = await first.evaluate(() => window.DURATION);
  const from = Number(args.from || 0), to = Math.min(dur, Number(args.to || dur));
  const f0 = Math.round(from * FPS), f1 = Math.round(to * FPS);
  for (const f of fs.readdirSync(FRAMES)) fs.unlinkSync(path.join(FRAMES, f));
  const pages = [first]; for (let i = 1; i < WORKERS; i++) pages.push(await openPage());
  const per = Math.ceil((f1 - f0) / pages.length);
  const t0 = Date.now(); let done = 0;
  await Promise.all(pages.map(async (p, w) => {
    for (let f = f0 + w * per; f < Math.min(f1, f0 + (w + 1) * per); f++) {   // contiguous chunks keep the physics cache warm
      await renderFrame(p, f / FPS, path.join(FRAMES, `${String(f - f0).padStart(5, '0')}.jpg`));
      if (++done % 30 === 0) {
        const el = (Date.now() - t0) / 1000, eta = el / done * (f1 - f0 - done);
        process.stdout.write(`\r${done}/${f1 - f0} frames · ${(el / done * 1000).toFixed(0)} ms/frame · ETA ${Math.round(eta)}s   `);
      }
    }
  }));
  console.log(`\nframes done in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  const name = args.out || (from === 0 && to === dur ? 'game-theory.mp4' : `game-theory_${from}-${to}.mp4`);
  const mp4 = path.join(OUT, name);
  const ff = spawnSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(FRAMES, '%05d.jpg'),
    '-ss', String(from), '-t', String(to - from), '-i', path.join(ROOT, 'assets/audio/bgm60.m4a'),
    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', mp4], { stdio: 'inherit' });
  if (ff.status !== 0) { console.error('ffmpeg failed — is ffmpeg installed and on PATH?'); process.exitCode = 1; }
  else console.log('✔', mp4);
}
await browser.close();
srv.close();

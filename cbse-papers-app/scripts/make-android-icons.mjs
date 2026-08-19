// Generate Android launcher icons + splash screens directly into android/app/src/main/res
import sharp from "sharp";
import { writeFile } from "node:fs/promises";

const ICON = "assets-src/icon-master.png";
const RES = "android/app/src/main/res";
const BRAND = { r: 49, g: 46, b: 129, alpha: 1 }; // #312E81

// --- launcher icons (legacy square + round) ---
const launcherSizes = { mdpi: 48, hdpi: 72, xhdpi: 96, xxhdpi: 144, xxxhdpi: 192 };
const master = sharp(ICON);
for (const [dpi, px] of Object.entries(launcherSizes)) {
  const sq = await master.clone().resize(px, px).png().toBuffer();
  // round: circle-cropped
  const roundMask = Buffer.from(
    `<svg width="${px}" height="${px}"><circle cx="${px / 2}" cy="${px / 2}" r="${px / 2}" fill="#fff"/></svg>`,
  );
  const rd = await sharp(sq)
    .composite([{ input: roundMask, blend: "dest-in" }])
    .png()
    .toBuffer();
  await sharp(sq).toFile(`${RES}/mipmap-${dpi}/ic_launcher.png`);
  await sharp(rd).toFile(`${RES}/mipmap-${dpi}/ic_launcher_round.png`);
  console.log(`✓ mipmap-${dpi}`);
}

// --- adaptive icon foreground (artwork with safe padding on transparent bg) ---
const fgSizes = { mdpi: 108, hdpi: 162, xhdpi: 216, xxhdpi: 324, xxxhdpi: 432 };
for (const [dpi, px] of Object.entries(fgSizes)) {
  const inner = Math.round(px * 0.66);
  const art = await sharp({
    create: { width: px, height: px, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite([
      {
        input: await sharp(ICON).resize(inner, inner).png().toBuffer(),
        left: Math.round((px - inner) / 2),
        top: Math.round((px - inner) / 2),
      },
    ])
    .png()
    .toBuffer();
  await sharp(art).toFile(`${RES}/mipmap-${dpi}/ic_launcher_foreground.png`);
}
console.log("✓ adaptive foregrounds");

// brand colour as adaptive-icon background
await writeFile(
  `${RES}/values/ic_launcher_background.xml`,
  `<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#312E81</color>\n</resources>\n`,
);

// --- splash screens: brand background, centered artwork ---
const portDensities = { mdpi: [320, 480], hdpi: [480, 720], xhdpi: [640, 960], xxhdpi: [960, 1440], xxxhdpi: [1280, 1920] };
async function splash(w, h, file) {
  const inner = Math.round(Math.min(w, h) * 0.5);
  const img = await sharp({ create: { width: w, height: h, channels: 4, background: BRAND } })
    .composite([
      {
        input: await sharp(ICON).resize(inner, inner).png().toBuffer(),
        left: Math.round((w - inner) / 2),
        top: Math.round((h - inner) / 2),
      },
    ])
    .png()
    .toBuffer();
  await sharp(img).toFile(file);
}
for (const [dpi, [w, h]] of Object.entries(portDensities)) {
  await splash(w, h, `${RES}/drawable-port-${dpi}/splash.png`);
  await splash(h, w, `${RES}/drawable-land-${dpi}/splash.png`);
}
await splash(480, 320, `${RES}/drawable/splash.png`);
console.log("✓ splash screens");
console.log("Android resources generated.");

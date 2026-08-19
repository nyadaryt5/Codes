// Generate all PWA / favicon icons from assets-src/icon-master.png
import sharp from "sharp";
import { mkdir } from "node:fs/promises";

const SRC = "assets-src/icon-master.png";
const OUT = "public/icons";
await mkdir(OUT, { recursive: true });

const jobs = [
  { file: `${OUT}/icon-192.png`, size: 192 },
  { file: `${OUT}/icon-512.png`, size: 512 },
  { file: "public/favicon.png", size: 64 },
  { file: `${OUT}/apple-touch-180.png`, size: 180 },
];

for (const j of jobs) {
  await sharp(SRC).resize(j.size, j.size).png().toFile(j.file);
  console.log("✓", j.file);
}

// Maskable icon: artwork scaled to the safe zone (~62%) on brand-colour background
const inner = await sharp(SRC).resize(318, 318).png().toBuffer();
await sharp({
  create: { width: 512, height: 512, channels: 4, background: { r: 49, g: 46, b: 129, alpha: 1 } },
})
  .composite([{ input: inner, left: 97, top: 97 }])
  .png()
  .toFile(`${OUT}/maskable-512.png`);
console.log("✓", `${OUT}/maskable-512.png`);

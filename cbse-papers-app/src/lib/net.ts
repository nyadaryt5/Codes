/**
 * Network layer: downloads official CBSE zip files / PDFs.
 * On Android (Capacitor) the download goes through the native HTTP plugin so
 * it is not affected by WebView CORS; in the PWA/browser it uses fetch and
 * degrades gracefully to "open the official page" when CORS blocks a request.
 */
import { Capacitor, CapacitorHttp } from "@capacitor/core";
import JSZip from "jszip";

export const isNative = () => Capacitor.getPlatform() !== "web";

export type BinaryKind = "zip" | "pdf";

export interface Downloaded {
  kind: BinaryKind;
  url: string;
  bytes: ArrayBuffer;
}

export class DownloadError extends Error {
  readonly tried: string[];
  constructor(message: string, tried: string[]) {
    super(message);
    this.name = "DownloadError";
    this.tried = tried;
  }
}

function detectKind(bytes: ArrayBuffer): BinaryKind | null {
  const b = new Uint8Array(bytes.slice(0, 4));
  if (b[0] === 0x50 && b[1] === 0x4b) return "zip"; // PK..
  if (b[0] === 0x25 && b[1] === 0x50 && b[2] === 0x44 && b[3] === 0x46) return "pdf"; // %PDF
  return null;
}

async function fetchNative(url: string, onProgress?: (frac: number) => void): Promise<ArrayBuffer> {
  onProgress?.(0.1);
  const res = await CapacitorHttp.get({
    url,
    responseType: "blob",
    connectTimeout: 20000,
    readTimeout: 60000,
    headers: { "User-Agent": "CBSE-Papers-App/1.0 (+android)" },
  });
  if (res.status >= 400) throw new Error(`HTTP ${res.status}`);
  const blob = res.data as Blob | string;
  onProgress?.(0.8);
  if (blob instanceof Blob) return blob.arrayBuffer();
  // some bridges return base64 strings
  const bin = atob(String(res.data));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

async function fetchWeb(url: string, onProgress?: (frac: number) => void): Promise<ArrayBuffer> {
  const res = await fetch(url, { mode: "cors", redirect: "follow" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const total = Number(res.headers.get("content-length") ?? 0);
  if (!res.body || !total) {
    onProgress?.(0.7);
    return res.arrayBuffer();
  }
  const reader = res.body.getReader();
  const chunks: Uint8Array[] = [];
  let got = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value) {
      chunks.push(value);
      got += value.length;
      onProgress?.(Math.min(0.95, got / total));
    }
  }
  const out = new Uint8Array(got);
  let off = 0;
  for (const c of chunks) {
    out.set(c, off);
    off += c.length;
  }
  return out.buffer;
}

/** Try each candidate URL until one returns a real zip or pdf. */
export async function downloadFirstWorking(
  urls: string[],
  onProgress?: (frac: number) => void,
): Promise<Downloaded> {
  const tried: string[] = [];
  for (const url of urls) {
    tried.push(url);
    try {
      const bytes = isNative()
        ? await fetchNative(url, onProgress)
        : await fetchWeb(url, onProgress);
      const kind = detectKind(bytes);
      if (kind) return { kind, url, bytes };
      // server returned something else (usually an HTML 404 page) — keep trying
    } catch {
      /* try next candidate */
    }
  }
  throw new DownloadError("The official file could not be downloaded right now.", tried);
}

export interface ZipEntry {
  name: string;
  getBytes: () => Promise<ArrayBuffer>;
  size: number;
}

/** List the PDF files inside an official CBSE zip (one per question-paper set). */
export async function listZipPdfs(bytes: ArrayBuffer): Promise<ZipEntry[]> {
  const zip = await JSZip.loadAsync(bytes);
  const out: ZipEntry[] = [];
  zip.forEach((path, file) => {
    if (!file.dir && /\.pdf$/i.test(path)) {
      out.push({
        name: path.replace(/^.*\//, ""),
        size: (file as unknown as { _data?: { uncompressedSize?: number } })._data
          ?.uncompressedSize ?? 0,
        getBytes: () => file.async("arraybuffer"),
      });
    }
  });
  out.sort((a, b) => a.name.localeCompare(b.name));
  return out;
}

/** Open a URL in the system browser (native) or a new tab (web). */
export function openExternal(url: string) {
  window.open(url, "_blank", "noopener,noreferrer");
}

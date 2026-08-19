/**
 * Offline paper storage in IndexedDB (works in the browser, the installed
 * PWA, and inside the Capacitor Android WebView).
 */

export interface PaperRecord {
  id: string;
  title: string;
  classId: string;
  subjectName: string;
  sessionLabel: string;
  setName?: string;
  kind: string;
  sourceUrl: string;
  size: number;
  savedAt: number;
  /** "saved" = user explicitly downloaded; "cache" = auto-cached, pruned when full */
  persisted: "saved" | "cache";
  favorite?: boolean;
  data: Blob;
}

const DB_NAME = "cbse-papers-db";
const STORE = "papers";
const CACHE_LIMIT_BYTES = 180 * 1024 * 1024; // keep auto-cache under ~180 MB

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        const os = db.createObjectStore(STORE, { keyPath: "id" });
        os.createIndex("savedAt", "savedAt");
        os.createIndex("persisted", "persisted");
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function tx<T>(mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  return openDb().then(
    (db) =>
      new Promise<T>((resolve, reject) => {
        const t = db.transaction(STORE, mode);
        const req = fn(t.objectStore(STORE));
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
        t.oncomplete = () => db.close();
        t.onerror = () => reject(t.error);
      }),
  );
}

export async function putPaper(rec: PaperRecord): Promise<void> {
  await tx("readwrite", (s) => s.put(rec));
  if (rec.persisted === "cache") await pruneCache();
}

export const getPaper = (id: string) =>
  tx<PaperRecord | undefined>("readonly", (s) => s.get(id) as IDBRequest<PaperRecord | undefined>);

export const deletePaper = (id: string) => tx("readwrite", (s) => s.delete(id));

export async function listPapers(): Promise<PaperRecord[]> {
  const all = await tx<PaperRecord[]>("readonly", (s) => s.getAll() as IDBRequest<PaperRecord[]>);
  return all.sort((a, b) => b.savedAt - a.savedAt);
}

export async function setFavorite(id: string, fav: boolean): Promise<void> {
  const rec = await getPaper(id);
  if (rec) {
    rec.favorite = fav;
    await tx("readwrite", (s) => s.put(rec));
  }
}

export async function markSaved(id: string): Promise<void> {
  const rec = await getPaper(id);
  if (rec) {
    rec.persisted = "saved";
    await tx("readwrite", (s) => s.put(rec));
  }
}

export async function storageUsage(): Promise<{ used: number; count: number }> {
  const all = await listPapers();
  return { used: all.reduce((n, r) => n + r.size, 0), count: all.length };
}

async function pruneCache(): Promise<void> {
  const all = await listPapers();
  let total = 0;
  const cached: PaperRecord[] = [];
  for (const r of all) {
    if (r.persisted === "cache") cached.push(r);
    total += r.size;
  }
  // delete oldest cached items until we're under the limit
  for (let i = cached.length - 1; i >= 0 && total > CACHE_LIMIT_BYTES; i--) {
    await deletePaper(cached[i].id);
    total -= cached[i].size;
  }
}

export const paperKey = (sourceUrl: string, setName?: string) =>
  `${sourceUrl}::${setName ?? "single"}`;

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

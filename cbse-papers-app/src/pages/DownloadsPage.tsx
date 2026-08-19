import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState, PageHeader, SectionHeader, Chip } from "../components/ui";
import {
  deletePaper,
  formatBytes,
  listPapers,
  setFavorite,
  storageUsage,
  type PaperRecord,
} from "../lib/db";

export default function DownloadsPage() {
  const [all, setAll] = useState<PaperRecord[]>([]);
  const [usage, setUsage] = useState({ used: 0, count: 0 });
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    const [papers, u] = await Promise.all([listPapers(), storageUsage()]);
    setAll(papers);
    setUsage(u);
    setLoading(false);
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const saved = all.filter((r) => r.persisted === "saved");
  const cached = all.filter((r) => r.persisted === "cache");
  const favorites = saved.filter((r) => r.favorite);

  const clearCache = async () => {
    await Promise.all(cached.map((r) => deletePaper(r.id)));
    await reload();
  };

  return (
    <div>
      <PageHeader title="Offline library" subtitle="Papers stored on this device" />
      <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
        {/* usage */}
        <div className="flex items-center justify-between rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 p-4 text-white shadow">
          <div>
            <p className="text-xs font-semibold text-indigo-200">Storage used</p>
            <p className="text-xl font-extrabold">{formatBytes(usage.used)}</p>
            <p className="text-xs text-indigo-200">{usage.count} papers on device</p>
          </div>
          <Link
            to="/import"
            className="pressable rounded-xl bg-white/15 px-4 py-2.5 text-sm font-bold ring-1 ring-white/30"
          >
            ＋ Add PDFs
          </Link>
        </div>

        {loading ? null : all.length === 0 ? (
          <EmptyState
            icon="📚"
            title="Nothing saved yet"
            body="Open any paper and tap “Save” to keep it for the exam hall run — no internet needed afterwards. Cached copies also appear here automatically."
            action={
              <Link to="/" className="pressable mt-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-bold text-white">
                Browse papers
              </Link>
            }
          />
        ) : (
          <>
            {favorites.length > 0 && (
              <>
                <SectionHeader>⭐ Favourites</SectionHeader>
                <PaperList rows={favorites} onChanged={reload} />
              </>
            )}

            {saved.length > 0 && (
              <>
                <SectionHeader>Saved offline</SectionHeader>
                <PaperList rows={saved} onChanged={reload} />
              </>
            )}

            {cached.length > 0 && (
              <>
                <SectionHeader
                  right={
                    <button onClick={() => void clearCache()} className="text-xs font-bold text-rose-500">
                      Clear all
                    </button>
                  }
                >
                  Auto-downloaded copies
                </SectionHeader>
                <PaperList rows={cached} onChanged={reload} />
                <p className="mt-2 text-[11px] text-slate-400">
                  These keep recently-viewed papers available offline and are cleaned up
                  automatically when space runs low. Tap ⬇ on a paper to keep it forever.
                </p>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function PaperList({ rows, onChanged }: { rows: PaperRecord[]; onChanged: () => void | Promise<void> }) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
      {rows.map((r, i) => (
        <div key={r.id} className={`flex items-center gap-3 px-4 py-3 ${i > 0 ? "border-t border-slate-100" : ""}`}>
          <Link to={`/view/${encodeURIComponent(r.id)}`} className="pressable flex min-w-0 flex-1 items-center gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-lg">📄</span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-bold text-slate-800">
                {r.setName ? r.setName.replace(/\.pdf$/i, "") : r.title}
              </span>
              <span className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-slate-400">
                <Chip tone="indigo">Class {r.classId}</Chip>
                <span className="truncate">{r.subjectName} · {r.sessionLabel}</span>
                <span>{formatBytes(r.size)}</span>
              </span>
            </span>
          </Link>
          <button
            aria-label="Favorite"
            onClick={async () => {
              await setFavorite(r.id, !r.favorite);
              await onChanged();
            }}
            className={`pressable p-2 ${r.favorite ? "text-amber-400" : "text-slate-300"}`}
          >
            <svg viewBox="0 0 24 24" fill={r.favorite ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8" className="h-5 w-5">
              <path d="m12 3 2.7 5.6 6.3.8-4.6 4.3 1.2 6.1L12 16.9l-5.6 3 1.2-6.2L3 9.4l6.3-.8z" />
            </svg>
          </button>
          <button
            aria-label="Delete"
            onClick={async () => {
              await deletePaper(r.id);
              await onChanged();
            }}
            className="pressable p-2 text-slate-300 hover:text-rose-500"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
              <path d="M4 7h16" />
              <path d="M9 7V4h6v3" />
              <path d="M6 7l1 14h10l1-14" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}

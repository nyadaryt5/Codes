import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { classById, paperFor, sessionsFor, subjectsFor } from "../data/catalog";
import { Chip, PageHeader, ProgressBar, Spinner } from "../components/ui";
import PdfViewer from "../components/PdfViewer";
import { downloadFirstWorking, listZipPdfs, openExternal, type ZipEntry } from "../lib/net";
import {
  formatBytes,
  getPaper,
  listPapers,
  markSaved,
  paperKey,
  putPaper,
  type PaperRecord,
} from "../lib/db";

interface SetRow {
  name: string;
  size: number;
  getBytes: () => Promise<ArrayBuffer>;
  recordId?: string;
}

type Phase =
  | { kind: "checking" }
  | { kind: "downloading"; frac: number }
  | { kind: "listing"; resolvedFrom: string }
  | { kind: "ready"; resolvedFrom: string; rows: SetRow[] }
  | { kind: "error"; message: string };

const pretty = (name: string) =>
  name.replace(/\.pdf$/i, "").replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();

export default function PaperPage() {
  const [params] = useSearchParams();
  const c = params.get("c");
  const sid = params.get("s");
  const e = params.get("e");
  const info = classById(c ?? undefined);
  const subject = info ? subjectsFor(info.id).find((x) => x.id === sid) : undefined;
  const session = info?.boardExam
    ? sessionsFor(info.id).find((x) => x.id === e)
    : undefined;

  const paper = useMemo(
    () =>
      info && subject && session ? paperFor(info.id, subject, session) : undefined,
    [info, subject, session],
  );

  const [phase, setPhase] = useState<Phase>({ kind: "checking" });
  const [records, setRecords] = useState<Map<string, PaperRecord>>(new Map());
  const [viewer, setViewer] = useState<{ title: string; getBytes: () => Promise<ArrayBuffer> } | null>(null);

  const refreshRecords = useCallback(async () => {
    const all = await listPapers();
    setRecords(new Map(all.map((r) => [r.id, r])));
  }, []);

  const load = useCallback(async () => {
    if (!paper) return;
    setViewer(null);

    /* 1) offline-first: any sets already on device? */
    setPhase({ kind: "checking" });
    const all = await listPapers();
    const cached = all.filter((r) => paper.zipUrls.includes(r.sourceUrl));
    if (cached.length > 0) {
      setRecords(new Map(all.map((r) => [r.id, r])));
      setPhase({
        kind: "ready",
        resolvedFrom: "on-device copy",
        rows: cached.map((r) => ({
          name: r.setName ?? r.title,
          size: r.size,
          getBytes: () => r.data.arrayBuffer(),
          recordId: r.id,
        })),
      });
      return;
    }

    /* 2) download from the official archive */
    setPhase({ kind: "downloading", frac: 0 });
    try {
      const dl = await downloadFirstWorking(paper.zipUrls, (f) =>
        setPhase({ kind: "downloading", frac: f }),
      );
      setPhase({ kind: "listing", resolvedFrom: dl.url });

      const entries: ZipEntry[] =
        dl.kind === "zip"
          ? await listZipPdfs(dl.bytes)
          : [
              {
                name: `${paper.subjectName} ${paper.sessionId}.pdf`,
                size: dl.bytes.byteLength,
                getBytes: async () => dl.bytes,
              },
            ];

      /* 3) auto-cache every set so revisits are instant & offline */
      const rows: SetRow[] = [];
      for (const en of entries) {
        const id = paperKey(dl.url, en.name);
        let rec = await getPaper(id);
        if (!rec) {
          const bytes = await en.getBytes();
          rec = {
            id,
            title: `${paper.subjectName} – ${paper.sessionLabel}`,
            classId: paper.classId,
            subjectName: paper.subjectName,
            sessionLabel: paper.sessionLabel,
            setName: en.name,
            kind: paper.kind,
            sourceUrl: dl.url,
            size: bytes.byteLength,
            savedAt: Date.now(),
            persisted: "cache",
            data: new Blob([bytes], { type: "application/pdf" }),
          };
          await putPaper(rec);
        }
        rows.push({ name: en.name, size: rec.size, getBytes: () => rec!.data.arrayBuffer(), recordId: rec.id });
      }
      await refreshRecords();
      setPhase({ kind: "ready", resolvedFrom: dl.url, rows });
    } catch (err) {
      setPhase({
        kind: "error",
        message:
          err instanceof Error
            ? err.message
            : "Download failed. Check your internet and try again.",
      });
    }
  }, [paper, refreshRecords]);

  useEffect(() => {
    if (!paper || paper.kind === "sample") return;
    void load();
  }, [paper, load]);

  if (!paper) return <Navigate to="/" replace />;

  /* Official sample papers live on CBSE Academic pages — open & explain. */
  if (paper.kind === "sample") {
    return (
      <div>
        <PageHeader back title={paper.subjectName} subtitle={paper.sessionLabel} />
        <div className="mx-auto max-w-3xl px-4 pt-8 pb-8">
          <div className="rounded-3xl bg-white p-6 text-center shadow-sm ring-1 ring-slate-100">
            <div className="text-5xl">📝</div>
            <h2 className="mt-3 text-lg font-extrabold text-slate-900">
              Official sample paper &amp; marking scheme
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-slate-500">
              CBSE publishes sample papers on its Academic website (free PDFs, with solutions /
              marking scheme for every subject). Tap below to open the official{" "}
              <b>{paper.sessionLabel}</b> page and choose{" "}
              <b>{paper.subjectName}</b>.
            </p>
            <button
              onClick={() => openExternal(paper.pageUrl)}
              className="pressable mt-5 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-bold text-white shadow"
            >
              Open official page
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M14 4h6v6" />
                <path d="M20 4 10 14" />
                <path d="M20 14v6H4V4h6" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        back
        title={paper.subjectName}
        subtitle={paper.sessionLabel}
        actions={
          <button
            aria-label="Open official source"
            onClick={() => openExternal(paper.pageUrl)}
            className="pressable flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-slate-600"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
              <path d="M14 4h6v6" />
              <path d="M20 4 10 14" />
              <path d="M20 14v6H4V4h6" />
            </svg>
          </button>
        }
      />

      {viewer ? (
        <ViewerView
          title={pretty(viewer.title)}
          getBytes={viewer.getBytes}
          onClose={() => setViewer(null)}
        />
      ) : (
        <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
          {phase.kind === "checking" && (
            <Center icon={<Spinner className="h-8 w-8 text-indigo-600" />} text="Checking on-device copy…" />
          )}

          {phase.kind === "downloading" && (
            <div className="pt-16">
              <Center icon={<div className="text-5xl">⬇️</div>} text="Downloading from cbse.gov.in…" />
              <div className="mx-auto mt-4 max-w-xs">
                <ProgressBar frac={phase.frac} />
              </div>
            </div>
          )}

          {phase.kind === "listing" && (
            <Center icon={<Spinner className="h-8 w-8 text-indigo-600" />} text="Reading question paper sets…" />
          )}

          {phase.kind === "error" && (
            <div className="rounded-3xl bg-white p-6 pt-10 text-center shadow-sm ring-1 ring-slate-100">
              <div className="text-5xl">📡</div>
              <p className="mt-3 font-extrabold text-slate-900">Couldn't fetch the paper</p>
              <p className="mx-auto mt-1 max-w-sm text-sm text-slate-500">{phase.message}</p>
              <div className="mt-5 flex justify-center gap-2">
                <button
                  onClick={() => void load()}
                  className="pressable rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white"
                >
                  Retry
                </button>
                <button
                  onClick={() => openExternal(paper.pageUrl)}
                  className="pressable rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700"
                >
                  Open official archive
                </button>
              </div>
              <p className="mt-4 text-[11px] text-slate-400">
                Papers are served directly from the official CBSE website — if it's busy (exam
                season!), opening the archive in your browser works too.
              </p>
            </div>
          )}

          {phase.kind === "ready" && (
            <>
              <div className="mb-2 flex items-center justify-between">
                <h2 className="text-sm font-bold tracking-wide text-slate-500 uppercase">
                  Question paper sets
                </h2>
                <Chip tone="emerald">{phase.resolvedFrom === "on-device copy" ? "📴 offline copy" : "✓ official"}</Chip>
              </div>
              <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
                {phase.rows.map((row, i) => {
                  const rec = row.recordId ? records.get(row.recordId) : undefined;
                  const saved = rec?.persisted === "saved";
                  return (
                    <div
                      key={row.name}
                      className={`flex items-center gap-3 px-4 py-3 ${i > 0 ? "border-t border-slate-100" : ""}`}
                    >
                      <button
                        className="pressable flex min-w-0 flex-1 items-center gap-3 text-left"
                        onClick={() => setViewer({ title: row.name, getBytes: row.getBytes })}
                      >
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-lg">
                          📄
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-bold text-slate-800">
                            {pretty(row.name)}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {row.size ? formatBytes(row.size) : "PDF"}
                            {saved ? " · saved offline" : rec ? " · offline copy" : ""}
                          </span>
                        </span>
                      </button>
                      {saved ? (
                        <Chip tone="emerald">✓ Saved</Chip>
                      ) : (
                        rec && (
                          <button
                            onClick={async () => {
                              await markSaved(rec.id);
                              await refreshRecords();
                            }}
                            className="pressable flex items-center gap-1 rounded-full bg-indigo-50 px-3 py-1.5 text-xs font-bold text-indigo-700"
                          >
                            ⬇ Save
                          </button>
                        )
                      )}
                    </div>
                  );
                })}
              </div>
              <p className="mt-3 text-center text-[11px] text-slate-400">
                Source: cbse.gov.in (official CBSE archive) · sets are cached automatically for
                offline use
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Center({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex flex-col items-center gap-3 pt-16">
      {icon}
      <p className="text-sm font-medium text-slate-500">{text}</p>
    </div>
  );
}

function ViewerView({
  title,
  getBytes,
  onClose,
}: {
  title: string;
  getBytes: () => Promise<ArrayBuffer>;
  onClose: () => void;
}) {
  return (
    <div>
      <div className="safe-top sticky top-0 z-20 flex items-center gap-2 border-b border-slate-200 bg-white/90 px-3 py-2 backdrop-blur">
        <button
          onClick={onClose}
          className="pressable flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-700"
          aria-label="Back to sets"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <p className="truncate text-sm font-bold text-slate-800">{title}</p>
      </div>
      <PdfViewer title={title} getData={getBytes} />
    </div>
  );
}

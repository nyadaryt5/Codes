import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { EmptyState, PageHeader, SectionHeader, Chip } from "../components/ui";
import { CLASSES, subjectsFor, type ClassId } from "../data/catalog";
import { deletePaper, formatBytes, listPapers, type PaperRecord } from "../lib/db";

export default function ImportPage() {
  const [params] = useSearchParams();
  const [cls, setCls] = useState<ClassId>((params.get("class") as ClassId) || "5");
  const [subject, setSubject] = useState(params.get("subject") ?? "");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<string[]>([]);
  const [imported, setImported] = useState<PaperRecord[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  const reload = useCallback(async () => {
    const all = await listPapers();
    setImported(all.filter((r) => r.kind === "imported"));
  }, []);
  useEffect(() => {
    void reload();
  }, [reload]);

  const onFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setBusy(true);
    setDone([]);
    const ok: string[] = [];
    const { putPaper } = await import("../lib/db");
    for (const f of Array.from(files)) {
      if (!/\.pdf$/i.test(f.name) && f.type !== "application/pdf") continue;
      try {
        const bytes = await f.arrayBuffer();
        const subj = subject.trim() || "General";
        const rec: PaperRecord = {
          id: `imported-${crypto.randomUUID()}`,
          title: `${subj} – Class ${cls}`,
          classId: cls,
          subjectName: subj,
          sessionLabel: "Imported paper",
          setName: f.name,
          kind: "imported",
          sourceUrl: "local",
          size: bytes.byteLength,
          savedAt: Date.now(),
          persisted: "saved",
          data: new Blob([bytes], { type: "application/pdf" }),
        };
        await putPaper(rec);
        ok.push(f.name);
      } catch {
        /* skip file */
      }
    }
    setDone(ok);
    setBusy(false);
    await reload();
  };

  return (
    <div>
      <PageHeader back title="Add your own papers" subtitle="PDF imports · stored only on this device" />
      <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
        <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="text-xs font-bold text-slate-500">Class</span>
              <select
                value={cls}
                onChange={(e) => setCls(e.target.value as ClassId)}
                className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-800 outline-none focus:border-indigo-400"
              >
                {CLASSES.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
                <option value="misc">Other</option>
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-bold text-slate-500">Subject</span>
              <input
                list="subjects"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Mathematics"
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-semibold text-slate-800 outline-none focus:border-indigo-400"
              />
              <datalist id="subjects">
                {(cls === "5" || cls === "8" || cls === "10" || cls === "12"
                  ? subjectsFor(cls)
                  : []
                ).map((x) => (
                  <option key={x.id} value={x.name} />
                ))}
              </datalist>
            </label>
          </div>

          <button
            onClick={() => fileRef.current?.click()}
            disabled={busy}
            className="pressable mt-4 flex w-full flex-col items-center gap-2 rounded-2xl border-2 border-dashed border-indigo-200 bg-indigo-50/50 px-4 py-8 text-center"
          >
            <span className="text-3xl">{busy ? "⏳" : "📥"}</span>
            <span className="text-sm font-bold text-indigo-900">
              {busy ? "Importing…" : "Tap to choose PDF files"}
            </span>
            <span className="text-[11px] text-indigo-400">
              Question papers from your school, tuition or teacher — one or many at once
            </span>
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            hidden
            onChange={(e) => void onFiles(e.target.files)}
          />

          {done.length > 0 && (
            <p className="mt-3 rounded-xl bg-emerald-50 px-3 py-2 text-center text-xs font-bold text-emerald-700">
              ✓ Imported {done.length} paper{done.length > 1 ? "s" : ""} — available offline
            </p>
          )}
        </div>

        <SectionHeader>Imported papers ({imported.length})</SectionHeader>
        {imported.length === 0 ? (
          <EmptyState icon="🗂" title="No imports yet" body="Papers you add show up here and inside each class's subject page." />
        ) : (
          <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
            {imported.map((r, i) => (
              <div key={r.id} className={`flex items-center gap-3 px-4 py-3 ${i > 0 ? "border-t border-slate-100" : ""}`}>
                <Link to={`/view/${encodeURIComponent(r.id)}`} className="pressable flex min-w-0 flex-1 items-center gap-3">
                  <span className="text-xl">📄</span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-bold text-slate-800">{r.setName}</span>
                    <span className="mt-0.5 flex items-center gap-1.5 text-[11px] text-slate-400">
                      <Chip tone="indigo">Class {r.classId}</Chip>
                      <span className="truncate">{r.subjectName}</span>
                      <span>{formatBytes(r.size)}</span>
                    </span>
                  </span>
                </Link>
                <button
                  aria-label="Delete"
                  onClick={async () => {
                    await deletePaper(r.id);
                    await reload();
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
        )}
      </div>
    </div>
  );
}

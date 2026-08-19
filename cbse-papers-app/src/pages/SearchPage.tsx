import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, EmptyState, Chip } from "../components/ui";
import { CLASSES, sessionsFor, subjectsFor } from "../data/catalog";

interface Hit {
  title: string;
  sub: string;
  icon: string;
  to: string;
  cls: string;
  hay: string;
}

function buildIndex(): Hit[] {
  const hits: Hit[] = [];
  for (const c of CLASSES) {
    for (const sub of subjectsFor(c.id)) {
      hits.push({
        title: sub.name,
        sub: `${c.title} · ${c.boardExam ? "all papers" : "pattern resources"}`,
        icon: sub.emoji,
        to: `/class/${c.id}/subject/${sub.id}`,
        cls: c.id,
        hay: `${sub.name} class ${c.id} ${c.boardExam ? "board exam sample paper" : "pattern"}`.toLowerCase(),
      });
      if (c.boardExam) {
        for (const se of sessionsFor(c.id)) {
          hits.push({
            title: `${sub.name} – ${se.label}`,
            sub: `${c.title} · ${se.kind === "sample" ? "sample paper" : se.kind === "compartment" ? "compartment" : "board exam"}`,
            icon: se.kind === "sample" ? "📝" : "📄",
            to: `/paper?c=${c.id}&s=${sub.id}&e=${se.id}`,
            cls: c.id,
            hay: `${sub.name} ${se.label} ${se.id} class ${c.id} question paper ${se.kind}`.toLowerCase(),
          });
        }
      }
    }
  }
  return hits;
}

export default function SearchPage() {
  const [q, setQ] = useState("");
  const index = useMemo(buildIndex, []);
  const [cls, setCls] = useState<string | null>(null);

  const results = useMemo(() => {
    const tokens = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (tokens.length === 0) return [];
    return index
      .filter((h) => (cls ? h.cls === cls : true))
      .filter((h) => tokens.every((t) => h.hay.includes(t)))
      .slice(0, 60);
  }, [q, index, cls]);

  return (
    <div>
      <PageHeader title="Search papers" />
      <div className="sticky top-[57px] z-10 border-b border-slate-100 bg-slate-50/95 px-4 pt-2 pb-3 backdrop-blur">
        <div className="mx-auto max-w-3xl">
          <div className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 shadow-sm ring-1 ring-slate-200">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-5 w-5 text-slate-400">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              autoFocus
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="e.g. physics 2026, maths sample paper, SST…"
              className="w-full bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400"
            />
            {q && (
              <button onClick={() => setQ("")} className="text-xs font-bold text-slate-400">
                Clear
              </button>
            )}
          </div>
          <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
            {["5", "8", "10", "12"].map((c) => (
              <button
                key={c}
                onClick={() => setCls((x) => (x === c ? null : c))}
                className={`pressable shrink-0 rounded-full px-3.5 py-1.5 text-xs font-bold ${
                  cls === c ? "bg-indigo-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"
                }`}
              >
                Class {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
        {q.trim() === "" ? (
          <EmptyState
            icon="🔎"
            title="Search everything"
            body="Try a subject, a year, or “sample paper”. Matching board papers appear instantly."
          />
        ) : results.length === 0 ? (
          <EmptyState icon="🤔" title={`No matches for “${q}”`} body="Check the spelling, or browse the class from the Home tab." />
        ) : (
          <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
            {results.map((r, i) => (
              <Link
                key={`${r.to}-${i}`}
                to={r.to}
                className={`pressable flex items-center gap-3 px-4 py-3 ${i > 0 ? "border-t border-slate-100" : ""}`}
              >
                <span className="text-xl">{r.icon}</span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-bold text-slate-800">{r.title}</span>
                  <span className="text-[11px] text-slate-400">{r.sub}</span>
                </span>
                <Chip tone="indigo">Class {r.cls}</Chip>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

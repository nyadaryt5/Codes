import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import {
  classById,
  schoolResources,
  sessionsFor,
  subjectsFor,
  type ExamSession,
} from "../data/catalog";
import { Chip, EmptyState, PageHeader, SectionHeader } from "../components/ui";
import { listPapers, type PaperRecord } from "../lib/db";
import { openExternal } from "../lib/net";

export default function SubjectPage() {
  const { classId, subjectId } = useParams();
  const info = classById(classId);
  const subject = info && subjectsFor(info.id).find((x) => x.id === subjectId);
  if (!info || !subject) return <Navigate to="/" replace />;
  return info.boardExam ? (
    <BoardSubject info={info} subjectId={subject.id} />
  ) : (
    <SchoolSubject classId={info.id as "5" | "8"} subjectName={subject.name} emoji={subject.emoji} title={info.title} />
  );
}

/* ------------------------------------------------------------------ */
/* Classes 10 & 12 → official exam sessions                            */
/* ------------------------------------------------------------------ */
function BoardSubject({ info, subjectId }: { info: NonNullable<ReturnType<typeof classById>>; subjectId: string }) {
  const subject = subjectsFor(info.id).find((x) => x.id === subjectId)!;
  const sessions = sessionsFor(info.id);
  const board = sessions.filter((x) => x.kind === "board");
  const comptt = sessions.filter((x) => x.kind === "compartment");
  const sample = sessions.filter((x) => x.kind === "sample");

  return (
    <div>
      <PageHeader back title={subject.name} subtitle={`${info.title} · question papers`} />
      <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
        <SectionHeader>Board exam question papers</SectionHeader>
        <SessionList classId={info.id} subjectId={subject.id} sessions={board} />

        <SectionHeader right={<Chip tone="amber">Extra attempt</Chip>}>
          {info.id === "10" ? "Second board exam" : "Compartment exam"}
        </SectionHeader>
        <SessionList classId={info.id} subjectId={subject.id} sessions={comptt} />

        <SectionHeader right={<Chip tone="indigo">With marking scheme</Chip>}>
          Official CBSE sample papers
        </SectionHeader>
        <SessionList classId={info.id} subjectId={subject.id} sessions={sample} sample />
      </div>
    </div>
  );
}

function SessionList({
  classId,
  subjectId,
  sessions,
  sample = false,
}: {
  classId: string;
  subjectId: string;
  sessions: ExamSession[];
  sample?: boolean;
}) {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
      {sessions.map((se, i) => (
        <Link
          key={se.id}
          to={`/paper?c=${classId}&s=${subjectId}&e=${se.id}`}
          className={`pressable flex items-center gap-3 px-4 py-3.5 ${i > 0 ? "border-t border-slate-100" : ""}`}
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-lg">
            {sample ? "📝" : se.kind === "compartment" ? "🔁" : "📄"}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-bold text-slate-800">{se.label}</span>
            <span className="block text-[11px] text-slate-400">
              {sample ? "PDFs & marking scheme · official CBSE Academic" : "PDF sets · official CBSE archive"}
            </span>
          </span>
          <button
            aria-label="Open source page"
            className="pressable rounded-full p-2 text-slate-300 hover:text-indigo-500"
            onClick={(e) => {
              e.preventDefault();
              openExternal(se.pageUrl);
            }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
              <path d="M14 4h6v6" />
              <path d="M20 4 10 14" />
              <path d="M20 14v6H4V4h6" />
            </svg>
          </button>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 shrink-0 text-slate-300">
            <path d="m9 6 6 6-6 6" />
          </svg>
        </Link>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Classes 5 & 8 → pattern resources + own uploads                     */
/* ------------------------------------------------------------------ */
function SchoolSubject({
  classId,
  subjectName,
  emoji,
  title,
}: {
  classId: "5" | "8";
  subjectName: string;
  emoji: string;
  title: string;
}) {
  const [own, setOwn] = useState<PaperRecord[]>([]);
  const resources = useMemo(() => schoolResources(classId, subjectName), [classId, subjectName]);

  useEffect(() => {
    listPapers().then((all) =>
      setOwn(all.filter((r) => r.kind === "imported" && r.classId === classId && r.subjectName === subjectName)),
    );
  }, [classId, subjectName]);

  return (
    <div>
      <PageHeader back title={subjectName} subtitle={`${title} · CBSE pattern`} />
      <div className="mx-auto max-w-3xl px-4 pt-3 pb-8">
        <div className="rounded-2xl border border-sky-200 bg-sky-50 p-4 text-[13px] leading-snug text-sky-900">
          {emoji} CBSE does not publish board papers for {title.toLowerCase()}. Add your school's
          question papers here — they stay on your device and work offline.
        </div>

        <SectionHeader
          right={
            <Link
              to={`/import?class=${classId}&subject=${encodeURIComponent(subjectName)}`}
              className="pressable rounded-full bg-indigo-600 px-3 py-1.5 text-xs font-bold text-white"
            >
              ＋ Add paper (PDF)
            </Link>
          }
        >
          My {subjectName} papers
        </SectionHeader>
        {own.length === 0 ? (
          <div className="rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
            <EmptyState
              icon="📥"
              title="No papers added yet"
              body="Import question papers your school or teacher shared (PDF) — e.g. half-yearly, annual, revision tests."
              action={
                <Link
                  to={`/import?class=${classId}&subject=${encodeURIComponent(subjectName)}`}
                  className="pressable mt-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-bold text-white"
                >
                  Import a PDF
                </Link>
              }
            />
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
            {own.map((r, i) => (
              <Link
                key={r.id}
                to={`/view/${encodeURIComponent(r.id)}`}
                className={`pressable flex items-center gap-3 px-4 py-3 ${i > 0 ? "border-t border-slate-100" : ""}`}
              >
                <span className="text-xl">📄</span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-bold text-slate-800">{r.setName ?? r.title}</span>
                  <span className="text-[11px] text-slate-400">{r.sessionLabel} · on-device</span>
                </span>
              </Link>
            ))}
          </div>
        )}

        <SectionHeader>Free official resources</SectionHeader>
        <div className="space-y-2.5">
          {resources.map((r) => (
            <button
              key={r.title}
              onClick={() => openExternal(r.url)}
              className="pressable flex w-full items-center gap-3 rounded-2xl bg-white p-4 text-left shadow-sm ring-1 ring-slate-100"
            >
              <span className="text-2xl">{r.icon}</span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-bold text-slate-800">{r.title}</span>
                <span className="mt-0.5 block text-xs leading-snug text-slate-500">{r.description}</span>
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 shrink-0 text-slate-300">
                <path d="M14 4h6v6" />
                <path d="M20 4 10 14" />
                <path d="M20 14v6H4V4h6" />
              </svg>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

import { Link, Navigate, useParams } from "react-router-dom";
import { classById, subjectsFor } from "../data/catalog";
import { Chip, PageHeader } from "../components/ui";

export default function ClassPage() {
  const { classId } = useParams();
  const info = classById(classId);
  if (!info) return <Navigate to="/" replace />;
  const subjects = subjectsFor(info.id);
  const popular = subjects.filter((x) => x.popular);
  const rest = subjects.filter((x) => !x.popular);

  return (
    <div>
      <PageHeader back title={info.title} subtitle={info.subtitle} />
      <div className={`bg-gradient-to-br ${info.gradient} px-4 pt-6 pb-8`}>
        <div className="mx-auto flex max-w-3xl items-center gap-4">
          <div className="text-5xl drop-shadow">{info.emoji}</div>
          <div className="text-white">
            <p className="text-xl font-extrabold">{info.title}</p>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {info.boardExam ? (
                <>
                  <Chip tone="indigo" >🏛 Official board papers</Chip>
                  <Chip tone="emerald">2023–2026 + compartment</Chip>
                  <Chip tone="amber">Sample papers 2020–26</Chip>
                </>
              ) : (
                <>
                  <Chip tone="emerald">CBSE pattern</Chip>
                  <Chip tone="amber">Add your school papers</Chip>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-4 pt-4 pb-8">
        {popular.length > 0 && (
          <>
            <h2 className="mb-2 text-sm font-bold tracking-wide text-slate-500 uppercase">
              {info.boardExam ? "Most practised" : "Subjects"}
            </h2>
            <SubjectTiles classId={info.id} list={popular} />
          </>
        )}
        {rest.length > 0 && (
          <>
            <h2 className="mt-6 mb-2 text-sm font-bold tracking-wide text-slate-500 uppercase">
              {popular.length > 0 ? "All subjects" : "Subjects"}
            </h2>
            <SubjectTiles classId={info.id} list={rest} />
          </>
        )}
      </div>
    </div>
  );
}

function SubjectTiles({ classId, list }: { classId: string; list: ReturnType<typeof subjectsFor> }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {list.map((sub) => (
        <Link
          key={sub.id}
          to={`/class/${classId}/subject/${sub.id}`}
          className="pressable flex items-center gap-3 rounded-2xl bg-white p-3.5 shadow-sm ring-1 ring-slate-100"
        >
          <span className="text-2xl">{sub.emoji}</span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm leading-tight font-bold text-slate-800">
              {sub.name}
            </span>
            <span className="mt-0.5 block text-[11px] text-slate-400">
              {sub.stems.length ? "Board + sample papers" : "Pattern resources"}
            </span>
          </span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 shrink-0 text-slate-300">
            <path d="m9 6 6 6-6 6" />
          </svg>
        </Link>
      ))}
    </div>
  );
}

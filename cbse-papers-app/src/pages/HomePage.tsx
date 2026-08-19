import { Link } from "react-router-dom";
import { CLASSES, sessionsFor, subjectsFor } from "../data/catalog";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-3xl px-4">
      {/* Hero */}
      <section className="mt-4 overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-800 via-indigo-700 to-violet-700 p-6 text-white shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-bold tracking-widest text-indigo-200 uppercase">
              Classes 5 · 8 · 10 · 12
            </p>
            <h1 className="mt-1 text-2xl leading-tight font-extrabold">
              Previous Year
              <br />
              CBSE Question Papers
            </h1>
            <p className="mt-2 max-w-[26ch] text-sm text-indigo-100">
              Every subject. Official sources. Read offline. Free forever.
            </p>
          </div>
          <div className="text-6xl drop-shadow-lg select-none">🎓</div>
        </div>
        <Link
          to="/search"
          className="pressable mt-4 flex items-center gap-2 rounded-xl bg-white/15 px-4 py-3 text-sm text-indigo-100 ring-1 ring-white/25 backdrop-blur"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-4 w-4">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          Search “Physics 2026”, “Maths sample paper”…
        </Link>
      </section>

      {/* Class cards */}
      <section className="mt-6 grid grid-cols-2 gap-3">
        {CLASSES.map((c) => {
          const subj = subjectsFor(c.id).length;
          const sessions = c.boardExam ? sessionsFor(c.id).length : 0;
          return (
            <Link
              key={c.id}
              to={`/class/${c.id}`}
              className={`pressable rounded-2xl bg-gradient-to-br ${c.gradient} p-4 text-white shadow-md`}
            >
              <div className="text-3xl">{c.emoji}</div>
              <div className="mt-2 text-lg font-extrabold">{c.title}</div>
              <div className="text-xs text-white/85">{c.subtitle}</div>
              <div className="mt-3 inline-flex rounded-full bg-white/20 px-2 py-0.5 text-[11px] font-semibold">
                {c.boardExam ? `${subj} subjects · ${sessions} exams` : `${subj} subjects · pattern papers`}
              </div>
            </Link>
          );
        })}
      </section>

      {/* Trust strip */}
      <section className="mt-6 grid grid-cols-3 gap-3">
        {[
          ["🏛", "Official CBSE sources", "Papers served from cbse.gov.in"],
          ["📴", "Works offline", "Save papers, read anywhere"],
          ["🚫", "No ads, no sign-up", "Open and start practising"],
        ].map(([icon, t, b]) => (
          <div key={t} className="rounded-2xl bg-white p-3 shadow-sm ring-1 ring-slate-100">
            <div className="text-2xl">{icon}</div>
            <div className="mt-1 text-[13px] leading-tight font-bold text-slate-800">{t}</div>
            <div className="mt-0.5 text-[11px] leading-snug text-slate-500">{b}</div>
          </div>
        ))}
      </section>

      {/* Note for classes 5 & 8 / imports */}
      <section className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4">
        <p className="text-sm font-bold text-amber-900">📌 About Classes 5 &amp; 8</p>
        <p className="mt-1 text-[13px] leading-snug text-amber-900/80">
          CBSE conducts board exams only for Classes 10 &amp; 12. For Classes 5 &amp; 8 your school sets
          CBSE-pattern papers — so the app gives you the official resources, and lets you{" "}
          <Link to="/import" className="font-bold underline">
            import your own school papers
          </Link>{" "}
          to read &amp; organise them offline.
        </p>
      </section>

      <p className="mt-6 pb-4 text-center text-[11px] text-slate-400">
        Independent study app · not affiliated with or endorsed by CBSE
      </p>
    </div>
  );
}

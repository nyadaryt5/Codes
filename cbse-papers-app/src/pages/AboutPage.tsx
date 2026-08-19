import { PageHeader, SectionHeader } from "../components/ui";
import { openExternal } from "../lib/net";

const VERSION = "1.0.0";

export default function AboutPage() {
  return (
    <div>
      <PageHeader title="About" subtitle="How this app works" />
      <div className="mx-auto max-w-3xl space-y-5 px-4 pt-4 pb-8">
        <section className="rounded-3xl bg-gradient-to-br from-indigo-800 to-violet-700 p-5 text-white shadow">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-3xl">🎓</div>
            <div>
              <p className="text-lg font-extrabold">CBSE Papers</p>
              <p className="text-xs text-indigo-200">Previous year question papers · v{VERSION}</p>
            </div>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-indigo-100">
            A free, ad-free study companion: every previous-year CBSE board paper for Classes 10
            &amp; 12, official sample papers, and a place to keep your own school papers for Classes
            5 &amp; 8 — all readable offline.
          </p>
        </section>

        <section className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
          <SectionHeader>Where papers come from</SectionHeader>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-600">
            <li>
              🏛 <b>Board papers (Classes 10 &amp; 12)</b> — downloaded on demand directly from the{" "}
              <button className="font-semibold text-indigo-600 underline" onClick={() => openExternal("https://www.cbse.gov.in/cbsenew/question-paper.html")}>
                official CBSE archive
              </button>{" "}
              (cbse.gov.in), covering 2023–2026 including compartment / second-board exams.
            </li>
            <li>
              📝 <b>Sample papers &amp; marking schemes</b> — from CBSE's Academic website
              (cbseacademic.nic.in), sessions 2020-21 to 2025-26.
            </li>
            <li>
              🎒 <b>Classes 5 &amp; 8</b> — CBSE holds no board exams here, so the app organises{" "}
              <i>your</i> imported papers plus links to NCERT / CBSE Academic resources.
            </li>
          </ul>
        </section>

        <section className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
          <SectionHeader>Offline &amp; storage</SectionHeader>
          <p className="text-sm leading-relaxed text-slate-600">
            Papers you open are cached on your device automatically, and ⬇ <b>Save</b> keeps them
            forever — both work fully without internet. Everything stays on your device; nothing is
            uploaded anywhere. You can clear the cache any time from the Offline tab.
          </p>
        </section>

        <section className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
          <SectionHeader>Privacy</SectionHeader>
          <p className="text-sm leading-relaxed text-slate-600">
            No accounts, no analytics, no tracking, no ads. The app only connects to official CBSE
            websites to fetch papers you ask for. Full policy:
          </p>
          <button
            onClick={() =>
              openExternal("https://github.com/nyadaryt5/Codes/blob/main/cbse-papers-app/PRIVACY_POLICY.md")
            }
            className="pressable mt-2 rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700"
          >
            Read privacy policy ↗
          </button>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-[13px] leading-relaxed text-slate-500">
            <b>Disclaimer:</b> This is an independent study app and is{" "}
            <b>not affiliated with, sponsored, or endorsed by the Central Board of Secondary
            Education (CBSE)</b> or NCERT. Question papers are © CBSE and are served from CBSE's own
            public servers for educational use. “CBSE” is referenced only to identify the exam
            board the papers belong to.
          </p>
        </section>

        <p className="pb-2 text-center text-[11px] text-slate-400">
          Made with 💙 for students across India
        </p>
      </div>
    </div>
  );
}

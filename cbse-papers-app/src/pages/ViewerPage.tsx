import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PdfViewer from "../components/PdfViewer";
import { PageHeader, Spinner } from "../components/ui";
import { deletePaper, getPaper, setFavorite, type PaperRecord } from "../lib/db";

export default function ViewerPage() {
  const { recordId } = useParams();
  const nav = useNavigate();
  const id = decodeURIComponent(recordId ?? "");
  const [rec, setRec] = useState<PaperRecord | null | undefined>(undefined);

  useEffect(() => {
    getPaper(id).then((r) => setRec(r ?? null));
  }, [id]);

  if (rec === undefined) {
    return (
      <div>
        <PageHeader back title="Opening…" />
        <div className="flex justify-center py-20 text-indigo-600">
          <Spinner className="h-8 w-8" />
        </div>
      </div>
    );
  }
  if (rec === null) {
    return (
      <div>
        <PageHeader back title="Not found" />
        <p className="px-6 py-16 text-center text-sm text-slate-500">
          This paper was removed from your device.
        </p>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        back
        title={rec.setName?.replace(/\.pdf$/i, "") ?? rec.title}
        subtitle={`${rec.subjectName} · ${rec.sessionLabel}`}
        actions={
          <div className="flex gap-2">
            <button
              aria-label="Favorite"
              onClick={async () => {
                await setFavorite(rec.id, !rec.favorite);
                setRec({ ...rec, favorite: !rec.favorite });
              }}
              className={`pressable flex h-9 w-9 items-center justify-center rounded-full ${
                rec.favorite ? "bg-amber-100 text-amber-500" : "bg-slate-100 text-slate-500"
              }`}
            >
              <svg viewBox="0 0 24 24" fill={rec.favorite ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
                <path d="m12 3 2.7 5.6 6.3.8-4.6 4.3 1.2 6.1L12 16.9l-5.6 3 1.2-6.2L3 9.4l6.3-.8z" />
              </svg>
            </button>
            <button
              aria-label="Delete"
              onClick={async () => {
                await deletePaper(rec.id);
                nav(-1);
              }}
              className="pressable flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-slate-500"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M4 7h16" />
                <path d="M9 7V4h6v3" />
                <path d="M6 7l1 14h10l1-14" />
              </svg>
            </button>
          </div>
        }
      />
      <PdfViewer title={rec.title} getData={() => rec.data.arrayBuffer()} />
    </div>
  );
}

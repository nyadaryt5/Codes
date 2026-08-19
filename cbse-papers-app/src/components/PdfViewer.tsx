import { useCallback, useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { Spinner } from "./ui";

pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

interface Props {
  /** supplies the PDF bytes (rom network, IndexedDB or a local file) */
  getData: () => Promise<ArrayBuffer>;
  title?: string;
  /** called once the document is ready */
  onLoaded?: (pages: number) => void;
}

export default function PdfViewer({ getData, title, onLoaded }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [doc, setDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [pageNum, setPageNum] = useState(1);
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const renderTask = useRef<pdfjsLib.RenderTask | null>(null);

  /* Load document */
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const bytes = await getData();
        const task = pdfjsLib.getDocument({ data: bytes });
        const d = await task.promise;
        if (cancelled) {
          void task.destroy();
          return;
        }
        setDoc(d);
        setNumPages(d.numPages);
        setPageNum(1);
        onLoaded?.(d.numPages);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not open this PDF.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [title]);

  /* Render current page */
  const render = useCallback(async () => {
    if (!doc || !canvasRef.current || !containerRef.current) return;
    try {
      renderTask.current?.cancel();
      const page = await doc.getPage(pageNum);
      const cssWidth = Math.min(containerRef.current.clientWidth, 860) - 16;
      const base = page.getViewport({ scale: 1 });
      const s = (cssWidth / base.width) * scale;
      const viewport = page.getViewport({ scale: s });
      const canvas = canvasRef.current;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;
      canvas.getContext("2d")!;
      const task = page.render({ canvas, viewport });
      renderTask.current = task;
      await task.promise;
    } catch (e) {
      if (!(e instanceof Error && e.name === "RenderingCancelledException")) {
        console.error(e);
      }
    }
  }, [doc, pageNum, scale]);

  useEffect(() => {
    void render();
  }, [render]);

  useEffect(() => {
    const onResize = () => void render();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [render]);

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-3 py-20 text-indigo-600">
        <Spinner className="h-8 w-8" />
        <p className="text-sm font-medium text-slate-500">Preparing {title ?? "paper"}…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-md px-6 py-16 text-center">
        <div className="text-5xl">😕</div>
        <p className="mt-2 font-bold text-slate-800">Couldn't display this PDF</p>
        <p className="mt-1 text-sm text-slate-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* toolbar */}
      <div className="sticky top-0 z-10 flex items-center justify-between gap-2 border-b border-slate-200 bg-white/90 px-3 py-2 backdrop-blur">
        <div className="flex items-center gap-1">
          <button
            className="pressable rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-bold text-slate-700 disabled:opacity-40"
            disabled={pageNum <= 1}
            onClick={() => setPageNum((p) => Math.max(1, p - 1))}
          >
            ‹ Prev
          </button>
          <button
            className="pressable rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-bold text-slate-700 disabled:opacity-40"
            disabled={pageNum >= numPages}
            onClick={() => setPageNum((p) => Math.min(numPages, p + 1))}
          >
            Next ›
          </button>
        </div>
        <span className="text-xs font-semibold text-slate-600">
          {pageNum} / {numPages}
        </span>
        <div className="flex items-center gap-1">
          <button
            className="pressable rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-bold text-slate-700"
            onClick={() => setScale((s) => Math.max(0.6, +(s - 0.2).toFixed(2)))}
            aria-label="Zoom out"
          >
            −
          </button>
          <button
            className="pressable rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-bold text-slate-700"
            onClick={() => setScale((s) => Math.min(3, +(s + 0.2).toFixed(2)))}
            aria-label="Zoom in"
          >
            +
          </button>
        </div>
      </div>

      <div ref={containerRef} className="flex justify-center overflow-auto bg-slate-100 px-2 py-4">
        <canvas ref={canvasRef} className="rounded-lg shadow-md" />
      </div>
    </div>
  );
}

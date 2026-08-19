import { useEffect } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import BottomNav from "./components/BottomNav";
import HomePage from "./pages/HomePage";
import ClassPage from "./pages/ClassPage";
import SubjectPage from "./pages/SubjectPage";
import PaperPage from "./pages/PaperPage";
import ViewerPage from "./pages/ViewerPage";
import DownloadsPage from "./pages/DownloadsPage";
import SearchPage from "./pages/SearchPage";
import ImportPage from "./pages/ImportPage";
import AboutPage from "./pages/AboutPage";

function ScrollToTop() {
  const { pathname, search } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname, search]);
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-dvh bg-slate-50 text-slate-900">
        <main className="pb-24">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/class/:classId" element={<ClassPage />} />
            <Route path="/class/:classId/subject/:subjectId" element={<SubjectPage />} />
            <Route path="/paper" element={<PaperPage />} />
            <Route path="/view/:recordId" element={<ViewerPage />} />
            <Route path="/downloads" element={<DownloadsPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/import" element={<ImportPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<HomePage />} />
          </Routes>
        </main>
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}

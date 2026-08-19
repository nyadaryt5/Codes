/**
 * Content catalog for the app.
 *
 * Papers are NOT bundled — the app resolves them from the official CBSE
 * question-paper archive (cbse.gov.in) and the CBSE Academic sample-paper
 * pages (cbseacademic.nic.in) at runtime, so papers stay complete and current
 * as CBSE publishes new ones.
 */

export type ClassId = "5" | "8" | "10" | "12";

export interface ClassInfo {
  id: ClassId;
  title: string;
  subtitle: string;
  emoji: string;
  /** tailwind gradient classes */
  gradient: string;
  boardExam: boolean;
}

export const CLASSES: ClassInfo[] = [
  {
    id: "5",
    title: "Class 5",
    subtitle: "CBSE-pattern annual papers",
    emoji: "🎒",
    gradient: "from-emerald-500 to-teal-600",
    boardExam: false,
  },
  {
    id: "8",
    title: "Class 8",
    subtitle: "CBSE-pattern annual papers",
    emoji: "📘",
    gradient: "from-sky-500 to-blue-600",
    boardExam: false,
  },
  {
    id: "10",
    title: "Class 10",
    subtitle: "Official CBSE Board papers",
    emoji: "🎯",
    gradient: "from-indigo-500 to-violet-600",
    boardExam: true,
  },
  {
    id: "12",
    title: "Class 12",
    subtitle: "Official CBSE Board papers",
    emoji: "🎓",
    gradient: "from-rose-500 to-orange-600",
    boardExam: true,
  },
];

export interface Subject {
  id: string;
  name: string;
  short: string;
  emoji: string;
  /** filename stems tried, in order, to locate the official zip */
  stems: string[];
  popular?: boolean;
}

const s = (
  id: string,
  name: string,
  emoji: string,
  stems: string[],
  popular = false,
): Subject => ({
  id,
  name,
  short: name,
  emoji,
  stems,
  popular,
});

/* ------------------------------------------------------------------ */
/* Class X                                                             */
/* ------------------------------------------------------------------ */
export const SUBJECTS_10: Subject[] = [
  s("maths-std", "Mathematics (Standard)", "📐",
    ["Mathematics_Standard", "Maths_Standard", "MATHEMATICS_STANDARD", "Mathematicsstandard"], true),
  s("maths-basic", "Mathematics (Basic)", "🧮",
    ["Mathematics_Basic", "Maths_Basic", "MATHEMATICS_BASIC"]),
  s("science", "Science", "🔬", ["Science", "SCIENCE", "science"], true),
  s("sst", "Social Science", "🌍",
    ["Social_Science", "SOCIAL_SCIENCE", "social_science"], true),
  s("english", "English (Lang. & Lit.)", "📖",
    ["English_Lang_Lit", "English_Language_Literature", "ENGLISH_LANG_LIT", "English"], true),
  s("hindi-a", "Hindi A", "🅰", ["Hindi_A", "HINDI_A", "Hindi-course-A"]),
  s("hindi-b", "Hindi B", "🅱", ["Hindi_B", "HINDI_B", "Hindi-course-B"]),
  s("sanskrit", "Sanskrit", "🕉", ["Sanskrit", "SANSKRIT"]),
  s("computer", "Computer Applications", "💻",
    ["Computer_Application", "COMPUTER_APPLICATION", "Computer_Applications", "Computer"]),
  s("ai", "Artificial Intelligence", "🤖",
    ["Artificial_Intelligence", "Artificial_Intelleigence", "ARTIFICIAL_INTELLIGENCE", "AI"]),
  s("it", "Information Technology", "🖥",
    ["Information_Technology", "INFORMATION_TECHNOLOGY", "IT"]),
  s("assamese", "Assamese", "✍", ["Assamese", "ASSAMESE"]),
  s("bengali", "Bengali", "✍", ["Bengali", "BENGALI"]),
  s("french", "French", "🗼", ["French", "FRENCH"]),
  s("urdu", "Urdu", "✍", ["Urdu", "URDU", "Urdu_1"]),
];

/* ------------------------------------------------------------------ */
/* Class XII                                                           */
/* ------------------------------------------------------------------ */
export const SUBJECTS_12: Subject[] = [
  s("physics", "Physics", "🧲", ["Physics", "PHYSICS", "physics"], true),
  s("chemistry", "Chemistry", "⚗️", ["Chemistry", "CHEMISTRY", "chemistry"], true),
  s("biology", "Biology", "🧬", ["Biology", "BIOLOGY", "biology"], true),
  s("maths", "Mathematics", "📐", ["Mathematics", "MATHEMATICS", "mathematics"], true),
  s("applied-maths", "Applied Mathematics", "📊",
    ["Applied_Maths", "Applied_Mathematics", "APPLIED_MATHS", "Applied_Math"]),
  s("english-core", "English Core", "📖",
    ["English_Core", "ENGLISH_CORE", "English"], true),
  s("english-elective", "English Elective", "📚",
    ["English_Elective", "ENGLISH_ELECTIVE"]),
  s("hindi-core", "Hindi Core", "🅰", ["Hindi_Core", "HINDI_CORE"]),
  s("hindi-elective", "Hindi Elective", "🅱", ["Hindi_Elective", "HINDI_ELECTIVE"]),
  s("accountancy", "Accountancy", "🧾", ["Accountancy", "ACCOUNTANCY", "accountancy"], true),
  s("bst", "Business Studies", "💼",
    ["Business_Studies", "BUSINESS_STUDIES", "business_studies"], true),
  s("economics", "Economics", "📈", ["Economics", "ECONOMICS", "economics"], true),
  s("cs", "Computer Science", "💻",
    ["Computer_Science", "COMPUTER_SCIENCE", "computer_science"]),
  s("ip", "Informatics Practices", "🖥",
    ["Informatics_Practices", "Informatics_Practice", "INFORMATICS_PRACTICES"]),
  s("history", "History", "🏛", ["History", "HISTORY"]),
  s("pol-sci", "Political Science", "🗳",
    ["Political_Science", "POLITICAL_SCIENCE", "political_science"]),
  s("geography", "Geography", "🗺", ["Geography", "GEOGRAPHY"]),
  s("psychology", "Psychology", "🧠", ["Psychology", "PSYCHOLOGY", "psychology"]),
  s("sociology", "Sociology", "👥", ["Sociology", "SOCIOLOGY"]),
  s("phys-ed", "Physical Education", "🏅",
    ["Physical_Education", "PHYSICAL_EDUCATION", "PE"]),
  s("entrepreneurship", "Entrepreneurship", "🚀",
    ["Entrepreneurship", "ENTREPRENEURSHIP"]),
  s("legal", "Legal Studies", "⚖️", ["Legal_Studies", "LEGAL_STUDIES","Legal_studies"]),
  s("biotech", "Biotechnology", "🧪", ["Biotechnology", "BIOTECHNOLOGY"]),
];

export function subjectsFor(classId: ClassId): Subject[] {
  if (classId === "10") return SUBJECTS_10;
  if (classId === "12") return SUBJECTS_12;
  if (classId === "8") return SUBJECTS_8;
  return SUBJECTS_5;
}

/* ------------------------------------------------------------------ */
/* Classes 5 & 8 (school-level, CBSE pattern)                          */
/* ------------------------------------------------------------------ */
export const SUBJECTS_5: Subject[] = [
  s("english", "English", "📖", []),
  s("hindi", "Hindi", "🅰", []),
  s("maths", "Mathematics", "🧮", []),
  s("evs", "EVS", "🌿", []),
  s("computer", "Computer", "💻", []),
  s("sanskrit", "Sanskrit", "🕉", []),
  s("gk", "General Knowledge", "🌟", []),
];

export const SUBJECTS_8: Subject[] = [
  s("english", "English", "📖", []),
  s("hindi", "Hindi", "🅰", []),
  s("maths", "Mathematics", "🧮", []),
  s("science", "Science", "🔬", []),
  s("sst", "Social Science", "🌍", []),
  s("sanskrit", "Sanskrit", "🕉", []),
  s("computer", "Computer", "💻", []),
];

/* ------------------------------------------------------------------ */
/* Exam sessions                                                       */
/* ------------------------------------------------------------------ */
export type SessionKind = "board" | "compartment" | "sample";

export interface ExamSession {
  id: string;
  label: string;
  short: string;
  kind: SessionKind;
  /** base directory of official zip files (board/compartment) */
  zipBase?: string;
  /** official page (always available as a fallback / "view all") */
  pageUrl: string;
}

const QP_ARCHIVE = "https://www.cbse.gov.in/cbsenew/question-paper.html";
const QP_BASE = "https://www.cbse.gov.in/cbsenew/question-paper";

function boardSessions(level: "X" | "XII"): ExamSession[] {
  const out: ExamSession[] = [];
  for (const year of ["2026", "2025", "2024", "2023"]) {
    out.push({
      id: `${year}`,
      label: `Board Exam ${year}`,
      short: year,
      kind: "board",
      zipBase: `${QP_BASE}/${year}/${level}`,
      pageUrl: QP_ARCHIVE,
    });
  }
  for (const year of ["2026", "2025", "2024"]) {
    out.push({
      id: `${year}-comptt`,
      label:
        level === "X"
          ? `Second Board Exam ${year}`
          : `Compartment Exam ${year}`,
      short: `${year} (C)`,
      kind: "compartment",
      zipBase: `${QP_BASE}/${year}-COMPTT/${level}`,
      pageUrl: QP_ARCHIVE,
    });
  }
  return out;
}

function sampleSessions(level: "X" | "XII"): ExamSession[] {
  return [
    ["2025-26", "2025-26"],
    ["2024-25", "2024-25"],
    ["2023-24", "2023-24"],
    ["2022-23", "2022-23"],
    ["2021-22", "2021-22"],
    ["2020-21", "2020-21"],
  ].map(([id, yr]) => ({
    id: `sqp-${id}`,
    label: `Sample Paper ${yr} (official)`,
    short: `SQP ${yr.slice(0, 4)}`,
    kind: "sample" as SessionKind,
    pageUrl: `https://cbseacademic.nic.in/SQP_CLASS${level === "X" ? "X" : "XII"}_${id}.html`,
  }));
}

export function sessionsFor(classId: ClassId): ExamSession[] {
  if (classId === "10") {
    return [...boardSessions("X"), ...sampleSessions("X")];
  }
  return [...boardSessions("XII"), ...sampleSessions("XII")];
}

/* ------------------------------------------------------------------ */
/* A single paper reference                                            */
/* ------------------------------------------------------------------ */
export interface PaperRef {
  classId: ClassId;
  subjectId: string;
  subjectName: string;
  sessionId: string;
  sessionLabel: string;
  kind: SessionKind;
  title: string;
  /** candidate direct zip URLs, tried in order */
  zipUrls: string[];
  /** official web page to open as fallback / source */
  pageUrl: string;
}

export function paperFor(
  classId: ClassId,
  subject: Subject,
  session: ExamSession,
): PaperRef {
  const zipUrls =
    session.zipBase != null
      ? subject.stems.map((stem) => `${session.zipBase}/${encodeURIComponent(stem)}.zip`)
      : [];
  return {
    classId,
    subjectId: subject.id,
    subjectName: subject.name,
    sessionId: session.id,
    sessionLabel: session.label,
    kind: session.kind,
    title: `${subject.name} – ${session.label}`,
    zipUrls,
    pageUrl: session.pageUrl,
  };
}

/** Classes 5 & 8 — useful official resources per subject */
export interface SchoolResource {
  title: string;
  url: string;
  icon: string;
  description: string;
}

export function schoolResources(classId: "5" | "8", subjectName: string): SchoolResource[] {
  const enc = encodeURIComponent(subjectName);
  return [
    {
      title: "NCERT Textbooks (free PDF)",
      url: "https://ncert.nic.in/textbook.php",
      icon: "📚",
      description: `Official NCERT textbook for Class ${classId} ${subjectName} — every exam question is based on it.`,
    },
    {
      title: "CBSE Academic – Curriculum & Resources",
      url: "https://cbseacademic.nic.in",
      icon: "🏛",
      description: "Syllabus, workbooks and practice material published by the CBSE academics wing.",
    },
    {
      title: `Class ${classId} ${subjectName} — practice papers (web search)`,
      url: `https://www.google.com/search?q=class+${classId}+${enc}+cbse+pattern+annual+question+paper+pdf`,
      icon: "🔎",
      description: "CBSE does not publish board papers for this class; find school / CBSE-pattern papers shared publicly.",
    },
  ];
}

export const classById = (id: string | undefined): ClassInfo | undefined =>
  CLASSES.find((c) => c.id === id);

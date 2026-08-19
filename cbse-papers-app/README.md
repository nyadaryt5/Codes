# 📚 CBSE Papers — Previous Year Question Papers App

A free, offline-ready mobile app (PWA **and** native Android via Capacitor) that puts every
previous-year CBSE question paper in a student's pocket.

| | |
|---|---|
| **Classes 10 & 12** | Official board-exam papers 2023–2026 (main + compartment/second-board) and CBSE sample papers 2020-21 → 2025-26, fetched on demand straight from `cbse.gov.in` / `cbseacademic.nic.in` |
| **Classes 5 & 8** | CBSE-pattern resources + import your own school papers (PDF) |
| **Offline** | Every opened paper is auto-cached on-device; ⬇ Save keeps papers forever |
| **UX** | Class → subject → exam → set picker → fast built-in PDF viewer (pdf.js), favourites, search, no ads, no accounts |

## Tech stack

- **React 19 + TypeScript + Vite 8**, Tailwind CSS 4
- **pdf.js** viewer (pages render locally in canvas)
- **JSZip** to unpack CBSE's official per-subject ZIPs (one ZIP = several paper sets)
- **IndexedDB** offline library with auto-cache pruning (~180 MB cap)
- **PWA** (`vite-plugin-pwa`) → installable from the browser
- **Capacitor 8** → native Android app (`android/`, minSdk 24 / target 36, brand icons & splash included)

## Run it (web)

```bash
npm ci
npm run dev        # http://localhost:5173
npm run build      # production build → dist/
npm run preview    # serve the production build
```

## Build the Android app

```bash
npm run android:sync     # build web app + copy into android/
npm run android:open     # open in Android Studio (first time: let it sync Gradle)
```

- Debug APK (sideload testing): `npm run android:apk`
- Release AAB (Play Store): see **[PLAY_STORE_GUIDE.md](./PLAY_STORE_GUIDE.md)** — signing,
  listing copy, data-safety answers, review tips.

## Project map

```
src/
  data/catalog.ts     # classes, subjects, exam sessions, official URL resolver
  lib/net.ts          # downloads (Capacitor HTTP on Android, fetch on web) + zip handling
  lib/db.ts           # IndexedDB offline store (papers, favourites, cache)
  pages/              # Home / Class / Subject / Paper / Viewer / Downloads / Search / Import / About
  components/         # PdfViewer, BottomNav, UI primitives
scripts/              # icon generators (PWA + Android) from assets-src/
android/              # Capacitor Android project (ready for Android Studio)
assets-src/           # master artwork (app icon, Play feature graphic)
```

## Notes

- Papers are **not bundled**; they're downloaded from official CBSE servers when a student
  opens one, so the app is tiny and always current. PWA downloads depend on those servers'
  CORS; the **Android app downloads natively** (recommended path), and the web app degrades
  gracefully to opening the official page.
- The app is an independent study tool, **not affiliated with CBSE**. Question papers © CBSE.

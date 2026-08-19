# 🚀 Publishing "CBSE Papers" to the Google Play Store

This app is **publishing-ready**: the web app builds offline-first, the Android project
(`android/`) is generated with icons & splash screens, and this guide walks you through
every remaining step. Expect ~2–4 hours of your time + Google's review (usually 3–7 days).

---

## Part 1 — One-time setup (your computer)

1. **Install Android Studio** (free): https://developer.android.com/studio
   It bundles everything the build needs: a JDK 17, the Android SDK (API 36), and Gradle.
2. **Install Node.js LTS**: https://nodejs.org
3. **Create a Google Play Developer account**: https://play.google.com/console
   – one-time **$25 registration fee** – requires ID verification (Google can take
   1–2 days to verify).

## Part 2 — Build the release file (AAB)

```bash
cd cbse-papers-app
npm ci                      # install dependencies (first time only)
npm run android:sync        # build web app + copy into the Android project
```

Now sign it. Android requires every upload to be signed with a key **you** control:

```bash
keytool -genkey -v -keystore cbse-papers.keystore -alias cbsepapers \
  -keyalg RSA -keysize 2048 -validity 10950
```

(`keytool` ships with the JDK in Android Studio, e.g.
`C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe` on Windows,
`…/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool` on macOS.)

> ⚠️ **Back up `cbse-papers.keystore` and its passwords somewhere safe (cloud + offline).**
> Google Play's "Play App Signing" (enabled by default on first upload) protects you if you
> lose it, but the upload key is still precious. **Never commit the keystore to git.**

Create `android/keystore.properties` (already git-ignored):

```properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=cbsepapers
storeFile=../cbse-papers.keystore
```

Add this to `android/app/build.gradle` **above** the `android { … }` block:

```gradle
def keystorePropertiesFile = rootProject.file("keystore.properties")
def keystoreProperties = new Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

and **inside** `android { … }`:

```gradle
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
        }
    }
```

Then build the **Android App Bundle** (Play only accepts AAB, not APK):

```bash
cd android && ./gradlew bundleRelease
#  (Windows: gradlew.bat bundleRelease)
```

📦 Output: `android/app/build/outputs/bundle/release/app-release.aab`

> Want to test the unsigned-ish build on a phone first? `npm run android:apk` makes a
> debug APK at `android/app/build/outputs/apk/debug/app-debug.apk` you can sideload.

## Part 3 — Play Console listing

1. **Create app** → name: `CBSE Papers – Class 5, 8, 10, 12 PYQs` (≤ 30 chars) →
   default language English (India) → Free app.
2. **Store assets** (all ready in this repo):
   | Asset | File |
   |---|---|
   | App icon 512×512 | `public/icons/icon-512.png` |
   | Feature graphic 1024×500 | `assets-src/feature-graphic.png` |
   | Phone screenshots (min 2) | take on your phone / emulator after installing the debug build |
3. **Short description** (≤ 80 chars):
   > Previous year CBSE board papers (Class 10 & 12) + official sample papers. Works offline. Free.
4. **Full description** (paste & tweak):

   > Cracking the boards starts with past papers. CBSE Papers puts every previous-year
   > question paper in your pocket — free, no ads, no sign-up.
   >
   > 🏛 OFFICIAL SOURCES ONLY
   > Papers for Class 10 & 12 are fetched straight from the official CBSE archive
   > (cbse.gov.in) — Board exams 2023–2026, Compartment / Second Board exams, and CBSE's
   > own Sample Papers with marking schemes (2020-26).
   >
   > 📚 EVERY SUBJECT
   > Maths, Science, Social Science, English, Hindi, Physics, Chemistry, Biology,
   > Accountancy, Business Studies, Economics, Computer Science, History, Political
   > Science, Geography, Psychology, Physical Education & more.
   >
   > 📴 READ OFFLINE
   > Save any paper once and revise in the exam hall corridor — no internet needed.
   >
   > 🎒 CLASSES 5 & 8
   > CBSE doesn't hold board exams for these classes, so keep your school's CBSE-pattern
   > papers here: import PDFs and they're organised by subject, always with you.
   >
   > ⭐ BUILT FOR STUDENTS
   > Fast, light, dark-on-eyes UI • favourites • subject & year search • no ads, ever.
   >
   > Not affiliated with or endorsed by CBSE. Question papers © CBSE.

5. **App category:** Education. **Tags:** education, books.
6. **Privacy policy URL** (required):
   Enable GitHub Pages on the repo once (Settings → Pages → deploy from `main`), then use:
   `https://nyadaryt5.github.io/Codes/cbse-papers-app/PRIVACY_POLICY.html`
   (or host `PRIVACY_POLICY.md` anywhere public).
7. **Data safety form** — the honest answers are easy:
   - *Collects or shares data?* → **No**
   - That’s it. The app has no accounts, no analytics, no ads.
8. **Content rating** questionnaire → category *Education/Reference*; answer **No** to
   violence, UGC, etc. You'll get *Everyone*.
9. **Target audience:** ⚠️ Important choice —
   - **Recommended:** select **"13 and older"**. The app is a study tool; it doesn't need
     Google's stricter "Designed for Families" program.
   - If you want under-13 discovery ("Teacher Approved"), you must join the Families
     program and comply with its extra policy (the app already qualifies: no ads/SDK tracking).
10. **Declarations:** no news app, no COVID app, ads → **"No, the app does not contain ads"**.
11. **Countries:** pick India (or worldwide — CBSE schools exist in Gulf/other countries too).
12. Upload the **AAB** to *Production* (or *Internal testing* first — highly recommended:
    add your own Gmail, install from the testing link on a real phone, and click through
    every screen once), then **Send for review**.

## Part 4 — Releasing updates later

1. Edit `android/app/build.gradle`: bump `versionCode` (integer, must increase) and
   `versionName` (e.g. `1.1.0`).
2. Rebuild web + AAB (`npm run android:aab` after configuring signing).
3. Upload to a new release; Google reviews usually within a week.

## Troubleshooting

| Problem | Fix |
|---|---|
| `JAVA_HOME not set` | Open the `android` folder in Android Studio once, or set JAVA_HOME to Android Studio's `jbr` folder |
| SDK licenses | `sdkmanager --licenses` (in Android Studio → Settings → SDK Manager installs the same) |
| Papers won't download on phone | Check the phone is online; cbse.gov.in can be slow during result/exam season — the app retries candidates automatically and offers "Retry" |
| Review rejected: "Broken functionality" | Run the internal-testing build on a real device; ensure at least one paper downloads on mobile data |
| Review rejected: trademark | The store text already includes "Not affiliated with CBSE" — keep it; reply to the appeal form pointing to the disclaimer in-app and in the listing |

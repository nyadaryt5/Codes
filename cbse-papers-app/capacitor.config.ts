import type { CapacitorConfig } from "@capacitor/cli";

/**
 * Capacitor wraps the built web app (dist/) into a native Android app.
 *
 * Change `appId` to a package name you own before publishing to Google Play.
 * It can NEVER be changed after the first Play Store upload.
 */
const config: CapacitorConfig = {
  appId: "com.pyqpapers.cbse",
  appName: "CBSE Papers",
  webDir: "dist",
  android: {
    backgroundColor: "#312e81",
  },
  plugins: {
    CapacitorHttp: {
      // Lets the Android app download PDFs directly (bypasses web-view CORS).
      enabled: true,
    },
    SplashScreen: {
      launchAutoHide: true,
      backgroundColor: "#312e81",
      androidSplashResourceName: "splash",
    },
  },
};

export default config;

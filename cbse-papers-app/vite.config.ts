import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.png", "icons/icon-192.png", "icons/icon-512.png"],
      manifest: {
        id: "/",
        name: "Board Papers CBSE – Previous Year Papers (5–12)",
        short_name: "CBSE Papers",
        description:
          "Previous year CBSE question papers & official sample papers for Classes 5, 8, 10 and 12 — every subject, offline-ready.",
        lang: "en",
        start_url: "/",
        scope: "/",
        display: "standalone",
        orientation: "portrait",
        background_color: "#0f172a",
        theme_color: "#312e81",
        categories: ["education", "books"],
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          {
            src: "icons/maskable-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
        navigateFallback: "index.html",
      },
    }),
  ],
  server: {
    host: true,
    port: 5173,
    allowedHosts: true,
    watch: { ignored: ["**/android/**", "**/dist/**"] },
  },
  preview: { host: true, port: 4173, allowedHosts: true },
});

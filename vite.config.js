import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  base: "/static/dist/",
  build: {
    outDir: resolve(__dirname, "seedboxsync/front/static/dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, "seedboxsync/front/static/src/main.js"),
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`,
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
      },
    },
  },
});

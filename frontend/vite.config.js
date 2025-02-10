import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // Listen on all network interfaces
    port: 8080,
    strictPort: true,
    hmr: {
      host: 'localhost',
      port: 8080
    },
    watch: {
      usePolling: true,  // Important for Docker volumes
      interval: 500,     // Check for changes every 500ms
    }
  }
});

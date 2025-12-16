// vite.config.ts
import path from "path";
import { defineConfig, loadEnv } from "file:///C:/Users/annac/shukabase-ai/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/annac/shukabase-ai/node_modules/@vitejs/plugin-react/dist/index.js";
var __vite_injected_original_dirname = "C:\\Users\\annac\\shukabase-ai";
var vite_config_default = defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  return {
    server: {
      port: 5173,
      host: "0.0.0.0",
      watch: {
        ignored: ["**/public/books/**", "**/src-tauri/**", "**/.git/**", "**/node_modules/**"]
      }
    },
    optimizeDeps: {
      entries: ["index.html", "src/**/*.{ts,tsx}"]
      // exclude: ['vitest', '@testing-library/jest-dom', '@testing-library/react', 'jsdom']
    },
    plugins: [react()],
    define: {
      "process.env.API_KEY": JSON.stringify(env.GEMINI_API_KEY),
      "process.env.GEMINI_API_KEY": JSON.stringify(env.GEMINI_API_KEY),
      "process.env.SHUKABASE_LANG": JSON.stringify(process.env.SHUKABASE_LANG || "all"),
      "process.env.SHUKABASE_DATA_ID": JSON.stringify(process.env.SHUKABASE_DATA_ID)
    },
    resolve: {
      alias: {
        "@": path.resolve(__vite_injected_original_dirname, ".")
      }
    },
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/setup.ts",
      css: true
    }
  };
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxhbm5hY1xcXFxzaHVrYWJhc2UtYWlcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkM6XFxcXFVzZXJzXFxcXGFubmFjXFxcXHNodWthYmFzZS1haVxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vQzovVXNlcnMvYW5uYWMvc2h1a2FiYXNlLWFpL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHBhdGggZnJvbSAncGF0aCc7XG5pbXBvcnQgeyBkZWZpbmVDb25maWcsIGxvYWRFbnYgfSBmcm9tICd2aXRlJztcbmltcG9ydCByZWFjdCBmcm9tICdAdml0ZWpzL3BsdWdpbi1yZWFjdCc7XG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZygoeyBtb2RlIH0pID0+IHtcbiAgY29uc3QgZW52ID0gbG9hZEVudihtb2RlLCAnLicsICcnKTtcbiAgcmV0dXJuIHtcbiAgICBzZXJ2ZXI6IHtcbiAgICAgIHBvcnQ6IDUxNzMsXG4gICAgICBob3N0OiAnMC4wLjAuMCcsXG4gICAgICB3YXRjaDoge1xuICAgICAgICBpZ25vcmVkOiBbJyoqL3B1YmxpYy9ib29rcy8qKicsICcqKi9zcmMtdGF1cmkvKionLCAnKiovLmdpdC8qKicsICcqKi9ub2RlX21vZHVsZXMvKionXVxuICAgICAgfVxuICAgIH0sXG4gICAgb3B0aW1pemVEZXBzOiB7XG4gICAgICBlbnRyaWVzOiBbJ2luZGV4Lmh0bWwnLCAnc3JjLyoqLyoue3RzLHRzeH0nXSxcbiAgICAgIC8vIGV4Y2x1ZGU6IFsndml0ZXN0JywgJ0B0ZXN0aW5nLWxpYnJhcnkvamVzdC1kb20nLCAnQHRlc3RpbmctbGlicmFyeS9yZWFjdCcsICdqc2RvbSddXG4gICAgfSxcbiAgICBwbHVnaW5zOiBbcmVhY3QoKV0sXG4gICAgZGVmaW5lOiB7XG4gICAgICAncHJvY2Vzcy5lbnYuQVBJX0tFWSc6IEpTT04uc3RyaW5naWZ5KGVudi5HRU1JTklfQVBJX0tFWSksXG4gICAgICAncHJvY2Vzcy5lbnYuR0VNSU5JX0FQSV9LRVknOiBKU09OLnN0cmluZ2lmeShlbnYuR0VNSU5JX0FQSV9LRVkpLFxuICAgICAgJ3Byb2Nlc3MuZW52LlNIVUtBQkFTRV9MQU5HJzogSlNPTi5zdHJpbmdpZnkocHJvY2Vzcy5lbnYuU0hVS0FCQVNFX0xBTkcgfHwgJ2FsbCcpLFxuICAgICAgJ3Byb2Nlc3MuZW52LlNIVUtBQkFTRV9EQVRBX0lEJzogSlNPTi5zdHJpbmdpZnkocHJvY2Vzcy5lbnYuU0hVS0FCQVNFX0RBVEFfSUQpXG4gICAgfSxcbiAgICByZXNvbHZlOiB7XG4gICAgICBhbGlhczoge1xuICAgICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuJyksXG4gICAgICB9XG4gICAgfSxcbiAgICB0ZXN0OiB7XG4gICAgICBnbG9iYWxzOiB0cnVlLFxuICAgICAgZW52aXJvbm1lbnQ6ICdqc2RvbScsXG4gICAgICBzZXR1cEZpbGVzOiAnLi9zcmMvc2V0dXAudHMnLFxuICAgICAgY3NzOiB0cnVlXG4gICAgfVxuICB9O1xufSk7XG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQTJRLE9BQU8sVUFBVTtBQUM1UixTQUFTLGNBQWMsZUFBZTtBQUN0QyxPQUFPLFdBQVc7QUFGbEIsSUFBTSxtQ0FBbUM7QUFJekMsSUFBTyxzQkFBUSxhQUFhLENBQUMsRUFBRSxLQUFLLE1BQU07QUFDeEMsUUFBTSxNQUFNLFFBQVEsTUFBTSxLQUFLLEVBQUU7QUFDakMsU0FBTztBQUFBLElBQ0wsUUFBUTtBQUFBLE1BQ04sTUFBTTtBQUFBLE1BQ04sTUFBTTtBQUFBLE1BQ04sT0FBTztBQUFBLFFBQ0wsU0FBUyxDQUFDLHNCQUFzQixtQkFBbUIsY0FBYyxvQkFBb0I7QUFBQSxNQUN2RjtBQUFBLElBQ0Y7QUFBQSxJQUNBLGNBQWM7QUFBQSxNQUNaLFNBQVMsQ0FBQyxjQUFjLG1CQUFtQjtBQUFBO0FBQUEsSUFFN0M7QUFBQSxJQUNBLFNBQVMsQ0FBQyxNQUFNLENBQUM7QUFBQSxJQUNqQixRQUFRO0FBQUEsTUFDTix1QkFBdUIsS0FBSyxVQUFVLElBQUksY0FBYztBQUFBLE1BQ3hELDhCQUE4QixLQUFLLFVBQVUsSUFBSSxjQUFjO0FBQUEsTUFDL0QsOEJBQThCLEtBQUssVUFBVSxRQUFRLElBQUksa0JBQWtCLEtBQUs7QUFBQSxNQUNoRixpQ0FBaUMsS0FBSyxVQUFVLFFBQVEsSUFBSSxpQkFBaUI7QUFBQSxJQUMvRTtBQUFBLElBQ0EsU0FBUztBQUFBLE1BQ1AsT0FBTztBQUFBLFFBQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsR0FBRztBQUFBLE1BQ2xDO0FBQUEsSUFDRjtBQUFBLElBQ0EsTUFBTTtBQUFBLE1BQ0osU0FBUztBQUFBLE1BQ1QsYUFBYTtBQUFBLE1BQ2IsWUFBWTtBQUFBLE1BQ1osS0FBSztBQUFBLElBQ1A7QUFBQSxFQUNGO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K

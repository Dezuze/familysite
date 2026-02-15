declare const process: any;

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  // point to the Tailwind entry in the Nuxt app folder
  css: ['~/assets/css/tailwind.css'],
  postcss: {
    plugins: {
      "@tailwindcss/postcss": {},
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || 'http://localhost:8000',
      // Respect env var; default to false (call backend by default)
      localAuth: process.env.LOCAL_AUTH === 'true' ? true : false,
    },
  },

  modules: [
    'nuxt-aos',
    '@formkit/auto-animate',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    '@pinia-plugin-persistedstate/nuxt',
  ],
  vite: {
    vue: {
      inspector: false
    }
  }
})

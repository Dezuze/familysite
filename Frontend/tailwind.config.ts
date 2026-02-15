import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './app/**/*.{vue,ts,js,html}',
    './components/**/*.{vue,ts,js,html}',
    './pages/**/*.{vue,ts,js,html}',
  ],
  theme: {
    extend: {
       fontFamily: {
        arima: ['Arima', 'cursive'],
        itim: ['Itim', 'cursive'],
      },
      colors: {
        // Colors are now defined in Frontend/app/assets/css/tailwind.css using @theme block for Tailwind v4 compatibility.
      },
    },
  },
}

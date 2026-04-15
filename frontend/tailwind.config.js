/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        sakura: {
          50:  '#FDF2F5',
          100: '#FAE4EA',
          200: '#F5C8D6',
          300: '#EEA0B8',
          400: '#E57696',
          500: '#D9506F',
          600: '#C23458',
          700: '#A22549',
          800: '#87203E',
          900: '#6E1D35',
        },
        washi: '#FAF7F2',
        sumi:  '#1C1817',
      },
      fontFamily: {
        sans:   ['"Noto Sans JP"', 'Hiragino Kaku Gothic ProN', 'system-ui', 'sans-serif'],
        serif:  ['"Noto Serif JP"', 'Hiragino Mincho ProN', 'Georgia', 'serif'],
      },
      aspectRatio: {
        '4/3': '4 / 3',
        '3/2': '3 / 2',
      },
      letterSpacing: {
        widest2: '0.2em',
      },
    },
  },
  plugins: [],
}

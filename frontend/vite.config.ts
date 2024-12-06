import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths';
import path from 'path';

console.log('dirname', __dirname) 
console.log(path.resolve(__dirname, 'src/lib'))

// https://vite.dev/config/
export default defineConfig({
  root:__dirname,
  plugins: [tsconfigPaths(),react()],
  resolve: {
    alias: {
      '@/lib':path.resolve(__dirname, 'src/lib') ,
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/hooks': path.resolve(__dirname, 'src/hooks'),
    },
  },
})

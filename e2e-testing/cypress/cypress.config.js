import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000/',
    experimentalRunAllSpecs: true,
    env: {
      prefix: 'schmilblick',
      baseUrl: '',
    },
    supportFile: 'src/support/e2e.ts',
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
  },
});

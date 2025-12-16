// app.tsx
import { createDocsApp, DocsPage } from '@usecross/docs'
import '@usecross/docs/styles.css'
import './styles.css'
import CustomHomePage from './CustomHomePage'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': CustomHomePage,
  },
  title: (title) => `${title} - My Docs`,
})

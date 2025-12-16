// app.tsx
import { createDocsApp, DocsPage, HomePage } from '@usecross/docs'
import '@usecross/docs/styles.css'
import './styles.css'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': HomePage,
  },
  title: (title) => `${title} - My Docs`,
})

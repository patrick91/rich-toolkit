// app.tsx
import { createDocsApp, DocsPage } from '@usecross/docs'
import '@usecross/docs/styles.css'
import './styles.css'
import CustomHomePage from './CustomHomePage'
import TerminalExample from './TerminalExample'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': CustomHomePage,
  },
  components: {
    TerminalExample,
  },
  title: (title) => `${title} - My Docs`,
})

# Cross-Docs Architecture Diagram

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT REQUEST                                │
│                         GET /docs/getting-started                       │
└────────────────────────────────────────────────────────────────────────┬┘
                                                                           │
                                                                           │
                            ┌──────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  FastAPI Backend (Python)   │
              │  routes.py - docs_page()    │
              └──────────────┬──────────────┘
                             │
                             │ 1. Load markdown file
                             │
                             ▼
              ┌─────────────────────────────┐
              │  markdown.py                │
              │  parse_frontmatter()        │
              │  load_markdown()            │
              │                             │
              │ Extracts:                   │
              │ - title (from YAML)         │
              │ - description (from YAML)   │
              │ - body (raw markdown)       │
              └──────────────┬──────────────┘
                             │
                             │ 2. Prepare Inertia Props
                             │
                             ▼
              ┌─────────────────────────────┐
              │  Inertia Response           │
              │  (JSON to Frontend)         │
              │                             │
              │ {                           │
              │   "props": {                │
              │     "content": {            │
              │       "title": "...",       │
              │       "description": "...", │
              │       "body": "# Markdown"  │
              │     },                      │
              │     "nav": [...],           │
              │     "currentPath": "..."    │
              │   },                        │
              │   "component": "docs/..."   │
              │ }                           │
              └──────────────┬──────────────┘
                             │
                             │ 3. HTTP Response (JSON)
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
          ▼                                     ▼
    ┌──────────────────┐              ┌───────────────────┐
    │  Browser JS      │              │  Hydration HTML   │
    │  (React Client)  │              │  (SSR Pre-render) │
    └────────┬─────────┘              └───────────────────┘
             │
             │ 4. React Hydration/Render
             │
             ▼
    ┌─────────────────────────────────────┐
    │  app.tsx                            │
    │  createDocsApp({ pages: {...} })    │
    │                                     │
    │  Resolves component name            │
    │  ↓                                  │
    │  pages['docs/DocsPage']             │
    └────────┬────────────────────────────┘
             │
             │ 5. DocsPage Component
             │
             ▼
    ┌─────────────────────────────────────┐
    │  DocsPage.tsx                       │
    │                                     │
    │  <DocsLayout>                       │
    │    <Markdown                        │
    │      content={props.content.body}   │
    │      components={props.components}  │
    │    />                               │
    │  </DocsLayout>                      │
    └────────┬────────────────────────────┘
             │
             │ 6. Markdown Parsing & Rendering
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Markdown.tsx                       │
    │  (react-markdown wrapper)           │
    │                                     │
    │  <ReactMarkdown                     │
    │    content="# Getting Started..."   │
    │    remarkPlugins={[                 │
    │      remarkGfm                      │
    │    ]}                               │
    │    rehypePlugins={[                 │
    │      rehypeRaw                      │
    │    ]}                               │
    │    components={{                    │
    │      code: CustomCodeBlock,         │
    │      a: CustomLink,                 │
    │      table: CustomTable,            │
    │      ...userComponents              │
    │    }}                               │
    │  />                                 │
    └────────┬────────────────────────────┘
             │
             ├─ remarkGfm: Markdown → AST
             │  (handles tables, strikethrough, etc.)
             │
             ├─ rehypeRaw: AST → HTML AST
             │  (parses raw HTML nodes)
             │
             ├─ Components Mapping:
             │  (HTML elements → React components)
             │  - <code> → CodeBlock (with Shiki)
             │  - <a> → styled Link
             │  - <table> → styled Table
             │  - <div>, <span>, etc. → plain elements
             │  - custom component overrides via props
             │
             ▼
    ┌─────────────────────────────────────┐
    │  React Elements (JSX)               │
    │                                     │
    │  <article className="prose">        │
    │    <h1>Getting Started</h1>         │
    │    <p>Introduction text...</p>      │
    │    <CodeBlock language="python">... │
    │    <table>...</table>               │
    │    <a href="/docs/...">Link</a>     │
    │  </article>                         │
    │                                     │
    │  + DocsLayout wrapper:              │
    │    - Fixed navigation (header)      │
    │    - Sidebar navigation             │
    │    - Mobile menu                    │
    │    - Footer                         │
    └────────┬────────────────────────────┘
             │
             │ 7. React DOM Rendering
             │
             ▼
    ┌─────────────────────────────────────┐
    │  Final HTML Rendered in DOM         │
    │  (with Tailwind CSS styling)        │
    │                                     │
    │  Displayed in Browser               │
    └─────────────────────────────────────┘
```

---

## Component Hierarchy

```
App (Inertia.js)
├── DocsLayout
│   ├── Fixed Nav
│   │   ├── Logo
│   │   ├── Nav Links
│   │   └── GitHub Icon
│   ├── Main Content Area
│   │   ├── Sidebar (Desktop)
│   │   │   └── Navigation Tree
│   │   └── Article Content
│   │       └── Markdown Component ◄── CUSTOM COMPONENTS INJECTED HERE
│   │           ├── (Paragraphs)
│   │           ├── (Code Blocks) → CodeBlock with Shiki
│   │           ├── (Links)
│   │           ├── (Tables)
│   │           └── (Custom Components from Props)
│   └── Footer
└── Mobile Menu (Overlay)
    └── Sidebar
```

---

## Markdown Rendering Pipeline (Detailed)

```
Raw Markdown String:
"# Getting Started\n\n```python\nprint('hello')\n```\n\n[Link](/docs/guide)"

                            │
                            ▼
         ┌──────────────────────────────────┐
         │  remark plugins                  │
         │  (markdown parser)               │
         │                                  │
         │  - remarkGfm                     │
         │    (adds GFM support)            │
         │  - custom plugins                │
         │    (e.g., callout, tabs)         │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  Markdown AST                    │
         │                                  │
         │  {                               │
         │    type: 'root',                 │
         │    children: [                   │
         │      {                           │
         │        type: 'heading',          │
         │        depth: 1,                 │
         │        children: [               │
         │          { type: 'text',         │
         │            value: 'Getting...'   │
         │          }                       │
         │        ]                         │
         │      },                          │
         │      {                           │
         │        type: 'code',             │
         │        lang: 'python',           │
         │        value: "print('hello')"   │
         │      },                          │
         │      ...                         │
         │    ]                             │
         │  }                               │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  rehype plugins                  │
         │  (AST transformer)               │
         │                                  │
         │  - rehypeRaw                     │
         │    (allows raw HTML)             │
         │  - custom plugins                │
         │    (transforms nodes)            │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  HTML AST (HAST)                 │
         │                                  │
         │  {                               │
         │    type: 'root',                 │
         │    children: [                   │
         │      {                           │
         │        type: 'element',          │
         │        tagName: 'h1',            │
         │        children: [...]           │
         │      },                          │
         │      {                           │
         │        type: 'element',          │
         │        tagName: 'pre',           │
         │        children: [               │
         │          {                       │
         │            type: 'element',      │
         │            tagName: 'code',      │
         │            className: [          │
         │              'language-python'   │
         │            ],                    │
         │            children: [...]       │
         │          }                       │
         │        ]                         │
         │      },                          │
         │      ...                         │
         │    ]                             │
         │  }                               │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  Components Mapping               │
         │  (HTML elements → React)          │
         │                                  │
         │  For each HTML node:             │
         │  - h1 → <h1>                     │
         │  - pre → (skip, handled by code) │
         │  - code → CodeBlock component    │
         │  - a → styled <a>                │
         │  - table → styled <table>        │
         │  - * → override from components  │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  React JSX Elements              │
         │                                  │
         │  <>                              │
         │    <h1>Getting Started</h1>      │
         │    <CodeBlock                    │
         │      code="print('hello')"       │
         │      language="python"           │
         │    />                            │
         │    <a href="/docs/guide">        │
         │      Link                        │
         │    </a>                          │
         │  </>                             │
         └──────────────┬───────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────┐
         │  React Rendering                 │
         │  (JSX → HTML in DOM)             │
         └──────────────────────────────────┘
```

---

## Custom Components Integration Points

### Current (Limited):
```
react-markdown
├── remarkPlugins: []
├── rehypePlugins: []
└── components: {          ◄── Only this accepts custom components
    code: (props) => ...,
    a: (props) => ...,
    p: (props) => ...,
    ...customOverrides    ◄── User-provided overrides
  }
```

### Proposed (For rich-toolkit):
```
createDocsApp({
  pages: { ... },
  title: (t) => ...,
  components: {           ◄── NEW: Component registry
    Alert: AlertComponent,
    Card: CardComponent,
    Callout: CalloutComponent,
  }
})

                        ↓ (passed via Inertia props)

DocsPage receives components prop
                        ↓
Markdown component receives components prop
                        ↓
ReactMarkdown spreads components into its config
                        ↓
Custom components available in markdown rendering
```

---

## Code Block Rendering (Detailed Example)

```
Markdown Input:
─────────────────────────────────────
```python title="main.py" showLineNumbers
def hello():
    print("Hello, World!")
```
─────────────────────────────────────

                        │
                        ▼

AST (from remarkGfm + rehypeRaw):
─────────────────────────────────────
{
  type: 'code',
  lang: 'python',
  meta: 'title="main.py" showLineNumbers',
  value: 'def hello():\n    print("Hello, World!")'
}
─────────────────────────────────────

                        │
                        ▼

Markdown.tsx component mapping (code handler):
─────────────────────────────────────
code({ node, className, children, ...props }) {
  const match = /language-(\w+)/.exec(className || '')
  const meta = node?.data?.meta as string
  const titleMatch = /title="([^"]+)"/.exec(meta)
  const filename = titleMatch ? titleMatch[1] : undefined
  const showLineNumbers = meta.includes('showLineNumbers')

  return (
    <CodeBlock
      code={String(children).replace(/\n$/, '')}
      language={match ? match[1] : 'text'}
      filename="main.py"
      showLineNumbers={true}
    />
  )
}
─────────────────────────────────────

                        │
                        ▼

CodeBlock.tsx rendering:
─────────────────────────────────────
1. Uses getHighlighter() to load Shiki
2. Calls highlighter.codeToHtml() with language="python"
3. Gets back HTML with syntax highlighting
4. Renders in div with:
   - Filename header (if provided)
   - Code content with HTML highlighting
   - Copy button
   - Optional line numbers
5. Uses dangerouslySetInnerHTML to inject Shiki HTML
─────────────────────────────────────

                        │
                        ▼

Final Rendered HTML:
─────────────────────────────────────
<div class="group relative overflow-hidden rounded-lg bg-[#24292f]">
  <div class="flex items-center gap-2 border-b border-slate-700 ...">
    <svg>...</svg>
    <span>main.py</span>
  </div>
  <button class="absolute right-2 top-2 ...">Copy</button>
  <div class="overflow-x-auto text-sm [&_pre]:m-0 ...">
    <pre class="shiki" style="background-color: #24292f">
      <code class="grid grid-cols-[auto_1fr]">
        <!-- Shiki-generated HTML with syntax highlighting -->
        <span class="line-number">1</span>
        <span class="line"><span style="color: #ff7b72">def</span> <span style="color: #d4d4d4">hello</span>...</span>
      </code>
    </pre>
  </div>
</div>
─────────────────────────────────────
```

---

## Plugin System (Extensibility)

### Current Plugins:
```
remarkPlugins: [
  remarkGfm  ◄── Only one plugin currently
]

rehypePlugins: [
  rehypeRaw  ◄── Only one plugin currently
]
```

### How Plugins Work:

```
Plugin is a function: (options?) => (tree, file) => tree

Example:
────────────────────────────────────────────
const remarkCallout = () => {
  return (tree) => {
    // Find nodes matching a pattern
    visit(tree, 'code', (node) => {
      if (node.lang === 'callout') {
        // Transform the node
        node.type = 'jsx'
        node.value = '<Callout>{content}</Callout>'
      }
    })
  }
}

// Usage:
<ReactMarkdown
  remarkPlugins={[remarkGfm, remarkCallout]}
  ...
>
────────────────────────────────────────────
```

### Unified Ecosystem:
- Remark plugins: transform markdown AST
- Rehype plugins: transform HTML AST
- 1000+ plugins available in npm
- Can create custom plugins for rich-toolkit components

---

## Summary: Where Customization Happens

| Layer | Technology | Customization Points | Current State |
|-------|-----------|----------------------|----------------|
| Backend | FastAPI + markdown.py | Frontmatter parsing | No customization |
| Transport | Inertia.js | Props structure | No customization |
| Frontend Setup | app.tsx | Page resolution | Limited (pages only) |
| Layout | DocsLayout.tsx | Logo, nav, footer | Partial (logo, footer props) |
| Markdown Render | Markdown.tsx | Component mapping | Available but not exposed |
| Parser Plugins | remark/rehype | AST transformation | Not exposed in API |
| Syntax Highlight | Shiki | Theme, language support | Partial (theme prop on CodeBlock) |

**Best integration point: Markdown.tsx components prop + DocsAppConfig extension**

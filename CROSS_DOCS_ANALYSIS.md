# Cross-Docs Codebase Analysis: Markdown Processing & Custom Components

## Overview
Cross-Docs is a documentation framework built with:
- **Backend**: FastAPI (Python) - loads markdown files, parses frontmatter, serves via Inertia
- **Frontend**: React with Inertia.js - renders markdown using react-markdown
- **Processing Pipeline**: Raw markdown → Backend parsing → Frontend React rendering

---

## 1. HOW MARKDOWN IS PROCESSED

### Backend Processing (Python)

**File**: `/Users/patrick/github/usecross/cross-docs/python/cross_docs/markdown.py`

#### Markdown Loading & Frontmatter Parsing
```python
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, parts[2].strip()


def load_markdown(content_dir: Path, path: str) -> dict:
    """Load and parse a markdown file.

    Returns:
        Dict with title, description, and body
    """
    file_path = content_dir / f"{path}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Content not found: {path}")

    content = file_path.read_text()
    frontmatter, body = parse_frontmatter(content)

    return {
        "title": frontmatter.get("title", "Untitled"),
        "description": frontmatter.get("description", ""),
        "body": body,  # Raw markdown body
    }
```

**Key Point**: Backend only extracts frontmatter and returns raw markdown body. No HTML conversion happens on the backend.

**File**: `/Users/patrick/github/usecross/cross-docs/python/cross_docs/routes.py`

#### Inertia Props Delivery
```python
@router.get("/{path:path}")
async def docs_page(path: str, request: Request, inertia: InertiaDep):
    """Serve a docs page by path."""
    path = path.rstrip("/")
    if not path:
        path = config.index_page

    doc_path = f"docs/{path}"

    # Return raw markdown if requested
    if config.enable_markdown_response and wants_markdown(request):
        return PlainTextResponse(
            load_raw_markdown(content_dir, doc_path),
            media_type="text/markdown",
        )

    content = load_markdown(content_dir, doc_path)
    props = {
        "content": content,  # Contains title, description, body (raw markdown)
        **share_data(request),
    }

    return inertia.render(
        docs_component,  # "docs/DocsPage" by default
        props,
        view_data={"page_title": content["title"]},
    )
```

### Frontend Processing (React)

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/Markdown.tsx`

#### React Markdown with Plugins
```tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { CodeBlock } from './CodeBlock'
import type { MarkdownProps } from '../types'

/**
 * Markdown renderer with syntax highlighting and GFM support.
 */
export function Markdown({ content, components }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}        // Enables GitHub Flavored Markdown
      rehypePlugins={[rehypeRaw]}         // Allows raw HTML in markdown
      components={{
        // Override pre to avoid double wrapping with CodeBlock
        pre({ children }) {
          return <>{children}</>
        },
        // Custom code block rendering with syntax highlighting
        code({ node, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !match && !className

          if (isInline) {
            return (
              <code
                className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200"
                {...props}
              >
                {children}
              </code>
            )
          }

          // Parse meta string from code fence (e.g., ```python title="app.py")
          const meta = (node?.data?.meta as string) || ''
          const titleMatch = /title="([^"]+)"/.exec(meta)
          const filename = titleMatch ? titleMatch[1] : undefined
          const showLineNumbers = meta.includes('showLineNumbers')

          return (
            <CodeBlock
              code={String(children).replace(/\n$/, '')}
              language={match ? match[1] : 'text'}
              filename={filename}
              showLineNumbers={showLineNumbers}
            />
          )
        },
        // Custom link styling
        a({ href, children }) {
          const isExternal = href?.startsWith('http')
          return (
            <a
              href={href}
              className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              {...(isExternal ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
            >
              {children}
            </a>
          )
        },
        // Tables, th, td with custom styles...

        // Allow component overrides
        ...components,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
```

#### Pipeline Summary
1. **input**: Raw markdown string
2. **remarkPlugins**: Parse markdown to AST
   - `remarkGfm`: Supports tables, strikethrough, etc.
3. **rehypePlugins**: Convert to HTML AST
   - `rehypeRaw`: Parses raw HTML nodes in markdown
4. **components**: React component mapping for each HTML element
5. **output**: React JSX elements rendered to DOM

---

## 2. THE `components` CONFIG OPTION IN createDocsApp

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/types.ts`

### Type Definitions
```typescript
/** Props for Markdown component */
export interface MarkdownProps {
  content: string
  /** Override default markdown components */
  components?: Record<string, React.ComponentType<any>>
}

/** Configuration for createDocsApp */
export interface DocsAppConfig {
  pages: Record<string, React.ComponentType<any>>
  title?: (pageTitle: string) => string
  // NOTE: No 'components' option at createDocsApp level
}
```

### Current Usage
The `components` option in Markdown.tsx is **NOT exposed** in createDocsApp config. It would need to be:

**Current**:
```tsx
// In app.tsx
createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
  },
  title: (title) => `${title} - My Docs`,
  // No way to pass custom markdown components
})
```

**To Add Support**:
```tsx
// Desired usage
createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
  },
  components: {
    Alert: CustomAlert,
    Card: CustomCard,
    // etc.
  }
})
```

This would require:
1. Adding `components` to DocsAppConfig type
2. Passing components through the Inertia props
3. Using them in the DocsPage/Markdown components

---

## 3. WHERE MARKDOWN IS CONVERTED TO HTML/REACT

### The Conversion Happens in React via react-markdown

**Primary File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/Markdown.tsx`

#### Conversion Pipeline:
```
Raw Markdown String
       ↓
   ReactMarkdown Component
       ↓
   remark plugins (markdown → AST)
       ├─ remarkGfm (GitHub Flavored Markdown)
       ├─ (custom plugins can be added)
       ↓
   rehype plugins (AST → HTML AST)
       ├─ rehypeRaw (parse raw HTML)
       ├─ (custom plugins can be added)
       ↓
   components mapping (HTML elements → React components)
       ├─ <code> → custom CodeBlock or inline code
       ├─ <a> → styled link
       ├─ <table> → styled table
       ├─ <pre> → avoided (handled by code)
       ├─ Custom components via ...components spread
       ↓
   React JSX Elements
       ↓
   React DOM
```

#### Key Libraries:
- **react-markdown** (v10.1.0): Wrapper around remark/rehype
- **remark-gfm** (v4.0.1): GFM support
- **rehype-raw** (v7.0.0): Raw HTML support

#### No Backend HTML Generation:
- Backend returns plain `.body` string (raw markdown)
- Frontend does all parsing and conversion
- This allows for SSR, custom theming, and dynamic components

---

## 4. HOW CUSTOM COMPONENTS ARE REGISTERED AND USED

### Current Component Registration System

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/Markdown.tsx`

```tsx
<ReactMarkdown
  // ... plugins ...
  components={{
    // Built-in overrides
    code({ node, className, children, ...props }) {
      // Custom rendering
    },
    a({ href, children }) {
      // Custom styling
    },
    table({ children }) {
      // Custom styling
    },
    // ...

    // Allow component overrides from props
    ...components,  // <-- This is the key line!
  }}
>
  {content}
</ReactMarkdown>
```

### How it Works Now:
1. `components` prop comes from the Markdown component
2. Gets spread into the ReactMarkdown components object
3. Allows overriding any HTML element type

**Example Usage** (currently not exposed in API):
```tsx
<Markdown
  content={rawMarkdown}
  components={{
    // Override blockquote
    blockquote: ({ children }) => (
      <blockquote className="custom-quote">
        {children}
      </blockquote>
    ),
    // Override paragraph
    p: ({ children }) => (
      <p className="custom-paragraph">
        {children}
      </p>
    ),
  }}
/>
```

### Component Props from react-markdown:
react-markdown passes props based on HTML element type. Examples:

```typescript
// For <code>
code(props: {
  node: Element
  className: string
  children: ReactNode
  ...props: any
})

// For <a>
a(props: {
  href: string
  title: string
  children: ReactNode
  ...props: any
})

// For <img>
img(props: {
  src: string
  alt: string
  title: string
  ...props: any
})
```

---

## 5. EXISTING SUPPORT FOR CUSTOM COMPONENTS IN MARKDOWN

### Current State: NO Direct Support for Custom HTML Tags

The system currently uses standard HTML elements:
- `<code>`, `<pre>` for code blocks
- `<a>` for links
- `<table>`, `<th>`, `<td>` for tables
- `<h1>` through `<h6>` for headings
- `<p>`, `<blockquote>`, `<ul>`, `<ol>` for text
- `<img>` for images

### What rehypeRaw Does Enable:
With `rehypeRaw` plugin enabled, raw HTML is parsed, e.g.:

```markdown
<div class="custom">
  <span>Some content</span>
</div>
```

This gets converted to React elements, but **plain HTML tags only** - no custom React components.

### Gap: No JSX/Component Tag Support
You **CANNOT** currently write:
```markdown
<Alert type="warning">
  This is a warning
</Alert>
```

And have it render as a React component. It would just render as plain HTML.

---

## CRITICAL FINDINGS FOR RICH-TOOLKIT INTEGRATION

### What Works:
✅ HTML element component overrides via `components` prop
✅ Code block meta information parsing (title, showLineNumbers)
✅ Shiki syntax highlighting integration
✅ rehypeRaw allows raw HTML in markdown

### What Doesn't Work:
❌ JSX/React component tags in markdown (e.g., `<Alert type="warning">`)
❌ `components` config not exposed in createDocsApp API
❌ Component registration system is minimal

### For rich-toolkit Integration, You Could:

#### Option 1: Extend via HTML Elements (Current Approach)
```tsx
// In the markdown
<div class="callout" data-type="info">
  Important information
</div>

// In components config
components={{
  div: ({ className, 'data-type': type, children }) => {
    if (className?.includes('callout')) {
      return <Callout type={type}>{children}</Callout>
    }
    return <div className={className}>{children}</div>
  }
}}
```

#### Option 2: Custom Remark Plugin (Recommended)
Create a remark plugin that transforms special markdown syntax into custom JSX:

```tsx
// Example: Transform ```callout into <Callout>
const remarkCallout = () => {
  return (tree) => {
    // Find code blocks with language "callout"
    // Transform to custom JSX nodes
  }
}

// Use in Markdown.tsx:
<ReactMarkdown
  remarkPlugins={[remarkGfm, remarkCallout]}
  // ...
>
```

#### Option 3: MDX-like Syntax (Future)
Use unified plugin system to support component syntax:
```markdown
<Alert type="info">
  This is an alert
</Alert>
```

Would require building a custom parser layer.

---

## FILE STRUCTURE SUMMARY

```
/cross-docs/
├── python/
│   └── cross_docs/
│       ├── config.py           # Configuration loading
│       ├── markdown.py          # Markdown parsing (frontmatter only)
│       ├── routes.py            # Inertia props delivery
│       ├── navigation.py        # Nav structure generation
│       └── middleware.py        # Request handling
│
└── js/
    └── src/
        ├── components/
        │   ├── Markdown.tsx      # Main markdown renderer (react-markdown wrapper)
        │   ├── DocsPage.tsx      # Default docs page component
        │   ├── DocsLayout.tsx    # Main layout with sidebar
        │   ├── CodeBlock.tsx     # Syntax highlighting with Shiki
        │   ├── HomePage.tsx      # Homepage with compound components
        │   ├── Sidebar.tsx       # Navigation sidebar
        │   └── index.ts          # Exports
        ├── app.tsx               # createDocsApp entry point
        ├── ssr.tsx               # Server-side rendering
        ├── types.ts              # TypeScript definitions
        ├── lib/
        │   ├── shiki.ts          # Syntax highlighter setup
        │   └── utils.ts          # Utilities
        └── index.ts              # Public API
```

---

## KEY INTEGRATION POINTS FOR RICH-TOOLKIT

1. **Markdown.tsx** (line 10-93)
   - Accept custom components via props
   - Spread into ReactMarkdown components object
   - Filter/validate component types

2. **DocsPage.tsx** (line 13-18)
   - Pass components through to Markdown
   - Receive from props chain

3. **types.ts**
   - Extend DocsAppConfig with components option
   - Add component type validation

4. **app.tsx**
   - Expose components in createDocsApp config
   - Pass through to page components via Inertia props

5. **routes.py** (Python backend)
   - No changes needed - stays pure markdown delivery
   - Component configuration is client-side only

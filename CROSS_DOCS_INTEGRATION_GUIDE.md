# Cross-Docs & Rich-Toolkit Integration Guide

## Quick Summary

Cross-Docs uses a **clean separation of concerns**:
- **Backend (Python)**: Raw markdown + frontmatter extraction only
- **Frontend (React)**: All rendering via react-markdown + custom components
- **No HTML conversion on backend** - just pass raw markdown through

This is **perfect** for rich-toolkit because:
1. Custom components can be injected at the React layer
2. No backend modification needed
3. Full control over markdown element rendering
4. Standard react-markdown patterns

---

## Key Code Snippets

### 1. Where Raw Markdown is Loaded (Backend)

**File**: `/Users/patrick/github/usecross/cross-docs/python/cross_docs/markdown.py:33-57`

```python
def load_markdown(content_dir: Path, path: str) -> dict:
    """Load and parse a markdown file.

    Returns:
        Dict with title, description, and body
    """
    file_path = content_dir / f"{path}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Content not found: {path}")

    content = file_path.read_text()
    frontmatter, body = parse_frontmatter(content)  # Only splits frontmatter

    return {
        "title": frontmatter.get("title", "Untitled"),
        "description": frontmatter.get("description", ""),
        "body": body,  # ◄── RAW MARKDOWN STRING
    }
```

**Key Point**: The `.body` is raw markdown - no HTML generation.

---

### 2. Markdown Rendering with Component Overrides (Frontend)

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/Markdown.tsx:10-93`

```tsx
export function Markdown({ content, components }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        // Built-in component overrides
        code({ node, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !match && !className

          if (isInline) {
            return (
              <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">
                {children}
              </code>
            )
          }

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
        table({ children }) {
          return (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">{children}</table>
            </div>
          )
        },
        th({ children }) {
          return (
            <th className="border-b border-gray-200 bg-gray-50 px-4 py-2 font-semibold dark:border-gray-700 dark:bg-gray-800">
              {children}
            </th>
          )
        },
        td({ children }) {
          return (
            <td className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
              {children}
            </td>
          )
        },
        // ◄── KEY LINE: Allow component overrides from props
        ...components,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
```

**Key Point**: Line `...components` spreads user-provided components into the ReactMarkdown config.

---

### 3. Type Definition for Components

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/types.ts:70-75`

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
  // NOTE: No 'components' option currently
}
```

**Gap**: `DocsAppConfig` doesn't have a `components` option yet.

---

### 4. Where Components Are Used (DocsPage)

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/DocsPage.tsx:13-19`

```tsx
export function DocsPage({ content, ...layoutProps }: DocsPageProps) {
  return (
    <DocsLayout title={content?.title ?? ''} description={content?.description} {...layoutProps}>
      <Markdown content={content?.body ?? ''} />
      {/* ◄── Markdown component accepts components via props */}
    </DocsLayout>
  )
}
```

**Gap**: The `components` prop is never passed to `<Markdown>`.

---

### 5. App Creation Entry Point

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/app.tsx:20-46`

```tsx
export function createDocsApp(config: DocsAppConfig): void {
  const { pages, title } = config

  if (typeof window !== 'undefined') {
    window.history.scrollRestoration = 'manual'
    window.scrollTo(0, 0)
  }

  createInertiaApp({
    title: title ?? ((pageTitle) => (pageTitle ? `${pageTitle}` : 'Documentation')),
    resolve: (name) => {
      const page = pages[name]
      if (!page) {
        throw new Error(`Page component "${name}" not found`)
      }
      return page
    },
    setup({ el, App, props }) {
      if (el.hasChildNodes()) {
        hydrateRoot(el, <App {...props} />)
      } else {
        createRoot(el).render(<App {...props} />)
      }
    },
  })
}
```

**Gap**: No way to pass custom components through config.

---

## Integration Steps for Rich-Toolkit

### Step 1: Extend DocsAppConfig Type

**File to modify**: `/Users/patrick/github/usecross/cross-docs/js/src/types.ts`

```typescript
export interface DocsAppConfig {
  pages: Record<string, React.ComponentType<any>>
  title?: (pageTitle: string) => string
  // ADD THIS:
  components?: Record<string, React.ComponentType<any>>
}
```

---

### Step 2: Pass Components Through createDocsApp

**File to modify**: `/Users/patrick/github/usecross/cross-docs/js/src/app.tsx`

```tsx
export function createDocsApp(config: DocsAppConfig): void {
  const { pages, title, components } = config  // ◄── Extract components

  // ... existing code ...

  createInertiaApp({
    // ... existing code ...
    setup({ el, App, props }) {
      // Inject components into shared props
      const enhancedProps = {
        ...props,
        components: components,  // ◄── Add components
      }

      if (el.hasChildNodes()) {
        hydrateRoot(el, <App {...enhancedProps} />)
      } else {
        createRoot(el).render(<App {...enhancedProps} />)
      }
    },
  })
}
```

---

### Step 3: Update DocsPage to Accept Components

**File to modify**: `/Users/patrick/github/usecross/cross-docs/js/src/components/DocsPage.tsx`

```tsx
interface DocsPageProps extends Omit<DocsLayoutProps, 'children' | 'title'> {
  content: DocContent
  components?: Record<string, React.ComponentType<any>>  // ◄── ADD THIS
}

export function DocsPage({ content, components, ...layoutProps }: DocsPageProps) {
  return (
    <DocsLayout title={content?.title ?? ''} description={content?.description} {...layoutProps}>
      <Markdown
        content={content?.body ?? ''}
        components={components}  // ◄── PASS TO MARKDOWN
      />
    </DocsLayout>
  )
}
```

---

### Step 4: Verify Markdown Component (No Changes Needed)

**File**: `/Users/patrick/github/usecross/cross-docs/js/src/components/Markdown.tsx`

The Markdown component already accepts and uses the `components` prop correctly:

```tsx
export function Markdown({ content, components }: MarkdownProps) {
  return (
    <ReactMarkdown
      // ...
      components={{
        // built-in overrides...
        ...components,  // ◄── Already spreads user components
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
```

**No changes needed!**

---

## How Users Would Use It (Rich-Toolkit)

### Example 1: Custom Alert Component

```tsx
// User's app.tsx
import { createDocsApp, DocsPage, HomePage } from '@usecross/docs'
import { Alert, Card, Callout } from '@my-org/components'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': HomePage,
  },
  title: (title) => `${title} - My Docs`,
  components: {
    Alert,      // Map custom <Alert> component
    Card,       // Map custom <Card> component
    Callout,    // Map custom <Callout> component
  }
})
```

### Example 2: In Markdown

```markdown
# My Documentation

<Alert type="warning">
  This is important!
</Alert>

<Card>
  <h3>Card Title</h3>
  <p>Card content</p>
</Card>

<Callout>
  Some callout text
</Callout>
```

### Key Limitation

With **current implementation**, component tags would need to use standard HTML elements that react-markdown understands. For true JSX-like component support, we'd need:

#### Option A: Use HTML elements with custom renderer

```markdown
<div data-component="alert" data-type="warning">
  This is important!
</div>
```

```tsx
components={{
  div: ({ 'data-component': component, 'data-type': type, children }) => {
    if (component === 'alert') {
      return <Alert type={type}>{children}</Alert>
    }
    return <div>{children}</div>
  }
}}
```

#### Option B: Use Custom Remark Plugin (Recommended)

Create a remark plugin to transform special syntax:

```tsx
const remarkRichComponents = () => {
  return (tree) => {
    // Transform <Alert>...</Alert> syntax
    // Into React component nodes
  }
}

// In Markdown.tsx:
<ReactMarkdown
  remarkPlugins={[remarkGfm, remarkRichComponents]}
  rehypePlugins={[rehypeRaw]}
  components={{ ... }}
>
```

---

## Testing the Integration

### Test Case 1: Basic Component Override

```tsx
createDocsApp({
  pages: { 'docs/DocsPage': DocsPage },
  components: {
    a: ({ href, children }) => (
      <a href={href} className="custom-link-class">
        🔗 {children}
      </a>
    )
  }
})
```

**Expected**: All markdown links render with custom styling and emoji.

---

### Test Case 2: Component with Children

```tsx
createDocsApp({
  pages: { 'docs/DocsPage': DocsPage },
  components: {
    blockquote: ({ children }) => (
      <blockquote className="custom-quote">
        <span>💭</span>
        {children}
      </blockquote>
    )
  }
})
```

**Expected**: Blockquotes render with custom styling and emoji.

---

### Test Case 3: Code Block Override

```tsx
createDocsApp({
  pages: { 'docs/DocsPage': DocsPage },
  components: {
    code: ({ className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '')
      if (!match) {
        return <code className="custom-inline-code">{children}</code>
      }
      return (
        <pre className="custom-code-block">
          <code className={className}>{children}</code>
        </pre>
      )
    }
  }
})
```

**Expected**: Code blocks and inline code render with custom styling.

---

## Component Props Reference

### Props passed to component functions by react-markdown:

```typescript
// For heading elements (h1, h2, etc.)
h1(props: {
  children: React.ReactNode
  node?: Element
  ...rest: any
})

// For paragraph
p(props: {
  children: React.ReactNode
  node?: Element
  ...rest: any
})

// For links
a(props: {
  href?: string
  title?: string
  children: React.ReactNode
  node?: Element
  ...rest: any
})

// For images
img(props: {
  src?: string
  alt?: string
  title?: string
  ...rest: any
})

// For code/pre
code(props: {
  node?: Element
  inline?: boolean
  className?: string
  children: React.ReactNode
  ...rest: any
})

pre(props: {
  children: React.ReactNode
  node?: Element
  ...rest: any
})

// For list items
ul(props: { children: React.ReactNode })
ol(props: { children: React.ReactNode })
li(props: { children: React.ReactNode, index?: number })

// For tables
table(props: { children: React.ReactNode })
thead(props: { children: React.ReactNode })
tbody(props: { children: React.ReactNode })
tr(props: { children: React.ReactNode })
th(props: { children: React.ReactNode })
td(props: { children: React.ReactNode })

// For blockquote
blockquote(props: { children: React.ReactNode })
```

---

## Files Modified Summary

| File | Change | Complexity |
|------|--------|------------|
| `types.ts` | Add `components` to `DocsAppConfig` | Very Simple |
| `app.tsx` | Pass `components` through Inertia props | Simple |
| `DocsPage.tsx` | Accept and forward `components` prop | Simple |
| `Markdown.tsx` | Already works - no changes needed | N/A |

**Total complexity**: Low - just prop plumbing

---

## Benefits for Rich-Toolkit

✅ Users can inject custom Rich components
✅ Markdown authors don't need to learn custom syntax
✅ Works with all standard markdown
✅ Backwards compatible (optional prop)
✅ Follows react-markdown patterns
✅ No backend changes required
✅ Works with SSR

---

## Next Steps

1. Create a PR to add `components` to `DocsAppConfig`
2. Test with simple example (styled links, blockquotes)
3. Document in cross-docs README
4. Consider custom remark plugin for advanced use cases
5. Add TypeScript examples to docs

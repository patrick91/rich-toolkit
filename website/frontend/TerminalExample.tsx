import { useEffect, useState } from 'react'

interface TerminalExampleProps {
  src?: string
  example?: string
  height?: string
  format?: 'html' | 'mp4'
}

export function TerminalExample({
  src,
  example,
  height = 'auto',
  format = 'mp4'  // Default to MP4 for VHS videos
}: TerminalExampleProps) {
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [contentType, setContentType] = useState<'html' | 'video'>('video')

  useEffect(() => {
    const fetchExample = async () => {
      try {
        setLoading(true)
        setError(null)

        // Determine the URL and content type
        let url = src
        let type: 'html' | 'video' = 'html'

        if (example) {
          // Convert example.py to the appropriate format
          const baseName = example.replace(/\.py$/, '')
          if (format === 'mp4') {
            url = `/examples/${baseName}.mp4`
            type = 'video'
          } else {
            url = `/examples/${baseName}.html`
            type = 'html'
          }
        }

        if (!url) {
          throw new Error('Either src or example prop must be provided')
        }

        setContentType(type)

        if (type === 'html') {
          const response = await fetch(url)

          if (!response.ok) {
            throw new Error(`Failed to load example: ${response.statusText}`)
          }

          const htmlContent = await response.text()
          setContent(htmlContent)
        } else {
          // For video, just store the URL
          setContent(url)
        }
      } catch (err) {
        console.error('Error loading terminal example:', err)
        setError(err instanceof Error ? err.message : 'Failed to load example')
      } finally {
        setLoading(false)
      }
    }

    fetchExample()
  }, [src, example, format])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-800 rounded-lg animate-pulse">
        <div className="text-gray-400">Loading example...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
        <div className="text-red-400 text-sm">Error: {error}</div>
      </div>
    )
  }

  if (contentType === 'video') {
    return (
      <div className="terminal-example my-6 rounded-lg overflow-hidden">
        <video
          src={content}
          loop
          muted
          autoPlay
          playsInline
          style={{
            width: '100%',
            height: 'auto',
            display: 'block'
          }}
        >
          Your browser does not support the video tag.
        </video>
      </div>
    )
  }

  return (
    <div
      className="terminal-example my-6"
      style={{ height }}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
}

export default TerminalExample

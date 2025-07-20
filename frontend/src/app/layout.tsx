import type { Metadata } from 'next'
import { QueryProvider } from '@/lib/query-provider'
import Layout from '@/components/ui/layout'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'Louden Swain Wrestling Platform',
  description: 'NCAA D1 Wrestling Championship Data Platform',
  keywords: ['wrestling', 'ncaa', 'tournament', 'brackets'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased">
        <QueryProvider>
          <Layout>
            {children}
          </Layout>
        </QueryProvider>
      </body>
    </html>
  )
}
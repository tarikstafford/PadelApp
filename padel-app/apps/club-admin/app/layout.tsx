import { Geist, Geist_Mono } from "next/font/google"

import "@workspace/ui/globals.css"
import { Providers } from "@/components/providers"
import { AuthProvider } from "@/contexts/AuthContext"
import { Toaster } from "@workspace/ui/components/sonner"
import ErrorBoundary from "@/components/ErrorBoundary"
import { DashboardPage } from "@/components/layout/Dashboard"

const fontSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${fontSans.variable} ${fontMono.variable} font-sans antialiased `}
      >
        <ErrorBoundary fallback={<div>Something went wrong</div>}>
          <Providers>
            <AuthProvider>
              <DashboardPage>{children}</DashboardPage>
              <Toaster richColors position="top-right" />
            </AuthProvider>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
} 
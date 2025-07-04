import { Geist, Geist_Mono } from "next/font/google"
import { Inter } from "next/font/google"
import { ThemeProvider } from "next-themes"
import "@workspace/ui/globals.css"
import { Providers } from "@/components/providers"
import { AuthProvider } from "@/contexts/AuthContext"
import { ClubProvider } from "@/contexts/ClubContext"
import { Toaster } from "@workspace/ui/components/sonner"
import ErrorBoundary from "@/components/ErrorBoundary"
import { v4 as uuidv4 } from 'uuid'

const fontSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

// Polyfill for crypto.randomUUID for environments that don't support it
if (typeof window !== 'undefined' && !window.crypto.randomUUID) {
  window.crypto.randomUUID = uuidv4 as any
}

const inter = Inter({ subsets: ["latin"] });

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
              <ClubProvider>
                {children}
                <Toaster richColors position="top-right" />
              </ClubProvider>
            </AuthProvider>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
} 
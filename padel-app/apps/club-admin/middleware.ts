import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedRoutes = ['/dashboard', '/courts', '/bookings', '/profile'];
const publicRoutes = ['/login', '/register', '/'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value
  const { pathname } = request.nextUrl

  // If the user is logged in
  if (token) {
    // And tries to access a public-only route (like login), redirect to dashboard
    if (publicRoutes.includes(pathname)) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  } 
  // If the user is not logged in
  else {
    // And tries to access a protected route, redirect to login
    if (protectedRoutes.some(prefix => pathname.startsWith(prefix))) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
} 
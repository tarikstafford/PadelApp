import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value
  const role = request.cookies.get('role')?.value
  const { pathname } = request.nextUrl

  // If trying to access login or register page while authenticated, redirect to dashboard
  if (token && (pathname === '/login' || pathname === '/register')) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // If trying to access a protected route without a token, redirect to login
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // If trying to access a protected route without the correct role, redirect to unauthorized
  if (role !== 'CLUB_ADMIN') {
    return NextResponse.redirect(new URL('/unauthorized', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/courts/:path*',
    '/bookings/:path*',
    '/profile/:path*',
    '/login',
    '/register',
  ],
} 
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value
  const role = request.cookies.get('role')?.value

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

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
  ],
} 
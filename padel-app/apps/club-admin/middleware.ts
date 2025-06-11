import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  sub: string;
  role: string;
  exp: number;
}

const protectedRoutes = ['/dashboard', '/courts', '/bookings', '/profile', '/admin'];
const publicRoutes = ['/login', '/register', '/'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const clubId = request.cookies.get('clubId')?.value;
  const { pathname } = request.nextUrl;

  // If the user is not logged in and tries to access a protected route
  if (!token && protectedRoutes.some(prefix => pathname.startsWith(prefix))) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If the user is logged in
  if (token) {
    // If they try to access a public route (like login), redirect to dashboard
    if (publicRoutes.includes(pathname)) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    try {
      const decodedToken: DecodedToken = jwtDecode(token);

      // Special handling for CLUB_ADMIN role
      if (decodedToken.role === 'club_admin') {
        // If they are a club admin but haven't created a club yet
        if (!clubId && pathname !== '/register') {
          // Force them to the onboarding flow
          return NextResponse.redirect(new URL('/register', request.url));
        }
        // If they have created a club and try to go to the register page
        if (clubId && pathname === '/register') {
          // Redirect them to their dashboard
          return NextResponse.redirect(new URL('/dashboard', request.url));
        }
      }
    } catch (error) {
      // Invalid token, redirect to login
      console.error("Invalid token:", error);
      // Clear cookies and redirect
      const response = NextResponse.redirect(new URL('/login', request.url));
      response.cookies.delete('token');
      response.cookies.delete('clubId');
      return response;
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
} 
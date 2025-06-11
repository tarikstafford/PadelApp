import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  sub: string;
  role: string;
  exp: number;
}

const protectedRoutes = ['/dashboard', '/courts', '/bookings', '/profile', '/admin'];
const authRoutes = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const clubId = request.cookies.get('clubId')?.value;
  const { pathname } = request.nextUrl;

  // If user is not logged in and trying to access a protected route, redirect to login
  if (!token && protectedRoutes.some(prefix => pathname.startsWith(prefix))) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If user is logged in
  if (token) {
    try {
      const decodedToken: DecodedToken = jwtDecode(token);

      // Handle the specific case of a club admin during onboarding
      if (decodedToken.role === 'club_admin' && !clubId) {
        // If they are on the register page, let them continue.
        if (pathname === '/register') {
          return NextResponse.next();
        }
        // If they are anywhere else, force them to the register page.
        return NextResponse.redirect(new URL('/register', request.url));
      }

      // For all other logged-in users (or fully onboarded admins),
      // if they try to access an auth route, redirect them to the dashboard.
      if (authRoutes.includes(pathname)) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
      }

    } catch (error) {
      // Invalid token, redirect to login and clear cookies
      console.error("Invalid token:", error);
      const response = NextResponse.redirect(new URL('/login', request.url));
      response.cookies.delete('token');
      response.cookies.delete('clubId');
      return response;
    }
  }

  // For any other case, allow the request to proceed
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
} 
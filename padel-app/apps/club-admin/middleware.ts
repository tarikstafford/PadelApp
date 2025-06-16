import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  sub: string;
  role?: string;
  exp: number;
}

const protectedRoutes = ['/dashboard', '/courts', '/bookings', '/profile', '/admin'];
const authRoutes = ['/login', '/register'];
const clubCreationPath = '/admin/club/new/edit';

// This function needs to be async to use await for fetch
export async function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const { pathname } = request.nextUrl;
  const absoluteUrl = (path: string) => new URL(path, request.url).toString();

  // If user is not logged in and trying to access a protected route, redirect to login
  if (!token && protectedRoutes.some(prefix => pathname.startsWith(prefix))) {
    return NextResponse.redirect(absoluteUrl('/login'));
  }

  // If user is logged in
  if (token) {
    try {
      const decodedToken: DecodedToken = jwtDecode(token);

      // If the user is a club admin, check if they have a club
      if (
        decodedToken.role === 'club_admin' &&
        !pathname.startsWith('/api') && // Avoid running on API routes
        pathname !== clubCreationPath &&
        !authRoutes.includes(pathname)
      ) {
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
        const clubCheckUrl = `${apiUrl}/api/v1/admin/my-club`;

        const response = await fetch(clubCheckUrl, {
          headers: { 'Authorization': `Bearer ${token}` },
          // Important for fetch in middleware
          cache: 'no-store',
        });

        // If no club exists, redirect to the creation page
        if (response.status === 404) {
          return NextResponse.redirect(absoluteUrl(clubCreationPath));
        }
      }

      // If a logged-in user tries to access an auth route, redirect them to the dashboard.
      if (authRoutes.includes(pathname)) {
        return NextResponse.redirect(absoluteUrl('/dashboard'));
      }

    } catch (error) {
      // Invalid token, redirect to login and clear cookies
      console.error("Invalid token:", error);
      const response = NextResponse.redirect(absoluteUrl('/login'));
      response.cookies.delete('token');
      return response;
    }
  }

  // For any other case, allow the request to proceed
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
} 
"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="w-full py-12 bg-gray-900 text-white">
      <div className="container px-4 md:px-6">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">PadelGo</h3>
            <p className="text-sm text-gray-400">
              Your ultimate padel experience starts here. Find courts, join tournaments, and connect with the community.
            </p>
          </div>
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Features</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/discover" className="hover:text-white transition-colors">Find Courts</Link></li>
              <li><Link href="/tournaments" className="hover:text-white transition-colors">Tournaments</Link></li>
              <li><Link href="/leaderboard" className="hover:text-white transition-colors">Leaderboard</Link></li>
              <li><Link href="/teams" className="hover:text-white transition-colors">Teams</Link></li>
            </ul>
          </div>
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Account</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/auth/register" className="hover:text-white transition-colors">Sign Up</Link></li>
              <li><Link href="/auth/login" className="hover:text-white transition-colors">Log In</Link></li>
              <li><Link href="/profile" className="hover:text-white transition-colors">Profile</Link></li>
              <li><Link href="/bookings" className="hover:text-white transition-colors">My Bookings</Link></li>
            </ul>
          </div>
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Support</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="mailto:support@padelgo.com" className="hover:text-white transition-colors">Contact Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center">
          <p className="text-sm text-gray-400">© 2025 PadelGo. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
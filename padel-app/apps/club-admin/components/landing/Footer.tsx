"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="w-full py-12 bg-gray-900 text-white">
      <div className="container px-4 md:px-6">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">PadelGo Club Admin</h3>
            <p className="text-sm text-gray-400">
              The complete platform for managing your padel club. Streamline operations, increase revenue, and create amazing player experiences.
            </p>
          </div>
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Features</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              <li><Link href="/courts" className="hover:text-white transition-colors">Court Management</Link></li>
              <li><Link href="/bookings" className="hover:text-white transition-colors">Bookings</Link></li>
              <li><Link href="/tournaments" className="hover:text-white transition-colors">Tournaments</Link></li>
            </ul>
          </div>
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Account</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/register" className="hover:text-white transition-colors">Sign Up</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors">Login</Link></li>
              <li><Link href="/admin/club" className="hover:text-white transition-colors">Club Profile</Link></li>
              <li><Link href="/admin/schedule" className="hover:text-white transition-colors">Schedule Management</Link></li>
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
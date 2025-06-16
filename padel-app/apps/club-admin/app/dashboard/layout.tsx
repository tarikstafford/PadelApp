"use client";

import { DashboardPage } from "@/components/layout/Dashboard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardPage>{children}</DashboardPage>;
} 
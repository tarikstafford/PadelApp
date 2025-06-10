import AdminProtectedRoute from "@/components/auth/AdminProtectedRoute";
import { Sidebar } from "@/components/admin/Sidebar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AdminProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </AdminProtectedRoute>
  );
} 
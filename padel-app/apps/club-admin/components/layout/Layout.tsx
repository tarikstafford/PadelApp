import React from "react";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex min-h-screen flex-col">
      {/* We can add a header or sidebar here later */}
      <main className="flex-grow">{children}</main>
      {/* We can add a footer here later */}
    </div>
  );
};

export default Layout; 
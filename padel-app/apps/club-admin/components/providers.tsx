"use client";

import React from "react";
import { ToastProvider } from "@workspace/ui/components/toast";

export const Providers = ({ children }: { children: React.ReactNode }) => {
  return (
    <ToastProvider>
      {children}
    </ToastProvider>
  );
}; 
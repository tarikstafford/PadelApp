"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { ErrorMessage } from "./ui/ErrorMessage";
import { formatErrorMessage } from "@/lib/errorHandler";
import { Button } from "@workspace/ui/components/button";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      const errorDetails = formatErrorMessage(this.state.error);
      
      return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
          <ErrorMessage error={errorDetails} className="max-w-md" />
          <div className="mt-4">
            <Button 
              onClick={() => this.setState({ hasError: false, error: null })}
              variant="outline"
            >
              Try Again
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 
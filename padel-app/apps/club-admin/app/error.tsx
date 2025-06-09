'use client';

import { useEffect } from 'react';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Button } from '@workspace/ui/components/button';
import { formatErrorMessage } from '@/lib/errorHandler';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Page error:', error);
  }, [error]);

  const errorDetails = formatErrorMessage(error);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] p-4">
      <ErrorMessage error={errorDetails} className="max-w-md" />
      <Button
        onClick={reset}
        variant="outline"
        className="mt-4"
      >
        Try Again
      </Button>
    </div>
  );
} 
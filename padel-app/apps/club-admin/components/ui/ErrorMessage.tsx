import { AlertCircle, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@workspace/ui/components/alert";
import { ErrorDetails } from "@/lib/errorHandler";

interface ErrorMessageProps {
  error: ErrorDetails;
  className?: string;
}

export function ErrorMessage({ error, className }: ErrorMessageProps) {
  return (
    <Alert variant="destructive" className={className}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{error.type.charAt(0).toUpperCase() + error.type.slice(1)} Error {error.code && `(${error.code})`}</AlertTitle>
      <AlertDescription>
        <p>{error.message}</p>
        {error.actionable && (
          <p className="mt-2 text-sm font-medium">
            <Info className="h-3 w-3 inline mr-1" />
            {error.actionable}
          </p>
        )}
      </AlertDescription>
    </Alert>
  );
} 
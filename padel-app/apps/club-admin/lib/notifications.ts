import { toast } from "sonner";
import { ErrorDetails } from "./errorHandler";

export const showErrorToast = (error: ErrorDetails) => {
  toast.error(error.message, {
    description: error.actionable,
    duration: 5000,
  });
}; 
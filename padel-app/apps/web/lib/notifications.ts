import { toast } from 'sonner';

export const showErrorToast = (message: string) => {
  toast.error(message);
};

export const showSuccessToast = (message: string) => {
  toast.success(message);
}; 
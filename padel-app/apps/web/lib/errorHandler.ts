export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object') {
    if (error.detail) {
      if (Array.isArray(error.detail)) {
        return error.detail.map((err: any) => `${err.loc.join(' > ')}: ${err.msg}`).join('\n');
      }
      return error.detail;
    }
    if (error.message) {
      return error.message;
    }
  }
  return 'An unexpected error occurred. Please try again.';
}; 
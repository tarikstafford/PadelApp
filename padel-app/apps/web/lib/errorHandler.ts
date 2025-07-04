interface ErrorDetail {
  loc: string[];
  msg: string;
}

export const formatErrorMessage = (error: unknown): string => {
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object') {
    if ('detail' in error) {
      if (Array.isArray(error.detail)) {
        return error.detail.map((err: ErrorDetail) => `${err.loc.join(' > ')}: ${err.msg}`).join('\n');
      }
      return String(error.detail);
    }
    if ('message' in error) {
      return String(error.message);
    }
  }
  return 'An unexpected error occurred. Please try again.';
}; 
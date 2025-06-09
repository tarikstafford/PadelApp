export type ErrorType = 'auth' | 'form' | 'network' | 'server' | 'unknown';

export interface ErrorDetails {
  type: ErrorType;
  message: string;
  actionable?: string; // Suggested action user can take
  code?: string; // Optional error code for reference
}

export const formatErrorMessage = (error: any): ErrorDetails => {
  // Handle FastAPI validation errors
  if (error.detail) {
    const detail = Array.isArray(error.detail) ? error.detail[0].msg : error.detail;
    if (typeof detail === 'string' && detail.includes("Email already registered")) {
      return {
        type: 'form',
        message: 'This email address is already in use.',
        actionable: 'Please try a different email or log in.',
        code: 'AUTH-REG-001'
      };
    }
    return {
      type: 'server',
      message: detail,
      actionable: 'Please check the details and try again.',
      code: 'SRV-DETAIL'
    };
  }

  if (error.response) {
    const status = error.response.status;
    if (status === 401 || status === 403) {
      return {
        type: 'auth',
        message: 'You are not authorized to perform this action',
        actionable: 'Please log in again or contact your administrator',
        code: `AUTH-${status}`
      };
    }
  } else if (error.request) {
    return {
      type: 'network',
      message: 'Unable to connect to the server',
      actionable: 'Please check your internet connection and try again',
      code: 'NET-001'
    };
  }
  
  return {
    type: 'unknown',
    message: error.message || 'An unexpected error occurred',
    actionable: 'Please try again later or contact support',
    code: 'UNK-001'
  };
}; 
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // For session-based authentication, we need to include credentials (cookies)
  // and set proper headers for CORS
  const modifiedReq = req.clone({
    setHeaders: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    withCredentials: true // This ensures cookies are sent with the request
  });
  
  return next(modifiedReq);
};

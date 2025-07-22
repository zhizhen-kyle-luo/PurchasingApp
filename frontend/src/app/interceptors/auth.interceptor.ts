import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const user = localStorage.getItem('currentUser');
  if (user) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${JSON.parse(user).token || ''}` }
    });
  }
  return next(req);
};

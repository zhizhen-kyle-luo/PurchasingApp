import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);
  
  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) {
        localStorage.removeItem('currentUser');
        window.location.href = '/login';
      } else if (error.status >= 500) {
        snackBar.open('Server error occurred', 'Close', { duration: 5000 });
      }
      return throwError(() => error);
    })
  );
};

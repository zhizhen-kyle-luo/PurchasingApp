import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of, map } from 'rxjs';

import { User, LoginRequest, RegisterRequest, AuthResponse, PasswordResetRequest, PasswordResetConfirm } from '../models/user.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadCurrentUser();
  }

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  get isAuthenticated(): boolean {
    return !!this.currentUser;
  }

  get isRequester(): boolean {
    return this.currentUser?.role === 'requester';
  }

  get isSublead(): boolean {
    return this.currentUser?.role === 'sublead';
  }

  get isExecutive(): boolean {
    return this.currentUser?.role === 'executive';
  }

  get isBusiness(): boolean {
    return this.currentUser?.role === 'business';
  }

  get canApproveOrders(): boolean {
    return this.isSublead || this.isExecutive;
  }

  get canManageOrders(): boolean {
    return this.isBusiness;
  }

  get canViewAllOrders(): boolean {
    return this.isExecutive || this.isBusiness;
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/login`, credentials)
      .pipe(
        tap((response: AuthResponse) => {
          if (response.success && response.user) {
            this.setCurrentUser(response.user);
          }
        }),
        catchError((error: any) => {
          console.error('Login error:', error);
          return of({ success: false, message: 'Login failed' });
        })
      );
  }

  register(userData: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/register`, userData)
      .pipe(
        tap((response: AuthResponse) => {
          if (response.success && response.user) {
            this.setCurrentUser(response.user);
          }
        }),
        catchError((error: any) => {
          console.error('Registration error:', error);
          return of({ success: false, message: 'Registration failed' });
        })
      );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.API_URL}/auth/logout`, {})
      .pipe(
        tap(() => {
          this.clearCurrentUser();
        }),
        catchError((error: any) => {
          console.error('Logout error:', error);
          this.clearCurrentUser(); // Clear user even if logout request fails
          return of({ success: true });
        })
      );
  }

  forgotPassword(request: PasswordResetRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/forgot-password`, request)
      .pipe(
        catchError((error: any) => {
          console.error('Forgot password error:', error);
          return of({ success: false, message: 'Failed to send reset email' });
        })
      );
  }

  resetPassword(request: PasswordResetConfirm): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/reset-password`, request)
      .pipe(
        catchError((error: any) => {
          console.error('Reset password error:', error);
          return of({ success: false, message: 'Failed to reset password' });
        })
      );
  }

  getCurrentUser(): Observable<{ success: boolean; user: User | null }> {
    return this.http.get<{ success: boolean; user: User }>(`${this.API_URL}/auth/me`)
      .pipe(
        tap((response: { success: boolean; user: User }) => {
          if (response.success && response.user) {
            this.setCurrentUser(response.user);
          }
        }),
        catchError((error: any) => {
          console.error('Get current user error:', error);
          this.clearCurrentUser();
          return of({ success: false, user: null });
        })
      );
  }

  updateProfile(userData: Partial<User>): Observable<AuthResponse> {
    return this.http.put<AuthResponse>(`${this.API_URL}/auth/me`, userData)
      .pipe(
        tap((response: AuthResponse) => {
          if (response.success && response.user) {
            this.setCurrentUser(response.user);
          }
        }),
        catchError((error: any) => {
          console.error('Update profile error:', error);
          return of({ success: false, message: 'Failed to update profile' });
        })
      );
  }

  checkPermissions(requiredRole?: string, requiredPermissions?: string[]): Observable<any> {
    const request = {
      role: requiredRole,
      permissions: requiredPermissions
    };

    return this.http.post(`${this.API_URL}/auth/check-permissions`, request)
      .pipe(
        catchError((error: any) => {
          console.error('Check permissions error:', error);
          return of({ success: false, has_permissions: false });
        })
      );
  }

  updateUserName(newName: string): Observable<User> {
    return this.updateProfile({ full_name: newName }).pipe(
      map((response: AuthResponse) => {
        if (!response.success || !response.user) {
          throw new Error(response.message || 'Failed to update name');
        }
        return response.user;
      })
    );
  }

  private setCurrentUser(user: User): void {
    localStorage.setItem('currentUser', JSON.stringify(user));
    this.currentUserSubject.next(user);
  }

  private clearCurrentUser(): void {
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  private loadCurrentUser(): void {
    const userJson = localStorage.getItem('currentUser');
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        this.currentUserSubject.next(user);
        
        // Verify user is still valid with server
        this.getCurrentUser().subscribe();
      } catch (error) {
        console.error('Error parsing stored user:', error);
        this.clearCurrentUser();
      }
    }
  }
}

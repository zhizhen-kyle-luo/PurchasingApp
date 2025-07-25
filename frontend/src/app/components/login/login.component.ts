import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, MatSnackBarModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-blue-500">
      <img src="assets/Motorsports Logo Words.png" alt="" class="background-logo">
      <div class="bg-white p-10 rounded-xl card-shadow w-96 transform transition-all hover:scale-[1.01]">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-4">Welcome Back! </h1>
          <a routerLink="/register" class="text-blue-500 hover:underline inline-flex items-center">
            Don't have an account? Sign up
            <span class="ml-1">→</span>
          </a>
        </div>
       
        <div *ngIf="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          {{ errorMessage }}
        </div>
       
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="space-y-5">
          <div class="space-y-1">
            <label class="block text-gray-700 text-sm font-semibold">MIT Email</label>
            <input type="email" formControlName="email" required
                   class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                   placeholder="username@mit.edu">
          </div>
         
          <div class="space-y-1">
            <label class="block text-gray-700 text-sm font-semibold">Password</label>
            <input type="password" formControlName="password" required
                   class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors">
          </div>

          <div class="flex items-center justify-between mt-4">
            <div class="flex items-center">
              <input type="checkbox" formControlName="remember" id="remember"
                     class="h-4 w-4 text-blue-500 border-gray-300 rounded focus:ring-blue-500">
              <label for="remember" class="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>
            <a routerLink="/forgot-password" class="text-sm text-blue-500 hover:underline">
              Forgot password?
            </a>
          </div>
         
          <button type="submit"
                  class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transform transition-all active:scale-[.98] font-medium mt-6"
                  [disabled]="loginForm.invalid || loading">
            {{ loading ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .card-shadow {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .background-logo {
        position: fixed;
        width: 1000px;
        height: auto;
        opacity: 0.1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 0;
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  loading = false;
  errorMessage: string | null = null;

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router, private snackBar: MatSnackBar) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      remember: [false]
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      this.loading = true;
      this.errorMessage = null;
      this.authService.login(this.loginForm.value).subscribe({
        next: (response) => {
          if (response.success) {
            this.router.navigate(['/dashboard']);
          } else {
            this.errorMessage = response.message;
          }
          this.loading = false;
        },
        error: (err) => {
          this.errorMessage = err.error?.message || 'Login failed due to a server error.';
          if (this.errorMessage) {
            this.snackBar.open(this.errorMessage, 'Close', { duration: 5000 });
          }
          this.loading = false;
        }
      });
    }
  }
}
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, MatSnackBarModule],
  template: `
    <img src="assets/Motorsports Logo Words.png" alt="" class="background-logo">
    <div class="bg-white p-10 rounded-xl card-shadow w-96 transform transition-all hover:scale-[1.01]">
      <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-4">Reset Password</h1>
          <p class="text-gray-600 mb-4">
            Enter your MIT email address and we'll send you instructions to reset your password.
          </p>
        </div>
        
        <div *ngIf="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          {{ errorMessage }}
        </div>

        <div *ngIf="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6">
          {{ successMessage }}
        </div>
        
        <form [formGroup]="forgotForm" (ngSubmit)="onSubmit()" class="space-y-5">
          <div class="space-y-1">
            <label class="block text-gray-700 text-sm font-semibold">MIT Email</label>
            <input type="email" formControlName="email" required 
                   class="form-input w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                   placeholder="username@mit.edu">
          </div>
          
          <button type="submit" 
                  class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transform transition-all active:scale-[.98] font-medium mt-6"
                  [disabled]="forgotForm.invalid || loading">
            {{ loading ? 'Sending...' : 'Send Reset Instructions' }}
          </button>
          
          <div class="text-center mt-4">
            <a routerLink="/login" class="text-blue-500 hover:underline inline-flex items-center">
              Back to Login
              <span class="ml-1">→</span>
            </a>
          </div>
        </form>
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
    .form-input {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.2s ease;
    }
    
    .form-input:focus {
        background-color: white !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
  `]
})
export class ForgotPasswordComponent {
  forgotForm: FormGroup;
  loading = false;
  errorMessage: string | null = null;
  successMessage: string | null = null;

  constructor(private fb: FormBuilder, private authService: AuthService, private snackBar: MatSnackBar) {
    this.forgotForm = this.fb.group({ email: ['', [Validators.required, Validators.email]] });
  }

  onSubmit() {
    if (this.forgotForm.valid) {
      this.loading = true;
      this.errorMessage = null;
      this.successMessage = null;
      this.authService.forgotPassword(this.forgotForm.value).subscribe({
        next: (response) => {
          if (response.success) {
            this.successMessage = response.message;
          } else {
            this.errorMessage = response.message;
          }
          this.snackBar.open(response.message, 'Close', { duration: 5000 });
          this.loading = false;
        },
        error: (err) => {
          this.errorMessage = err.error?.message || 'Failed to send reset email.';
          if (this.errorMessage) {
            this.snackBar.open(this.errorMessage, 'Close', { duration: 5000 });
          }
          this.loading = false;
        }
      });
    }
  }
}

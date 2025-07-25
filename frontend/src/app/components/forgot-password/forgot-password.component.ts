import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-blue-500">
      <img src="assets/Motorsports Logo Words.png" alt="" class="background-logo">
      <div class="bg-white p-10 rounded-xl card-shadow w-96 transform transition-all hover:scale-[1.01]">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-4">Forgot Password</h1>
          <a routerLink="/login" class="text-blue-500 hover:underline inline-flex items-center">
            Back to Login
            <span class="ml-1">→</span>
          </a>
        </div>
       
        <div *ngIf="message" class="px-4 py-3 rounded-lg mb-6" [ngClass]="{'bg-green-100 border border-green-400 text-green-700': !isError, 'bg-red-100 border border-red-400 text-red-700': isError}">
          {{ message }}
        </div>
       
        <form (ngSubmit)="onSubmit()" class="space-y-5">
          <div class="space-y-1">
            <label class="block text-gray-700 text-sm font-semibold">Email</label>
            <input type="email" name="email" [(ngModel)]="email" required
                   class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                   placeholder="email@example.com">
          </div>
         
          <button type="submit"
                  class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transform transition-all active:scale-[.98] font-medium mt-6">
            Send Reset Link
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
export class ForgotPasswordComponent {
  email: string = '';
  message: string = '';
  isError: boolean = false;

  constructor(private authService: AuthService, private router: Router) { }

  onSubmit() {
    this.authService.forgotPassword({ email: this.email }).subscribe(response => {
      if (response.success) {
        this.isError = false;
        this.message = 'A password reset link has been sent to your email.';
      } else {
        this.isError = true;
        this.message = response.message || 'Failed to send password reset email.';
      }
    });
  }
}
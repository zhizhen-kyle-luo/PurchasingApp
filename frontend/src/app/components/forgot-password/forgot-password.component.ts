import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <mat-card-header><mat-card-title>Reset Password</mat-card-title></mat-card-header>
        <mat-card-content>
          <form [formGroup]="forgotForm" (ngSubmit)="onSubmit()">
            <mat-form-field class="full-width">
              <mat-label>Email</mat-label>
              <input matInput type="email" formControlName="email" required>
            </mat-form-field>
            <button mat-raised-button color="primary" type="submit" class="full-width mt-2" [disabled]="forgotForm.invalid || loading">
              {{loading ? 'Sending...' : 'Send Reset Link'}}
            </button>
          </form>
        </mat-card-content>
        <mat-card-actions>
          <a mat-button routerLink="/login">Back to Login</a>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`.login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; } .login-card { width: 100%; max-width: 400px; }`]
})
export class ForgotPasswordComponent {
  forgotForm: FormGroup;
  loading = false;

  constructor(private fb: FormBuilder, private authService: AuthService, private snackBar: MatSnackBar) {
    this.forgotForm = this.fb.group({ email: ['', [Validators.required, Validators.email]] });
  }

  onSubmit() {
    if (this.forgotForm.valid) {
      this.loading = true;
      this.authService.forgotPassword(this.forgotForm.value).subscribe({
        next: (response) => {
          this.snackBar.open(response.message, 'Close', { duration: 5000 });
          this.loading = false;
        },
        error: () => {
          this.snackBar.open('Failed to send reset email', 'Close', { duration: 5000 });
          this.loading = false;
        }
      });
    }
  }
}

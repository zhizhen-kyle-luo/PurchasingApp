import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <mat-card-header><mat-card-title>Reset Password</mat-card-title></mat-card-header>
        <mat-card-content>
          <form [formGroup]="resetForm" (ngSubmit)="onSubmit()">
            <mat-form-field class="full-width">
              <mat-label>New Password</mat-label>
              <input matInput type="password" formControlName="password" required>
            </mat-form-field>
            <button mat-raised-button color="primary" type="submit" class="full-width mt-2" [disabled]="resetForm.invalid || loading">
              {{loading ? 'Resetting...' : 'Reset Password'}}
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`.login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; } .login-card { width: 100%; max-width: 400px; }`]
})
export class ResetPasswordComponent implements OnInit {
  resetForm: FormGroup;
  loading = false;
  token = '';

  constructor(private fb: FormBuilder, private authService: AuthService, private route: ActivatedRoute, private router: Router, private snackBar: MatSnackBar) {
    this.resetForm = this.fb.group({ password: ['', [Validators.required, Validators.minLength(6)]] });
  }

  ngOnInit() {
    this.token = this.route.snapshot.params['token'];
  }

  onSubmit() {
    if (this.resetForm.valid) {
      this.loading = true;
      this.authService.resetPassword({ token: this.token, password: this.resetForm.value.password }).subscribe({
        next: (response) => {
          if (response.success) {
            this.snackBar.open('Password reset successfully', 'Close', { duration: 3000 });
            this.router.navigate(['/login']);
          } else {
            this.snackBar.open(response.message, 'Close', { duration: 5000 });
          }
          this.loading = false;
        },
        error: () => {
          this.snackBar.open('Failed to reset password', 'Close', { duration: 5000 });
          this.loading = false;
        }
      });
    }
  }
}

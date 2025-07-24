import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss']
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

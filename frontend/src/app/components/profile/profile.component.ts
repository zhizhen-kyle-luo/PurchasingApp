import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `
    <div class="page-container">
      <mat-card>
        <mat-card-header><mat-card-title>Profile</mat-card-title></mat-card-header>
        <mat-card-content>
          <div *ngIf="authService.currentUser">
            <p><strong>Name:</strong> {{authService.currentUser.full_name}}</p>
            <p><strong>Email:</strong> {{authService.currentUser.email}}</p>
            <p><strong>Role:</strong> {{authService.currentUser.role}}</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `
})
export class ProfileComponent {
  constructor(public authService: AuthService) {}
}

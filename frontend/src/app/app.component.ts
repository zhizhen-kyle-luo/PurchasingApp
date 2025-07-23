import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatSidenav, MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';

import { AuthService } from './services/auth.service';
import { User } from './models/user.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatSidenavModule,
    MatListModule
  ],
  template: `
    <div class="app-container">
      <mat-toolbar color="primary" *ngIf="currentUser">
        <button mat-icon-button (click)="sidenav.toggle()" *ngIf="currentUser">
          <mat-icon>menu</mat-icon>
        </button>
        
        <span class="app-title">MIT Motorsports - Purchasing</span>
        
        <span class="spacer"></span>
        
        <button mat-button [matMenuTriggerFor]="userMenu" *ngIf="currentUser">
          <mat-icon>account_circle</mat-icon>
          {{ currentUser.full_name }}
        </button>
        
        <mat-menu #userMenu="matMenu">
          <button mat-menu-item (click)="goToProfile()">
            <mat-icon>person</mat-icon>
            Profile
          </button>
          <button mat-menu-item (click)="logout()">
            <mat-icon>logout</mat-icon>
            Logout
          </button>
        </mat-menu>
      </mat-toolbar>

      <mat-sidenav-container class="sidenav-container" *ngIf="currentUser">
        <mat-sidenav #sidenav mode="side" opened class="sidenav">
          <mat-nav-list>
            <a mat-list-item routerLink="/dashboard" routerLinkActive="active">
              <mat-icon matListItemIcon>dashboard</mat-icon>
              <span matListItemTitle>Dashboard</span>
            </a>
            
            <a mat-list-item routerLink="/purchases" routerLinkActive="active">
              <mat-icon matListItemIcon>shopping_cart</mat-icon>
              <span matListItemTitle>My Orders</span>
            </a>
            
            <a mat-list-item routerLink="/purchases/new" routerLinkActive="active">
              <mat-icon matListItemIcon>add_shopping_cart</mat-icon>
              <span matListItemTitle>New Order</span>
            </a>
            
            <div mat-subheader *ngIf="canApproveOrders">Management</div>
            
            <a mat-list-item routerLink="/purchases?filter=pending" routerLinkActive="active" *ngIf="canApproveOrders">
              <mat-icon matListItemIcon>approval</mat-icon>
              <span matListItemTitle>Pending Approvals</span>
            </a>
            
            <a mat-list-item routerLink="/purchases?filter=all" routerLinkActive="active" *ngIf="canViewAllOrders">
              <mat-icon matListItemIcon>list_alt</mat-icon>
              <span matListItemTitle>All Orders</span>
            </a>
          </mat-nav-list>
        </mat-sidenav>

        <mat-sidenav-content class="main-content">
          <router-outlet></router-outlet>
        </mat-sidenav-content>
      </mat-sidenav-container>

      <!-- Show router outlet without sidenav for login/register pages -->
      <div class="auth-container" *ngIf="!currentUser">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .app-container {
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .spacer {
      flex: 1 1 auto;
    }

    .app-title {
      font-weight: 500;
      font-size: 1.2em;
    }

    .sidenav-container {
      flex: 1;
    }

    .sidenav {
      width: 250px;
      background-color: #fafafa;
    }

    .main-content {
      padding: 20px;
      background-color: #f5f5f5;
      min-height: calc(100vh - 64px);
    }

    .auth-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .active {
      background-color: rgba(0, 0, 0, 0.04);
    }

    mat-list-item {
      margin-bottom: 4px;
    }
  `]
})
export class AppComponent implements OnInit {
  @ViewChild('sidenav') sidenav!: MatSidenav;
  currentUser: User | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (!user && !this.isAuthRoute()) {
        this.router.navigate(['/login']);
      }
    });
  }

  get canApproveOrders(): boolean {
    return this.currentUser?.role === 'sublead' || this.currentUser?.role === 'executive';
  }

  get canViewAllOrders(): boolean {
    return this.currentUser?.role === 'executive' || this.currentUser?.role === 'business';
  }

  goToProfile() {
    this.router.navigate(['/profile']);
  }

  logout() {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/login']);
    });
  }

  private isAuthRoute(): boolean {
    const authRoutes = ['/login', '/register', '/forgot-password'];
    return authRoutes.some(route => this.router.url.startsWith(route));
  }
}

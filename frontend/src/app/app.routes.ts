import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('./components/forgot-password/forgot-password.component').then(m => m.ForgotPasswordComponent)
  },
  {
    path: 'reset-password/:token',
    loadComponent: () => import('./components/reset-password/reset-password.component').then(m => m.ResetPasswordComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'purchases',
    loadComponent: () => import('./components/purchase-list/purchase-list.component').then(m => m.PurchaseListComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'purchases/new',
    loadComponent: () => import('./components/purchase-form/purchase-form.component').then(m => m.PurchaseFormComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'new-purchase',
    loadComponent: () => import('./components/new-order/new-order.component').then(m => m.NewOrderComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'purchases/:id',
    loadComponent: () => import('./components/purchase-detail/purchase-detail.component').then(m => m.PurchaseDetailComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./components/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [AuthGuard]
  },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];

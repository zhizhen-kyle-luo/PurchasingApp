import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatGridListModule } from '@angular/material/grid-list';
import { PurchaseService } from '../../services/purchase.service';
import { AuthService } from '../../services/auth.service';
import { Purchase, PurchaseStatistics } from '../../models/purchase.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatGridListModule],
  template: `
    <div class="page-container">
      <h1>Dashboard</h1>
      <mat-grid-list cols="4" rowHeight="120px" gutterSize="16px">
        <mat-grid-tile><mat-card><mat-card-content><h3>{{stats.total_orders}}</h3><p>Total Orders</p></mat-card-content></mat-card></mat-grid-tile>
        <mat-grid-tile><mat-card><mat-card-content><h3>{{stats.pending_approval}}</h3><p>Pending Approval</p></mat-card-content></mat-card></mat-grid-tile>
        <mat-grid-tile><mat-card><mat-card-content><h3>{{stats.purchased_orders}}</h3><p>Purchased</p></mat-card-content></mat-card></mat-grid-tile>
        <mat-grid-tile><mat-card><mat-card-content><h3>\${{stats.total_value | number:'1.2-2'}}</h3><p>Total Value</p></mat-card-content></mat-card></mat-grid-tile>
      </mat-grid-list>
      
      <div class="actions mt-3">
        <button mat-raised-button color="primary" routerLink="/purchases/new">
          <mat-icon>add</mat-icon> New Purchase
        </button>
        <button mat-raised-button routerLink="/purchases">
          <mat-icon>list</mat-icon> View All Orders
        </button>
      </div>

      <mat-card class="mt-3" *ngIf="recentPurchases.length">
        <mat-card-header><mat-card-title>Recent Orders</mat-card-title></mat-card-header>
        <mat-card-content>
          <div *ngFor="let purchase of recentPurchases" class="purchase-item">
            <span>{{purchase.item_name}}</span>
            <span class="status-chip" [ngClass]="purchase.status.toLowerCase()">{{purchase.status}}</span>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .actions { display: flex; gap: 16px; }
    .purchase-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
  `]
})
export class DashboardComponent implements OnInit {
  stats: PurchaseStatistics = { total_orders: 0, pending_approval: 0, approved_orders: 0, purchased_orders: 0, shipped_orders: 0, arrived_orders: 0, total_value: 0 };
  recentPurchases: Purchase[] = [];

  constructor(private purchaseService: PurchaseService, public authService: AuthService) {}

  ngOnInit() {
    this.loadStatistics();
    this.loadRecentPurchases();
  }

  loadStatistics() {
    this.purchaseService.getStatistics().subscribe(response => {
      if (response.success) this.stats = response.statistics;
    });
  }

  loadRecentPurchases() {
    this.purchaseService.getPurchases({}, 1, 5).subscribe(response => {
      if (response.success) this.recentPurchases = response.purchases;
    });
  }
}

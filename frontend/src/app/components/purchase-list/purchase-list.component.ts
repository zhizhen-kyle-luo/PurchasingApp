import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { PurchaseService } from '../../services/purchase.service';
import { AuthService } from '../../services/auth.service';
import { Purchase, PurchaseFilters } from '../../models/purchase.model';

@Component({
  selector: 'app-purchase-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, MatTableModule, MatButtonModule, MatIconModule, MatChipsModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  template: `
    <div class="page-container">
      <div class="header">
        <h1>Purchase Orders</h1>
        <button mat-raised-button color="primary" routerLink="/purchases/new">
          <mat-icon>add</mat-icon> New Order
        </button>
      </div>

      <div class="filters">
        <mat-form-field>
          <mat-label>Search</mat-label>
          <input matInput [(ngModel)]="filters.search" (keyup.enter)="loadPurchases()">
        </mat-form-field>
        <mat-form-field>
          <mat-label>Status</mat-label>
          <mat-select [(ngModel)]="filters.status" (selectionChange)="loadPurchases()">
            <mat-option value="">All</mat-option>
            <mat-option value="Not Yet Purchased">Not Purchased</mat-option>
            <mat-option value="Purchased">Purchased</mat-option>
            <mat-option value="Shipped">Shipped</mat-option>
            <mat-option value="Arrived">Arrived</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <mat-table [dataSource]="purchases" class="mat-elevation-z8">
        <ng-container matColumnDef="item_name">
          <mat-header-cell *matHeaderCellDef>Item</mat-header-cell>
          <mat-cell *matCellDef="let purchase">{{purchase.item_name}}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="vendor_name">
          <mat-header-cell *matHeaderCellDef>Vendor</mat-header-cell>
          <mat-cell *matCellDef="let purchase">{{purchase.vendor_name}}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="total_cost">
          <mat-header-cell *matHeaderCellDef>Total</mat-header-cell>
          <mat-cell *matCellDef="let purchase">\${{purchase.total_cost | number:'1.2-2'}}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="status">
          <mat-header-cell *matHeaderCellDef>Status</mat-header-cell>
          <mat-cell *matCellDef="let purchase">
            <mat-chip [ngClass]="purchase.status.toLowerCase().replace(' ', '-')">{{purchase.status}}</mat-chip>
          </mat-cell>
        </ng-container>
        <ng-container matColumnDef="urgency">
          <mat-header-cell *matHeaderCellDef>Urgency</mat-header-cell>
          <mat-cell *matCellDef="let purchase">
            <mat-chip [ngClass]="purchase.urgency.toLowerCase()">{{purchase.urgency}}</mat-chip>
          </mat-cell>
        </ng-container>
        <ng-container matColumnDef="actions">
          <mat-header-cell *matHeaderCellDef>Actions</mat-header-cell>
          <mat-cell *matCellDef="let purchase">
            <button mat-icon-button [routerLink]="['/purchases', purchase.id]">
              <mat-icon>visibility</mat-icon>
            </button>
            <button mat-icon-button *ngIf="canApprove(purchase)" (click)="approve(purchase.id)">
              <mat-icon>check</mat-icon>
            </button>
          </mat-cell>
        </ng-container>
        <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
        <mat-row *matRowDef="let row; columns: displayedColumns;"></mat-row>
      </mat-table>
    </div>
  `,
  styles: [`
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .filters { display: flex; gap: 16px; margin-bottom: 20px; }
  `]
})
export class PurchaseListComponent implements OnInit {
  purchases: Purchase[] = [];
  filters: PurchaseFilters = {};
  displayedColumns = ['item_name', 'vendor_name', 'total_cost', 'status', 'urgency', 'actions'];

  constructor(private purchaseService: PurchaseService, public authService: AuthService) {}

  ngOnInit() {
    this.loadPurchases();
  }

  loadPurchases() {
    this.purchaseService.getPurchases(this.filters).subscribe(response => {
      if (response.success) this.purchases = response.purchases;
    });
  }

  canApprove(purchase: Purchase): boolean {
    return this.authService.canApproveOrders && purchase.is_pending_approval;
  }

  approve(id: number) {
    this.purchaseService.approvePurchase(id).subscribe(() => this.loadPurchases());
  }
}

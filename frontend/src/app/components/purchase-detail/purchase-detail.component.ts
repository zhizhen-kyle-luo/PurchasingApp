import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { PurchaseService } from '../../services/purchase.service';
import { Purchase } from '../../models/purchase.model';

@Component({
  selector: 'app-purchase-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatChipsModule],
  template: `
    <div class="page-container" *ngIf="purchase">
      <mat-card>
        <mat-card-header>
          <mat-card-title>{{purchase.item_name}}</mat-card-title>
          <mat-card-subtitle>Order #{{purchase.id}}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div class="detail-grid">
            <div><strong>Vendor:</strong> {{purchase.vendor_name}}</div>
            <div><strong>Price:</strong> \${{purchase.price | number:'1.2-2'}}</div>
            <div><strong>Shipping:</strong> \${{purchase.shipping_cost | number:'1.2-2'}}</div>
            <div><strong>Total:</strong> \${{purchase.total_cost | number:'1.2-2'}}</div>
            <div><strong>Quantity:</strong> {{purchase.quantity}}</div>
            <div><strong>Subteam:</strong> {{purchase.subteam}}</div>
            <div><strong>Requester:</strong> {{purchase.requester_name}}</div>
            <div><strong>Status:</strong> <mat-chip [ngClass]="purchase.status.toLowerCase()">{{purchase.status}}</mat-chip></div>
            <div><strong>Approval:</strong> <mat-chip [ngClass]="purchase.approval_status.toLowerCase()">{{purchase.approval_status}}</mat-chip></div>
            <div><strong>Urgency:</strong> <mat-chip [ngClass]="purchase.urgency.toLowerCase()">{{purchase.urgency}}</mat-chip></div>
          </div>
          <div *ngIf="purchase.purpose" class="mt-2">
            <strong>Purpose:</strong>
            <p>{{purchase.purpose}}</p>
          </div>
          <div *ngIf="purchase.notes" class="mt-2">
            <strong>Notes:</strong>
            <p>{{purchase.notes}}</p>
          </div>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button routerLink="/purchases">Back to List</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }`]
})
export class PurchaseDetailComponent implements OnInit {
  purchase: Purchase | null = null;

  constructor(private route: ActivatedRoute, private purchaseService: PurchaseService) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.params['id']);
    this.purchaseService.getPurchase(id).subscribe(response => {
      if (response.success) this.purchase = response.purchase;
    });
  }
}

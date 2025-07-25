import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Purchase } from '../../models/purchase.model';

@Component({
  selector: 'app-order-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './order-card.component.html',
  styleUrls: ['./order-card.component.scss']
})
export class OrderCardComponent {
  @Input() order!: Purchase;
  @Output() cardClick = new EventEmitter<Purchase>();

  showOrderDetails() {
    this.cardClick.emit(this.order);
  }

  getStatusBadgeClass(): string {
    if (this.order.status === 'Arrived') return 'status-arrived';
    if (this.order.status === 'Shipped') return 'status-shipped';
    if (this.order.status === 'Purchased') return 'status-purchased';
    if (this.order.approval_status === 'Fully Approved') return 'status-approved';
    if (this.order.approval_status === 'Pending Executive Approval') return 'status-pending-exec';
    if (this.order.approval_status === 'Pending Sublead Approval') return 'status-pending-sublead';
    return 'status-default';
  }

  getUrgencyBadgeClass(): string {
    if (this.order.urgency === 'Both' || this.order.urgency === 'Urgent') return 'urgency-urgent';
    if (this.order.urgency === 'Special/Large') return 'urgency-special';
    return 'urgency-normal';
  }

  getTotalCost(): number {
    return (this.order.price || 0) + (this.order.shipping_cost || 0);
  }
}

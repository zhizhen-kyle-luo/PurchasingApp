import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Purchase } from '../../models/purchase.model';
import { AuthService } from '../../services/auth.service';
import { PurchaseService } from '../../services/purchase.service';

@Component({
  selector: 'app-order-details-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './order-details-modal.component.html',
  styleUrls: ['./order-details-modal.component.scss']
})
export class OrderDetailsModalComponent {
  @Input() order: Purchase | null = null;
  @Input() showModal: boolean = false;
  @Output() closeModalEvent = new EventEmitter();
  @Output() orderUpdated = new EventEmitter();

  selectedFile: File | null = null;

  constructor(public authService: AuthService, private purchaseService: PurchaseService) { }

  closeModal() {
    this.closeModalEvent.emit();
  }

  deleteOrder() {
    if (this.order) {
      this.purchaseService.deletePurchase(this.order.id).subscribe(() => {
        this.orderUpdated.emit();
        this.closeModal();
      });
    }
  }

  restoreOrder() {
    if (this.order) {
      this.purchaseService.restorePurchase(this.order.id).subscribe(() => {
        this.orderUpdated.emit();
        this.closeModal();
      });
    }
  }

  approveOrder() {
    if (this.order) {
      this.purchaseService.approvePurchase(this.order.id).subscribe(() => {
        this.orderUpdated.emit();
        this.closeModal();
      });
    }
  }

  markAsPurchased() {
    if (this.order) {
      this.purchaseService.updatePurchaseStatus(this.order.id, 'Purchased').subscribe(() => {
        this.orderUpdated.emit();
        this.closeModal();
      });
    }
  }

  markAsShipped() {
    if (this.order) {
      this.purchaseService.updatePurchaseStatus(this.order.id, 'Shipped').subscribe(() => {
        this.orderUpdated.emit();
        this.closeModal();
      });
    }
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  markAsArrived() {
    if (this.order && this.selectedFile) {
      this.purchaseService.uploadFile(this.selectedFile).subscribe(response => {
        if (response.success && response.filename) {
          this.purchaseService.updatePurchaseStatus(this.order!.id, 'Arrived', response.filename).subscribe(() => {
            this.orderUpdated.emit();
            this.closeModal();
          });
        }
      });
    }
  }
}

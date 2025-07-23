import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Purchase } from '../../models/purchase.model';

@Component({
  selector: 'app-order-card',
  templateUrl: './order-card.component.html',
  styleUrls: ['./order-card.component.scss']
})
export class OrderCardComponent {
  @Input() order!: Purchase;
  @Output() cardClick = new EventEmitter<Purchase>();

  showOrderDetails() {
    this.cardClick.emit(this.order);
  }
}

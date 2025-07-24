import { Component, Input, Output, EventEmitter } from "@angular/core";
import {
  CommonModule,
  CurrencyPipe,
  DatePipe,
  NgIf,
  NgClass,
} from "@angular/common";

@Component({
  selector: "app-order-card",
  standalone: true,
  imports: [CommonModule, CurrencyPipe, DatePipe, NgIf, NgClass],
  templateUrl: "./order-card.component.html",
  styleUrls: ["./order-card.component.scss"],
})
export class OrderCardComponent {
  @Input() order: any;
  @Output() cardClick = new EventEmitter<any>();

  showOrderDetails() {
    this.cardClick.emit(this.order);
  }
}

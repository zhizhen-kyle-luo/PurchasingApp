import { Component, OnInit } from '@angular/core';
import { Purchase } from '../../models/purchase.model';
import { PurchaseService } from '../../services/purchase.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  currentView: string = 'myCurrentOrders';
  title: string = 'My Current Orders';
  myCurrentOrders: Purchase[] = [];
  allCurrentOrders: Purchase[] = [];
  allPastOrders: Purchase[] = [];
  selectedOrder: Purchase | null = null;
  showModal: boolean = false;

  constructor(private purchaseService: PurchaseService, private authService: AuthService) { }

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.purchaseService.getPurchases().subscribe(response => {
      if (response.success) {
        const currentUser = this.authService.currentUser;
        if (currentUser) {
          this.myCurrentOrders = response.purchases.filter(p => p.status !== 'Arrived' && p.user_id === currentUser.id);
        }
        this.allCurrentOrders = response.purchases.filter(p => p.status !== 'Arrived');
        this.allPastOrders = response.purchases.filter(p => p.status === 'Arrived');
      }
    });
  }

  onViewChanged(view: string): void {
    this.currentView = view;
    if (view === 'myCurrentOrders') {
      this.title = 'My Current Orders';
    } else if (view === 'allCurrentOrders') {
      this.title = 'All Current Orders';
    } else if (view === 'allPastOrders') {
      this.title = 'All Past Orders';
    }
  }

  showOrderDetails(order: Purchase): void {
    this.selectedOrder = order;
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.selectedOrder = null;
  }
}

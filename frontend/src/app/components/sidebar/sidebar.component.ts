import { Component, EventEmitter, Output } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  @Output() viewChanged = new EventEmitter<string>();

  constructor(private authService: AuthService) { }

  showMyCurrentOrders() {
    this.viewChanged.emit('myCurrentOrders');
  }

  showAllCurrentOrders() {
    this.viewChanged.emit('allCurrentOrders');
  }

  showAllPastOrders() {
    this.viewChanged.emit('allPastOrders');
  }

  showNameChangeModal() {
    // Implement name change modal logic
  }

  logout() {
    this.authService.logout();
  }
}

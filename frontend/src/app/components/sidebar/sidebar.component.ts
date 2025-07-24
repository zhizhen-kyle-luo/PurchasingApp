import { Component, EventEmitter, Output } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { AuthService } from "../../services/auth.service";
import { ChangeNameModalComponent } from "../change-name-modal/change-name-modal.component";
import { User } from "../../models/user.model";

@Component({
  selector: "app-sidebar",
  standalone: true,
  imports: [CommonModule, RouterModule, ChangeNameModalComponent],
  templateUrl: "./sidebar.component.html",
  styleUrls: ["./sidebar.component.scss"],
})
export class SidebarComponent {
  @Output() viewChanged = new EventEmitter<string>();

  showChangeNameModal = false;
  activeView = "myCurrentOrders";
  currentUser: User | null = null;

  constructor(private authService: AuthService) {
    this.currentUser = this.authService.currentUser;
  }

  setActiveView(view: string) {
    this.activeView = view;
    this.viewChanged.emit(view);
  }

  showMyCurrentOrders() {
    this.setActiveView("myCurrentOrders");
  }

  showAllCurrentOrders() {
    this.setActiveView("allCurrentOrders");
  }

  showAllPastOrders() {
    this.setActiveView("allPastOrders");
  }

  showNameChangeModal() {
    this.showChangeNameModal = true;
  }

  closeChangeNameModal() {
    this.showChangeNameModal = false;
  }

  onNameUpdated(newName: string) {
    // Update the current user's name in the local reference
    if (this.currentUser) {
      this.currentUser.full_name = newName;
    }
  }

  logout() {
    this.authService.logout();
  }
}

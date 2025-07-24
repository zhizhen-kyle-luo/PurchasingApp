import { Component, Input, Output, EventEmitter } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";

@Component({
  selector: "app-change-name-modal",
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: "./change-name-modal.component.html",
  styleUrls: ["./change-name-modal.component.scss"],
})
export class ChangeNameModalComponent {
  @Input() showModal = false;
  @Output() closeModalEvent = new EventEmitter<void>();
  @Output() nameUpdated = new EventEmitter<string>();

  newName = "";

  closeModal() {
    this.closeModalEvent.emit();
    this.newName = "";
  }

  updateName() {
    if (this.newName.trim()) {
      this.nameUpdated.emit(this.newName.trim());
    }
    this.closeModal();
  }
}

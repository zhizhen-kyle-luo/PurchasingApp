import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-change-name-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './change-name-modal.component.html',
  styleUrls: ['./change-name-modal.component.scss']
})
export class ChangeNameModalComponent {
  @Input() showModal = false;
  @Output() closeModalEvent = new EventEmitter<void>();
  @Output() nameUpdated = new EventEmitter<string>();
  
  newName = '';
  isLoading = false;
  errorMessage = '';

  constructor(private authService: AuthService) {}

  closeModal() {
    this.closeModalEvent.emit();
    this.newName = '';
    this.errorMessage = '';
  }

  updateName() {
    if (!this.newName.trim()) {
      this.errorMessage = 'Name cannot be empty';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.updateUserName(this.newName.trim()).subscribe({
      next: (user) => {
        this.isLoading = false;
        this.nameUpdated.emit(user.full_name);
        this.closeModal();
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Failed to update name';
      }
    });
  }
}

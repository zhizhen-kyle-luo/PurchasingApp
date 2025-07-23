import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

@Component({
  selector: 'app-alert',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="alertClasses" role="alert">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg [class]="iconClasses" fill="currentColor" viewBox="0 0 20 20">
            <!-- Info icon -->
            <path *ngIf="variant === 'info'" fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
            <!-- Success icon -->
            <path *ngIf="variant === 'success'" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            <!-- Warning icon -->
            <path *ngIf="variant === 'warning'" fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            <!-- Error icon -->
            <path *ngIf="variant === 'error'" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <h3 *ngIf="title" [class]="titleClasses">{{ title }}</h3>
          <div [class]="messageClasses">
            <ng-content></ng-content>
          </div>
        </div>
        <div *ngIf="dismissible" class="ml-auto pl-3">
          <button
            type="button"
            [class]="closeButtonClasses"
            (click)="onDismiss()"
          >
            <span class="sr-only">Dismiss</span>
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class AlertComponent {
  @Input() variant: AlertVariant = 'info';
  @Input() title?: string;
  @Input() dismissible = false;
  @Output() dismiss = new EventEmitter<void>();

  get alertClasses(): string {
    const baseClasses = 'p-4 rounded-lg border';
    const variantClasses = {
      info: 'bg-blue-50 border-blue-200 text-blue-800',
      success: 'bg-green-50 border-green-200 text-green-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      error: 'bg-red-50 border-red-200 text-red-800'
    };
    return `${baseClasses} ${variantClasses[this.variant]}`;
  }

  get iconClasses(): string {
    const baseClasses = 'h-5 w-5';
    const variantClasses = {
      info: 'text-blue-400',
      success: 'text-green-400',
      warning: 'text-yellow-400',
      error: 'text-red-400'
    };
    return `${baseClasses} ${variantClasses[this.variant]}`;
  }

  get titleClasses(): string {
    const variantClasses = {
      info: 'text-blue-800',
      success: 'text-green-800',
      warning: 'text-yellow-800',
      error: 'text-red-800'
    };
    return `text-sm font-medium ${variantClasses[this.variant]}`;
  }

  get messageClasses(): string {
    const baseClasses = 'text-sm';
    const titleSpacing = this.title ? 'mt-1' : '';
    return `${baseClasses} ${titleSpacing}`;
  }

  get closeButtonClasses(): string {
    const variantClasses = {
      info: 'text-blue-400 hover:text-blue-600',
      success: 'text-green-400 hover:text-green-600',
      warning: 'text-yellow-400 hover:text-yellow-600',
      error: 'text-red-400 hover:text-red-600'
    };
    return `inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${variantClasses[this.variant]}`;
  }

  onDismiss(): void {
    this.dismiss.emit();
  }
}

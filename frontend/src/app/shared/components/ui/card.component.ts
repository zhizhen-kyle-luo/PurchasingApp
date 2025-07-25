import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="cardClasses">
      <div *ngIf="title || subtitle" class="card-header mb-6">
        <h3 *ngIf="title" class="text-lg font-semibold text-gray-900 mb-1">{{ title }}</h3>
        <p *ngIf="subtitle" class="text-sm text-gray-600">{{ subtitle }}</p>
      </div>
      <div class="card-content">
        <ng-content></ng-content>
      </div>
      <div *ngIf="hasFooter" class="card-footer mt-6 pt-6 border-t border-gray-200">
        <ng-content select="[slot=footer]"></ng-content>
      </div>
    </div>
  `,
  styles: []
})
export class CardComponent {
  @Input() title?: string;
  @Input() subtitle?: string;
  @Input() padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
  @Input() shadow: 'none' | 'sm' | 'md' | 'lg' = 'md';
  @Input() hasFooter = false;

  get cardClasses(): string {
    const baseClasses = 'bg-white rounded-xl border border-gray-200';
    
    const paddingClasses = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8'
    };

    const shadowClasses = {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow-md',
      lg: 'shadow-lg'
    };

    return `${baseClasses} ${paddingClasses[this.padding]} ${shadowClasses[this.shadow]}`.trim();
  }
}

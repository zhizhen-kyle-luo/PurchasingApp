import { Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
export type InputSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-input',
  standalone: true,
  imports: [CommonModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true
    }
  ],
  template: `
    <div class="input-group">
      <label *ngIf="label" [for]="inputId" [class]="labelClasses">
        {{ label }}
        <span *ngIf="required" class="text-red-500 ml-1">*</span>
      </label>
      <div class="relative">
        <input
          [id]="inputId"
          [type]="type"
          [placeholder]="placeholder"
          [disabled]="disabled"
          [readonly]="readonly"
          [class]="inputClasses"
          [value]="value"
          (input)="onInput($event)"
          (blur)="onBlur()"
          (focus)="onFocus()"
        />
        <div *ngIf="error" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
      <p *ngIf="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
      <p *ngIf="hint && !error" class="mt-1 text-sm text-gray-500">{{ hint }}</p>
    </div>
  `,
  styles: [`
    .input-group {
      @apply w-full;
    }
  `]
})
export class InputComponent implements ControlValueAccessor {
  @Input() label?: string;
  @Input() type: InputType = 'text';
  @Input() size: InputSize = 'md';
  @Input() placeholder = '';
  @Input() disabled = false;
  @Input() readonly = false;
  @Input() required = false;
  @Input() error?: string;
  @Input() hint?: string;
  @Input() inputId = `input-${Math.random().toString(36).substr(2, 9)}`;

  @Output() valueChange = new EventEmitter<string>();
  @Output() inputFocus = new EventEmitter<void>();
  @Output() inputBlur = new EventEmitter<void>();

  value = '';
  private onChange = (value: string) => {};
  private onTouched = () => {};

  get labelClasses(): string {
    return 'block text-sm font-medium text-gray-700 mb-1';
  }

  get inputClasses(): string {
    const baseClasses = 'block w-full rounded-lg border transition-colors duration-200 focus:outline-none focus:ring-4';
    
    const sizeClasses = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-2.5 text-sm',
      lg: 'px-4 py-3 text-base'
    };

    const stateClasses = this.error
      ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-200'
      : 'border-gray-300 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-200';

    const disabledClasses = this.disabled
      ? 'bg-gray-50 text-gray-500 cursor-not-allowed'
      : 'bg-white hover:border-gray-400';

    return `${baseClasses} ${sizeClasses[this.size]} ${stateClasses} ${disabledClasses}`.trim();
  }

  onInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.value = target.value;
    this.onChange(this.value);
    this.valueChange.emit(this.value);
  }

  onFocus(): void {
    this.inputFocus.emit();
  }

  onBlur(): void {
    this.onTouched();
    this.inputBlur.emit();
  }

  // ControlValueAccessor implementation
  writeValue(value: string): void {
    this.value = value || '';
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PurchaseService } from '../../services/purchase.service';
import { AuthService } from '../../services/auth.service';
import { SUBTEAM_OPTIONS, SUBPROJECT_OPTIONS } from '../../models/purchase.model';

@Component({
  selector: 'app-purchase-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule],
  template: `
    <div class="page-container">
      <mat-card>
        <mat-card-header><mat-card-title>New Purchase Request</mat-card-title></mat-card-header>
        <mat-card-content>
          <form [formGroup]="purchaseForm" (ngSubmit)="onSubmit()">
            <div class="form-row">
              <mat-form-field class="full-width">
                <mat-label>Item Name</mat-label>
                <textarea matInput formControlName="item_name" rows="2" required></textarea>
              </mat-form-field>
            </div>
            <div class="form-row">
              <mat-form-field>
                <mat-label>Vendor</mat-label>
                <input matInput formControlName="vendor_name" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Item Link</mat-label>
                <input matInput formControlName="item_link" type="url">
              </mat-form-field>
            </div>
            <div class="form-row">
              <mat-form-field>
                <mat-label>Price ($)</mat-label>
                <input matInput formControlName="price" type="number" step="0.01" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Shipping Cost ($)</mat-label>
                <input matInput formControlName="shipping_cost" type="number" step="0.01">
              </mat-form-field>
              <mat-form-field>
                <mat-label>Quantity</mat-label>
                <input matInput formControlName="quantity" type="number" min="1">
              </mat-form-field>
            </div>
            <div class="form-row">
              <mat-form-field>
                <mat-label>Subteam</mat-label>
                <mat-select formControlName="subteam" (selectionChange)="onSubteamChange()" required>
                  <mat-option *ngFor="let team of subteams" [value]="team">{{team}}</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Subproject</mat-label>
                <mat-select formControlName="subproject">
                  <mat-option *ngFor="let project of subprojects" [value]="project">{{project}}</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Urgency</mat-label>
                <mat-select formControlName="urgency">
                  <mat-option value="Neither">Neither</mat-option>
                  <mat-option value="Urgent">Urgent</mat-option>
                  <mat-option value="Special/Large">Special/Large</mat-option>
                  <mat-option value="Both">Both</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
            <mat-form-field class="full-width">
              <mat-label>Purpose</mat-label>
              <textarea matInput formControlName="purpose" rows="3"></textarea>
            </mat-form-field>
            <mat-form-field class="full-width">
              <mat-label>Notes</mat-label>
              <textarea matInput formControlName="notes" rows="2"></textarea>
            </mat-form-field>
          </form>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="onSubmit()" [disabled]="purchaseForm.invalid || loading">
            {{loading ? 'Creating...' : 'Create Purchase'}}
          </button>
          <button mat-button (click)="cancel()">Cancel</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .form-row { display: flex; gap: 16px; }
    .form-row mat-form-field { flex: 1; }
  `]
})
export class PurchaseFormComponent implements OnInit {
  purchaseForm: FormGroup;
  loading = false;
  subteams = SUBTEAM_OPTIONS;
  subprojects: string[] = [];

  constructor(private fb: FormBuilder, private purchaseService: PurchaseService, private authService: AuthService, private router: Router, private snackBar: MatSnackBar) {
    this.purchaseForm = this.fb.group({
      item_name: ['', Validators.required],
      vendor_name: ['', Validators.required],
      item_link: [''],
      price: [0, [Validators.required, Validators.min(0)]],
      shipping_cost: [0, Validators.min(0)],
      quantity: [1, [Validators.required, Validators.min(1)]],
      subteam: ['', Validators.required],
      subproject: [''],
      urgency: ['Neither'],
      purpose: [''],
      notes: [''],
      requester_name: [''],
      requester_email: ['']
    });
  }

  ngOnInit() {
    const user = this.authService.currentUser;
    if (user) {
      this.purchaseForm.patchValue({
        requester_name: user.full_name,
        requester_email: user.email
      });
    }
  }

  onSubteamChange() {
    const subteam = this.purchaseForm.get('subteam')?.value;
    this.subprojects = SUBPROJECT_OPTIONS[subteam] || [];
    this.purchaseForm.get('subproject')?.setValue('');
  }

  onSubmit() {
    if (this.purchaseForm.valid) {
      this.loading = true;
      this.purchaseService.createPurchase(this.purchaseForm.value).subscribe({
        next: (response) => {
          if (response.success) {
            this.snackBar.open('Purchase created successfully', 'Close', { duration: 3000 });
            this.router.navigate(['/purchases']);
          } else {
            this.snackBar.open(response.message, 'Close', { duration: 5000 });
          }
          this.loading = false;
        },
        error: () => {
          this.snackBar.open('Failed to create purchase', 'Close', { duration: 5000 });
          this.loading = false;
        }
      });
    }
  }

  cancel() {
    this.router.navigate(['/purchases']);
  }
}

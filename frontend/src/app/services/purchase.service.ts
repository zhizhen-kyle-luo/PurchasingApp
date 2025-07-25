import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';

import { 
  Purchase, 
  CreatePurchaseRequest, 
  PurchaseFilters, 
  PurchaseListResponse, 
  PurchaseResponse,
  PurchaseStatistics 
} from '../models/purchase.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  private readonly API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPurchases(filters?: PurchaseFilters, page: number = 1, perPage: number = 20): Observable<PurchaseListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    if (filters) {
      if (filters.status) {
        params = params.set('status', filters.status);
      }
      if (filters.approval_status) {
        params = params.set('approval_status', filters.approval_status);
      }
      if (filters.subteam) {
        params = params.set('subteam', filters.subteam);
      }
      if (filters.search) {
        params = params.set('search', filters.search);
      }
      if (filters.include_deleted !== undefined) {
        params = params.set('include_deleted', filters.include_deleted.toString());
      }
    }

    return this.http.get<PurchaseListResponse>(`${this.API_URL}/api/purchases`, { params })
      .pipe(
        catchError(error => {
          console.error('Get purchases error:', error);
          return of({
            success: false,
            purchases: [],
            pagination: { page: 1, per_page: perPage, total: 0, pages: 0 }
          });
        })
      );
  }

  getPurchase(id: number): Observable<{ success: boolean; purchase: Purchase }> {
    return this.http.get<{ success: boolean; purchase: Purchase }>(`${this.API_URL}/api/purchases/${id}`)
      .pipe(
        catchError(error => {
          console.error('Get purchase error:', error);
          return of({ success: false, purchase: null as any });
        })
      );
  }

  createPurchase(purchaseData: CreatePurchaseRequest): Observable<PurchaseResponse> {
    return this.http.post<PurchaseResponse>(`${this.API_URL}/api/purchases`, purchaseData)
      .pipe(
        catchError(error => {
          console.error('Create purchase error:', error);
          return of({ success: false, message: 'Failed to create purchase' });
        })
      );
  }

  approvePurchase(id: number, reason?: string): Observable<{ success: boolean; message: string }> {
    const body = reason ? { reason } : {};
    return this.http.post<{ success: boolean; message: string }>(`${this.API_URL}/api/purchases/${id}/approve`, body)
      .pipe(
        catchError(error => {
          console.error('Approve purchase error:', error);
          return of({ success: false, message: 'Failed to approve purchase' });
        })
      );
  }

  rejectPurchase(id: number, reason?: string): Observable<{ success: boolean; message: string }> {
    const body = reason ? { reason } : {};
    return this.http.post<{ success: boolean; message: string }>(`${this.API_URL}/api/purchases/${id}/reject`, body)
      .pipe(
        catchError(error => {
          console.error('Reject purchase error:', error);
          return of({ success: false, message: 'Failed to reject purchase' });
        })
      );
  }

  updatePurchaseStatus(id: number, status: string, photoFilename?: string): Observable<{ success: boolean; message: string }> {
    const body: any = { status };
    if (photoFilename) {
      body.photo_filename = photoFilename;
    }

    return this.http.put<{ success: boolean; message: string }>(`${this.API_URL}/api/purchases/${id}/status`, body)
      .pipe(
        catchError(error => {
          console.error('Update purchase status error:', error);
          return of({ success: false, message: 'Failed to update purchase status' });
        })
      );
  }

  deletePurchase(id: number): Observable<{ success: boolean; message: string }> {
    return this.http.delete<{ success: boolean; message: string }>(`${this.API_URL}/api/purchases/${id}`)
      .pipe(
        catchError(error => {
          console.error('Delete purchase error:', error);
          return of({ success: false, message: 'Failed to delete purchase' });
        })
      );
  }

  restorePurchase(id: number): Observable<{ success: boolean; message: string }> {
    return this.http.post<{ success: boolean; message: string }>(`${this.API_URL}/api/purchases/${id}/restore`, {})
      .pipe(
        catchError(error => {
          console.error('Restore purchase error:', error);
          return of({ success: false, message: 'Failed to restore purchase' });
        })
      );
  }

  getStatistics(): Observable<{ success: boolean; statistics: PurchaseStatistics }> {
    return this.http.get<{ success: boolean; statistics: PurchaseStatistics }>(`${this.API_URL}/api/statistics`)
      .pipe(
        catchError(error => {
          console.error('Get statistics error:', error);
          return of({
            success: false,
            statistics: {
              total_orders: 0,
              pending_approval: 0,
              approved_orders: 0,
              purchased_orders: 0,
              shipped_orders: 0,
              arrived_orders: 0,
              total_value: 0
            }
          });
        })
      );
  }

  uploadFile(file: File, subfolder: string = 'arrival_photos'): Observable<{ success: boolean; message: string; filename?: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subfolder', subfolder);

    return this.http.post<{ success: boolean; message: string; filename?: string }>(`${this.API_URL}/api/upload`, formData)
      .pipe(
        catchError(error => {
          console.error('Upload file error:', error);
          return of({ success: false, message: 'Failed to upload file' });
        })
      );
  }
}

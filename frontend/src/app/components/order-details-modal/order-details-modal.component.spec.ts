import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OrderDetailsModalComponent } from './order-details-modal.component';

describe('OrderDetailsModalComponent', () => {
  let component: OrderDetailsModalComponent;
  let fixture: ComponentFixture<OrderDetailsModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrderDetailsModalComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OrderDetailsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

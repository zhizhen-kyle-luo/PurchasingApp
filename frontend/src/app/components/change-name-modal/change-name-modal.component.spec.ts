import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChangeNameModalComponent } from './change-name-modal.component';

describe('ChangeNameModalComponent', () => {
  let component: ChangeNameModalComponent;
  let fixture: ComponentFixture<ChangeNameModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChangeNameModalComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChangeNameModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

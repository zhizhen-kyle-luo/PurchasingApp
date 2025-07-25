import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { User } from './models/user.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet
  ],
  template: `<router-outlet></router-outlet>`
})
export class AppComponent implements OnInit {
  title = 'MIT Motorsports Purchasing';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Load current user on app start
    this.authService.getCurrentUser().subscribe();
  }
}

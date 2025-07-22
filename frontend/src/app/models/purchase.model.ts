export interface Purchase {
  id: number;
  item_name: string;
  vendor_name: string;
  item_link?: string;
  price: number;
  shipping_cost: number;
  quantity: number;
  subteam: string;
  subproject?: string;
  purpose?: string;
  notes?: string;
  requester_name: string;
  requester_email: string;
  approval_status: ApprovalStatus;
  status: PurchaseStatus;
  urgency: UrgencyLevel;
  purchase_date: string;
  shipped_at?: string;
  arrived_at?: string;
  sublead_email?: string;
  exec_email?: string;
  exec_approval_status: string;
  arrival_photo?: string;
  is_deleted: boolean;
  is_resolved: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
  total_cost: number;
  is_urgent: boolean;
  is_special_large: boolean;
  needs_executive_approval: boolean;
  can_be_purchased: boolean;
  is_pending_approval: boolean;
}

export type ApprovalStatus = 
  | 'Pending Sublead Approval'
  | 'Pending Executive Approval'
  | 'Fully Approved'
  | 'Rejected';

export type PurchaseStatus = 
  | 'Not Yet Purchased'
  | 'Purchased'
  | 'Shipped'
  | 'Arrived'
  | 'Cancelled';

export type UrgencyLevel = 
  | 'Neither'
  | 'Urgent'
  | 'Special/Large'
  | 'Both';

export interface CreatePurchaseRequest {
  item_name: string;
  vendor_name: string;
  item_link?: string;
  price: number;
  shipping_cost?: number;
  quantity?: number;
  subteam: string;
  subproject?: string;
  purpose?: string;
  notes?: string;
  requester_name: string;
  requester_email: string;
  urgency?: UrgencyLevel;
}

export interface PurchaseFilters {
  status?: PurchaseStatus;
  approval_status?: ApprovalStatus;
  subteam?: string;
  search?: string;
  include_deleted?: boolean;
}

export interface PurchaseListResponse {
  success: boolean;
  purchases: Purchase[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface PurchaseResponse {
  success: boolean;
  message: string;
  purchase?: Purchase;
}

export interface PurchaseStatistics {
  total_orders: number;
  pending_approval: number;
  approved_orders: number;
  purchased_orders: number;
  shipped_orders: number;
  arrived_orders: number;
  total_value: number;
}

export const SUBTEAM_OPTIONS = [
  'MechE Structures',
  'Electrical',
  'Software',
  'Business',
  'Aerodynamics',
  'Powertrain',
  'Suspension',
  'Other'
];

export const SUBPROJECT_OPTIONS: { [key: string]: string[] } = {
  'MechE Structures': [
    'Chassis',
    'Body/Aero',
    'Manufacturing',
    'Testing',
    'Other'
  ],
  'Electrical': [
    'PCB Design',
    'Wiring Harness',
    'Sensors',
    'Power Systems',
    'Testing Equipment',
    'Other'
  ],
  'Software': [
    'Data Acquisition',
    'Controls',
    'Simulation',
    'Tools',
    'Other'
  ],
  'Aerodynamics': [
    'Wind Tunnel',
    'CFD',
    'Manufacturing',
    'Testing',
    'Other'
  ],
  'Powertrain': [
    'Engine',
    'Drivetrain',
    'Cooling',
    'Fuel System',
    'Other'
  ],
  'Suspension': [
    'Design',
    'Manufacturing',
    'Testing',
    'Other'
  ]
};

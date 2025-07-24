import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from "@angular/forms";
import { Router, RouterModule } from "@angular/router";
import { PurchaseService } from "../../services/purchase.service";
import { AuthService } from "../../services/auth.service";

@Component({
  selector: "app-new-order",
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: "./new-order.component.html",
  styleUrls: ["./new-order.component.scss"],
})
export class NewOrderComponent implements OnInit {
  orderForm: FormGroup;
  showSubleadVerifier = true;
  fields = [
    {
      name: "vendor_name",
      label: "Name of Company",
      type: "text",
      description: [
        "First preference: McMaster, Digikey, and Amazon",
        '<a href="https://docs.google.com/spreadsheets/d/1Yc5VMqho-xrae6zBpSbBLjzb9Fmuj89p41ogwmlUk8Q/edit#gid=0" target="_blank" class="text-blue-600 hover:underline">Reference for preferred vendors</a>',
      ],
    },
    {
      name: "item_name",
      label: "Name/Description of Items Needed",
      type: "textarea",
      description: [
        'Consolidate items as best you can. If you can link it as a whole cart (e.g. Digikey/Mouser/McMaster), do that and write "Basket". Otherwise, each item needs its own form.',
      ],
    },
    {
      name: "quantity",
      label: "Quantity Needed",
      type: "number",
    },
    {
      name: "item_link",
      label: "Link to Items/Basket",
      type: "text",
      description: [
        "Provide a *single* link to the item or the cart. If there is no link, write the name of the company (McMaster, Digikey, Fictiv, etc).",
      ],
    },
    {
      name: "price",
      label: "Total Cost ($)",
      type: "number",
      description: ["Don't account for sales tax or shipping"],
    },
    {
      name: "shipping_cost",
      label: "Shipping Cost ($)",
      type: "number",
      description: ["Use zip code 02139 for shipping estimate"],
    },
    {
      name: "purpose",
      label: "Why do you need this item?",
      type: "textarea",
      description: [
        "Keep this brief but descriptive; edgerton needs to know this for approvals",
      ],
    },
    {
      name: "notes",
      label: "Any notes? (Optional)",
      type: "textarea",
    },
    {
      name: "subteam",
      label: "Subteam",
      type: "select",
      options: [
        { value: "", text: "Select a Subteam" },
        { value: "MechE Structures", text: "MechE Structures" },
        { value: "MechE Energetics", text: "MechE Energetics" },
        { value: "EE", text: "EE" },
        { value: "Software", text: "Software" },
        { value: "Testing", text: "Testing" },
        { value: "Driver Training", text: "Driver Training" },
        { value: "Business", text: "Business" },
      ],
    },
    {
      name: "subproject",
      label: "Sub-project",
      type: "select",
      options: [{ value: "", text: "Select a Sub-project" }],
    },
  ];

  SUBPROJECT_OPTIONS: any = {
    "MechE Structures": [
      "MechE Structures: General subteam",
      "Structures: A-Arms",
      "Structures: ARBs & Rockers",
      "Structures: Composites",
      "Structures: Frame",
      "Structures: Impact Attenuator",
      "Structures: Pedal Box",
      "Structures: Seat & Firewall",
      "Structures: Steering",
      "Structures: Steering Wheel",
      "Structures: Tools & Maintenance",
      "Dtrain: Bearings, lube, seals",
      "Dtrain: Brakes",
      "Dtrain: Drivetrain Sensors",
      "Dtrain: Gears",
      "Dtrain: Hubs",
      "Dtrain: Tires & Rim",
      "Dtrain: Uprights",
      "Aero: Testing",
      "Aero: Body Panels",
      "Aero: Diffuser",
      "Aero: Mounting",
      "Aero: Side Pods",
      "Aero: Wings",
    ],
    "MechE Energetics": [
      "Energetics: General subteam",
      "Energetics: Accumulator",
      "Energetics: Battery Box",
      "Energetics: Battery Cells",
      "Energetics: Cooling",
      "Energetics: HV Electronics",
      "Energetics: LV Electronics",
      "Energetics: Motors",
      "Energetics: Testing Equipment",
      "Energetics: Tools & Maintenance",
      "Energetics: Wiring",
    ],
    EE: [
      "EE: General Subteam",
      "EE: BMS/Battery",
      "EE: CSB/Charger",
      "EE: Dash",
      "EE: HVLV",
      "EE: LVBatt",
      "EE: RSP",
      "EE: Sensor Node",
      "EE: VCU",
    ],
    Software: ["Software: General Subteam"],
    Testing: [
      "Testing: General Subteam",
      "Testing: Comp Food/Gas",
      "Testing: Comp Vehicle Rentals",
      "Testing: Hybrid Housing",
      "Testing: Michigan Housing",
      "Testing: MY24 Maintenance",
      "Testing: Trip Gas",
      "Testing: Trip Food",
      "Testing: Truck Rental",
    ],
    "Driver Training": ["Driver: Sim PC", "Driver: Sim VR", "Driver: Software"],
    Business: [
      "Business: Livery",
      "Business: Media",
      "Business: Merch",
      "Business: Pizza",
      "Business: Shipping",
      "Business: Social",
    ],
  };

  constructor(
    private fb: FormBuilder,
    private purchaseService: PurchaseService,
    private authService: AuthService,
    private router: Router
  ) {
    this.orderForm = this.fb.group({
      vendor_name: ["", Validators.required],
      item_name: ["", Validators.required],
      quantity: [1, Validators.required],
      item_link: ["", Validators.required],
      price: [0, Validators.required],
      shipping_cost: [0, Validators.required],
      purpose: ["", Validators.required],
      notes: [""],
      subteam: ["", Validators.required],
      subproject: ["", Validators.required],
      urgency: ["Neither", Validators.required],
      sublead_verifier: [""],
      exec_verifier: ["", Validators.required],
      requester_name: [""],
      requester_email: [""]
    });
  }

  ngOnInit(): void {
    const user = this.authService.currentUser;
    if (user) {
      this.orderForm.patchValue({
        requester_name: user.full_name,
        requester_email: user.email
      });
    }
  }

  onSelectChange(fieldName: string, event: any) {
    if (fieldName === "subteam") {
      const subteam = event.target.value;
      const subprojectField = this.fields.find((f) => f.name === "subproject");
      if (subprojectField) {
        subprojectField.options = [
          { value: "", text: "Select a Sub-project" },
          ...(this.SUBPROJECT_OPTIONS[subteam] || []).map((opt: string) => ({
            value: opt,
            text: opt,
          })),
        ];
      }
      this.orderForm.patchValue({ subproject: "" });
    }
  }

  submitOrder() {
    if (this.orderForm.valid) {
      this.purchaseService.createPurchase(this.orderForm.value).subscribe({
        next: (response) => {
          if (response.success) {
            alert("Order submitted successfully!");
            this.router.navigate(['/dashboard']);
          } else {
            alert("Error: " + response.message);
          }
        },
        error: (error) => {
          console.error('Error submitting order:', error);
          alert("Failed to submit order. Please try again.");
        }
      });
    } else {
      alert("Please fill in all required fields.");
    }
  }
}
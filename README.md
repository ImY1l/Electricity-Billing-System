# ⚡ Electricity Billing System
Comprehensive solution aimed at improving the management of electricity services. It facilitates effective communication and coordination among key stakeholders, including customers, utility providers, support administrators, and staff. The system ensures secure user registration and authentication, accurate billing calculations, smooth payment processing, and comprehensive customer support.

## 🛠️ Use Cases
- System Registration
- Log in to the System
- Reset Password
- Make a Payment and Receive Payment Receipt
- View Bill Details
- Update Meter Reading and Tariff
- Track Overdue Bills
- Generate Monthly Bills
- Submit Feedback
- View Customer Bills
- View Customer Feedback and Analysis
- Submit and Resolve Customer Issue
- Manage Customer Accounts
- Track Overdue Bills
- Usage Monitoring
> **Note:** Each component is explained in detail in [Proj_PIII_T10L_G2_Yousef, Aamena, Faiz, Cheng.pdf](Proj_PIII_T10L_G2_Yousef, Aamena, Faiz, Cheng.pdf), including supporting diagrams such as sequence and activity diagrams.

## 🚀 Run Locally
1. Clone the repository
   ```bash
   git clone https://github.com/ImY1l/Electricity-Billing-System.git
   ```
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

> **Note:** Between steps 2 and 3, you may need to run `pip install django` if you don't have the required dependencies.

3. Run migrations
   ```bash
   python manage.py migrate
   ```
4. Start the development server
   ```bash
   python manage.py runserver
   ```
5. Open <http://127.0.0.1:8000/> and use the system

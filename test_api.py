"""
API Testing Examples using Python requests library

Install: pip install requests

Usage: python test_api.py
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_complete_flow():
    """Test complete user journey"""
    
    # 1. Register User
    print("\n🚀 Starting API Test Flow...")
    
    register_data = {
        "name": "Test User",
        "email": f"test.{uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "role": "USER"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print_response("1. Register User", response)
    
    if response.status_code != 201:
        print("❌ Registration failed!")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Check Wallet Balance
    response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
    print_response("2. Check Wallet Balance", response)
    
    # 3. Calculate EMI
    loan_data = {
        "principal_amount": 100000,
        "tenure_months": 12,
        "interest_rate": 12.0
    }
    
    response = requests.post(f"{BASE_URL}/api/loans/calculate-emi", json=loan_data, headers=headers)
    print_response("3. Calculate EMI", response)
    
    # 4. Apply for Loan
    response = requests.post(f"{BASE_URL}/api/loans/apply", json=loan_data, headers=headers)
    print_response("4. Apply for Loan", response)
    
    if response.status_code != 201:
        print("❌ Loan application failed!")
        return
    
    loan_id = response.json()["id"]
    
    # 5. View My Loans
    response = requests.get(f"{BASE_URL}/api/loans/my-loans", headers=headers)
    print_response("5. View My Loans", response)
    
    # 6. Admin Login (for approval)
    print("\n🔐 Switching to Admin...")
    admin_login = {
        "username": "admin@example.com",  # OAuth2 uses 'username' field
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=admin_login)
    print_response("6. Admin Login", response)
    
    if response.status_code != 200:
        print("❌ Admin login failed! Make sure to run seed_data.py first")
        return
    
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 7. View Pending Loans (Admin)
    response = requests.get(f"{BASE_URL}/api/loans/admin/pending", headers=admin_headers)
    print_response("7. View Pending Loans (Admin)", response)
    
    # 8. Approve Loan (Admin)
    approval_data = {
        "loan_id": loan_id,
        "approved": True
    }
    
    response = requests.post(f"{BASE_URL}/api/loans/admin/approve", json=approval_data, headers=admin_headers)
    print_response("8. Approve Loan (Admin)", response)
    
    # 9. Check Wallet Balance After Disbursement
    print("\n👤 Switching back to User...")
    response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
    print_response("9. Check Wallet Balance (After Disbursement)", response)
    
    # 10. View Transaction Ledger
    response = requests.get(f"{BASE_URL}/api/wallet/transactions", headers=headers)
    print_response("10. View Transaction Ledger", response)
    
    # 11. Make Repayment
    repayment_data = {
        "loan_id": loan_id,
        "amount": 10000,
        "idempotency_key": f"payment-{uuid4()}"
    }
    
    response = requests.post(f"{BASE_URL}/api/repayments/make-payment", json=repayment_data, headers=headers)
    print_response("11. Make Repayment", response)
    
    # 12. Check Updated Wallet Balance
    response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
    print_response("12. Check Wallet Balance (After Repayment)", response)
    
    # 13. View Updated Transaction Ledger
    response = requests.get(f"{BASE_URL}/api/wallet/transactions", headers=headers)
    print_response("13. View Updated Transaction Ledger", response)
    
    # 14. View Loan Repayments
    response = requests.get(f"{BASE_URL}/api/repayments/loan/{loan_id}", headers=headers)
    print_response("14. View Loan Repayments", response)
    
    # 15. Test Idempotency (retry same payment)
    print("\n🔄 Testing Idempotency...")
    response = requests.post(f"{BASE_URL}/api/repayments/make-payment", json=repayment_data, headers=headers)
    print_response("15. Retry Same Payment (Should Return Same Result)", response)
    
    print("\n" + "="*60)
    print("✅ Complete API Test Flow Finished!")
    print("="*60)


if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            test_complete_flow()
        else:
            print("❌ Server is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("💡 Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

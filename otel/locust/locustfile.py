import time
import random
from locust import HttpUser, task, between

IPS = [
    "8.8.8.8",            # US
    "99.79.66.59",        # Canada
    "51.145.123.29",      # UK
    "46.4.105.19",        # Germany
    "51.91.106.1",        # France
    "58.94.157.121",      # Japan
    "103.224.182.242",    # Australia
    "186.192.90.5",       # Brazil
    "122.160.17.83",      # India
    "196.21.247.1"        # South Africa
]

ENDPOINTS = {
    "payments": {
        "convert_currency": "/api/payments/currency/convert-currency",  # GET
        "get_exchange_rates": "/api/payments/currency/get-exchange-rates",  # GET
        "initiate_transfer": "/api/payments/orchestrator/initiate-transfer",  # GET
        "get_payment_status": "/api/payments/orchestrator/get-payment-status",  # GET
        "cancel_transfer": "/api/payments/orchestrator/cancel-transfer",  # POST
        "record_payment_history": "/api/payments/history/record-payment-history",  # GET
        "audit_payments": "/api/payments/history/audit-payments",  # GET
        "process_gateway": "/api/payments/processor/process-gateway",  # GET
        "settle_payment": "/api/payments/processor/settle-payment",  # POST
        "refund_payment": "/api/payments/processor/refund-payment",  # POST
    },
    "accounting": {
        "create_account": "/api/accounting/orchestrator/create-account",  # GET
        "close_account": "/api/accounting/orchestrator/close-account",  # POST
        "init_ledger": "/api/accounting/ledger/init-ledger",  # GET
        "get_balance": "/api/accounting/ledger/get-balance",  # GET
        "log_transaction_history": "/api/accounting/ledger/log-transaction-history",  # GET
        "reconcile_ledger": "/api/accounting/ledger/reconcile-ledger",  # POST
        "list_transactions": "/api/accounting/history/list-transactions",  # GET
        "export_transactions": "/api/accounting/history/export-transactions",  # GET
    },
    "risk": {
        "validate_transaction": "/api/risk/orchestrator/validate-transaction",  # GET
        "generate_report": "/api/risk/orchestrator/generate-report",  # GET
        "block_transaction": "/api/risk/orchestrator/block-transaction",  # POST
        "check_fraud": "/api/risk/analyzer/check-fraud",  # GET
        "screen_aml": "/api/risk/analyzer/screen-aml",  # GET
        "score_risk": "/api/risk/analyzer/score-risk",  # GET
        "flag_anomaly": "/api/risk/manager/flag-anomaly",  # GET
        "review_flags": "/api/risk/manager/review-flags",  # GET
    },
    "customer": {
        "register_user": "/api/customer/orchestrator/register-user",  # GET
        "get_profile": "/api/customer/orchestrator/get-profile",  # GET
        "verify_kyc": "/api/customer/verifier/verify-kyc",  # GET
        "generate_auth_token": "/api/customer/verifier/generate-auth-token",  # GET
        "notify_registration": "/api/customer/verifier/notify-registration",  # POST
        "update_profile": "/api/customer/profile-manager/update-profile",  # POST
        "search_profiles": "/api/customer/profile-manager/search-profiles",  # GET
    },
}

def get_random_ip():
    return random.choice(IPS)


class PaymentsUser(HttpUser):
    wait_time = between(5, 10)
    weight = 3

    @task
    def random_payment_task(self):
        endpoints = [
            ("get", "/api/payments/currency/convert-currency"),
            ("get", "/api/payments/currency/get-exchange-rates"),
            ("get", "/api/payments/orchestrator/initiate-transfer"),
            ("get", "/api/payments/orchestrator/get-payment-status"),
            ("post", "/api/payments/orchestrator/cancel-transfer"),
            ("get", "/api/payments/history/record-payment-history"),
            ("get", "/api/payments/history/audit-payments"),
            ("get", "/api/payments/processor/process-gateway"),
            ("post", "/api/payments/processor/settle-payment"),
            ("post", "/api/payments/processor/refund-payment"),
        ]
        method, url = random.choice(endpoints)
        headers = {"X-Forwarded-For": get_random_ip()}
        if method == "get":
            self.client.get(url, headers=headers)
        elif method == "post":
            self.client.post(url, headers=headers)

class AccountingUser(HttpUser):
    wait_time = between(10, 25)
    weight = 2

    @task
    def random_accounting_task(self):
        endpoints = [
            ("get", "/api/accounting/orchestrator/create-account"),
            ("post", "/api/accounting/orchestrator/close-account"),
            ("get", "/api/accounting/ledger/init-ledger"),
            ("get", "/api/accounting/ledger/get-balance"),
            ("get", "/api/accounting/ledger/log-transaction-history"),
            ("post", "/api/accounting/ledger/reconcile-ledger"),
            ("get", "/api/accounting/history/list-transactions"),
            ("get", "/api/accounting/history/export-transactions"),
        ]
        method, url = random.choice(endpoints)
        headers = {"X-Forwarded-For": get_random_ip()}
        if method == "get":
            self.client.get(url, headers=headers)
        elif method == "post":
            self.client.post(url, headers=headers)

class RiskUser(HttpUser):
    wait_time = between(5, 15)
    weight = 1

    @task
    def random_risk_task(self):
        endpoints = [
            ("get", "/api/risk/orchestrator/validate-transaction"),
            ("get", "/api/risk/orchestrator/generate-report"),
            ("post", "/api/risk/orchestrator/block-transaction"),
            ("get", "/api/risk/analyzer/check-fraud"),
            ("get", "/api/risk/analyzer/screen-aml"),
            ("get", "/api/risk/analyzer/score-risk"),
            ("get", "/api/risk/manager/flag-anomaly"),
            ("get", "/api/risk/manager/review-flags"),
        ]
        method, url = random.choice(endpoints)
        headers = {"X-Forwarded-For": get_random_ip()}
        if method == "get":
            self.client.get(url, headers=headers)
        elif method == "post":
            self.client.post(url, headers=headers)

class CustomerUser(HttpUser):
    wait_time = between(10, 15)
    weight = 2

    @task
    def random_customer_task(self):
        endpoints = [
            ("get", "/api/customer/orchestrator/register-user"),
            ("get", "/api/customer/orchestrator/get-profile"),
            ("get", "/api/customer/verifier/verify-kyc"),
            ("get", "/api/customer/verifier/generate-auth-token"),
            ("post", "/api/customer/verifier/notify-registration"),
            ("post", "/api/customer/profile-manager/update-profile"),
            ("get", "/api/customer/profile-manager/search-profiles"),
        ]
        method, url = random.choice(endpoints)
        headers = {"X-Forwarded-For": get_random_ip()}
        if method == "get":
            self.client.get(url, headers=headers)
        elif method == "post":
            self.client.post(url, headers=headers)

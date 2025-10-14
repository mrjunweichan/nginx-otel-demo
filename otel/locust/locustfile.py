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
    wait_times = between(1, 4)
    weight = 3

    @task(3)
    def convert_currency(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["convert_currency"], headers=headers)

    @task(3)
    def get_exchange_rates(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["get_exchange_rates"], headers=headers)

    @task(2)
    def initiate_transfer(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["initiate_transfer"], headers=headers)

    @task(2)
    def get_payment_status(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["get_payment_status"], headers=headers)

    @task(1)
    def cancel_transfer(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["payments"]["cancel_transfer"], headers=headers)

    @task(2)
    def record_payment_history(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["record_payment_history"], headers=headers)

    @task(1)
    def audit_payments(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["audit_payments"], headers=headers)

    @task(2)
    def process_gateway(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["payments"]["process_gateway"], headers=headers)

    @task(1)
    def settle_payment(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["payments"]["settle_payment"], headers=headers)

    @task(1)
    def refund_payment(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["payments"]["refund_payment"], headers=headers)


class AccountingUser(HttpUser):
    wait_times = between(1, 5)
    weight = 2

    @task(2)
    def create_account(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["create_account"], headers=headers)

    @task(1)
    def close_account(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["accounting"]["close_account"], headers=headers)

    @task(2)
    def init_ledger(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["init_ledger"], headers=headers)

    @task(3)
    def get_balance(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["get_balance"], headers=headers)

    @task(2)
    def log_transaction_history(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["log_transaction_history"], headers=headers)

    @task(1)
    def reconcile_ledger(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["accounting"]["reconcile_ledger"], headers=headers)

    @task(2)
    def list_transactions(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["list_transactions"], headers=headers)

    @task(1)
    def export_transactions(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["accounting"]["export_transactions"], headers=headers)


class RiskUser(HttpUser):
    wait_times = between(2, 6)
    weight = 1

    @task(2)
    def validate_transaction(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["validate_transaction"], headers=headers)

    @task(1)
    def generate_report(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["generate_report"], headers=headers)

    @task(1)
    def block_transaction(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["risk"]["block_transaction"], headers=headers)

    @task(2)
    def check_fraud(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["check_fraud"], headers=headers)

    @task(2)
    def screen_aml(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["screen_aml"], headers=headers)

    @task(2)
    def score_risk(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["score_risk"], headers=headers)

    @task(1)
    def flag_anomaly(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["flag_anomaly"], headers=headers)

    @task(1)
    def review_flags(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["risk"]["review_flags"], headers=headers)


class CustomerUser(HttpUser):
    wait_times = between(1, 5)
    weight = 2

    @task(2)
    def register_user(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["customer"]["register_user"], headers=headers)

    @task(2)
    def get_profile(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["customer"]["get_profile"], headers=headers)

    @task(2)
    def verify_kyc(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["customer"]["verify_kyc"], headers=headers)

    @task(1)
    def generate_auth_token(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["customer"]["generate_auth_token"], headers=headers)

    @task(1)
    def notify_registration(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["customer"]["notify_registration"], headers=headers)

    @task(1)
    def update_profile(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.post(ENDPOINTS["customer"]["update_profile"], headers=headers)

    @task(2)
    def search_profiles(self):
        headers = {"X-Forwarded-For": get_random_ip()}
        self.client.get(ENDPOINTS["customer"]["search_profiles"], headers=headers)

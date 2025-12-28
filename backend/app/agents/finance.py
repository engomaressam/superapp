<![CDATA["""
Finance Agent
Handles financial operations, budgeting, and payments.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.agents.base import BaseAgent, Tool, Task


class FinanceAgent(BaseAgent):
    """
    Agent specialized in financial services.
    
    Use Cases:
    - "What's my bank balance?"
    - "Pay my electricity bill"
    - "Transfer 500 EGP to Ahmed"
    - "How much did I spend this month?"
    - "Set a budget for groceries"
    
    Capabilities:
    - Check account balances
    - Pay bills (utilities, phone, internet)
    - Transfer money
    - Track expenses and spending patterns
    - Budget management
    - Financial insights
    
    Security Note:
    All financial operations require highest permission level
    and user confirmation.
    """
    
    name = "FinanceAgent"
    description = "Handles banking, payments, and financial tracking"
    
    SUPPORTED_TASKS = [
        "check_balance",
        "pay_bill",
        "transfer_money",
        "get_transactions",
        "get_spending_summary",
        "set_budget",
        "get_financial_insights"
    ]
    
    def _initialize_tools(self):
        """Initialize finance-specific tools."""
        self.tools = [
            Tool(
                name="check_balance",
                description="Check account balance",
                parameters={
                    "account_type": "checking/savings/all"
                },
                function=self._check_balance,
                requires_confirmation=False,  # Read-only
                timeout_seconds=15
            ),
            Tool(
                name="pay_bill",
                description="Pay a utility or service bill",
                parameters={
                    "bill_type": "electricity/water/gas/phone/internet",
                    "account_number": "Billing account number",
                    "amount": "Payment amount"
                },
                function=self._pay_bill,
                requires_confirmation=True,
                estimated_cost=0,  # Variable
                timeout_seconds=45
            ),
            Tool(
                name="transfer_money",
                description="Transfer money to another account",
                parameters={
                    "recipient": "Recipient name or account",
                    "amount": "Transfer amount",
                    "note": "Optional transfer note"
                },
                function=self._transfer_money,
                requires_confirmation=True,
                timeout_seconds=45
            ),
            Tool(
                name="get_transactions",
                description="Get recent transactions",
                parameters={
                    "days": "Number of days to look back",
                    "category": "Optional category filter"
                },
                function=self._get_transactions,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="get_spending_summary",
                description="Get spending summary by category",
                parameters={
                    "period": "week/month/year"
                },
                function=self._get_spending_summary,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="set_budget",
                description="Set a spending budget for a category",
                parameters={
                    "category": "Spending category",
                    "amount": "Budget amount",
                    "period": "weekly/monthly"
                },
                function=self._set_budget,
                requires_confirmation=True,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        
        if task_type == "check_balance":
            return [{
                "tool": "check_balance",
                "parameters": {
                    "account_type": params.get("account_type", "all")
                }
            }]
        
        elif task_type == "pay_bill":
            return [{
                "tool": "pay_bill",
                "parameters": {
                    "bill_type": params.get("bill_type"),
                    "account_number": params.get("account_number"),
                    "amount": params.get("amount")
                }
            }]
        
        elif task_type == "transfer_money":
            # Check balance first, then transfer
            return [
                {
                    "tool": "check_balance",
                    "parameters": {"account_type": "checking"}
                },
                {
                    "tool": "transfer_money",
                    "parameters": {
                        "recipient": params.get("recipient"),
                        "amount": params.get("amount"),
                        "note": params.get("note")
                    }
                }
            ]
        
        elif task_type == "get_transactions":
            return [{
                "tool": "get_transactions",
                "parameters": {
                    "days": params.get("days", 30),
                    "category": params.get("category")
                }
            }]
        
        elif task_type == "get_spending_summary":
            return [{
                "tool": "get_spending_summary",
                "parameters": {
                    "period": params.get("period", "month")
                }
            }]
        
        elif task_type == "set_budget":
            return [{
                "tool": "set_budget",
                "parameters": {
                    "category": params.get("category"),
                    "amount": params.get("amount"),
                    "period": params.get("period", "monthly")
                }
            }]
        
        return []
    
    async def _check_balance(
        self,
        account_type: str = "all"
    ) -> Dict[str, Any]:
        """Check account balances."""
        # Mock response (would integrate with banking API)
        accounts = {
            "checking": {
                "name": "Main Account",
                "balance": 15420.50,
                "currency": "EGP",
                "last_updated": datetime.now().isoformat()
            },
            "savings": {
                "name": "Savings Account",
                "balance": 45000.00,
                "currency": "EGP",
                "interest_rate": "8.5%",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        if account_type == "all":
            return {
                "accounts": accounts,
                "total_balance": sum(acc["balance"] for acc in accounts.values()),
                "currency": "EGP"
            }
        
        return {"account": accounts.get(account_type, {})}
    
    async def _pay_bill(
        self,
        bill_type: str,
        account_number: str,
        amount: float
    ) -> Dict[str, Any]:
        """Pay a bill."""
        transaction_id = f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "bill_type": bill_type,
            "provider": self._get_provider(bill_type),
            "account_number": account_number,
            "amount": amount,
            "currency": "EGP",
            "fee": 5.00,
            "total_deducted": amount + 5.00,
            "timestamp": datetime.now().isoformat(),
            "reference": transaction_id.upper(),
            "receipt_available": True
        }
    
    def _get_provider(self, bill_type: str) -> str:
        providers = {
            "electricity": "Egyptian Electricity Holding Company",
            "water": "Cairo Water Company",
            "gas": "Town Gas",
            "phone": "Vodafone Egypt",
            "internet": "WE (Telecom Egypt)"
        }
        return providers.get(bill_type, "Unknown Provider")
    
    async def _transfer_money(
        self,
        recipient: str,
        amount: float,
        note: str = None
    ) -> Dict[str, Any]:
        """Transfer money."""
        transaction_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "type": "transfer",
            "recipient": {
                "name": recipient,
                "masked_account": "**** **** **** 1234"
            },
            "amount": amount,
            "currency": "EGP",
            "fee": 0,
            "note": note,
            "timestamp": datetime.now().isoformat(),
            "can_cancel": True,
            "cancel_deadline": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
    
    async def _get_transactions(
        self,
        days: int = 30,
        category: str = None
    ) -> Dict[str, Any]:
        """Get recent transactions."""
        transactions = [
            {
                "id": "txn_001",
                "date": "2024-01-15",
                "description": "Carrefour",
                "category": "Groceries",
                "amount": -856.50,
                "balance_after": 15420.50
            },
            {
                "id": "txn_002",
                "date": "2024-01-14",
                "description": "Salary Deposit",
                "category": "Income",
                "amount": 25000.00,
                "balance_after": 16277.00
            },
            {
                "id": "txn_003",
                "date": "2024-01-13",
                "description": "Uber",
                "category": "Transport",
                "amount": -125.00,
                "balance_after": -8723.00
            },
            {
                "id": "txn_004",
                "date": "2024-01-12",
                "description": "Netflix",
                "category": "Entertainment",
                "amount": -199.00,
                "balance_after": -8598.00
            },
            {
                "id": "txn_005",
                "date": "2024-01-11",
                "description": "Restaurant - Zooba",
                "category": "Food",
                "amount": -245.00,
                "balance_after": -8399.00
            }
        ]
        
        if category:
            transactions = [t for t in transactions if t["category"].lower() == category.lower()]
        
        return {
            "transactions": transactions,
            "period_days": days,
            "total_income": 25000.00,
            "total_expenses": 1425.50,
            "currency": "EGP"
        }
    
    async def _get_spending_summary(
        self,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Get spending summary by category."""
        return {
            "period": period,
            "start_date": "2024-01-01",
            "end_date": "2024-01-15",
            "categories": [
                {"name": "Food & Dining", "amount": 3250.00, "percentage": 25, "trend": "up"},
                {"name": "Transport", "amount": 1850.00, "percentage": 14, "trend": "stable"},
                {"name": "Groceries", "amount": 2100.00, "percentage": 16, "trend": "down"},
                {"name": "Entertainment", "amount": 950.00, "percentage": 7, "trend": "up"},
                {"name": "Bills & Utilities", "amount": 2800.00, "percentage": 22, "trend": "stable"},
                {"name": "Shopping", "amount": 1500.00, "percentage": 12, "trend": "down"},
                {"name": "Other", "amount": 550.00, "percentage": 4, "trend": "stable"}
            ],
            "total_spent": 13000.00,
            "budget": 15000.00,
            "remaining": 2000.00,
            "currency": "EGP",
            "insights": [
                "Food spending is 15% higher than last month",
                "You're on track to stay within budget",
                "Consider setting a limit for entertainment"
            ]
        }
    
    async def _set_budget(
        self,
        category: str,
        amount: float,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """Set a spending budget."""
        return {
            "status": "success",
            "budget": {
                "category": category,
                "amount": amount,
                "period": period,
                "currency": "EGP",
                "start_date": datetime.now().strftime("%Y-%m-01"),
                "notifications": True,
                "alert_threshold": 80  # Alert at 80% spent
            },
            "message": f"Budget of {amount} EGP/{period} set for {category}"
        }
]]>

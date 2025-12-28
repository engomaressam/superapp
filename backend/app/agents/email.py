<![CDATA["""
Email Agent
Manages email communications and inbox organization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.agents.base import BaseAgent, Tool, Task


class EmailAgent(BaseAgent):
    """
    Agent specialized in email management.
    
    Use Cases:
    - "Check my unread emails"
    - "Send an email to John about the meeting"
    - "Find emails from Amazon"
    - "Summarize my important emails"
    - "Unsubscribe from newsletters"
    - "Schedule an email for tomorrow morning"
    
    Capabilities:
    - Read and search emails
    - Compose and send emails
    - Draft replies with AI assistance
    - Organize inbox (labels, archive)
    - Email summarization
    - Smart scheduling
    
    Integrations:
    - Gmail
    - Outlook
    - Apple Mail
    """
    
    name = "EmailAgent"
    description = "Manages emails, drafts, and inbox organization"
    
    SUPPORTED_TASKS = [
        "check_inbox",
        "search_emails",
        "send_email",
        "draft_reply",
        "summarize_emails",
        "organize_inbox",
        "schedule_email"
    ]
    
    def _initialize_tools(self):
        """Initialize email-specific tools."""
        self.tools = [
            Tool(
                name="check_inbox",
                description="Check unread emails and important messages",
                parameters={
                    "folder": "inbox/important/all",
                    "unread_only": "Boolean"
                },
                function=self._check_inbox,
                requires_confirmation=False,
                timeout_seconds=20
            ),
            Tool(
                name="search_emails",
                description="Search emails by sender, subject, or content",
                parameters={
                    "query": "Search query",
                    "from_sender": "Sender email",
                    "date_range": "Date range to search"
                },
                function=self._search_emails,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="send_email",
                description="Compose and send an email",
                parameters={
                    "to": "Recipient email(s)",
                    "subject": "Email subject",
                    "body": "Email content",
                    "attachments": "Optional attachments"
                },
                function=self._send_email,
                requires_confirmation=True,
                timeout_seconds=30
            ),
            Tool(
                name="draft_reply",
                description="Draft a reply to an email",
                parameters={
                    "email_id": "Original email ID",
                    "tone": "professional/casual/friendly",
                    "key_points": "Points to include in reply"
                },
                function=self._draft_reply,
                requires_confirmation=True,
                timeout_seconds=20
            ),
            Tool(
                name="summarize_emails",
                description="Get AI summary of emails",
                parameters={
                    "email_ids": "Emails to summarize",
                    "period": "today/week"
                },
                function=self._summarize_emails,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="organize_inbox",
                description="Organize emails with labels/folders",
                parameters={
                    "action": "archive/label/delete",
                    "email_ids": "Emails to organize",
                    "label": "Label name"
                },
                function=self._organize_inbox,
                requires_confirmation=True,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = task.type
        params = task.parameters
        
        if task_type == "check_inbox":
            return [{
                "tool": "check_inbox",
                "parameters": {
                    "folder": params.get("folder", "inbox"),
                    "unread_only": params.get("unread_only", True)
                }
            }]
        
        elif task_type == "search_emails":
            return [{
                "tool": "search_emails",
                "parameters": {
                    "query": params.get("query"),
                    "from_sender": params.get("from_sender"),
                    "date_range": params.get("date_range", "30d")
                }
            }]
        
        elif task_type == "send_email":
            return [{
                "tool": "send_email",
                "parameters": {
                    "to": params.get("to"),
                    "subject": params.get("subject"),
                    "body": params.get("body"),
                    "attachments": params.get("attachments")
                }
            }]
        
        elif task_type == "draft_reply":
            return [{
                "tool": "draft_reply",
                "parameters": {
                    "email_id": params.get("email_id"),
                    "tone": params.get("tone", "professional"),
                    "key_points": params.get("key_points")
                }
            }]
        
        elif task_type == "summarize_emails":
            return [{
                "tool": "summarize_emails",
                "parameters": {
                    "email_ids": params.get("email_ids"),
                    "period": params.get("period", "today")
                }
            }]
        
        elif task_type == "organize_inbox":
            return [{
                "tool": "organize_inbox",
                "parameters": {
                    "action": params.get("action"),
                    "email_ids": params.get("email_ids"),
                    "label": params.get("label")
                }
            }]
        
        return []
    
    async def _check_inbox(
        self,
        folder: str = "inbox",
        unread_only: bool = True
    ) -> Dict[str, Any]:
        """Check inbox for new emails."""
        emails = [
            {
                "id": "email_001",
                "from": {"name": "Ahmed Hassan", "email": "ahmed@company.com"},
                "subject": "Q1 Project Update - Action Required",
                "preview": "Hi, I wanted to follow up on the Q1 project timeline...",
                "date": "2024-01-15T09:30:00",
                "is_read": False,
                "is_starred": True,
                "has_attachment": True,
                "labels": ["Work", "Important"]
            },
            {
                "id": "email_002",
                "from": {"name": "Amazon", "email": "shipment@amazon.eg"},
                "subject": "Your order has shipped!",
                "preview": "Your order #123-456-789 is on its way...",
                "date": "2024-01-15T08:15:00",
                "is_read": False,
                "is_starred": False,
                "has_attachment": False,
                "labels": ["Shopping"]
            },
            {
                "id": "email_003",
                "from": {"name": "Sarah Mohamed", "email": "sarah@gmail.com"},
                "subject": "Dinner plans this weekend?",
                "preview": "Hey! Are you free this Saturday? I was thinking...",
                "date": "2024-01-14T22:45:00",
                "is_read": False,
                "is_starred": False,
                "has_attachment": False,
                "labels": ["Personal"]
            },
            {
                "id": "email_004",
                "from": {"name": "Netflix", "email": "info@netflix.com"},
                "subject": "New arrivals you might like",
                "preview": "Based on your watching history, we recommend...",
                "date": "2024-01-14T18:00:00",
                "is_read": True,
                "is_starred": False,
                "has_attachment": False,
                "labels": ["Newsletters"]
            }
        ]
        
        if unread_only:
            emails = [e for e in emails if not e["is_read"]]
        
        return {
            "folder": folder,
            "emails": emails,
            "total_unread": len([e for e in emails if not e["is_read"]]),
            "total_in_folder": len(emails),
            "summary": {
                "important": 1,
                "from_contacts": 2,
                "newsletters": 1
            }
        }
    
    async def _search_emails(
        self,
        query: str = None,
        from_sender: str = None,
        date_range: str = "30d"
    ) -> Dict[str, Any]:
        """Search emails."""
        # Mock search results
        results = [
            {
                "id": "email_010",
                "from": {"name": "Amazon", "email": "orders@amazon.eg"},
                "subject": "Your Amazon order confirmation",
                "preview": "Thank you for your order...",
                "date": "2024-01-10T14:30:00"
            },
            {
                "id": "email_011",
                "from": {"name": "Amazon", "email": "shipment@amazon.eg"},
                "subject": "Your package has been delivered",
                "preview": "Your order was delivered on...",
                "date": "2024-01-12T16:45:00"
            }
        ]
        
        return {
            "query": query,
            "from_filter": from_sender,
            "date_range": date_range,
            "results": results,
            "total_found": len(results)
        }
    
    async def _send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """Send an email."""
        message_id = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "sent",
            "message_id": message_id,
            "to": to if isinstance(to, list) else [to],
            "subject": subject,
            "body_preview": body[:100] + "..." if len(body) > 100 else body,
            "attachments": attachments or [],
            "sent_at": datetime.now().isoformat(),
            "can_undo": True,
            "undo_deadline": (datetime.now() + timedelta(seconds=30)).isoformat()
        }
    
    async def _draft_reply(
        self,
        email_id: str,
        tone: str = "professional",
        key_points: List[str] = None
    ) -> Dict[str, Any]:
        """Draft a reply using AI."""
        # Mock AI-generated draft
        draft_templates = {
            "professional": """Dear Ahmed,

Thank you for your email regarding the Q1 project update.

I have reviewed the timeline and would like to schedule a meeting to discuss the following points:
- Current progress status
- Resource allocation
- Key milestones

Would tomorrow at 2 PM work for you?

Best regards""",
            "casual": """Hi Ahmed,

Thanks for the update! I've looked through everything and have a few thoughts.

Can we hop on a quick call tomorrow to discuss? Maybe around 2 PM?

Cheers""",
            "friendly": """Hey Ahmed!

Thanks so much for keeping me in the loop on the Q1 project!

I'd love to chat more about this - how about we grab coffee tomorrow and go through it together? Say 2 PM?

Talk soon!"""
        }
        
        return {
            "email_id": email_id,
            "tone": tone,
            "draft": draft_templates.get(tone, draft_templates["professional"]),
            "key_points_addressed": key_points or ["Timeline review", "Meeting request"],
            "suggested_subject": "Re: Q1 Project Update - Action Required",
            "status": "draft",
            "edit_url": f"https://mail.google.com/draft/{email_id}"
        }
    
    async def _summarize_emails(
        self,
        email_ids: List[str] = None,
        period: str = "today"
    ) -> Dict[str, Any]:
        """Summarize emails using AI."""
        return {
            "period": period,
            "summary": {
                "total_emails": 15,
                "unread": 3,
                "important": 2,
                "action_required": 1
            },
            "highlights": [
                {
                    "type": "action_required",
                    "from": "Ahmed Hassan",
                    "summary": "Needs response on Q1 project timeline by EOD"
                },
                {
                    "type": "shipping",
                    "from": "Amazon",
                    "summary": "Your iPhone case has shipped, arriving tomorrow"
                },
                {
                    "type": "social",
                    "from": "Sarah Mohamed",
                    "summary": "Invited you for dinner this Saturday"
                }
            ],
            "categories": {
                "Work": 5,
                "Personal": 3,
                "Shopping": 4,
                "Newsletters": 3
            },
            "ai_insights": [
                "You have 1 email requiring immediate attention",
                "3 newsletters could be unsubscribed to reduce clutter",
                "Consider archiving 5 old promotional emails"
            ]
        }
    
    async def _organize_inbox(
        self,
        action: str,
        email_ids: List[str],
        label: str = None
    ) -> Dict[str, Any]:
        """Organize emails."""
        return {
            "status": "success",
            "action": action,
            "affected_emails": len(email_ids) if email_ids else 0,
            "label": label,
            "message": f"Successfully {action}d {len(email_ids) if email_ids else 0} emails",
            "can_undo": True
        }
]]>

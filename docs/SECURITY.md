<![CDATA[# 🔐 Security & Privacy Guide

## Overview

ARIA handles sensitive user data including personal information, credentials, and financial details. This document outlines our security architecture and best practices.

---

## Threat Model

### Assets to Protect

1. **User Credentials** - OAuth tokens, API keys
2. **Personal Information** - Names, addresses, phone numbers
3. **Financial Data** - Payment methods, transaction history
4. **Health Information** - Medical appointments, conditions
5. **Behavioral Data** - Usage patterns, preferences

### Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| External Attackers | Network attacks, API abuse | Data theft, fraud |
| Malicious Apps | On-device access | Data harvesting |
| Cloud Provider | Infrastructure access | Unlikely but possible |
| LLM Provider | Sees processed prompts | Data mining |

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY PERIMETER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: NETWORK SECURITY                         │   │
│  │  • TLS 1.3 for all connections                                       │   │
│  │  • Certificate pinning in mobile app                                 │   │
│  │  • WAF (Web Application Firewall)                                    │   │
│  │  • DDoS protection via Cloudflare                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 2: APPLICATION SECURITY                     │   │
│  │  • Input validation & sanitization                                   │   │
│  │  • Rate limiting per user/IP                                         │   │
│  │  • JWT with short expiration                                         │   │
│  │  • CORS policy enforcement                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 3: DATA SECURITY                            │   │
│  │  • PII detection & masking                                           │   │
│  │  • Encryption at rest (AES-256)                                      │   │
│  │  • Encryption in transit (TLS)                                       │   │
│  │  • Key management (HashiCorp Vault)                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 4: AGENT SECURITY                           │   │
│  │  • Action allowlisting                                               │   │
│  │  • Budget & scope limits                                             │   │
│  │  • Human-in-the-loop for sensitive actions                           │   │
│  │  • Audit logging                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PII Protection

### Detection & Masking

```python
# backend/app/security/pii_sanitizer.py

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import spacy

@dataclass
class PIIEntity:
    type: str
    value: str
    start: int
    end: int
    placeholder: str

class PIISanitizer:
    """
    Detects and masks Personally Identifiable Information (PII)
    before sending data to external LLMs.
    """
    
    # Regex patterns for common PII
    PATTERNS = {
        "PHONE_EG": r"(?:\+20|0)1[0-2,5]\d{8}",  # Egyptian phone
        "PHONE_INTL": r"\+?[\d\s\-\(\)]{10,15}",
        "EMAIL": r"[\w\.\-]+@[\w\.\-]+\.\w{2,}",
        "CREDIT_CARD": r"\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}",
        "SSN_US": r"\d{3}-\d{2}-\d{4}",
        "NATIONAL_ID_EG": r"\d{14}",  # Egyptian National ID
        "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "DATE_OF_BIRTH": r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
    }
    
    def __init__(self, use_ner: bool = True):
        """
        Initialize the sanitizer.
        
        Args:
            use_ner: Whether to use Named Entity Recognition for names/locations
        """
        self.use_ner = use_ner
        if use_ner:
            self.nlp = spacy.load("en_core_web_sm")
    
    def sanitize(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Sanitize text by replacing PII with placeholders.
        
        Args:
            text: Input text potentially containing PII
            
        Returns:
            Tuple of (sanitized_text, mapping_dict)
            mapping_dict maps placeholders back to original values
        """
        entities: List[PIIEntity] = []
        
        # Pattern-based detection
        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                entities.append(PIIEntity(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    placeholder=""  # Will be assigned later
                ))
        
        # NER-based detection for names and locations
        if self.use_ner:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "GPE", "LOC", "ORG"]:
                    entities.append(PIIEntity(
                        type=f"NER_{ent.label_}",
                        value=ent.text,
                        start=ent.start_char,
                        end=ent.end_char,
                        placeholder=""
                    ))
        
        # Sort by position (reverse) to replace from end to start
        entities.sort(key=lambda e: e.start, reverse=True)
        
        # Remove overlapping entities (keep longer ones)
        filtered_entities = self._remove_overlaps(entities)
        
        # Create mapping and replace
        mapping = {}
        sanitized = text
        counter = {}
        
        for entity in filtered_entities:
            # Generate unique placeholder
            type_key = entity.type
            counter[type_key] = counter.get(type_key, 0) + 1
            placeholder = f"[{type_key}_{counter[type_key]}]"
            
            entity.placeholder = placeholder
            mapping[placeholder] = entity.value
            
            # Replace in text
            sanitized = (
                sanitized[:entity.start] + 
                placeholder + 
                sanitized[entity.end:]
            )
        
        return sanitized, mapping
    
    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restore original PII values from placeholders.
        
        Args:
            text: Text with placeholders
            mapping: Dictionary mapping placeholders to original values
            
        Returns:
            Text with original values restored
        """
        restored = text
        for placeholder, original in mapping.items():
            restored = restored.replace(placeholder, original)
        return restored
    
    def _remove_overlaps(
        self, 
        entities: List[PIIEntity]
    ) -> List[PIIEntity]:
        """Remove overlapping entities, keeping longer ones."""
        if not entities:
            return []
        
        # Sort by length (descending) then by start position
        entities.sort(key=lambda e: (-(e.end - e.start), e.start))
        
        filtered = []
        covered = set()
        
        for entity in entities:
            positions = set(range(entity.start, entity.end))
            if not positions & covered:
                filtered.append(entity)
                covered |= positions
        
        return filtered


# Example usage
sanitizer = PIISanitizer()

# Input with PII
text = """
Book an appointment for Ahmed Hassan at +201234567890.
His email is ahmed.hassan@gmail.com and he lives in Nasr City.
Payment card: 4111-1111-1111-1111
"""

sanitized, mapping = sanitizer.sanitize(text)
print(sanitized)
# Output:
# Book an appointment for [NER_PERSON_1] at [PHONE_EG_1].
# His email is [EMAIL_1] and he lives in [NER_GPE_1].
# Payment card: [CREDIT_CARD_1]

# After LLM processing, restore values
restored = sanitizer.restore(llm_response, mapping)
```

---

## Encryption

### At-Rest Encryption

```python
# backend/app/security/encryption.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

class FieldEncryption:
    """
    Encrypt sensitive fields before database storage.
    """
    
    def __init__(self, master_key: bytes, salt: bytes = None):
        """
        Initialize with a master key.
        
        In production, master_key should come from a secret manager
        like HashiCorp Vault, AWS KMS, or Google Cloud KMS.
        """
        self.salt = salt or os.urandom(16)
        
        # Derive encryption key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string value."""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt an encrypted value."""
        return self.cipher.decrypt(ciphertext.encode()).decode()


class SecureCredentialStore:
    """
    Secure storage for OAuth tokens and API keys.
    """
    
    def __init__(self, encryption: FieldEncryption, redis_client):
        self.encryption = encryption
        self.redis = redis_client
    
    async def store_token(
        self, 
        user_id: str, 
        service: str, 
        token: str,
        expires_in: int = 3600
    ):
        """Store an encrypted OAuth token."""
        encrypted = self.encryption.encrypt(token)
        key = f"tokens:{user_id}:{service}"
        
        await self.redis.setex(key, expires_in, encrypted)
    
    async def get_token(self, user_id: str, service: str) -> str:
        """Retrieve and decrypt a token."""
        key = f"tokens:{user_id}:{service}"
        encrypted = await self.redis.get(key)
        
        if not encrypted:
            raise ValueError(f"No token found for {service}")
        
        return self.encryption.decrypt(encrypted)
    
    async def delete_token(self, user_id: str, service: str):
        """Delete a stored token."""
        key = f"tokens:{user_id}:{service}"
        await self.redis.delete(key)
```

---

## Permission Model

### Permission Levels

```python
# backend/app/security/permissions.py

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional

class PermissionLevel(IntEnum):
    """
    User-configurable permission levels for the AI agent.
    """
    
    # Level 0: Agent can only provide information
    READ_ONLY = 0
    
    # Level 1: Agent can suggest actions but needs confirmation for each
    SUGGEST_AND_CONFIRM = 1
    
    # Level 2: Agent can act autonomously within limits
    ACT_WITHIN_LIMITS = 2
    
    # Level 3: Full autonomous mode
    FULL_AUTONOMY = 3

@dataclass
class PermissionConfig:
    """
    Configuration for what the agent can do.
    """
    level: PermissionLevel
    
    # Spending limits (Level 2+)
    max_single_transaction: float = 50.0
    max_daily_spending: float = 200.0
    
    # Allowed actions per level
    allowed_actions: List[str] = None
    
    # Services that always require confirmation
    always_confirm_services: List[str] = None
    
    # Time restrictions (e.g., no actions after 11 PM)
    quiet_hours_start: Optional[int] = 23  # 11 PM
    quiet_hours_end: Optional[int] = 7     # 7 AM

class PermissionChecker:
    """
    Validates if an action is permitted based on user configuration.
    """
    
    # Actions categorized by required permission level
    ACTION_LEVELS = {
        PermissionLevel.READ_ONLY: [
            "view_calendar",
            "check_availability",
            "search_movies",
            "get_weather",
            "search_doctors",
        ],
        PermissionLevel.SUGGEST_AND_CONFIRM: [
            "create_calendar_event",
            "set_reminder",
            "draft_message",
        ],
        PermissionLevel.ACT_WITHIN_LIMITS: [
            "book_ride",
            "book_appointment",
            "send_notification",
        ],
        PermissionLevel.FULL_AUTONOMY: [
            "make_payment",
            "access_financial_data",
            "modify_settings",
        ],
    }
    
    # Actions that have financial impact
    FINANCIAL_ACTIONS = {
        "book_ride": lambda params: params.get("estimated_price", 0),
        "book_appointment": lambda params: params.get("consultation_fee", 0),
        "make_payment": lambda params: params.get("amount", 0),
    }
    
    def __init__(self, config: PermissionConfig):
        self.config = config
        self.daily_spending = 0.0
    
    def can_execute(
        self, 
        action: str, 
        params: dict = None
    ) -> tuple[bool, str]:
        """
        Check if an action is permitted.
        
        Returns:
            Tuple of (is_permitted, reason)
        """
        params = params or {}
        
        # Check quiet hours
        if self._is_quiet_hours():
            return False, "Action blocked during quiet hours"
        
        # Find required level for action
        required_level = None
        for level, actions in self.ACTION_LEVELS.items():
            if action in actions:
                required_level = level
                break
        
        if required_level is None:
            return False, f"Unknown action: {action}"
        
        # Check permission level
        if self.config.level < required_level:
            return False, f"Action '{action}' requires permission level {required_level.name}"
        
        # Check if service requires confirmation
        service = self._get_service_from_action(action)
        if service in (self.config.always_confirm_services or []):
            return False, f"Service '{service}' always requires confirmation"
        
        # Check financial limits
        if action in self.FINANCIAL_ACTIONS:
            cost = self.FINANCIAL_ACTIONS[action](params)
            
            if cost > self.config.max_single_transaction:
                return False, f"Transaction ${cost} exceeds limit ${self.config.max_single_transaction}"
            
            if self.daily_spending + cost > self.config.max_daily_spending:
                return False, f"Would exceed daily spending limit of ${self.config.max_daily_spending}"
        
        return True, "Permitted"
    
    def record_spending(self, amount: float):
        """Record a completed financial transaction."""
        self.daily_spending += amount
    
    def reset_daily_spending(self):
        """Reset daily spending counter (called at midnight)."""
        self.daily_spending = 0.0
    
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        from datetime import datetime
        
        if self.config.quiet_hours_start is None:
            return False
        
        hour = datetime.now().hour
        start = self.config.quiet_hours_start
        end = self.config.quiet_hours_end
        
        if start > end:  # Crosses midnight
            return hour >= start or hour < end
        else:
            return start <= hour < end
    
    def _get_service_from_action(self, action: str) -> str:
        """Extract service name from action."""
        service_map = {
            "book_ride": "uber",
            "book_appointment": "vezeeta",
            "create_calendar_event": "google_calendar",
        }
        return service_map.get(action, "unknown")
```

---

## Audit Logging

```python
# backend/app/security/audit.py

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

class AuditEventType(Enum):
    # Authentication events
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token_refresh"
    
    # Agent actions
    AGENT_ACTION_REQUESTED = "agent.action.requested"
    AGENT_ACTION_CONFIRMED = "agent.action.confirmed"
    AGENT_ACTION_REJECTED = "agent.action.rejected"
    AGENT_ACTION_EXECUTED = "agent.action.executed"
    AGENT_ACTION_FAILED = "agent.action.failed"
    
    # Data access
    PII_ACCESSED = "data.pii.accessed"
    DATA_EXPORTED = "data.exported"
    
    # Permission changes
    PERMISSION_CHANGED = "permission.changed"
    SERVICE_CONNECTED = "service.connected"
    SERVICE_DISCONNECTED = "service.disconnected"

@dataclass
class AuditEvent:
    event_type: AuditEventType
    user_id: str
    timestamp: datetime
    action: str
    resource: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    error_message: Optional[str] = None
    
    def to_json(self) -> str:
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)

class AuditLogger:
    """
    Secure audit logging for compliance and debugging.
    """
    
    def __init__(self, storage_backend):
        """
        Initialize with a storage backend.
        
        Backend could be:
        - PostgreSQL for queryable logs
        - Elasticsearch for searchable logs
        - S3 for long-term archival
        - CloudWatch/Datadog for real-time monitoring
        """
        self.storage = storage_backend
    
    async def log(self, event: AuditEvent):
        """Log an audit event."""
        # Add additional metadata
        event_data = {
            **asdict(event),
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "log_version": "1.0",
        }
        
        # Store the event
        await self.storage.store(event_data)
        
        # Alert on suspicious activity
        if self._is_suspicious(event):
            await self._send_alert(event)
    
    async def log_agent_action(
        self,
        user_id: str,
        action: str,
        parameters: dict,
        result: str,
        success: bool,
        request_context: dict
    ):
        """Convenience method for logging agent actions."""
        event = AuditEvent(
            event_type=AuditEventType.AGENT_ACTION_EXECUTED if success 
                       else AuditEventType.AGENT_ACTION_FAILED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            action=action,
            resource=parameters.get("resource"),
            details={
                "parameters": self._sanitize_params(parameters),
                "result": result,
            },
            ip_address=request_context.get("ip"),
            user_agent=request_context.get("user_agent"),
            success=success,
        )
        await self.log(event)
    
    def _sanitize_params(self, params: dict) -> dict:
        """Remove sensitive data from parameters before logging."""
        sensitive_keys = ["password", "token", "secret", "key", "credit_card"]
        sanitized = {}
        
        for key, value in params.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _is_suspicious(self, event: AuditEvent) -> bool:
        """Check if event indicates suspicious activity."""
        suspicious_patterns = [
            # Multiple failed actions
            event.event_type == AuditEventType.AGENT_ACTION_FAILED,
            # Permission escalation
            event.event_type == AuditEventType.PERMISSION_CHANGED,
            # Data export
            event.event_type == AuditEventType.DATA_EXPORTED,
        ]
        return any(suspicious_patterns)
    
    async def _send_alert(self, event: AuditEvent):
        """Send alert for suspicious activity."""
        # Integration with alerting system (PagerDuty, Slack, etc.)
        pass
```

---

## Security Checklist

### Before Deployment

- [ ] All secrets stored in environment variables or secret manager
- [ ] Database credentials rotated
- [ ] TLS certificates valid and pinned
- [ ] Rate limiting configured
- [ ] CORS policy restrictive
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Audit logging enabled
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies scanned for vulnerabilities

### Ongoing

- [ ] Regular security audits
- [ ] Penetration testing (quarterly)
- [ ] Dependency updates (weekly)
- [ ] Log monitoring and alerting
- [ ] Incident response plan tested
- [ ] User data access reviews
- [ ] Permission configuration audits

---

## Incident Response

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 | Data breach, service compromise | 15 minutes |
| P2 | Security vulnerability discovered | 1 hour |
| P3 | Suspicious activity detected | 4 hours |
| P4 | Security improvement needed | 24 hours |

### Response Steps

1. **Detect** - Automated monitoring alerts
2. **Contain** - Isolate affected systems
3. **Investigate** - Analyze audit logs
4. **Remediate** - Fix vulnerability
5. **Recover** - Restore service
6. **Review** - Post-incident analysis
]]>

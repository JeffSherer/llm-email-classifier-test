from typing import Dict

# In a real app, this could come from a DB or CRM system
USER_PROFILES = {
    "angry.customer@example.com": {"tone": "formal", "urgency_bias": "high"},
    "curious.shopper@example.com": {"tone": "friendly", "urgency_bias": "low"},
    "happy.user@example.com": {"tone": "enthusiastic", "urgency_bias": "low"},
    "tech.user@example.com": {"tone": "technical", "urgency_bias": "medium"},
    "business.client@example.com": {"tone": "professional", "urgency_bias": "medium"},
}

def get_user_profile(email_address: str) -> Dict:
    return USER_PROFILES.get(email_address, {"tone": "neutral", "urgency_bias": "unsure"})


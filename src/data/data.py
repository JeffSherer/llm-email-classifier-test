from typing import Dict

# Category definitions to anchor RAG-style prompting
CATEGORY_DEFINITIONS: Dict[str, str] = {
    "complaint": "A message expressing dissatisfaction or demanding resolution.",
    "inquiry": "A question or request for product or service information.",
    "feedback": "A comment providing praise, criticism, or a suggestion without requesting action.",
    "support_request": "A direct request for technical help or service support.",
    "other": "Does not fit into the above categories.",
}

# Example responses to guide tone/style for each category
SAMPLE_RESPONSES: Dict[str, str] = {
    "complaint": "We sincerely apologize for the inconvenience. Your issue is important, and we're here to make it right.",
    "inquiry": "Thank you for your question. We're happy to clarify any details to help with your decision.",
    "feedback": "We appreciate your feedback and will pass it on to the relevant team. Thank you for helping us improve.",
    "support_request": "Thank you for reporting this. We're looking into your issue and will respond with a solution as soon as possible.",
    "other": "Thank you for reaching out. We'll review your message and respond accordingly.",
}

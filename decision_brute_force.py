# Rule-Based Decision Table Implementation

DECISION_RULES = [
    # CRITICAL DENIAL RULES (Priority 1-10) - Check these first
    {
        "id": "fraud_denial",
        "priority": 1,
        "conditions": {
            "fraud_flag": "yes"
        },
        "decision": "DENY_REFUND",
        "reason": "Account flagged for fraud - all refunds denied",
        "confidence": 1.0
    },
    {
        "id": "suspended_account",
        "priority": 2,
        "conditions": {
            "account_status": "suspended"
        },
        "decision": "DENY_REFUND",
        "reason": "Suspended accounts are not eligible for refunds",
        "confidence": 1.0
    },
    
    # RETURN ABUSE RULES (Priority 11-20)
    {
        "id": "abuse_gold_exception",
        "priority": 11,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "yes",
            "loyalty_tier": "gold"
        },
        "decision": "OFFER_STORE_CREDIT",
        "reason": "Gold member with abuse history - store credit only",
        "confidence": 0.9
    },
    {
        "id": "abuse_silver_bronze_deny",
        "priority": 12,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "yes",
            "loyalty_tier": ["silver", "bronze"]  # Multiple values allowed
        },
        "decision": "DENY_REFUND",
        "reason": "Return abuse history - refund denied",
        "confidence": 0.95
    },
    
    # PERFECT APPROVAL SCENARIOS (Priority 21-30)
    {
        "id": "perfect_credit_card",
        "priority": 21,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": ["damaged", "defective"],
            "seller_type": "inhouse",
            "payment_method": "credit_card"
        },
        "decision": "APPROVE_FULL_REFUND",
        "reason": "Perfect case: Good customer, damaged item, within window, credit card",
        "confidence": 1.0
    },
    {
        "id": "perfect_paypal_debit",
        "priority": 22,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": ["damaged", "defective"],
            "seller_type": "inhouse",
            "payment_method": ["paypal", "debit_card"]
        },
        "decision": "APPROVE_FULL_REFUND",
        "reason": "Good customer, damaged item, within window - full refund approved",
        "confidence": 0.95
    },
    
    # PAYMENT METHOD RESTRICTIONS (Priority 31-40)
    {
        "id": "bnpl_store_credit",
        "priority": 31,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": ["damaged", "defective"],
            "seller_type": "inhouse",
            "payment_method": "bnpl"
        },
        "decision": "OFFER_STORE_CREDIT",
        "reason": "BNPL payments limited to store credit refunds",
        "confidence": 0.9
    },
    {
        "id": "gift_card_store_credit",
        "priority": 32,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": ["damaged", "defective"],
            "seller_type": "inhouse",
            "payment_method": "gift_card"
        },
        "decision": "OFFER_STORE_CREDIT",
        "reason": "Gift card purchases can only be refunded as store credit",
        "confidence": 0.9
    },
    
    # THIRD PARTY SELLER RULES (Priority 41-50)
    {
        "id": "thirdparty_partial",
        "priority": 41,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": ["damaged", "defective"],
            "seller_type": "thirdparty"
        },
        "decision": "APPROVE_PARTIAL_REFUND",
        "reason": "Third-party sellers: partial refund after seller fee deduction",
        "confidence": 0.85
    },
    
    # LOYALTY TIER BASED RULES FOR NORMAL ITEMS (Priority 51-60)
    {
        "id": "gold_normal_item",
        "priority": 51,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": "normal",
            "loyalty_tier": "gold"
        },
        "decision": "APPROVE_FULL_REFUND",
        "reason": "Gold members can return normal items - premium service",
        "confidence": 0.9
    },
    {
        "id": "silver_normal_item",
        "priority": 52,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no", 
            "return_abuse": "no",
            "return_window": "within",
            "item_condition": "normal",
            "loyalty_tier": "silver"
        },
        "decision": "OFFER_STORE_CREDIT",
        "reason": "Silver members: store credit for normal item returns",
        "confidence": 0.85
    },
    {
        "id": "bronze_normal_item",
        "priority": 53,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no", 
            "return_window": "within",
            "item_condition": "normal",
            "loyalty_tier": "bronze"
        },
        "decision": "DENY_REFUND",
        "reason": "Bronze members cannot return normal items (no defect)",
        "confidence": 0.9
    },
    
    # EXPIRED RETURN WINDOW RULES (Priority 61-70)
    {
        "id": "gold_late_damaged",
        "priority": 61,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "expired",
            "loyalty_tier": "gold",
            "item_condition": ["damaged", "defective"]
        },
        "decision": "APPROVE_PARTIAL_REFUND",
        "reason": "Gold member exception: partial refund for late defective items",
        "confidence": 0.75
    },
    {
        "id": "gold_late_normal",
        "priority": 62,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "expired",
            "loyalty_tier": "gold",
            "item_condition": "normal"
        },
        "decision": "OFFER_STORE_CREDIT",
        "reason": "Gold member late return: store credit only for normal items",
        "confidence": 0.7
    },
    {
        "id": "silver_bronze_late_deny",
        "priority": 63,
        "conditions": {
            "account_status": "good_standing",
            "fraud_flag": "no",
            "return_abuse": "no",
            "return_window": "expired",
            "loyalty_tier": ["silver", "bronze"]
        },
        "decision": "DENY_REFUND",
        "reason": "Late returns not allowed for silver/bronze members",
        "confidence": 0.95
    },
    
    # ACCOUNT ISSUES RULES (Priority 71-80)
    {
        "id": "issues_fraud_deny",
        "priority": 71,
        "conditions": {
            "account_status": "issues",
            "fraud_flag": "yes"
        },
        "decision": "DENY_REFUND",
        "reason": "Account has both issues and fraud flags - refund denied",
        "confidence": 1.0
    },
    {
        "id": "issues_no_fraud_review",
        "priority": 72,
        "conditions": {
            "account_status": "issues",
            "fraud_flag": "no"
        },
        "decision": "REQUIRE_MANUAL_REVIEW",
        "reason": "Account has issues but no fraud - human review required",
        "confidence": 0.9
    }
]

# Field priority order for "NEED_INFO" responses
FIELD_PRIORITY_ORDER = [
    "account_status",     # Must know first
    "fraud_flag",         # Security critical
    "return_abuse",       # Policy critical  
    "return_window",      # Time sensitive
    "item_condition",     # Affects decision type
    "loyalty_tier",       # Affects many rules
    "seller_type",        # Policy differences
    "payment_method",     # Refund method
    "item_category",      # Special rules
    "delivery_status"     # For specific cases
]

def make_refund_decision(data):
    """
    Rule-based decision making - replaces all if/else logic
    """
    # Sort rules by priority (lower number = higher priority)
    sorted_rules = sorted(DECISION_RULES, key=lambda x: x["priority"])
    
    # Try each rule in priority order
    for rule in sorted_rules:
        if matches_rule(data, rule["conditions"]):
            return {
                "decision": rule["decision"],
                "reason": rule["reason"],
                "confidence": rule["confidence"],
                "path": build_path_from_rule(rule, data),
                "rule_id": rule["id"]
            }
    
    # No rules matched - we need more information
    missing_field = find_next_needed_field(data)
    field_info = get_field_question_info(missing_field)
    
    return {
        "decision": "NEED_INFO",
        "field_needed": missing_field,
        "question": field_info["question"],
        "reason": field_info["reason"]
    }

def matches_rule(data, conditions):
    """
    Check if data matches all conditions in a rule
    Supports both single values and lists of values
    """
    for field, required_value in conditions.items():
        if field not in data:
            return False
        
        actual_value = get_field_value(data, field)
        
        # Handle list of acceptable values
        if isinstance(required_value, list):
            if actual_value not in required_value:
                return False
        else:
            # Single value requirement
            if actual_value != required_value:
                return False
    
    return True

def get_field_value(data, field):
    """
    Extract value from field data (handles both formats)
    """
    field_data = data[field]
    if isinstance(field_data, dict) and "value" in field_data:
        return field_data["value"]
    else:
        return field_data

def build_path_from_rule(rule, data):
    """
    Build decision path string from matched rule
    """
    path_parts = []
    for field, required_value in rule["conditions"].items():
        actual_value = get_field_value(data, field)
        path_parts.append(f"{field}={actual_value}")
    
    path_parts.append(rule["decision"])
    return " → ".join(path_parts)

def find_next_needed_field(data):
    """
    Find the next most important field we need
    """
    for field in FIELD_PRIORITY_ORDER:
        if field not in data:
            return field
    
    # Fallback - find any missing field
    from decision_nodes import DECISION_NODES
    for field in DECISION_NODES.keys():
        if field not in data:
            return field
    
    return "unknown_field"

def get_field_question_info(field):
    """
    Get appropriate question and reason for a field
    """
    field_questions = {
        "account_status": {
            "question": "What is your account status?",
            "reason": "Account status is the foundation of refund eligibility"
        },
        "fraud_flag": {
            "question": "Are there any fraud concerns with your account?",
            "reason": "Security check required before processing refund"
        },
        "return_abuse": {
            "question": "Do you have a history of excessive returns?",
            "reason": "Return history affects refund policy"
        },
        "return_window": {
            "question": "When did you purchase this item (within return window or expired)?",
            "reason": "Return timing is essential for determining eligibility"
        },
        "item_condition": {
            "question": "What condition is the item in (damaged/defective/normal)?",
            "reason": "Item condition is crucial for determining refund eligibility"
        },
        "loyalty_tier": {
            "question": "What is your loyalty tier (gold/silver/bronze)?",
            "reason": "Loyalty tier determines return policy and benefits"
        },
        "seller_type": {
            "question": "Who sold you this item - us directly or a marketplace seller?",
            "reason": "Seller type affects refund policy and amount"
        },
        "payment_method": {
            "question": "How did you pay for this item (credit card, PayPal, gift card, etc.)?",
            "reason": "Payment method determines refund type available"
        }
    }
    
    return field_questions.get(field, {
        "question": f"What is your {field}?",
        "reason": f"Need {field} information to continue"
    })

# Keep existing utility functions that other files use
def get_decision_outcomes():
    """Return all possible decision outcomes"""
    return [
        "APPROVE_FULL_REFUND",
        "APPROVE_PARTIAL_REFUND", 
        "OFFER_STORE_CREDIT",
        "DENY_REFUND",
        "REQUIRE_MANUAL_REVIEW",
        "NEED_INFO"
    ]

def get_critical_fields():
    """Return fields most important for making decisions"""
    return [
        "account_status",
        "fraud_flag", 
        "return_abuse",
        "loyalty_tier",
        "item_condition",
        "return_window",
        "payment_method",
        "seller_type"
    ]

def traverse_decision_tree(data):
    """
    Navigate the decision tree as far as possible with available data
    Returns detailed traversal information
    """
    result = make_refund_decision(data)
    
    if result["decision"] == "NEED_INFO":
        return {
            "status": "NEED_MORE_INFO",
            "stopping_field": result["field_needed"],
            "current_path": result.get("path", "Start"),
            "question": result["question"],
            "reason": result["reason"],
            "context": build_question_context(data, result["field_needed"])
        }
    else:
        return {
            "status": "DECISION_REACHED",
            "final_decision": result["decision"],
            "reason": result["reason"],
            "path": result["path"],
            "confidence": result.get("confidence", 1.0)
        }

def build_question_context(data, missing_field):
    """
    Build context for question generation based on available data
    """
    context = {
        "available_info": {},
        "customer_profile": {},
        "situation_summary": ""
    }
    
    # Extract available information
    for field, info in data.items():
        if isinstance(info, dict) and "value" in info:
            context["available_info"][field] = info["value"]
    
    # Build customer profile
    if "loyalty_tier" in context["available_info"]:
        context["customer_profile"]["tier"] = context["available_info"]["loyalty_tier"]
    if "account_status" in context["available_info"]:
        context["customer_profile"]["status"] = context["available_info"]["account_status"]
    
    # Create situation summary
    item_info = context["available_info"].get("item_category", "item")
    condition_info = context["available_info"].get("item_condition", "")
    
    if condition_info:
        context["situation_summary"] = f"Customer wants to return {condition_info} {item_info}"
    else:
        context["situation_summary"] = f"Customer wants to return {item_info}"
    
    return context

def get_next_logical_field(data):
    """
    Determine the most logical next field to ask about based on current data
    """
    # This follows the decision tree logic to find the next needed field
    result = make_refund_decision(data)
    if result["decision"] == "NEED_INFO":
        return result["field_needed"]
    return None
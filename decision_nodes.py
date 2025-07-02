# Definition of decision node data structure for extractable information

DECISION_NODES = {
    "account_status": {
        "description": "Customer account standing",
        "values": ["good_standing", "issues", "unknown"],
        "keywords": ["account", "standing", "suspended", "good", "bad", "issues"]
    },
    
    "loyalty_tier": {
        "description": "Customer loyalty level", 
        "values": ["gold", "silver", "bronze", "unknown"],
        "keywords": ["loyalty", "tier", "membership", "gold", "silver", "bronze", "premium"]
    },
    
    "fraud_flag": {
        "description": "Fraud flag on account",
        "values": ["yes", "no", "unknown"],
        "keywords": ["fraud", "security", "flag", "suspicious", "blocked"]
    },
    
    "return_abuse": {
        "description": "History of return abuse",
        "values": ["yes", "no", "unknown"], 
        "keywords": ["return abuse", "multiple returns", "frequent returns", "abuse"]
    },
    
    "item_category": {
        "description": "Type of item",
        "values": ["physical", "digital", "perishable", "unknown"],
        "keywords": ["physical", "digital", "download", "game", "software", "food", "electronics", "clothing"]
    },
    
    "item_condition": {
        "description": "Condition of item",
        "values": ["damaged", "defective", "normal", "unknown"],
        "keywords": ["damaged", "broken", "defective", "faulty", "not working", "cracked", "normal", "fine"]
    },
    
    "item_returnable": {
        "description": "Item returnability status",
        "values": ["yes", "no", "unknown"],
        "keywords": ["returnable", "non-returnable", "final sale", "no returns"]
    },
    
    "return_window": {
        "description": "Return timeframe status",
        "values": ["within", "expired", "unknown"],
        "keywords": ["days ago", "weeks ago", "months ago", "yesterday", "last week", "recently"]
    },
    
    "delivery_status": {
        "description": "Delivery status",
        "values": ["delivered", "not_delivered", "unknown"],
        "keywords": ["delivered", "received", "arrived", "not delivered", "never came", "missing"]
    },
    
    "shipping_issue_type": {
        "description": "Type of shipping issue",
        "values": ["lost", "delayed", "pending", "unknown"],
        "keywords": ["lost in transit", "lost", "delayed", "late", "pending", "stuck"]
    },
    
    "seller_type": {
        "description": "Seller type",
        "values": ["inhouse", "thirdparty", "unknown"],
        "keywords": ["sold by", "third party", "marketplace", "external seller", "directly"]
    },
    
    "payment_method": {
        "description": "Payment method used",
        "values": ["credit_card", "bnpl", "gift_card", "prepaid", "unknown"],
        "keywords": ["credit card", "debit card", "buy now pay later", "klarna", "afterpay", "gift card"]
    },
    
    "late_return_eligible": {
        "description": "Eligibility for late return",
        "values": ["yes", "no", "unknown"],
        "keywords": ["special circumstances", "exception", "late", "extenuating"]
    },
    
    "inhouse_policy_met": {
        "description": "Meets in-house policy requirements",
        "values": ["yes", "no", "unknown"],
        "keywords": ["policy", "requirements", "meets criteria", "qualifies"]
    },
    
    "thirdparty_policy_allows": {
        "description": "Third-party seller allows return",
        "values": ["yes", "no", "unknown"],
        "keywords": ["seller policy", "third party policy", "marketplace rules"]
    },
    
    "bnpl_allows_refund": {
        "description": "BNPL provider allows refunds",
        "values": ["yes", "no", "unknown"],
        "keywords": ["bnpl policy", "klarna refund", "afterpay refund"]
    },
    
    "gift_card_allows_refund": {
        "description": "Gift card terms allow cash refund",
        "values": ["yes", "no", "unknown"],
        "keywords": ["gift card refund", "store credit", "cash back"]
    }
}
# Utility functions for decision nodes

def get_node_info(node_name):
    return DECISION_NODES.get(node_name, {})

def get_all_nodes():
    return list(DECISION_NODES.keys())

def find_relevant_nodes(user_input):
    """Find relevant nodes based on keywords"""
    user_input_lower = user_input.lower()
    relevant = []
    
    for node_name, node_info in DECISION_NODES.items():
        keywords = node_info.get("keywords", [])
        for keyword in keywords:
            if keyword in user_input_lower:
                relevant.append(node_name)
                break
    
    return relevant
# Add to decision_brute_force.py

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
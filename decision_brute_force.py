def make_refund_decision(data):
    """
    Brute force decision tree - hardcoded every possible path
    Returns decision with reasoning and path taken
    """
    
    # Extract values with defaults - handle both account data and extracted data formats
    def get_value(field_name):
        if field_name in data:
            field_data = data[field_name]
            if isinstance(field_data, dict) and "value" in field_data:
                return field_data["value"]
            else:
                return field_data
        return "unknown"
    
    account_status = get_value("account_status")
    fraud_flag = get_value("fraud_flag") 
    return_abuse = get_value("return_abuse")
    loyalty_tier = get_value("loyalty_tier")
    item_condition = get_value("item_condition")
    return_window = get_value("return_window")
    payment_method = get_value("payment_method")
    seller_type = get_value("seller_type")
    item_category = get_value("item_category")
    delivery_status = get_value("delivery_status")
    
    # LEVEL 1: Account Status Check
    if account_status == "good_standing":
        
        # LEVEL 2: Fraud Flag Check
        if fraud_flag == "yes":
            return {
                "decision": "DENY_REFUND",
                "reason": "Account flagged for fraud - all refunds denied",
                "path": "good_standing → fraud_yes → DENY",
                "confidence": 1.0
            }
        
        elif fraud_flag == "no":
            
            # LEVEL 3: Return Abuse Check
            if return_abuse == "yes":
                
                # LEVEL 4: Loyalty Tier for Abuse Cases
                if loyalty_tier == "gold":
                    return {
                        "decision": "OFFER_STORE_CREDIT", 
                        "reason": "Gold member with abuse history - store credit only",
                        "path": "good_standing → no_fraud → abuse_yes → gold → STORE_CREDIT",
                        "confidence": 0.9
                    }
                elif loyalty_tier in ["silver", "bronze"]:
                    return {
                        "decision": "DENY_REFUND",
                        "reason": f"{loyalty_tier.title()} member with return abuse history",
                        "path": f"good_standing → no_fraud → abuse_yes → {loyalty_tier} → DENY",
                        "confidence": 0.95
                    }
                else:
                    return {
                        "decision": "NEED_INFO",
                        "field_needed": "loyalty_tier",
                        "question": "What is your loyalty tier status (gold/silver/bronze)?",
                        "reason": "Need loyalty tier to determine refund eligibility for customers with return history"
                    }
            
            elif return_abuse == "no":
                
                # LEVEL 4: Return Window Check
                if return_window == "within":
                    
                    # LEVEL 5: Item Condition Check
                    if item_condition in ["damaged", "defective"]:
                        
                        # LEVEL 6: Seller Type Check
                        if seller_type == "inhouse":
                            
                            # LEVEL 7: Payment Method Check
                            if payment_method == "credit_card":
                                return {
                                    "decision": "APPROVE_FULL_REFUND",
                                    "reason": "Perfect case: Good customer, damaged item, within window, credit card",
                                    "path": "good_standing → no_fraud → no_abuse → within → damaged → inhouse → credit_card → APPROVE_FULL",
                                    "confidence": 1.0
                                }
                            elif payment_method == "bnpl":
                                return {
                                    "decision": "OFFER_STORE_CREDIT",
                                    "reason": "BNPL payments limited to store credit refunds",
                                    "path": "good_standing → no_fraud → no_abuse → within → damaged → inhouse → bnpl → STORE_CREDIT",
                                    "confidence": 0.9
                                }
                            elif payment_method == "gift_card":
                                return {
                                    "decision": "OFFER_STORE_CREDIT", 
                                    "reason": "Gift card purchases can only be refunded as store credit",
                                    "path": "good_standing → no_fraud → no_abuse → within → damaged → inhouse → gift_card → STORE_CREDIT",
                                    "confidence": 0.9
                                }
                            elif payment_method in ["paypal", "debit_card"]:
                                return {
                                    "decision": "APPROVE_FULL_REFUND",
                                    "reason": f"{payment_method.title()} payments eligible for full refund",
                                    "path": f"good_standing → no_fraud → no_abuse → within → damaged → inhouse → {payment_method} → APPROVE_FULL",
                                    "confidence": 0.95
                                }
                            else:
                                return {
                                    "decision": "NEED_INFO",
                                    "field_needed": "payment_method",
                                    "question": "How did you pay for this item (credit card, PayPal, gift card, etc.)?",
                                    "reason": "Payment method determines refund type available"
                                }
                        
                        elif seller_type == "thirdparty":
                            return {
                                "decision": "APPROVE_PARTIAL_REFUND",
                                "reason": "Third-party sellers: partial refund after seller fee deduction",
                                "path": "good_standing → no_fraud → no_abuse → within → damaged → thirdparty → APPROVE_PARTIAL",
                                "confidence": 0.85
                            }
                        
                        else:
                            return {
                                "decision": "NEED_INFO",
                                "field_needed": "seller_type", 
                                "question": "Who sold you this item - us directly or a marketplace seller?",
                                "reason": "Seller type affects refund policy and amount"
                            }
                    
                    elif item_condition == "normal":
                        
                        # LEVEL 6: Loyalty Tier for Normal Items (change of mind)
                        if loyalty_tier == "gold":
                            return {
                                "decision": "APPROVE_FULL_REFUND",
                                "reason": "Gold members can return normal items - premium service",
                                "path": "good_standing → no_fraud → no_abuse → within → normal → gold → APPROVE_FULL",
                                "confidence": 0.9
                            }
                        elif loyalty_tier == "silver":
                            return {
                                "decision": "OFFER_STORE_CREDIT",
                                "reason": "Silver members: store credit for normal item returns",
                                "path": "good_standing → no_fraud → no_abuse → within → normal → silver → STORE_CREDIT",
                                "confidence": 0.85
                            }
                        elif loyalty_tier == "bronze":
                            return {
                                "decision": "DENY_REFUND",
                                "reason": "Bronze members cannot return normal items (no defect)",
                                "path": "good_standing → no_fraud → no_abuse → within → normal → bronze → DENY",
                                "confidence": 0.9
                            }
                        else:
                            return {
                                "decision": "NEED_INFO",
                                "field_needed": "loyalty_tier",
                                "question": "What is your loyalty tier (gold/silver/bronze)?",
                                "reason": "Loyalty tier determines return policy for normal items"
                            }
                    
                    else:
                        return {
                            "decision": "NEED_INFO",
                            "field_needed": "item_condition",
                            "question": "What condition is the item in (damaged/defective/normal)?",
                            "reason": "Item condition is crucial for determining refund eligibility"
                        }
                
                elif return_window == "expired":
                    
                    # LEVEL 5: Loyalty Tier for Expired Returns
                    if loyalty_tier == "gold":
                        if item_condition in ["damaged", "defective"]:
                            return {
                                "decision": "APPROVE_PARTIAL_REFUND",
                                "reason": "Gold member exception: partial refund for late defective items",
                                "path": "good_standing → no_fraud → no_abuse → expired → gold → defective → APPROVE_PARTIAL",
                                "confidence": 0.75
                            }
                        else:
                            return {
                                "decision": "OFFER_STORE_CREDIT",
                                "reason": "Gold member late return: store credit only for normal items",
                                "path": "good_standing → no_fraud → no_abuse → expired → gold → normal → STORE_CREDIT",
                                "confidence": 0.7
                            }
                    
                    elif loyalty_tier in ["silver", "bronze"]:
                        return {
                            "decision": "DENY_REFUND",
                            "reason": f"{loyalty_tier.title()} members cannot make returns after deadline",
                            "path": f"good_standing → no_fraud → no_abuse → expired → {loyalty_tier} → DENY",
                            "confidence": 0.95
                        }
                    
                    else:
                        return {
                            "decision": "NEED_INFO",
                            "field_needed": "loyalty_tier",
                            "question": "What is your loyalty tier? This affects late return policies.",
                            "reason": "Loyalty tier determines if late returns are eligible"
                        }
                
                else:
                    return {
                        "decision": "NEED_INFO",
                        "field_needed": "return_window",
                        "question": "When did you purchase this item (within return window or expired)?",
                        "reason": "Return timing is essential for determining eligibility"
                    }
            
            else:
                return {
                    "decision": "NEED_INFO",
                    "field_needed": "return_abuse",
                    "question": "Do you have a history of excessive returns?",
                    "reason": "Return history affects refund policy"
                }
        
        else:
            return {
                "decision": "NEED_INFO", 
                "field_needed": "fraud_flag",
                "question": "Are there any fraud concerns with your account?",
                "reason": "Security check required before processing refund"
            }
    
    elif account_status == "issues":
        
        # LEVEL 2: Fraud Check for Problem Accounts
        if fraud_flag == "yes":
            return {
                "decision": "DENY_REFUND",
                "reason": "Account has both issues and fraud flags - refund denied",
                "path": "issues → fraud_yes → DENY",
                "confidence": 1.0
            }
        elif fraud_flag == "no":
            return {
                "decision": "REQUIRE_MANUAL_REVIEW",
                "reason": "Account has issues but no fraud - human review required",
                "path": "issues → fraud_no → MANUAL_REVIEW",
                "confidence": 0.9
            }
        else:
            return {
                "decision": "NEED_INFO",
                "field_needed": "fraud_flag", 
                "question": "Are there any fraud concerns with your account?",
                "reason": "Need fraud status to determine review process"
            }
    
    elif account_status == "suspended":
        return {
            "decision": "DENY_REFUND",
            "reason": "Suspended accounts are not eligible for refunds",
            "path": "suspended → DENY",
            "confidence": 1.0
        }
    
    else:
        return {
            "decision": "NEED_INFO",
            "field_needed": "account_status",
            "question": "What is your account status?",
            "reason": "Account status is the foundation of refund eligibility"
        }

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
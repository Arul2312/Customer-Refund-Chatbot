# Updated conversation_manager.py with keyword extraction fix
from extractor import InformationExtractor
from decision_brute_force import traverse_decision_tree, build_question_context, get_critical_fields
from decision_nodes import DECISION_NODES
import json

class ConversationManager:
    """
    Manages the conversational flow for refund requests
    """
    
    def __init__(self, account_data_file="account_data.json"):
        self.extractor = InformationExtractor(account_data_file)
        self.conversation_history = []
        self.current_state = "INITIAL"
        self.current_field_needed = None  # Track what field we're asking about
        
    def start_conversation(self, initial_request):
        """
        Start a new refund conversation with initial request
        """
        print("REFUND REQUEST ANALYSIS")
        print("=" * 50)
        print(f"Processing: '{initial_request}'")
        
        # Enhanced initial extraction with item category detection
        extracted = self.enhance_initial_extraction(initial_request)
        
        if extracted:
            print(f"\nFound {len(extracted)} pieces of information:")
            for field, data in extracted.items():
                confidence_level = self.get_confidence_level(data['confidence'])
                print(f"  [{confidence_level}] {field}: {data['value']}")
        
        # Try to traverse decision tree
        return self.continue_conversation()
    
    def enhance_initial_extraction(self, initial_request):
        """
        Better extraction of item category and other details from initial request
        """
        # First do normal extraction
        extracted = self.extractor.extract_info(initial_request)
        
        # Add item category detection if not found
        if "item_category" not in extracted:
            item_keywords = {
                "laptop": "physical",
                "computer": "physical", 
                "phone": "physical",
                "tablet": "physical",
                "headphones": "physical",
                "electronics": "physical",
                "food": "perishable",
                "pizza": "perishable",
                "meal": "perishable",
                "groceries": "perishable",
                "software": "digital",
                "app": "digital",
                "course": "digital",
                "ebook": "digital",
                "download": "digital",
                "jacket": "physical",
                "shirt": "physical",
                "shoes": "physical",
                "clothing": "physical",
                "furniture": "physical",
                "appliance": "physical"
            }
            
            request_lower = initial_request.lower()
            for keyword, category in item_keywords.items():
                if keyword in request_lower:
                    # Add to extracted data manually
                    self.extractor.extracted_data["item_category"] = {
                        "value": category,
                        "confidence": 0.80,
                        "source": "user_input",
                        "reasoning": f"Detected '{keyword}' indicates {category} item"
                    }
                    extracted["item_category"] = self.extractor.extracted_data["item_category"]
                    break
        
        return extracted
    
    def continue_conversation(self):
        """
        Continue the conversation by traversing the decision tree
        """
        complete_data = self.extractor.get_complete_data()
        traversal_result = traverse_decision_tree(complete_data)
        
        if traversal_result["status"] == "DECISION_REACHED":
            return self.handle_final_decision(traversal_result)
        else:
            return self.handle_need_more_info(traversal_result)
    
    def handle_final_decision(self, result):
        """
        Handle when we've reached a final decision
        """
        print(f"\nDECISION REACHED!")
        print("=" * 30)
        print(f"RESULT: {result['final_decision']}")
        print(f"REASON: {result['reason']}")
        print(f"CONFIDENCE: {result['confidence']:.2f}")
        print(f"PATH: {result['path']}")
        
        # Show what information was used
        complete_data = self.extractor.get_complete_data()
        print(f"\nBased on the following information:")
        for field, info in complete_data.items():
            source_label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(info.get("source"), "UNKNOWN")
            print(f"  [{source_label}] {field}: {info['value']}")
        
        return {
            "status": "COMPLETE",
            "decision": result['final_decision'],
            "reason": result['reason']
        }
    
    def handle_need_more_info(self, result):
        """
        Handle when we need more information with progress indication
        """
        # Show progress
        complete_data = self.extractor.get_complete_data()
        critical_fields = get_critical_fields()
        
        available_critical = len([f for f in critical_fields if f in complete_data])
        total_critical = len(critical_fields)
        
        print(f"\nNeed more information to proceed...")
        print(f"Progress: {available_critical}/{total_critical} critical fields collected")
        print(f"Current decision path: {result['current_path']}")
        
        # Store what field we're asking about
        self.current_field_needed = result["stopping_field"]
        
        # Generate contextual question using LLM
        question = self.generate_smart_question(
            result["stopping_field"], 
            result["context"],
            result["question"]  # fallback question
        )
        
        print(f"\nQUESTION: {question}")
        
        return {
            "status": "NEED_INPUT",
            "question": question,
            "field_needed": result["stopping_field"]
        }
    
    def process_user_response(self, user_response):
        """
        Process user's response with better error handling and keyword matching
        """
        # Handle common uncertain responses
        if user_response.lower() in ['i dont know', "don't know", 'not sure', 'unsure', 'idk']:
            return self.handle_uncertain_response()
        
        if user_response.lower() in ['skip', 'next', 'pass']:
            return self.handle_skip_request()
        
        print(f"\nProcessing response: '{user_response}'")
        
        # First try direct keyword matching for the current field we're asking about
        direct_match = self.try_direct_keyword_match(user_response, self.current_field_needed)
        
        if direct_match:
            print("Direct keyword match found:")
            print(f"  {direct_match['field']}: {direct_match['value']} (confidence: {direct_match['confidence']:.2f})")
            
            # Add to extractor data
            self.extractor.extracted_data[direct_match['field']] = {
                "value": direct_match['value'],
                "confidence": direct_match['confidence'],
                "source": "user_input",
                "reasoning": f"Direct keyword match for {direct_match['field']}"
            }
        else:
            # Try normal LLM extraction
            extracted = self.extractor.extract_info(user_response)
            
            if extracted:
                print("Extracted new information:")
                for field, data in extracted.items():
                    print(f"  {field}: {data['value']} (confidence: {data['confidence']:.2f})")
            else:
                return self.handle_no_extraction(user_response)
        
        # Continue the conversation
        return self.continue_conversation()
    
    def try_direct_keyword_match(self, user_response, field_needed):
        """
        Try to match user response directly to field values
        """
        if not field_needed or field_needed not in DECISION_NODES:
            return None
        
        field_info = DECISION_NODES[field_needed]
        possible_values = field_info.get('values', [])
        
        response_lower = user_response.lower().strip()
        
        # Direct exact matches
        for value in possible_values:
            if response_lower == value.lower():
                return {
                    "field": field_needed,
                    "value": value,
                    "confidence": 0.95
                }
        
        # Partial matches and common variations
        keyword_mappings = {
            "seller_type": {
                "direct": ["inhouse", "directly", "official", "your store", "your website"],
                "third party": ["thirdparty", "third-party", "marketplace", "vendor", "seller", "partner"],
                "unknown": ["unknown", "not sure", "don't know", "unsure"]
            },
            "payment_method": {
                "credit_card": ["credit", "credit card", "visa", "mastercard", "amex"],
                "debit_card": ["debit", "debit card"],
                "paypal": ["paypal", "pay pal"],
                "bnpl": ["afterpay", "klarna", "buy now pay later", "bnpl"],
                "gift_card": ["gift card", "giftcard", "store credit"],
                "prepaid_card": ["prepaid", "prepaid card"]
            },
            "return_window": {
                "within": ["within", "recent", "recently", "last week", "few days", "yesterday"],
                "expired": ["expired", "long time", "months ago", "old", "while ago"]
            },
            "item_condition": {
                "damaged": ["damaged", "broken", "defective", "faulty"],
                "wrong_item": ["wrong", "incorrect", "different"],
                "not_as_described": ["not as described", "different than expected"],
                "change_of_mind": ["changed mind", "don't want", "don't need"]
            },
            "delivery_status": {
                "delivered": ["delivered", "received", "got it"],
                "not_delivered": ["never arrived", "didn't arrive", "not delivered", "missing"],
                "damaged_in_transit": ["damaged shipping", "broken in shipping", "arrived broken"]
            }
        }
        
        if field_needed in keyword_mappings:
            for value, keywords in keyword_mappings[field_needed].items():
                for keyword in keywords:
                    if keyword in response_lower:
                        # Map common terms back to official values
                        if field_needed == "seller_type":
                            if value == "direct":
                                return {"field": field_needed, "value": "inhouse", "confidence": 0.90}
                            elif value == "third party":
                                return {"field": field_needed, "value": "thirdparty", "confidence": 0.90}
                        
                        return {
                            "field": field_needed,
                            "value": value,
                            "confidence": 0.85
                        }
        
        return None
    
    def handle_uncertain_response(self):
        """
        Handle when user is uncertain about information
        """
        print("\nNo problem! Let me try a different approach.")
        
        # Get what we still need
        complete_data = self.extractor.get_complete_data()
        critical_fields = get_critical_fields()
        missing_critical = [f for f in critical_fields if f not in complete_data]
        
        if missing_critical:
            # Ask about a different field or provide more guidance
            next_field = missing_critical[0]
            field_info = DECISION_NODES.get(next_field, {})
            options = field_info.get('values', [])
            
            if options:
                print(f"Let me ask about something else. For {next_field}, the options are:")
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
                print("Which one best describes your situation?")
            else:
                print(f"Let me ask about {next_field} instead.")
        
        return {
            "status": "NEED_INPUT",
            "question": "Which option best describes your situation?",
            "field_needed": missing_critical[0] if missing_critical else None
        }
    
    def handle_skip_request(self):
        """
        Handle when user wants to skip a question
        """
        print("\nSkipping this question and trying to proceed...")
        
        # Try to make decision with current data
        complete_data = self.extractor.get_complete_data()
        traversal_result = traverse_decision_tree(complete_data)
        
        if traversal_result["status"] == "DECISION_REACHED":
            return self.handle_final_decision(traversal_result)
        else:
            # Ask about next most important field
            missing_fields = [f for f in get_critical_fields() if f not in complete_data]
            if missing_fields:
                next_field = missing_fields[0]
                self.current_field_needed = next_field
                print(f"I'll ask about {next_field} instead, which is also important for your refund.")
                
                return {
                    "status": "NEED_INPUT",
                    "question": f"Can you tell me about your {next_field}?",
                    "field_needed": next_field
                }
            else:
                print("Let me try to make a decision with what we have...")
                return self.continue_conversation()
    
    def handle_no_extraction(self, user_response):
        """
        Handle when no information could be extracted from user response
        """
        print("I didn't catch any specific information from that response.")
        print("Could you try being more specific?")
        
        # Show options for current field
        if self.current_field_needed and self.current_field_needed in DECISION_NODES:
            field_info = DECISION_NODES[self.current_field_needed]
            options = field_info.get('values', [])
            
            if options:
                print(f"\nFor {self.current_field_needed}, I'm looking for one of these:")
                for option in options:
                    print(f"  • {option}")
                print("Which one matches your situation?")
                
                # Also show common ways to say each option
                if self.current_field_needed == "seller_type":
                    print("\nOr you can say:")
                    print("  • 'directly from you' or 'your website' for inhouse")
                    print("  • 'marketplace seller' or 'third party' for thirdparty")
                    print("  • 'not sure' for unknown")
        
        return {
            "status": "NEED_INPUT",
            "question": "Could you be more specific?",
            "field_needed": self.current_field_needed
        }
    
    def generate_smart_question(self, missing_field, context, fallback_question):
        """
        Generate a contextual question using LLM
        """
        try:
            # Get field description for context
            field_info = DECISION_NODES.get(missing_field, {})
            field_description = field_info.get('description', '')
            field_options = field_info.get('values', [])
            
            # Build context for LLM
            situation = context.get("situation_summary", "Customer refund request")
            available_info = context.get("available_info", {})
            
            # Create more specific prompts based on field type
            if missing_field == "return_window":
                prompt = f"""Generate a customer service question asking when they purchased the item.

Context: {situation}
What we know: {', '.join([f"{k}={v}" for k, v in available_info.items()])}

Make it conversational and explain why timing matters for the return policy.
Keep it under 50 words."""

            elif missing_field == "payment_method":
                prompt = f"""Generate a customer service question asking how they paid.

Context: {situation}
What we know: {', '.join([f"{k}={v}" for k, v in available_info.items()])}
Options: {', '.join(field_options)}

Explain that payment method affects refund options. Keep it under 50 words."""

            elif missing_field == "seller_type":
                prompt = f"""Generate a customer service question asking if they bought from us directly or a marketplace seller.

Context: {situation}
What we know: {', '.join([f"{k}={v}" for k, v in available_info.items()])}

Explain that this affects which policy applies. Keep it under 50 words."""

            else:
                prompt = f"""Generate a natural customer service question to ask about: {missing_field}

Context: {situation}
What we know: {', '.join([f"{k}={v}" for k, v in available_info.items()])}
Field description: {field_description}
Possible values: {', '.join(field_options)}

Make it conversational, helpful, and explain why you need this information.
Keep it under 50 words."""

            # Use extractor's LLM to generate question
            response = self.extractor.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            generated_question = response.choices[0].message.content.strip()
            # Remove quotes if LLM added them
            if generated_question.startswith('"') and generated_question.endswith('"'):
                generated_question = generated_question[1:-1]
            
            return generated_question
            
        except Exception as e:
            print(f"Warning: Could not generate smart question ({e}), using fallback")
            return fallback_question
    
    def get_confidence_level(self, confidence):
        """Convert numeric confidence to readable level"""
        if confidence >= 0.9:
            return "VERY HIGH"
        elif confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_conversation_summary(self):
        """Get summary of current conversation state"""
        complete_data = self.extractor.get_complete_data()
        return {
            "total_fields": len(complete_data),
            "completion_percentage": self.extractor.get_completion_percentage(),
            "available_data": complete_data
        }
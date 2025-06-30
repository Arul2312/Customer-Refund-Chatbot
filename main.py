from extractor import InformationExtractor
from decision_nodes import DECISION_NODES
from decision_brute_force import make_refund_decision, get_decision_outcomes, get_critical_fields
import json
import sys

def main():
    """
    Main application loop for the Enhanced Refund Bot with Decision Tree
    Handles account data loading, information extraction, and automated decision making
    """
    
    # Application Header
    print("=" * 80)
    print("ENHANCED REFUND BOT - AI Information Extractor + Decision Tree")
    print("=" * 80)
    print("Features: Account Integration • Natural Language Processing • Automated Decisions")
    print("\nHow to use:")
    print("   • Describe your refund situation in natural language")
    print("   • System will extract information and guide you to a decision")
    print("   • Use commands for advanced features")
    
    print(f"\nAvailable Commands:")
    print("   'show'    - Display all extracted information")
    print("   'missing' - Show what information is still needed") 
    print("   'decide'  - Make refund decision with current data")
    print("   'guide'   - Interactive step-by-step decision process")
    print("   'stats'   - View extraction and decision statistics")
    print("   'nodes'   - See all available fields and options")
    print("   'clear'   - Reset extracted data (preserves account data)")
    print("   'help'    - Show detailed help and examples")
    print("   'quit'    - Exit application")
    print("-" * 80)
    
    # Initialize extractor with account data
    try:
        extractor = InformationExtractor("account_data.json")
        print("System ready! Start by describing your refund situation...\n")
    except Exception as e:
        print(f"Warning: Could not load account data - {e}")
        print("System will work with extracted information only.\n")
        extractor = InformationExtractor()
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
                
            # ==================== COMMAND HANDLING ====================
            
            # Exit commands
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\nThank you for using Enhanced Refund Bot!")
                print("Your session data has been cleared for privacy.")
                print("Run again anytime for new refund requests. Goodbye!")
                break
            
            # Show current information
            elif user_input.lower() in ['show', 's']:
                show_extracted_data(extractor)
                continue
                
            # Show missing fields
            elif user_input.lower() in ['missing', 'm']:
                show_missing_fields(extractor)
                continue
                
            # Make decision with current data
            elif user_input.lower() in ['decide', 'd']:
                make_decision(extractor)
                continue
                
            # Interactive guided decision process
            elif user_input.lower() in ['guide', 'g']:
                interactive_guide(extractor)
                continue
                
            # Clear extracted data (preserve account data)
            elif user_input.lower() in ['clear', 'reset', 'c']:
                extractor.clear_data()
                print("Extracted data cleared successfully!")
                print("Account data preserved for continued use.")
                print("Ready for new refund request description...")
                continue
                
            # Show all available nodes/fields
            elif user_input.lower() in ['nodes', 'fields', 'n']:
                show_all_nodes()
                continue
                
            # Show help information
            elif user_input.lower() in ['help', 'h', '?']:
                show_help()
                continue
                
            # Show statistics
            elif user_input.lower() in ['stats', 'statistics', 'info']:
                show_stats(extractor)
                continue
            
            # ================== NATURAL LANGUAGE PROCESSING ==================
            
            print(f"\nAnalyzing your request: '{user_input}'")
            print("Processing with AI...")
            
            # Get current context for extraction
            context = extractor.get_complete_data()
            
            # Extract information using LLM
            extracted = extractor.extract_info(user_input, context)
            
            # Process extraction results
            if extracted:
                print(f"\nFound {len(extracted)} new pieces of information:")
                
                # Display extracted information with confidence levels
                for field, data in extracted.items():
                    confidence_level = get_confidence_level(data['confidence'])
                    
                    print(f"  [{confidence_level}] {field}: {data['value']}")
                    
                    # Show reasoning if available
                    if data.get('reasoning'):
                        print(f"      Reasoning: {data['reasoning']}")
                    
                    # Show confidence score
                    print(f"      Confidence: {data['confidence']:.2f}")
                
                # Check if we can make a decision now
                print(f"\nChecking decision readiness...")
                decision_status = auto_decision_check(extractor)
                
                if decision_status["can_decide"]:
                    print(f"READY: {decision_status['message']}")
                    print(f"Type 'decide' to see the final refund decision!")
                else:
                    print(f"WAITING: {decision_status['message']}")
                    if decision_status.get('next_field'):
                        print(f"Most helpful next: {decision_status['next_field']}")
                
            else:
                print(f"\nNo new information extracted from your message.")
                print(f"Try being more specific about:")
                print(f"   • When you bought the item")
                print(f"   • What's wrong with it") 
                print(f"   • How you paid")
                print(f"   • Item condition")
                
                # Show what we still need
                missing = extractor.get_missing_fields()
                if missing:
                    critical_missing = [f for f in get_critical_fields() if f in missing]
                    if critical_missing:
                        print(f"Critical missing: {', '.join(critical_missing[:3])}")
            
            # Show current progress
            print(f"\nProgress Update:")
            completion = extractor.get_completion_percentage()
            complete_data = extractor.get_complete_data()
            
            # Progress bar
            progress_filled = int(completion / 10)
            progress_bar = "█" * progress_filled + "░" * (10 - progress_filled)
            print(f"   [{progress_bar}] {completion:.1f}% complete ({len(complete_data)}/{len(DECISION_NODES)} fields)")
            
            # Quick summary of key information
            critical_fields = get_critical_fields()
            critical_available = [f for f in critical_fields if f in complete_data]
            
            if critical_available:
                print(f"   Key info: {len(critical_available)}/{len(critical_fields)} critical fields")
                
                # Show top 3 most confident extractions
                if complete_data:
                    sorted_data = sorted(complete_data.items(), 
                                       key=lambda x: x[1].get('confidence', 0), 
                                       reverse=True)
                    top_3 = sorted_data[:3]
                    
                    print(f"   Top confident: ", end="")
                    for i, (field, data) in enumerate(top_3):
                        if i > 0:
                            print(", ", end="")
                        source_label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(data.get("source"), "UNKNOWN")
                        print(f"{source_label}:{field}({data.get('confidence', 0):.2f})", end="")
                    print()
            
            print()  # Add spacing for next input
            
        except KeyboardInterrupt:
            print(f"\n\nSession interrupted by user (Ctrl+C)")
            print(f"Your progress has been saved in memory.")
            confirm = input("Do you want to exit? (y/n): ").lower()
            if confirm in ['y', 'yes']:
                print(f"Goodbye! Thanks for using Enhanced Refund Bot.")
                break
            else:
                print(f"Continuing session...")
                continue
                
        except Exception as e:
            print(f"\nUnexpected error occurred: {str(e)}")
            print(f"Please try again or contact support if the issue persists.")
            print(f"You can also try:")
            print(f"   • 'clear' to reset and start over")
            print(f"   • 'help' for usage guidance")
            print(f"   • 'quit' to exit safely")
            continue

# ================== HELPER FUNCTIONS FOR MAIN ==================

def get_confidence_level(confidence):
    """Convert numeric confidence to readable level"""
    if confidence >= 0.9:
        return "VERY HIGH"
    elif confidence >= 0.8:
        return "HIGH"
    elif confidence >= 0.7:
        return "MEDIUM"
    else:
        return "LOW"

def auto_decision_check(extractor):
    """Check if decision can be made and return status"""
    complete_data = extractor.get_complete_data()
    result = make_refund_decision(complete_data)
    
    if result["decision"] != "NEED_INFO":
        return {
            "can_decide": True,
            "message": f"Decision ready: {result['decision']}",
            "decision": result["decision"]
        }
    else:
        missing_field = result.get('field_needed')
        return {
            "can_decide": False,
            "message": f"Still need information about: {missing_field}",
            "next_field": missing_field
        }

def make_decision(extractor):
    """Make refund decision using brute force tree"""
    complete_data = extractor.get_complete_data()
    
    print(f"\nMAKING REFUND DECISION...")
    print("=" * 50)
    
    result = make_refund_decision(complete_data)
    
    if result["decision"] == "NEED_INFO":
        print(f"NEED MORE INFORMATION:")
        print(f"   Field Required: {result['field_needed']}")
        print(f"   Question: {result['question']}")
        print(f"   Why: {result['reason']}")
        
        # Show what we do have
        print(f"\nCurrent Information:")
        critical_fields = get_critical_fields()
        for field in critical_fields:
            if field in complete_data:
                value = complete_data[field].get('value', 'unknown')
                source = complete_data[field].get('source', 'unknown')
                source_label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(source, "UNKNOWN")
                print(f"   [{source_label}] {field}: {value}")
            else:
                print(f"   [MISSING] {field}: missing")
    
    else:
        print(f"FINAL DECISION: {result['decision']}")
        print(f"Reason: {result['reason']}")
        print(f"Decision Path: {result['path']}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        
        # Show what data was used for decision
        print(f"\nDecision Based On:")
        for field, info in complete_data.items():
            if field in get_critical_fields():
                source_label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(info.get("source"), "UNKNOWN")
                print(f"   [{source_label}] {field}: {info['value']}")

def interactive_guide(extractor):
    """Interactive step-by-step decision guidance"""
    print(f"\nINTERACTIVE DECISION GUIDE")
    print("=" * 40)
    print("I'll guide you through getting all the information needed for a decision.")
    print("Answer each question, or type 'skip' to move on.\n")
    
    complete_data = extractor.get_complete_data()
    max_attempts = 10  # Prevent infinite loops
    attempt = 0
    
    while attempt < max_attempts:
        result = make_refund_decision(complete_data)
        
        if result["decision"] == "NEED_INFO":
            field_needed = result["field_needed"]
            question = result["question"]
            
            print(f"QUESTION: {question}")
            user_response = input("Your answer: ").strip()
            
            if user_response.lower() == 'skip':
                print("Skipping this question...\n")
                break
            elif user_response.lower() in ['quit', 'exit']:
                return
            elif user_response:
                # Extract information from the response
                extracted = extractor.extract_info(f"Regarding {field_needed}: {user_response}")
                complete_data = extractor.get_complete_data()
                print()  # Add spacing
            else:
                print("Please provide an answer or type 'skip'\n")
        else:
            # We have a decision!
            print(f"DECISION REACHED!")
            print(f"RESULT: {result['decision']}")
            print(f"REASON: {result['reason']}")
            break
        
        attempt += 1
    
    if attempt >= max_attempts:
        print("Maximum questions reached. Type 'decide' to see current decision status.")

def show_extracted_data(extractor):
    """Display all available data (account + extracted)"""
    complete_data = extractor.get_complete_data()
    
    if not complete_data:
        print("\nNo information available yet.")
        print("Try describing your refund situation!")
        return
    
    print(f"\nCOMPLETE INFORMATION ({len(complete_data)} fields):")
    print("=" * 50)
    
    # Group by categories for better display
    categories = {
        "Customer Info": ["account_status", "loyalty_tier", "fraud_flag", "return_abuse"],
        "Item Details": ["item_category", "item_condition", "item_returnable"],
        "Timing": ["return_window", "late_return_eligible"],
        "Delivery": ["delivery_status", "shipping_issue_type"],
        "Business": ["seller_type", "inhouse_policy_met", "thirdparty_policy_allows"],
        "Payment": ["payment_method", "bnpl_allows_refund", "gift_card_allows_refund"]
    }
    
    for category, fields in categories.items():
        category_data = {field: complete_data[field] for field in fields if field in complete_data}
        if category_data:
            print(f"\n{category}:")
            for field, info in category_data.items():
                node_desc = DECISION_NODES.get(field, {}).get('description', '')
                confidence_level = get_confidence_level(info['confidence'])
                source_label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(info.get("source"), "UNKNOWN")
                print(f"  [{source_label}] {field}: {info['value']} [{confidence_level}]")
                print(f"    Description: {node_desc}")
                if info.get('reasoning'):
                    print(f"    Reasoning: {info['reasoning']}")

def show_missing_fields(extractor):
    """Display missing fields categorized"""
    missing = extractor.get_missing_fields()
    total = len(DECISION_NODES)
    available = len(extractor.get_complete_data())
    
    if not missing:
        print(f"\nALL FIELDS COMPLETE!")
        print(f"All {total} required fields have been identified.")
        print("Ready for decision tree processing!")
        return
    
    print(f"\nMISSING INFORMATION ({len(missing)} fields):")
    print("=" * 50)
    
    # Highlight critical missing fields
    critical_fields = get_critical_fields()
    critical_missing = [field for field in missing if field in critical_fields]
    
    if critical_missing:
        print(f"\nCRITICAL for Decision Making:")
        for field in critical_missing:
            node_info = DECISION_NODES.get(field, {})
            description = node_info.get('description', 'No description')
            print(f"   • {field}: {description}")
    
    # Group remaining missing fields by categories
    categories = {
        "Customer Info": ["account_status", "loyalty_tier", "fraud_flag", "return_abuse"],
        "Item Details": ["item_category", "item_condition", "item_returnable"],
        "Timing": ["return_window", "late_return_eligible"],
        "Delivery": ["delivery_status", "shipping_issue_type"],
        "Business": ["seller_type", "inhouse_policy_met", "thirdparty_policy_allows"],
        "Payment": ["payment_method", "bnpl_allows_refund", "gift_card_allows_refund"]
    }
    
    other_missing = [field for field in missing if field not in critical_fields]
    if other_missing:
        print(f"\nOther Missing Fields:")
        for category, fields in categories.items():
            missing_in_category = [field for field in fields if field in other_missing]
            if missing_in_category:
                print(f"\n{category}:")
                for field in missing_in_category:
                    node_info = DECISION_NODES.get(field, {})
                    description = node_info.get('description', 'No description')
                    print(f"  • {field}: {description}")

def show_all_nodes():
    """Display all available fields and their options"""
    print(f"\nALL AVAILABLE FIELDS ({len(DECISION_NODES)} total):")
    print("=" * 60)
    
    # Highlight critical fields
    critical_fields = get_critical_fields()
    
    categories = {
        "CRITICAL for Decisions": critical_fields,
        "Customer Info": ["account_status", "loyalty_tier", "fraud_flag", "return_abuse"],
        "Item Details": ["item_category", "item_condition", "item_returnable"],
        "Timing": ["return_window", "late_return_eligible"],
        "Delivery": ["delivery_status", "shipping_issue_type"],
        "Business": ["seller_type", "inhouse_policy_met", "thirdparty_policy_allows"],
        "Payment": ["payment_method", "bnpl_allows_refund", "gift_card_allows_refund"]
    }
    
    for category, fields in categories.items():
        if category == "CRITICAL for Decisions":
            print(f"\n{category}:")
            for field in fields:
                if field in DECISION_NODES:
                    node_info = DECISION_NODES[field]
                    description = node_info.get('description', 'No description')
                    values = ', '.join(node_info.get('values', []))
                    print(f"  * {field}: {description}")
                    print(f"    Options: {values}")
        else:
            print(f"\n{category}:")
            for field in fields:
                if field in DECISION_NODES and field not in critical_fields:
                    node_info = DECISION_NODES[field]
                    description = node_info.get('description', 'No description')
                    values = ', '.join(node_info.get('values', []))
                    print(f"  • {field}: {description}")
                    print(f"    Options: {values}")

def show_stats(extractor):
    """Show extraction statistics including account data"""
    complete_data = extractor.get_complete_data()
    extracted_data = extractor.get_extracted_data()
    account_data = extractor.account_data
    high_conf = extractor.get_high_confidence_data()
    completion = extractor.get_completion_percentage()
    
    print(f"\nEXTRACTION STATISTICS:")
    print("=" * 30)
    print(f"Account data fields: {len([k for k, v in complete_data.items() if v.get('source') == 'account_data'])}")
    print(f"Extracted from input: {len(extracted_data)}")
    print(f"Total available fields: {len(complete_data)}")
    print(f"High confidence fields: {len(high_conf)}")
    print(f"Completion percentage: {completion:.1f}%")
    
    if complete_data:
        avg_confidence = sum(item['confidence'] for item in complete_data.values()) / len(complete_data)
        print(f"Average confidence: {avg_confidence:.2f}")
    
    # Show breakdown by source
    if complete_data:
        sources = {}
        for field, data in complete_data.items():
            source = data.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\nBreakdown by source:")
        for source, count in sources.items():
            label = {"account_data": "ACCOUNT", "user_input": "INPUT", "inferred": "INFERRED"}.get(source, "UNKNOWN")
            print(f"  {label}: {count} fields")
    
    # Decision readiness
    critical_fields = get_critical_fields()
    critical_available = [field for field in critical_fields if field in complete_data]
    critical_missing = [field for field in critical_fields if field not in complete_data]
    
    print(f"\nDecision Readiness:")
    print(f"  Critical fields available: {len(critical_available)}/{len(critical_fields)}")
    if critical_missing:
        print(f"  Still need: {', '.join(critical_missing)}")
    else:
        print(f"  READY for decision making!")

def show_help():
    """Display help information and usage examples"""
    print(f"\nHELP - Enhanced Refund Bot with Decision Tree")
    print("=" * 60)
    
    print(f"\nPURPOSE:")
    print("This bot extracts information from refund requests and makes automated")
    print("refund decisions using a comprehensive decision tree.")
    
    print(f"\nHOW TO USE:")
    print("Simply describe your refund situation in natural language:")
    print("• 'I want to return my broken laptop from last week'")
    print("• 'The food never arrived and I paid with credit card'")
    print("• 'My software download won't install properly'")
    print("• 'I need to return this jacket - wrong size'")
    
    print(f"\nCOMMANDS:")
    print("• show     - Display all extracted information")
    print("• missing  - Show what information is still needed")
    print("• decide   - Make a refund decision with current data")
    print("• guide    - Interactive step-by-step decision process")
    print("• stats    - View extraction and decision statistics")
    print("• nodes    - See all available fields and options")
    print("• clear    - Reset extracted data (keeps account data)")
    print("• help     - Show this help message")
    print("• quit     - Exit the application")
    
    print(f"\nDECISION OUTCOMES:")
    outcomes = get_decision_outcomes()
    for outcome in outcomes:
        if outcome != "NEED_INFO":
            print(f"• {outcome}")
    
    print(f"\nDATA SOURCES:")
    print("ACCOUNT - Loaded from your account file")
    print("INPUT - Extracted from your messages")
    print("INFERRED - Deduced from context and account info")
    
    print(f"\nTIPS:")
    print("• Use 'guide' for step-by-step question answering")
    print("• Use 'decide' to see if a decision can be made")
    print("• Be specific about timing, payment method, and item condition")
    print("• The system needs critical fields for decision making")

if __name__ == "__main__":
        main()
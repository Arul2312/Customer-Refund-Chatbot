from conversation_manager import ConversationManager
from extractor import InformationExtractor
from decision_nodes import DECISION_NODES
from decision_brute_force import make_refund_decision, get_decision_outcomes, get_critical_fields
import json
import sys

def main():
    """
    Main application with conversational refund processing
    """
    print("=" * 70)
    print("CONVERSATIONAL REFUND BOT - Intelligent Decision Tree")
    print("=" * 70)
    print("Describe your refund request and I'll guide you through the process.")
    print("\nCommands available: 'reset', 'status', 'help', 'quit'")
    print("-" * 70)
    
    # Initialize conversation manager
    try:
        conversation = ConversationManager("account_data.json")
        print("System ready! What would you like to return today?\n")
    except Exception as e:
        print(f"Warning: {e}")
        conversation = ConversationManager()
    
    # Main conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using Conversational Refund Bot!")
                break
            
            elif user_input.lower() in ['reset', 'start over']:
                conversation = ConversationManager("account_data.json")
                print("Conversation reset. What would you like to return?")
                continue
            
            elif user_input.lower() in ['status', 'summary']:
                show_conversation_status(conversation)
                continue
            
            elif user_input.lower() in ['help', '?']:
                show_conversational_help()
                continue
            
            # Process as part of ongoing conversation
            if conversation.current_state == "INITIAL":
                # This is the initial refund request
                result = conversation.start_conversation(user_input)
                conversation.current_state = "IN_PROGRESS"
            else:
                # This is a response to our question
                result = conversation.process_user_response(user_input)
            
            # Check if conversation is complete
            if result["status"] == "COMPLETE":
                print(f"\nRefund request processed successfully!")
                print(f"You can start a new request or type 'quit' to exit.")
                conversation.current_state = "COMPLETE"
            elif result["status"] == "NEED_INPUT":
                # Continue waiting for user response
                pass
            
        except KeyboardInterrupt:
            print(f"\n\nSession interrupted. Type 'quit' to exit or continue...")
            continue
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'help' for assistance.")
            continue

def show_conversation_status(conversation):
    """Show current conversation status"""
    summary = conversation.get_conversation_summary()
    print(f"\nCONVERSATION STATUS:")
    print(f"Fields collected: {summary['total_fields']}")
    print(f"Completion: {summary['completion_percentage']:.1f}%")
    print(f"Current state: {conversation.current_state}")

def show_conversational_help():
    """Show help for conversational mode"""
    print(f"\nCONVERSATIONAL REFUND BOT HELP:")
    print("=" * 40)
    print("This bot uses natural conversation to process refund requests.")
    print("\nHow it works:")
    print("1. Describe what you want to return")
    print("2. Answer the questions I ask")
    print("3. Get your refund decision")
    print("\nExample conversation:")
    print("You: 'I want to return my broken laptop'")
    print("Bot: 'When did you purchase this laptop?'")
    print("You: 'Last week'")
    print("Bot: 'Did you buy it directly from us?'")
    print("You: 'Yes, from your website'")
    print("Bot: 'How did you pay?'")
    print("You: 'Credit card'")
    print("Bot: 'Approved for full refund!'")
    print("\nCommands:")
    print("• reset - Start a new refund request")
    print("• status - Show conversation progress")
    print("• help - Show this help")
    print("• quit - Exit the bot")

if __name__ == "__main__":
    main()
import openai
import json
import re
from config import OPENAI_API_KEY, MODEL_NAME, CONFIDENCE_THRESHOLD, MAX_TOKENS, TEMPERATURE
from decision_nodes import DECISION_NODES, find_relevant_nodes

class InformationExtractor:
    
    def __init__(self, account_data_file="account_data.json"):
        """Initialize OpenAI client and load account data"""
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # Main storage: extracted information stored here during session
        self.extracted_data = {}
        # Account data loaded from JSON file
        self.account_data = self.load_account_data(account_data_file)
    
    def load_account_data(self, filename):
        """Load customer account data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"✅ Loaded account data for: {data.get('customer_id', 'Unknown Customer')}")
            return data
        except FileNotFoundError:
            print(f"⚠️  Account data file {filename} not found. Using empty account data.")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {filename}. Using empty account data.")
            return {}
    
    def get_complete_data(self):
        """Returns combined account data and extracted data"""
        complete_data = {}
        
        # Add account data (map to decision node fields)
        account_mapping = {
            "account_status": "account_status",
            "loyalty_tier": "loyalty_tier", 
            "fraud_flag": "fraud_flag",
            "return_abuse": "return_abuse"
        }
        
        for account_field, decision_field in account_mapping.items():
            if account_field in self.account_data:
                complete_data[decision_field] = {
                    "value": self.account_data[account_field],
                    "confidence": 1.0,
                    "source": "account_data",
                    "reasoning": f"From customer account: {account_field}"
                }
        
        # Add extracted data (override account data if higher confidence)
        for field, data in self.extracted_data.items():
            if field in complete_data:
                # Keep higher confidence data
                if data.get("confidence", 0) > complete_data[field].get("confidence", 0):
                    complete_data[field] = {**data, "source": "user_input"}
            else:
                complete_data[field] = {**data, "source": "user_input"}
        
        return complete_data

    def extract_info(self, user_input, context=None):
        """Main method: extracts information from user input using account context"""
        # Include account data in context
        enhanced_context = self.get_complete_data()
        prompt = self._build_optimized_prompt(user_input, enhanced_context)
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise information extraction system. Extract information from customer refund requests using account context. Return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            extracted = self._parse_response(content)
            
            # Update main storage with new extractions
            self._update_data(extracted)
            
            return extracted
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return {}
    
    def _build_optimized_prompt(self, user_input, context):
        """Builds prompt with account data context and focuses on relevant fields"""
        context_str = ""
        if context:
            # Separate account data from extracted data
            account_info = {k: v["value"] for k, v in context.items() if v.get("source") == "account_data"}
            extracted_info = {k: v["value"] for k, v in context.items() if v.get("source") == "user_input"}
            
            if account_info:
                context_str += f"Customer account info: {', '.join([f'{k}: {v}' for k, v in account_info.items()])}\n"
            if extracted_info:
                context_str += f"Previously extracted: {', '.join([f'{k}: {v}' for k, v in extracted_info.items()])}\n"
        
        # Find relevant nodes based on keywords
        relevant_nodes = find_relevant_nodes(user_input)
        if not relevant_nodes:
            relevant_nodes = list(DECISION_NODES.keys())[:8]
        
        node_descriptions = []
        for node_name in relevant_nodes:
            node_info = DECISION_NODES[node_name]
            values = ", ".join(node_info["values"])
            node_descriptions.append(f"{node_name}: {values}")
        
        return f"""Extract refund information from the customer message using account context.

Customer message: "{user_input}"
{context_str}
Available fields to extract:
{chr(10).join(node_descriptions)}

Rules:
1. Use information explicitly stated in the message
2. Use account context to infer information when logical
3. Use "unknown" if information is unclear or missing
4. Provide confidence score (0.0-1.0) based on certainty
5. Only include extractions with confidence > 0.7
6. Mark source as "inferred" if using account context to deduce information

Response format (JSON):
{{
    "extractions": {{
        "field_name": {{
            "value": "extracted_value",
            "confidence": 0.85,
            "reasoning": "brief explanation including source"
        }}
    }}
}}

If no clear information found, return: {{"extractions": {{}}}}"""
    
    def _parse_response(self, content):
        """Converts JSON response to validated dictionary"""
        try:
            data = json.loads(content)
            extractions = data.get("extractions", {})
            
            # Validate each extraction
            validated = {}
            for field, extraction in extractions.items():
                if (field in DECISION_NODES and 
                    isinstance(extraction, dict) and
                    "value" in extraction and
                    "confidence" in extraction):
                    validated[field] = extraction
            
            return validated
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {}
    
    def _update_data(self, new_extractions):
        """Updates self.extracted_data with new extractions using confidence-based merging"""
        for field, data in new_extractions.items():
            if field in DECISION_NODES:
                confidence = data.get("confidence", 0)
                value = data.get("value", "unknown")
                
                # Validate value against allowed options
                allowed_values = DECISION_NODES[field]["values"]
                if value not in allowed_values:
                    continue
                
                if confidence >= CONFIDENCE_THRESHOLD:
                    # Update if new field or higher confidence
                    if (field not in self.extracted_data or 
                        confidence > self.extracted_data[field].get("confidence", 0)):
                        self.extracted_data[field] = data
    
    def get_extracted_data(self):
        """Returns all data stored in self.extracted_data"""
        return self.extracted_data
    
    def get_missing_fields(self):
        """Returns list of fields not yet available (account + extracted)"""
        all_fields = set(DECISION_NODES.keys())
        complete_data = self.get_complete_data()
        available_fields = set(complete_data.keys())
        return list(all_fields - available_fields)
    
    def clear_data(self):
        """Empties self.extracted_data storage (keeps account data)"""
        self.extracted_data = {}
    
    def get_completion_percentage(self):
        """Calculates percentage of fields available (account + extracted)"""
        total = len(DECISION_NODES)
        complete_data = self.get_complete_data()
        available = len(complete_data)
        return (available / total) * 100 if total > 0 else 0
    
    def display_progress(self):
        """Shows current extraction progress with visual bars"""
        total = len(DECISION_NODES)
        complete_data = self.get_complete_data()
        available = len(complete_data)
        percentage = self.get_completion_percentage()
        
        print(f"\nProgress: {available}/{total} fields available ({percentage:.1f}% complete)")
        
        if complete_data:
            print("\nAvailable Information:")
            for field, data in complete_data.items():
                # Visual confidence bar
                confidence = data.get('confidence', 0)
                confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
                source_emoji = {"account_data": "👤", "user_input": "💬", "inferred": "🔍"}.get(data.get("source"), "❓")
                print(f"  {source_emoji} {field}: {data['value']} [{confidence_bar}] {confidence:.2f}")
        
        missing = self.get_missing_fields()
        if missing and len(missing) <= 5:
            print(f"\nStill needed:")
            for field in missing:
                node_info = DECISION_NODES.get(field, {})
                print(f"  • {field}: {node_info.get('description', '')}")
        elif missing:
            print(f"\nStill needed: {len(missing)} more fields (type 'missing' to see all)")
    
    def get_high_confidence_data(self, threshold=0.8):
        """Returns only extractions above confidence threshold from complete data"""
        complete_data = self.get_complete_data()
        return {
            field: data for field, data in complete_data.items()
            if data.get("confidence", 0) >= threshold
        }
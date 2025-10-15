"""LLM client for NAI endpoints"""
import requests
import json
import warnings
from typing import List, Dict, Optional

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class NAIClient:
    """Client for Nutanix AI endpoints"""
    
    def __init__(self, api_key: str, endpoint_url: str, model_name: str, max_tokens: int = 512):
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def chat_completion(self, messages: List[Dict], 
                       tools: Optional[List[Dict]] = None,
                       temperature: float = 0.01,
                       max_tokens: int = None) -> Dict:
        """Make a chat completion request"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Warning: LLM request failed: {e}")
            return {"choices": [{"message": {"content": "Analysis unavailable", "role": "assistant"}}]}
    
    def extract_tool_calls(self, response: Dict) -> List[Dict]:
        """Extract tool calls from LLM response"""
        if not response.get('choices'):
            return []
        
        message = response['choices'][0].get('message', {})
        tool_calls = message.get('tool_calls', [])
        
        return tool_calls
    
    def format_tool_response(self, tool_call_id: str, tool_result: Dict) -> Dict:
        """Format tool execution result for LLM"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(tool_result)
        }


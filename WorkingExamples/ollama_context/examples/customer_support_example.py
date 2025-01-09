# examples/customer_support_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import sys
import asyncio  
import signal

class SupportResponse(BaseModel):
    greeting: str
    solution: str
    next_steps: list[str]
    escalation_needed: bool
    reference_links: Optional[list[str]] = None

class CustomerProfile(BaseModel):
    id: str
    tier: str
    history: list[str]
    preferences: dict[str, str]
    active_subscriptions: list[str]

async def cleanup(engine):
    """Properly cleanup engine resources."""
    try:
        if hasattr(engine, '_loop') and engine._loop and not engine._loop.is_closed():
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

async def handle_shutdown(engine):
    """Handle shutdown signals gracefully."""
    await cleanup(engine)
    sys.exit(0)

async def setup_signal_handlers(engine):
    """Set up signal handlers for graceful shutdown."""
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(handle_shutdown(engine))
        )

async def main():
    # Initialize engine
    engine = ContextEngine(
        mode="auto",
        log_level=logging.INFO,
        database="examples/support_db"
    )
    
    # Set up signal handlers
    await setup_signal_handlers(engine)
    
    try:
        # Support knowledge base
        kb_content = """
        Product Documentation:
        
        Common Issues:
        1. Login Problems
        - Check email verification
        - Reset password if needed
        - Clear browser cache
        
        2. Billing Issues
        - Update payment method
        - View invoice history
        - Cancel subscription
        
        3. Performance Issues
        - Check system requirements
        - Clear application cache
        - Update to latest version
        
        Escalation Policy:
        - Tier 1: Basic troubleshooting
        - Tier 2: Technical issues
        - Tier 3: Complex problems
        - Emergency: System outages
        
        Response Guidelines:
        - Be courteous and professional
        - Acknowledge the issue
        - Provide clear steps
        - Follow up as needed
        """
        
        # Save knowledge base
        with open("examples/support_kb.txt", "w") as f:
            f.write(kb_content)
        
        # Index with metadata
        engine.load_and_index_documents(
            "examples/support_kb.txt",
            metadatas=[
                {"category": "technical"},
                {"category": "billing"},
                {"category": "policy"}
            ]
        )
        
        # Register support templates
        response_template = """
        Support Level: {level}
        Tone: {tone}
        Language: {language}
        Customer Tier: {customer_tier}
        Response Format:
        1. Greeting
        2. Understanding
        3. Solution
        4. Next Steps
        5. Closing
        """
        
        profile_template = """
        Customer ID: {id}
        Support Tier: {tier}
        Language: {language}
        Previous Issues: {history}
        Preferences: {preferences}
        """
        
        # Set up contexts
        response_vars = {
            "level": "Tier 1",
            "tone": "Professional and friendly",
            "language": "English",
            "customer_tier": "Premium"
        }
        
        profile_vars = {
            "id": "CUST-123",
            "tier": "Premium",
            "language": "English",
            "history": "Previous login issues",
            "preferences": "Email communication preferred"
        }
        
        engine.register_context("response", response_template, response_vars)
        engine.register_context("profile", profile_template, profile_vars)
        
        # Example 1: Handle login issue using RAG mode
        print("\n=== Login Issue Response (RAG Mode) ===")
        login_response = engine.query_structured(
            prompt="Customer cannot log in after password reset",
            response_model=SupportResponse,
            where={"category": "technical"},
            mode="retrieval"  # Using only RAG
        )
        print(f"Greeting: {login_response.greeting}")
        print(f"Solution: {login_response.solution}")
        print("Next Steps:")
        for step in login_response.next_steps:
            print(f"- {step}")
        if login_response.reference_links:
            print("Reference Links:")
            for link in login_response.reference_links:
                print(f"- {link}")
        
        # Example 2: Get customer profile using CAG mode
        print("\n=== Customer Profile (CAG Mode) ===")
        profile = engine.query_structured(
            prompt="Get customer profile information",
            response_model=CustomerProfile,
            context_name="profile",
            mode="context"  # Using only CAG
        )
        print(f"Customer ID: {profile.id}")
        print(f"Tier: {profile.tier}")
        print(f"History: {', '.join(profile.history)}")
        print(f"Preferences: {profile.preferences}")
        print(f"Active Subscriptions: {', '.join(profile.active_subscriptions)}")
        
        # Example 3: Handle billing inquiry using combined mode
        print("\n=== Billing Inquiry (Combined Mode) ===")
        billing_response = engine.query(
            prompt="Customer wants to update payment method",
            context_name="response",
            where={"category": "billing"},
            mode="combined"  # Using both RAG and CAG
        )
        print(billing_response['result'])
        
        # Example 4: Use default auto mode for escalation policy
        print("\n=== Escalation Policy Query (Auto Mode) ===")
        auto_response = engine.query(
            prompt="What's the escalation policy for technical issues?",
            context_name="response",
            where={"category": "policy"}
            # No mode specified - uses default auto mode
        )
        print(auto_response['result'])
        
        # Example 5: Update context and handle follow-up
        print("\n=== Follow-up Query with Updated Context ===")
        # Update the response context with urgency
        engine.update_context_variables(
            "response",
            {
                "level": "Tier 2",
                "tone": "Urgent and professional"
            }
        )
        
        urgent_response = engine.query(
            prompt="Customer reports critical system outage",
            context_name="response",
            where={"category": "policy"},
            mode="combined"
        )
        print(urgent_response['result'])
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Ensure proper cleanup
        await cleanup(engine)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import uuid
from .models import ChatMessage, ChatSession


def chatbot_home(request):
    return render(request, 'chatbot/chatbot.html')


@require_POST
def chatbot_message(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = data.get('message', '')
    session_id_str = data.get('session_id', '')

    session = None
    if session_id_str:
        try:
            session_uuid = uuid.UUID(session_id_str)
            session, created = ChatSession.objects.get_or_create(session_id=session_uuid)
        except (ValueError, TypeError):
            session = ChatSession.objects.create()

    if not session:
        session = ChatSession.objects.create()

    response = get_bot_response(user_message)

    ChatMessage.objects.create(
        session=session,
        user=request.user if request.user.is_authenticated else None,
        role='user',
        message=user_message,
    )

    ChatMessage.objects.create(
        session=session,
        user=request.user if request.user.is_authenticated else None,
        role='bot',
        message=response,
        response=user_message,
    )

    return JsonResponse({'reply': response, 'session_id': str(session.session_id)})


def get_bot_response(message):
    message_lower = message.lower()
    
    # Product-related queries
    if 'product' in message_lower or 'buy' in message_lower:
        return "We offer various digital products including bots, automation tools, website templates, and courses. You can browse our products on the home page. What type of product are you looking for?"
    
    # Price-related queries
    if 'price' in message_lower or 'cost' in message_lower or 'how much' in message_lower:
        return "Our prices vary by product. We accept both USD and GBP. You can switch currency using the selector in the top right corner. Check individual product pages for specific pricing."
    
    # Order-related queries
    if 'order' in message_lower or 'delivery' in message_lower or 'download' in message_lower:
        return "Digital products are delivered instantly after payment via download link. You can also access your orders from your account dashboard. Need help with a specific order?"
    
    # Payment-related queries
    if 'payment' in message_lower or 'stripe' in message_lower or 'credit card' in message_lower:
        return "We accept payments via Stripe, which supports all major credit and debit cards. Your payment information is secure and encrypted. We support both USD and GBP currencies."
    
    # Support-related queries
    if 'help' in message_lower or 'support' in message_lower or 'contact' in message_lower:
        return "I'm here to help! You can ask me about products, pricing, orders, payments, or any other questions. For complex issues, you can also reach us via email at support@macgunjon.com"
    
    # Greeting
    if 'hello' in message_lower or 'hi' in message_lower or 'hey' in message_lower:
        return "Hello! Welcome to Mac GunJon - Is Bot. How can I help you today? I can assist with product information, orders, payments, and more."
    
    # Default response
    return "I'm not sure I understand. Could you please rephrase your question? I can help with products, orders, payments, and general support."

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os

# IMPORT YOUR ML BRAIN
# Ensure your file is named 'ml_brain.py' in the same folder
from .ml_brain import get_response 

# ==========================================
# 1. AUTHENTICATION VIEWS
# ==========================================

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken.'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')

    return render(request, 'signup.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

# ==========================================
# 2. MAIN PAGE VIEWS
# ==========================================

def home(request):
    return render(request, 'home_page.html') # Ensure this matches your template filename

@login_required(login_url='login')
def chatbot(request):
    return render(request, 'chatbot.html')

@login_required(login_url='login')
def prakriti_assessment(request):
    return render(request, 'prakriti_assessment.html')

@login_required(login_url='login')
def yoga_recommendation(request):
    return render(request, 'yoga_recommendation.html')

@login_required(login_url='login')
def personalized_diet_and_lifestyle(request):
    return render(request, 'personalized_diet_and_lifestyle.html')

@login_required(login_url='login')
def result(request):
    return render(request, 'result.html')

# ==========================================
# 3. DYNAMIC DASHBOARD LOGIC
# ==========================================

@login_required(login_url='login')
def dashboard(request):
    # 1. Fetch Vitals & Health Data (with defaults)
    vitals = request.session.get('vitals', {
        'heart_rate': 72, 
        'spo2': 98, 
        'steps': 5000, 
        'sleep': '7h',
        'condition': 'None' # Stores diseases like Migraine, Diabetes etc.
    })
    
    # 2. Fetch Prakriti Result (from Assessment)
    prakriti = request.session.get('prakriti_result', None) 
    
    # 3. Generate Smart Suggestions based on Prakriti
    suggestions = {
        'yoga': 'Surya Namaskar (Sun Salutation)',
        'diet': 'Balanced home-cooked meals',
        'lifestyle': 'Maintain a consistent sleep schedule'
    }
    
    if prakriti:
        p_lower = prakriti.lower()
        if 'vata' in p_lower:
            suggestions = {
                'yoga': 'Tree Pose (Vrikshasana) for grounding',
                'diet': 'Warm soups, cooked grains, ghee, ginger',
                'lifestyle': 'Routine is key. Sleep early and stay warm.'
            }
        elif 'pitta' in p_lower:
            suggestions = {
                'yoga': 'Moon Salutation (Chandra Namaskar) for cooling',
                'diet': 'Sweet fruits, cucumber, mint, avoid spicy food',
                'lifestyle': 'Avoid overheating and conflicts. Stay cool.'
            }
        elif 'kapha' in p_lower:
            suggestions = {
                'yoga': 'Warrior Pose (Virabhadrasana) for energy',
                'diet': 'Spicy, light foods, honey, avoid dairy/sweets',
                'lifestyle': 'Vigorous exercise and wake up before 6 AM.'
            }

    return render(request, 'dashboard.html', {
        'user': request.user.username,
        'vitals': vitals,
        'prakriti': prakriti,
        'suggestions': suggestions
    })

# ==========================================
# 4. API ENDPOINTS (DATA HANDLING)
# ==========================================

# Chatbot API
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # CALL THE ML BRAIN
            bot_reply = get_response(user_message)
            
            return JsonResponse({'response': bot_reply})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'response': 'My brain is offline temporarily.'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Save Prakriti Result (From Assessment Page)
@csrf_exempt
def save_prakriti_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prakriti = data.get('result')
            
            # Save to user session
            request.session['prakriti_result'] = prakriti
            request.session.modified = True
            
            return JsonResponse({'status': 'success', 'message': 'Prakriti saved'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Update Vitals (From Dashboard Edit Modal)
@csrf_exempt
def update_vitals(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get existing vitals from session
            current_vitals = request.session.get('vitals', {})
            
            # Update with new data (Heart Rate, Steps, Disease, etc.)
            current_vitals.update(data)
            
            # Save back to session
            request.session['vitals'] = current_vitals
            request.session.modified = True
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)
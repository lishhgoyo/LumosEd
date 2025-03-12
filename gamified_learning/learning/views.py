from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Badge,Reward
from django.utils.timezone import now
import random
from django.db.models import Avg
from .models import LearningActivity, Recommendation
import google.generativeai as genai
from .models import QuizAttempt

genai.configure(api_key="AIzaSyC6y4wisGIhFzvoXA4OYowPsQQeRYwqKcA")
# Create your views here.
def home(request):
    return render(request, 'learning/home.html')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'learning/dashboard.html', {'user': request.user})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Signup successful! You can log in now.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match!")

    return render(request, 'learning/signup.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'learning/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

@login_required
def complete_task(request):
    profile = request.user.profile
    profile.add_xp(10)  # Award 10 XP for completing a task
    profile.update_streak()
    
    #Award extra XP for 5-day streaks
    if profile.streak % 5 == 0:
        profile.add_xp(20)

    # Check for badge eligibility
    beginner_badge, _ = Badge.objects.get_or_create(name="Beginner", description="Earned for reaching 50 XP")
    intermediate_badge, _ = Badge.objects.get_or_create(name="Intermediate", description="Earned for reaching 200 XP")
    advanced_badge, _ = Badge.objects.get_or_create(name="Advanced", description="Earned for reaching 500 XP")

    if profile.xp >= 50 and beginner_badge not in profile.badges.all():
        profile.badges.add(beginner_badge)
    if profile.xp >= 200 and intermediate_badge not in profile.badges.all():
        profile.badges.add(intermediate_badge)
    if profile.xp >= 500 and advanced_badge not in profile.badges.all():
        profile.badges.add(advanced_badge)
        
    # Check for streak-based badge
    streak_badge, _ = Badge.objects.get_or_create(name="Streak Master", description="Maintain a 7-day streak!")
    if profile.streak >= 7 and streak_badge not in profile.badges.all():
        profile.badges.add(streak_badge)

    profile.save()
    return redirect('dashboard')

@login_required
def leaderboard(request):
    users = Profile.objects.filter(user__is_superuser=False).order_by('-xp')[:10]  # Top 10 users
    return render(request, 'learning/leaderboard.html', {'users': users})

@login_required
def rewards(request):
    available_rewards = Reward.objects.filter(required_xp__lte=request.user.profile.xp)
    return render(request, 'learning/rewards.html', {'rewards': available_rewards})

@login_required
def daily_challenge(request):
    profile = request.user.profile
    challenge_xp = 20  # XP reward for completing the daily challenge
    
    if profile.last_active == now().date():
        messages.error(request, "You have already completed today's challenge!")
    else:
        profile.add_xp(challenge_xp)
        profile.update_streak()
        messages.success(request, f"You earned {challenge_xp} XP from today's challenge!")

    return redirect('dashboard')

@login_required
def personalized_recommendations(request):
    user = request.user
    avg_score = LearningActivity.objects.filter(user=user).aggregate(Avg('score'))['score__avg'] or 0

    # Determine learning level
    if avg_score < 50:
        level = "Beginner"
    elif 50 <= avg_score < 80:
        level = "Intermediate"
    else:
        level = "Advanced"

    # Sample content recommendations (Replace with database-driven content)
    content_options = {
        "Beginner": ["Introduction to Python", "Basic Data Types", "Loops & Conditionals"],
        "Intermediate": ["Object-Oriented Programming", "Data Structures", "API Integrations"],
        "Advanced": ["Machine Learning Basics", "AI Model Training", "Deep Learning Frameworks"]
    }

    recommendation = Recommendation.objects.create(
        user=user,
        content=random.choice(content_options[level]),
        level=level
    )

    return render(request, 'learning/recommendations.html', {'recommendation': recommendation})

@login_required
def personalized_quiz(request):
    user = request.user
    avg_score = LearningActivity.objects.filter(user=user).aggregate(Avg('score'))['score__avg'] or 0

    # Adjust quiz difficulty based on performance
    if avg_score < 50:
        quiz_difficulty = "Easy"
    elif 50 <= avg_score < 80:
        quiz_difficulty = "Medium"
    else:
        quiz_difficulty = "Hard"

    return render(request, 'learning/quiz.html', {'difficulty': quiz_difficulty})

@login_required
def generate_quiz(request, topic):
    """Generates a quiz using Gemini AI."""
    
    # Check if the user already took a quiz today
    profile = request.user.profile
    if profile.last_quiz_taken == now().date():
        messages.error(request, "You have already taken a quiz today!")
        return redirect('dashboard')
    
    avg_score = QuizAttempt.objects.filter(user=request.user).aggregate(Avg('score'))['score__avg'] or 0
    difficulty = "Easy" if avg_score < 50 else "Medium" if avg_score < 80 else "Hard"

    prompt = f"""
    Generate a {difficulty} difficulty multiple-choice quiz on {topic}. 
    Include 5 questions, each with 4 answer choices and a correct answer in JSON format:
    Example:
    {{
        "questions": [
            {{"text": "What is Python?", "choices": ["Language", "Snake", "Tool", "None"], "correct_answer": "Language"}},
            ...
        ]
    }}
    """

    response = genai.generate_text(prompt)
    quiz_data = response.text  # Extract AI-generated quiz data

    return render(request, 'learning/quiz.html', {'quiz': quiz_data, 'topic': topic,'difficulty': difficulty})

@login_required
def submit_quiz(request):
    """Validates quiz answers and awards XP only if answered correctly."""
    
    if request.method == "POST":
        profile = request.user.profile
        correct_answers = int(request.POST.get("correct_answers", 0))
        total_questions = int(request.POST.get("total_questions", 5))
        difficulty = request.POST.get("difficulty", "Easy")
        topic = request.POST.get("topic", "General")

        xp_rewards = {"Easy": 10, "Medium": 30, "Hard": 50}
        
        QuizAttempt.objects.create(
            user=request.user,
            topic=topic,
            score=correct_answers,
            total_questions=total_questions,
            difficulty=difficulty,
        )

        # Ensure at least 80% accuracy for XP reward
        if correct_answers >= (0.8 * total_questions):
            if profile.last_quiz_taken != now().date():  # Prevent multiple XP gains per day
                profile.add_xp(xp_rewards[difficulty])
                profile.last_quiz_taken = now().date()
                profile.save()
                messages.success(request, f"You earned {xp_rewards[difficulty]} XP!")
            else:
                messages.error(request, "XP already awarded for today!")
        else:
            messages.warning(request, "You need 80% accuracy to earn XP.")

        return redirect('dashboard')

    return redirect('quiz')

@login_required
def quiz_history(request):
    quizzes = QuizAttempt.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'learning/quiz_history.html', {'quizzes': quizzes})






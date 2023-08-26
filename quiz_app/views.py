from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import Question, Score, UserDetails, QuestionCategory, UserResponse, EmailVerification
from .forms import UserAnswerForm, UserDetailsForm
import random, json
from django.db.models import Sum
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import reverse

def index(request):
    return render(request, 'index.html')

def user_details(request):
    print("Session data:", request.session)
    print("Session quiz_start_time:", request.session.get('quiz_start_time'))
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            # Create and save a UserDetails instance
            user_details = UserDetails.objects.create(name=name, email=email)
            request.session['user_details_id'] = user_details.id

            all_questions = list(Question.objects.all())
            print(all_questions)
            random.shuffle(all_questions)
            print(all_questions)
            
            # Store the shuffled question order in the session
            question_order = [question.code for question in all_questions]
            print(question_order)
            request.session['question_order'] = question_order
                      
            if 'quiz_start_time' in request.session:
                request.session['quiz_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("the time is :", request.session['quiz_start_time'])
                print("quiz")
                return redirect('quiz')
            print("noquiz")   
            return render(request, 'user_details.html', {'form': form, 'email': email, 'show_verification': True})
                            
    else:
        form = UserDetailsForm()
    return render(request, 'user_details.html', {'form': form})

def send_verification_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if email:
            email_verification = EmailVerification(email=email)
            email_verification.save()  # This will generate the verification code in the save method

            subject = 'Email Verification'
            message = f'Your verification code is: {email_verification.verification_code}'
            from_email = 'chandusekhar.0904@gmail.com'  # Replace with your email
            recipient_list = [email]

            try:
                print("heloo")
                send_mail(subject, message, from_email, recipient_list)
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error_message': str(e)})

        return JsonResponse({'success': False, 'error_message': 'Email not provided'})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
         
def verify_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        verification_code = data.get('verification_code')
        print(email, verification_code)

        try:
            print("try block")
            email_verification = EmailVerification.objects.filter(email=email, verification_code=verification_code).exists()
            print(email,verification_code)
            print(email_verification)
            if email_verification == True:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error_message': 'Incorrect verification code'})

        except EmailVerification.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Incorrect verification code'})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

def get_user_responses(request):
    user_responses = request.session.get('user_responses', {})
    return JsonResponse({'user_responses': user_responses})

def quiz(request, question_number=None):
    user_details_id = request.session.get('user_details_id')
    if not user_details_id:
        return redirect('user_details')
    
    user_details = UserDetails.objects.get(pk=user_details_id)

    total_questions_limit_per_user = 6
    
    question_order = request.session.get('question_order')
    if not question_order:
        return redirect('user_details')  # Redirect to user details if question order is not found

    if 'quiz_question_order' not in request.session:
        request.session['quiz_question_order'] = question_order

    quiz_question_order = request.session['question_order']
    quiz_questions = [Question.objects.get(code=code) for code in quiz_question_order]
    quiz_questions_list = list(quiz_questions)
    
    if 'user_responses' not in request.session:
        request.session['user_responses'] = {}
    user_responses_dict = request.session['user_responses']

    question_status_dict = {}  # Create the dictionary here

    question_number = question_number or 1  # Use 1 as default if question_number is None

    for q_number, question_code in enumerate(quiz_question_order, start=1):
        if question_code in user_responses_dict:
            if user_responses_dict[question_code]:
                question_status_dict[q_number] = 'answered_saved'
            else:
                question_status_dict[q_number] = 'answered_not_saved'
        elif q_number < question_number:
            question_status_dict[q_number] = 'answered_not_saved'
        else:
            question_status_dict[q_number] = 'not_answered'
    
    # Handle question navigation
    if question_number is None:
        question_number = int(request.GET.get('question_number', 1))
    if question_number < 1:
        question_number = 1
    elif question_number > total_questions_limit_per_user:
        del request.session['quiz_question_order']
        return redirect('quiz_finished')
    
    total_questions = len(quiz_questions)
    next_question_number = question_number + 1 if question_number is not None else None

    # Calculate the next question number
    is_last_question = question_number == total_questions_limit_per_user

    # Get the current question
    current_question = quiz_questions[question_number - 1]

    quiz_numbers = list(range(1, total_questions_limit_per_user + 1))

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'Save Answer' or action == 'Next':
            # Handle saving or updating the user's answer in the database
            question_code = request.POST.get('question_code')
            user_answer = request.POST.get(f'question_{question_code}', '')

            question = Question.objects.get(code=question_code)
            correct_answer = question.correct_answer  # Get the correct answer

            is_correct = user_answer.lower() == correct_answer.lower()
            score = question.max_score if is_correct else 0

            # Delete any previous UserResponse for this question
            UserResponse.objects.filter(user=user_details, question=question).delete()

            # Create or update the UserResponse for the current question
            user_response, created = UserResponse.objects.get_or_create(
                user=user_details,
                question=question,
                defaults={'user_answer': user_answer, 'correct_answer': correct_answer, 'score': score}
            )

            if not created:
                user_response.user_answer = user_answer
                user_response.correct_answer = correct_answer
                user_response.score = score
                user_response.save()

            user_responses_dict[question_code] = user_answer
            request.session['user_responses'] = user_responses_dict

            if action == 'Next':
                return redirect('quiz_with_number', question_number=next_question_number)

        elif action == 'Submit All':
            # Save all answers and redirect to the quiz finished page
            for question in quiz_questions:
                question_code = question.code
                user_answer = request.POST.get(f'question_{question_code}', '')

                if user_answer:
                    correct_answer = question.correct_answer  # Get the correct answer
                    is_correct = user_answer.lower() == correct_answer.lower()
                    score = question.max_score if is_correct else 0

                    user_response, created = UserResponse.objects.get_or_create(
                        user=user_details,
                        question=question,
                        defaults={'user_answer': user_answer, 'correct_answer': correct_answer, 'score': score}
                    )

                    if not created:
                        user_response.user_answer = user_answer
                        user_response.correct_answer = correct_answer
                        user_response.score = score
                        user_response.save()

            # Calculate and update the total score for user_details
            total_score = UserResponse.objects.filter(user=user_details).aggregate(total_score=Sum('score'))['total_score']
            user_details.total_score = total_score or 0
            user_details.save()

            del request.session['quiz_question_order']
            del request.session['user_responses']
            return redirect('quiz_finished')

    # Prepare a dictionary with user's responses for rendering
    user_responses_dict = {}
    user_responses = UserResponse.objects.filter(user=user_details, question__in=quiz_questions)
    for response in user_responses:
        user_responses_dict[response.question.code] = response.user_answer

    form = UserAnswerForm(questions=quiz_questions_list, user=user_details, prefix='answer', initial=user_responses_dict)

    return render(
    request,
    'quiz.html',
    {
        'form': form,
        'question_data' : (current_question, user_responses_dict.get(current_question.code, None)),
        'question': current_question,
        'question_number': question_number,
        'next_question_number': next_question_number,        
        'total_questions_limit': total_questions_limit_per_user,
        'quiz_numbers': quiz_numbers,
        'user_responses_dict': user_responses_dict,
        'is_last_question': is_last_question,  # Pass the variable to the template
        'quiz_start_time' : request.session.get('quiz_start_time'),
        'question_status_dict': question_status_dict,
        
    }
)
    
def save_user_response(request):
    if request.method == 'POST':
        user_details_id = request.session.get('user_details_id')
        if user_details_id:
            user_details = UserDetails.objects.get(pk=user_details_id)
            question_code = request.POST.get('question_code')
            user_answer = request.POST.get('user_answer')

            question = Question.objects.get(code=question_code)
            is_correct = user_answer == question.correct_answer
            score = question.max_score if is_correct else 0

            # Create the UserResponse instance without answered_question_codes
            user_response = UserResponse(
                user=user_details,
                question=question,
                user_answer=user_answer,
                score=score,
            )
            user_response.save()  # Manually call the save method to execute custom logic

            # Update the user's total score
            user_details.total_score += score
            user_details.save()

            # Create the Score instance
            score_instance = Score(
                user=user_details,
                total_score=user_details.total_score,  # Use the user's total score
            )
            score_instance.save()

            return redirect('next_question_url')  # Replace with the actual URL or view name
    return HttpResponseBadRequest("Invalid request method")


def quiz_finished(request):
    user_details_id = request.session.get('user_details_id')
    if user_details_id:
        user_details = UserDetails.objects.get(pk=user_details_id)

        # Calculate the total score based on UserResponse scores
        total_score = UserResponse.objects.filter(user=user_details).aggregate(total_score=Sum('score'))['total_score']

        # Update the total score in the UserDetails instance
        user_details.total_score = total_score or 0
        user_details.save()

    else:
        user_details = None
        total_score = 0

    return render(request, 'quiz_finished.html', {'user_details': user_details, 'total_score': total_score})
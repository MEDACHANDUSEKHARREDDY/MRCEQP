from django import forms
from .models import UserResponse, Question, Score # Import the UserResponse and Question models

class UserDetailsForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        questions = kwargs.pop('questions')
        super(UserAnswerForm, self).__init__(*args, **kwargs)
        for question in questions:
            self.fields[f'question_{question.code}'] = forms.ChoiceField(
                choices=[(option, option) for option in question.get_options()],
                widget=forms.RadioSelect,
                label=question.question_text,
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        for name, value in self.cleaned_data.items():
            if name.startswith('question_'):
                question_code = name.split('_')[1]
                question = Question.objects.get(code=question_code)
                user_answer = value
                is_correct = user_answer == question.correct_answer
                score = question.max_score if is_correct else 0
                user_response = UserResponse.objects.create(user=self.user, question=question, user_answer=user_answer, score=score)

                # Optionally, update the answered_question_codes field
                instance.answered_question_codes += f"{question_code}:{user_answer};"

        if commit:
            instance.save()

        return instance
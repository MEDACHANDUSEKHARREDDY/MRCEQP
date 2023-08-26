from django.db import models
import random,string

class QuestionCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=400)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=100)
    max_score = models.IntegerField(default=0)
    code = models.CharField(max_length=12, blank=True, editable=False)

    def __str__(self):
        return self.question_text

    def generate_question_code(self):
        category_code = self.category.code.upper()
        question_count = Question.objects.filter(category=self.category).count()
        return f"{category_code}{str(question_count + 1).zfill(3)}{str(self.max_score).zfill(1)}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_question_code()
        super().save(*args, **kwargs)

    def get_options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]

class UserDetails(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Calculate and update the total score based on UserResponse scores and max scores of questions
        user_responses = UserResponse.objects.filter(user=self)
        total_score = sum(response.score for response in user_responses)
        self.total_score = total_score
        super().save(*args, **kwargs)

class UserResponse(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name='user_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_responses')
    user_answer = models.CharField(max_length=1)
    score = models.IntegerField(default=0)
    answered_question_codes = models.TextField(blank=True)
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.user} - {self.question} - {self.user_answer}"

    def save(self, *args, **kwargs):
        if not self.answered_question_codes:
            self.answered_question_codes = f"{self.question.code}"
        else:
            self.answered_question_codes += f";{self.question.code}"
        
        super().save(*args, **kwargs)

class Score(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name='scores')
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Score for {self.user.name}"

    def save(self, *args, **kwargs):
        # Calculate and update the total score based on UserResponse scores
        user_responses = UserResponse.objects.filter(user=self.user)
        total_score = sum(response.score for response in user_responses)
        self.total_score = total_score
        super().save(*args, **kwargs)
        
class EmailVerification(models.Model):
    email = models.EmailField()
    verification_code = models.CharField(max_length=4)  # Adjust length as needed
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=4))
from django.contrib import admin
from .models import UserDetails, Question, Score, QuestionCategory, UserResponse, EmailVerification
from .forms import UserAnswerForm

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('category','code','question_text','correct_answer', 'max_score')
    readonly_fields = ('code',)  # Make the code field read-only

    def get_readonly_fields(self, request, obj=None):
        # Allow the code field to be editable when adding a new question
        if obj is None:
            return ()
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        # Generate and set the question code before saving the question
        if not obj.pk:
            obj.code = obj.generate_question_code()
        super().save_model(request, obj, form, change)
        
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
        
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'total_score')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user','total_score')
    
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user_name','question','correct_answer','user_answer','score','answered_question_codes')
    
    def user_name(self, obj):
        return obj.user.name
    
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email','verification_code')
    
# Register your models here
admin.site.register(UserDetails, UserDetailsAdmin)
admin.site.register(Question, QuestionAdmin)  # Use the customized QuestionAdmin
admin.site.register(Score, ScoreAdmin)
admin.site.register(QuestionCategory,QuestionCategoryAdmin)
admin.site.register(UserResponse,UserResponseAdmin)
admin.site.register(EmailVerification,EmailVerificationAdmin)
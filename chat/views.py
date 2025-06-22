
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def global_chat_view(request):
    return render(request, 'chat/global_chat.html')
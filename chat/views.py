from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from chat.models import ChatModel
from .forms import PorukaForm
from accounts.models import UserProfile, Account
#from chats.models import ChatModel
# Create your views here.


User = get_user_model()


def poruke(request):
    users = User.objects.exclude(username=request.user.username)
    userprofile = UserProfile.objects.select_related('user').all()
    return render(request, 'accounts/poruke.html', context={'users': users, 'userprofile':userprofile})
    
def chatPage(request, username):
    user_obj = User.objects.get(username=username)
    users = User.objects.exclude(username=request.user.username)

    if request.user.id > user_obj.id:
        thread_name = f'chat_{request.user.id}-{user_obj.id}'
    else:
        thread_name = f'chat_{user_obj.id}-{request.user.id}'
    message_objs = ChatModel.objects.filter(thread_name=thread_name)
    userprofile = UserProfile.objects.select_related('user').all()
    return render(request, 'accounts/main_chat.html', context={'users': users,'messages':message_objs, 'userprofile':userprofile, 'user':user_obj})

def poruke(request, user_id):
    url = request.META.get('HTTP_REFERER')
    user_id=int(user_id)
    user_obj = Account.objects.get(id=user_id)
    if request.user.id > user_obj.id:
        naziv = f'chat_{request.user.id}-{user_obj.id}'
    else:
        naziv = f'chat_{user_obj.id}-{request.user.id}'
    if request.method == 'POST':
        try:
            form = PorukaForm(request.POST)
            if form.is_valid():
                data = ChatModel()
                data.message = form.cleaned_data['message']
                data.sender = request.user.id
                data.receiver_id = user_id
                data.thread_name = naziv  
                data.save()
                return redirect(url)
        except:
            pass
        return redirect(url)


from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.transaction import commit
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import LoginForm, RegistrationForm, ProfileForm, ChatRoomForm


# ----------------------------AUTH----------------------------------------

def register_view(request):
    if request.method == 'POST':
         form = RegistrationForm(request.POST)
         if form.is_valid():
             form.save()
             return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form':form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                profile = Profile.objects.filter(user=user).first()
                if profile:
                    return redirect('homepage')
                else:
                    return redirect('create_profile')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form':form})

@login_required(login_url='login/')
def logout_view(request):
    logout(request)
    return redirect('login')


# ----------------------------HOME------------------------
@login_required(login_url='login/')
def homepage(request):
    chatrooms = ChatRoom.objects.filter(members=request.user.profile)
    number = [{"chatroom":chatroom, "member_count":chatroom.members.count()}
              for chatroom in chatrooms]


    return render(request, 'homepage.html', {'chatrooms':number })

@login_required(login_url='login/')
def create_profile(request):
    if request.method == 'POST':
            form  = ProfileForm(request.POST)
            print(form.errors)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
            return redirect('homepage')
    else:
        form = ProfileForm()

    return render(request, 'create_profile.html', {'form':form})

# ------------------------------------------CHAT-------------------------------------
@login_required(login_url='login/')
def create_chatroom(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user = request.user)
            chatroom = form.save(commit=False)
            chatroom.save()

            chatroom.members.add(profile)
            return redirect('homepage')
    else:
        form = ChatRoomForm()

    return render(request, 'create_chat.html', {'form':form})

@login_required(login_url='login/')
def join_chatroom(request):
    if request.method == "POST":
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            chatroom = ChatRoom.objects.filter(name=name, password=password).first()
            if chatroom:
                 chatroom.members.add(profile)
                 return redirect('homepage')
            else:
                messages.error(request, "Chatroom not found or incorrect password.")
    else:
        form = ChatRoomForm()

    return render(request, 'join_chat.html', {'form':form})


# -------------------CHAT MESSAGES-----------------------------
@login_required(login_url='login/')
def view_chat(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)
    message = Message.objects.filter(chatroom=chat).order_by('sent_time')

    if request.method == "POST":
        content = request.POST.get('message')
        if content.strip():
            Message.objects.create(chatroom=chat, sender=request.user.profile, content=content)
            return redirect('view_chat', chat_id = chat.id)
        else:
            messages.error("Message can't be empty")

    return render(request, 'chatroom.html', {'chat': chat, 'messages': message})
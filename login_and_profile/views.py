import re
from .models import User, Item, HouseMembership, House, BalanceDue, Notification
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.

################### Login Methods ###################


def index(request):
    return render(request, "login.html")

# not redirecting to /profile


def register(request):
    if request.method == "GET":
        return redirect('/')
    errors = User.objects.validation(request.POST)
    if errors:
        for e in errors.values():
            messages.error(request, e)
        return redirect('/')
    else:
        new_user = User.objects.register(request.POST)
        Notification.objects.create(receiver=new_user, action="REGISTERED")
        request.session['user_id'] = new_user.id
        request.session['first_name'] = new_user.first_name
        return redirect('/profile')


def login(request):
    if request.method == "GET":
        return redirect('/')
    if not User.objects.authenticate(request.POST['email'], request.POST['password']):
        messages.error(request, 'Invalid Email/Password')
        return redirect('/')
    user = User.objects.get(email=request.POST['email'])
    request.session['user_id'] = user.id
    request.session['first_name'] = user.first_name
    return redirect('/profile')


def logout(request):
    request.session.clear()
    return redirect('/')


################### Profile Methods ###################


def profile(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.get(id=request.session['user_id'])
    context = {
        'user': this_user,
    }
    # add if statement to redirect to main_house if existing?
    return render(request, 'profile.html', context)


def create_house(request):
    if request.method == "GET":
        return redirect('/profile')
    if len(request.POST['nickname']) < 2:
        e = "House nickname must be at least 2 characters."
        messages.error(request, e)
        return redirect('/profile')
    this_user = User.objects.get(id=request.session['user_id'])
    new_house = House.objects.create(
        nickname=request.POST['nickname'])
    HouseMembership.objects.create(
        house=new_house, pending_invite=False, user=this_user)
    Notification.objects.create(
        sender=this_user, house=new_house, action="CREATED")

    request.session['main_house_id'] = new_house.id
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return redirect(f'/profile/main_house/')


def add_housemate(request):
    if request.method == "GET":
        return redirect('/profile/house/')
    if User.objects.verifyAccountExists(request.POST['email']):
        messages.error(request, 'No users by that email exist')
        return redirect('/profile/main_house/')
    sender = User.objects.get(id=request.session['user_id'])
    receiverQuery = User.objects.filter(email=request.POST['email'])
    receiver = receiverQuery[0]
    house = House.objects.get(id=request.session['main_house_id'])
    print(receiver.first_name)
    if house.memberships.filter(user=receiver).exists():
        # if 1 == 2:
        messages.error(request, 'Invite already sent')
        return redirect('/profile/main_house/')
    membership = HouseMembership.objects.create(
        house=house, pending_invite=True, user=receiver)
    Notification.objects.create(
        sender=sender, action="INVITED", receiver=receiver, house=house, membership=membership)
    return redirect('/profile/main_house/')


def accept_invite(request, membership_id):
    if request.method == "GET":
        return redirect('/profile/house/')
    receiver = User.objects.get(id=request.session['user_id'])
    receiver.users


def select_main_house(request, house_id):
    if request.method == "GET":
        return redirect('/profile')
    request.session['main_house_id'] = house_id
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return redirect('/profile/main_house/')


def main_house(request):
    if 'main_house_id' not in request.session:
        return redirect('/profile')
    this_user = User.objects.get(id=request.session['user_id'])
    this_house = House.objects.get(id=request.session['main_house_id'])
    all_items = this_house.items.all()
    all_notifications = this_house.notifications.all()
    context = {
        'all_notifications': all_notifications,
        'house': this_house,
        'user': this_user,
        'all_items': all_items
    }
    return render(request, 'house.html', context)

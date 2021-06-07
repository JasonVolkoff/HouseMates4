# from Projects.HouseMates.housemates_proj.login_and_profile.views import main_house
from django.db import models
import re
from django.db.models.deletion import CASCADE
import bcrypt
from decimal import Decimal

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Create your models here.


class UserManager(models.Manager):
    def validation(self, form):
        errors = {}
        if len(form['firstName']) < 2:
            errors['firstName'] = 'First Name must be at least 2 characters'
        if len(form['lastName']) < 2:
            errors['lastName'] = 'Last Name must be at least 2 characters'
        if not EMAIL_REGEX.match(form['email']):
            errors['email'] = 'Invalid email address'
        email_check = self.filter(email=form['email'])
        if email_check:
            errors['email'] = "Email already in use"
        if len(form['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"
        if form['password'] != form['confirmPassword']:
            errors['password'] = 'Passwords do not match'
        return errors

    def authenticate(self, email, password):
        users = self.filter(email=email)
        if not users:
            return False
        user = users[0]
        return bcrypt.checkpw(password.encode(), user.password.encode())

    def register(self, form):
        pw = bcrypt.hashpw(form['password'].encode(),
                           bcrypt.gensalt()).decode()
        return self.create(
            first_name=form['firstName'],
            last_name=form['lastName'],
            email=form['email'],
            password=pw
        )

    def verifyAccountExists(self, email):
        users = self.filter(email=email)
        if not users:
            return True
        return False


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    notification_amount = models.IntegerField(default=0)
    total_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    # Eventually add default profile_image + upload option
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()


class House(models.Model):
    nickname = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0))
    owned_by = models.ManyToManyField(User, related_name="users_items")
    location = models.ForeignKey(
        House, related_name="items", on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def checkOwnership(self):
        # user = User.objects.get(id=user_id)
        # if self.owned_by.get(id=user).exists():
        #     return user_id
        # else:
        #     return user_id
        return "hello"

# Add Item fractional ownership model to indicate how much of the item you own


class HouseMembership(models.Model):
    pending_invite = models.BooleanField()
    house = models.ForeignKey(
        House, related_name="memberships", on_delete=CASCADE,)
    user = models.ForeignKey(
        User, related_name="users_memberships", on_delete=CASCADE)

    def checkFalse(self):
        if self.pending_invite == False:
            return True
        else:
            return False


class Notification(models.Model):
    ACTIONS = (
        ('PURCHASED', 'purchased'),
        ('INVITED', 'invited'),
        ('CREATED', 'created'),
        ('HELPED', 'helped purchase'),
        ('REGISTERED', 'registered an account'),
        ('ACCEPTED', 'accepted invite to'))
    sender = models.ForeignKey(
        User, on_delete=CASCADE, blank=True, null=True, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=CASCADE,
                                 blank=True, null=True, related_name='received_notifications')
    house = models.ForeignKey(
        House, on_delete=CASCADE, blank=True, null=True, related_name='notifications')
    item = models.ForeignKey(Item, blank=True, null=True,
                             related_name='item_notification', on_delete=CASCADE)
    action = models.CharField(
        choices=ACTIONS, default='CREATED', max_length=32)
    membership = models.ForeignKey(
        HouseMembership, blank=True, null=True, related_name='notification', on_delete=CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def profileFormat(self):
        action = f"{self.get_action_display()}"
        receiver = self.receiver
        house = self.house
        item = self.item
        sender = self.sender
        if self.action == "PURCHASED":
            notification = f'You {action} {item.name}'
        elif self.action == "INVITED":
            notification = f'{sender.first_name} {sender.last_name} {action} you to {house.nickname}'
        elif self.action == "CREATED":
            notification = f'You {action} {house.nickname}'
        elif self.action == "HELPED":
            pass  # add content
        elif self.action == "REGISTERED":
            notification = f'You {action}'
        elif self.action == "ACCEPTED":
            notification = f'You {action} {house.nickname}'
        return notification

    def houseFormat(self):
        action = f"{self.get_action_display()}"
        sender = self.sender
        receiver = self.receiver
        house = self.house
        item = self.item
        if self.action == "PURCHASED":
            notification = f'{sender.first_name} {action} {item.name}'
        elif self.action == "INVITED":
            notification = f'{sender.first_name} {action} {receiver.first_name} {receiver.last_name} to {house.nickname}'
        elif self.action == "CREATED":
            notification = f'{receiver.first_name} {action} {house.nickname}'
        elif self.action == "HELPED":
            pass  # add content
        elif self.action == "ACCEPTED":
            notification = f'{sender.first_name} {action} {house.nickname}'
        return notification

    def responseFormat(self):
        if self.action == "Invited":
            if self.membership.pending_invite == True:
                return "Pending"
            else:
                return "Accepted"
        if self.action == "Created":
            return "Yay!"
        if self.action == "Purchased":
            return self.item.price
        if self.action == "Helped":
            return self.item.split_cost


class BalanceDue(models.Model):
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    user = models.ManyToManyField(User, related_name="is_owed")


class BalanceOwed(models.Model):
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    user = models.ManyToManyField(User, related_name="owes")

# from Projects.HouseMates.housemates_proj.login_and_profile.views import main_house
from django.db import models
import re
from django.db.models.deletion import CASCADE
import bcrypt

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
        print(users)
        if not users:
            return False
        return True


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
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    owned_by = models.ManyToManyField(User, related_name="users_items")
    location = models.ForeignKey(
        House, related_name="items", on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    ACTIONS = (
        ('PURCHASED', 'purchased'),
        ('INVITED', 'invited'),
        ('CREATED', 'created'),
        ('HELPED', 'helped purchase'),
        ('REGISTERED', 'registered an account'))
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
    date = models.DateTimeField(auto_now_add=True)


class HouseMembership(models.Model):
    pending_invite = models.BooleanField(default=True)
    house = models.ForeignKey(
        House, related_name="memberships", on_delete=CASCADE,)
    user = models.ForeignKey(
        User, related_name="users_memberships", on_delete=CASCADE)


class BalanceDue(models.Model):
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    user = models.ManyToManyField(User, related_name="is_owed")


class BalanceOwed(models.Model):
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    user = models.ManyToManyField(User, related_name="owes")

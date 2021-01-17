from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Profile, Order
import json
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, OrderForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from random import random, randrange, getrandbits, randint
from django.db.models import F, Count, Value, Sum

@login_required(login_url='login')
def home(request):
    balance = Profile.objects.filter(user=request.user).values_list('wallet', flat=True)
    buy_op = Order.objects.filter(profile=request.user, execute=True, buy=True).values_list('quantity', flat=True)
    sell_op = Order.objects.filter(profile=request.user, execute=True, sell=True).values_list('quantity', flat=True)
    gain = Order.objects.filter(profile=request.user).aggregate(Sum('profit'))
    list = []
    val1 = sum(buy_op)
    val2 = sum(sell_op)
    for x in balance:
        list.append(x)
    if not list:
        el=0
    else:
        el = (val1+list[0])-val2
    contex = {'el': el,
              'gain': gain}
    return render(request, 'app/home.html', contex)

@login_required(login_url='login')
def active(request):
    active_orders = Order.objects.filter(execute=False)
    active_orders1 = serializers.serialize('json',active_orders)
    return HttpResponse(active_orders1, content_type="text/json-comment-filtered")

@login_required(login_url='login')
def execute(request):
    execute_orders = Order.objects.filter(execute=True)
    execute_orders1 = serializers.serialize('json',execute_orders)
    return HttpResponse(execute_orders1, content_type="text/json-comment-filtered")

@login_required(login_url='login')
def order(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            new_order = form.save()
            if new_order.buy is True:
                sellOrder = Order.objects.filter(sell=True, execute=False, price__lte=new_order.price).first()
                if sellOrder != None :
                    profitBuy = new_order.price - sellOrder.price
                    new_order.profit = profitBuy
                    new_order.execute = True
                    sellOrder.execute = True
                    sellOrder.save()
                else:
                    new_order.save()
            else:
                buyOrder = Order.objects.filter(buy=True, execute=False,price__gte=new_order.price).first()
                if buyOrder != None :
                    profitSell = buyOrder.price - new_order.price
                    new_order.profit = profitSell
                    new_order.execute = True
                    buyOrder.execute = True
                    buyOrder.save()
                else:
                    new_order.save()
            new_order.profile = request.user
            new_order.save()
            return redirect('home')
    else:
        form = OrderForm()
    contex = {'form': form}
    return render(request, 'app/new_order.html', contex)

def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            bonus = randint(1,10)
            new_profile = Profile.objects.create(user=new_user, wallet=bonus)
            new_profile.save()
            return redirect('login')
    else:
        form = CreateUserForm()
    contex = {'form':form}
    return render(request, 'app/register.html', contex)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    contex = {}
    return render(request, 'app/login.html', contex)

def logoutUser(request):
    logout(request)
    return redirect('login')

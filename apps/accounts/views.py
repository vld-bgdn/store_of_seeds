from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import ProfileUpdateForm, CustomPasswordChangeForm
from apps.orders.models import Order


def customer_register(request):
    """Registration view specifically for shop customers"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set as customer
            profile = user.userprofile
            profile.user_type = "customer"
            profile.save()

            messages.success(request, "Успешная регистрация!")
            login(request, user)
            return redirect("products:category_list")  # Redirect to shop
    else:
        form = UserCreationForm()

    return render(request, "accounts/customer_register.html", {"form": form})


@login_required
def profile_view(request):
    """View for users to see their profile"""
    profile = request.user.userprofile

    recent_orders = []
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by("-created")[:5]
        pass
    except:
        pass

    context = {
        "profile": profile,
        "user": request.user,
        "recent_orders": recent_orders,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    """View for users to edit their profile"""
    profile = request.user.userprofile

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    context = {
        "profile": profile,
        "user": request.user,
        "form": form,
    }

    return render(request, "accounts/profile_edit.html", context)


@login_required
def change_password(request):
    """View for users to change their password"""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Пароль успешно изменен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def orders_list(request):
    """View for users to see all their orders"""
    # profile = request.user.userprofile
    orders = []
    try:
        # Assuming you have an Order model
        orders_queryset = Order.objects.filter(user=request.user).order_by("-created")
        #
        # # Pagination
        paginator = Paginator(orders_queryset, 10)  # Show 10 orders per page
        page_number = request.GET.get("page")
        orders = paginator.get_page(page_number)
        pass
    except:
        messages.info(request, "Система заказов пока недоступна.")

    context = {
        "orders": orders,
    }

    return render(request, "accounts/orders_list.html", context)


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next parameter if exists, otherwise to products
            next_url = request.GET.get("next", "products:category_list")
            return redirect(next_url)
        else:
            return render(
                request, "accounts/login.html", {"error": "Invalid credentials"}
            )
    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect("products:category_list")

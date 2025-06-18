from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


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


def profile_view(request):
    """View for users to see/edit their profile"""
    profile = request.user.userprofile
    return render(request, "accounts/profile.html", {"profile": profile})


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("products:category_list")
        else:
            return render(
                request, "accounts/login.html", {"error": "Invalid credentials"}
            )
    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("products:category_list")


# def logout_confirmation(request):
#     return render(request, "accounts/logout.html")

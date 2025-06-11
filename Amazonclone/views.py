from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, RegisterForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def home(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    page = request.GET.get('page', 1)

    if category:
        products = products.filter(category=category)

    if search:
        products = products.filter(name__icontains=search)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 6)
    products_page = paginator.get_page(page)

    categories = [
        {'name': 'Mobiles'}, {'name': 'Books'}, {'name': 'Watches'},
        {'name': 'Shoes'}, {'name': 'Fashion'}, {'name': 'Electronics'},
    ]

    # ✅ Combine product sections into a list of tuples (title, items)
    product_sections = [
        ('Featured Products', [
            {'name': 'iPhone 16', 'price': '₹73,500', 'img': 'images/iphone16.jpg'},
            {'name': 'Harry Potter Book Set', 'price': '₹949', 'img': 'images/harrypotter.jpg'},
            {'name': 'Titan Watch', 'price': '₹1695', 'img': 'images/titanwatch.jpg'},
        ]),
        ('Best Sellers', [
            {'name': 'Samsung Galaxy S24 Ultra', 'price': '₹99,700', 'img': 'images/S24Ultra.jpg'},
            {'name': 'Nike Sports Shoes', 'price': '₹11,245', 'img': 'images/nikeshoes.jpg'},
        ]),
        ('Trending Items', [
            {'name': 'Noise Airwave Max5', 'price': '₹4,999', 'img': 'images/Bluetooth.jpg'},
            {'name': 'Levi\'s Jeans', 'price': '₹1,799', 'img': 'images/levisjeans.jpg'},
        ])
    ]

    context = {
        'categories': categories,
        'product_sections': product_sections,  
        'deals': [
            {'banner_img': 'images/dealoftheday1.png'},
            {'banner_img': 'images/dealoftheday2.png'},
        ],
        'deals_of_day': [
            {'name': 'Boat Bluetooth Speaker', 'price': '₹1,299', 'img': 'images/boatspeaker.jpg', 'discount': '35% Off'},
            {'name': 'Fastrack Watch', 'price': '₹2,499', 'img': 'images/fasttrackwatch.jpg', 'discount': '40% Off'},
            {'name': 'Dell Laptop Bag', 'price': '₹999', 'img': 'images/delllaptopbag.jpg', 'discount': '50% Off'},
        ],
        'products': products_page,
        'paginator': paginator,
    }

    return render(request, 'Amazonclone/home.html', context)

def product_detail(request):
    product_id = request.GET.get('id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            return render(request, 'Amazonclone/product_detail.html', {'product': product})
        except Product.DoesNotExist:
            return render(request, 'Amazonclone/product_not_found.html', status=404)
    return render(request, 'Amazonclone/product_not_found.html', status=400)


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart_view')


def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        cart = request.session.get('cart', {})
        cart[str(product_id)] = quantity
        request.session['cart'] = cart
    return redirect('cart_view')


def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    subtotal = 0

    for product in products:
        quantity = cart.get(str(product.id), 1)
        total_price = product.price * quantity
        subtotal += total_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price
        })

    estimated_shipping = 50 if subtotal else 0
    total = subtotal + estimated_shipping

    return render(request, 'Amazonclone/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'estimated_shipping': estimated_shipping,
        'total': total,
    })


def get_cart_item_count(request):
    return sum(request.session.get('cart', {}).values())


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # or use your custom RegisterForm
        if form.is_valid():
            user = form.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = f"http://yourdomain.com/activate/{uid}/{token}/"

            send_mail(
                 'Verify your email',
                 f'Click here to verify your email: {activation_link}',
                 'no-reply@yourdomain.com',
                 [user.email],
                )
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'Amazonclone/register.html', {'form': form})

@login_required
def profile_view(request):
    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'Amazonclone/profile.html', {'form': form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set')
    return render(request, 'Amazonclone/order_history.html', {'orders': orders})


@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = request.session.get('cart', {})

    for item in order.orderitem_set.all():
        cart[str(item.product.id)] = item.quantity

    request.session['cart'] = cart
    return redirect('cart_view')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'Amazonclone/login.html', {'form': form})



@login_required
def update_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in
            messages.success(request, "Password updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'Amazonclone/update_password.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
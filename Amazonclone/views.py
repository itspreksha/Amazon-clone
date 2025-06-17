from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash, get_backends, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm,UserCreationForm
from django.contrib import messages
from .forms import RegisterForm, ProfileForm,LoginForm
from .models import Profile, OTPVerification, Product, Order
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from allauth.account.models import EmailAddress
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import update_session_auth_hash
from .models import Order,OrderItem
from .models import Review,ProductQuestion
from .forms import ReviewForm,QuestionForm

def home(request):
    # No redirect — just check if logged in, and optionally show email warning
    email_warning = None
    if request.user.is_authenticated:
        verified = EmailAddress.objects.filter(user=request.user, verified=True).exists()
        if not verified:
            email_warning = "Please verify your email to access full features."

    # Fetch product filters and pagination
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
            {'name': "Levi's Jeans", 'price': '₹1,799', 'img': 'images/levisjeans.jpg'},
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
        'email_warning': email_warning,
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

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            otp = generate_otp()
            OTPVerification.objects.update_or_create(
                user=user,
                defaults={
                    'otp': otp,
                    'expires_at': timezone.now() + timedelta(minutes=2),
                    'verified': False
                }
            )
            send_mail(
                'Your OTP Verification Code',
                f'Your OTP is: {otp}',
                'no-reply@yourdomain.com',
                [user.email],
            )
            request.session['otp_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = RegisterForm()
    return render(request, 'Amazonclone/register.html', {'form': form})

User = get_user_model()

def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('register')

    try:
        user = User.objects.get(id=user_id)
        otp_record = OTPVerification.objects.get(user=user)
    except (User.DoesNotExist, OTPVerification.DoesNotExist):
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('userOTP', '').strip()
        stored_otp = str(otp_record.otp).strip()

        if entered_otp == stored_otp and otp_record.expires_at > timezone.now():
            otp_record.verified = True
            otp_record.save()
            user.is_active = True
            user.save()

            # Set backend manually since user is not authenticated via authenticate()
            from django.contrib.auth import get_backends
            user.backend = get_backends()[0].__module__ + "." + get_backends()[0].__class__.__name__
            login(request, user)

            del request.session['otp_user_id']
            return redirect('home')
        else:
            return render(request, 'Amazonclone/verify_otp.html', {
                'otpError': 'Invalid or expired OTP'
            })

    return render(request, 'Amazonclone/verify_otp.html')


def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')
    user = User.objects.get(id=user_id)
    new_otp = str(random.randint(100000, 999999))
    expiration_time = timezone.now() + timedelta(minutes=2)
    OTPVerification.objects.update_or_create(
        user=user,
        defaults={'otp': new_otp, 'expires_at': expiration_time, 'verified': False}
    )
    send_mail(
        'Your OTP Code',
        f'Your OTP is: {new_otp}',
        'no-reply@example.com',
        [user.email],
        fail_silently=False,
    )
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp')

def session_expired(request):
    return render(request, 'session_expired.html', {
        'message': 'Your session has expired. Please try again.',
    })

@login_required
def view_profile(request):
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
def reorder(request,order_id):
    old_order=get_object_or_404(Order,id=order_id,user=request.user)
    new_order=Order.objects.create(user=request.user,status='Pending',total_price=old_order.total_price)
    for item in OrderItem.objects.filter(order=old_order):
        OrderItem.objects.create(
            order=new_order,
            product_name=item.product_name,
            price=item.price,
            quantity=item.quantity
        )
    messages.success(request,f"Order#{order_id}has been re-ordered successfully.")
    return redirect('order_history')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is not verified. Please check your email.")
                    return redirect('login')
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'Amazonclone/login.html', {'form': form})

@login_required
def update_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully.")
            return redirect('view_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'Amazonclone/change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'Amazonclone/password_reset_form.html'
    email_template_name = 'Amazonclone/password_reset_email.html'
    subject_template_name = 'Amazonclone/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        form.save(
            request=self.request,
        )
        return super().form_valid(form)


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.username = request.POST.get('name', '')
        request.user.email = request.POST.get('email', '')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')  
        profile.city = request.POST.get('city', '')
        request.user.save()
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('view_profile')
    return render(request, 'Amazonclone/edit_profile.html', {'profile': profile})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully.")
            return redirect('view_profile')
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, 'Amazonclone/change_password.html', {'form': form})
    
@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    return render(request, 'Amazonclone/orders.html',{'orders':orders})

@property
def total_price(self):
    return sum(item.quantity * item.price for item in self.items.all())

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    sizes = [s.strip() for s in product.sizes.split(",")] if product.sizes else []
    colors = [c.strip() for c in product.colors.split(",")] if product.colors else []
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    questions = ProductQuestion.objects.filter(product=product).order_by('-asked_at')

    review_form = ReviewForm()
    question_form = QuestionForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', product_id=product.id)

        elif 'submit_question' in request.POST:
            question_form = QuestionForm(request.POST)
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.product = product
                question.user = request.user
                question.save()
                return redirect('product_detail', product_id=product.id)

    return render(request, 'Amazonclone/product_detail.html', {
        'product': product,
        'sizes': sizes,
        'colors': colors,
        'related_products': related_products,
        'reviews': reviews,
        'questions': questions,
        'review_form': review_form,
        'question_form': question_form
    })

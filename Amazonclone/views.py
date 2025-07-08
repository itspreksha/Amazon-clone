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
from .models import Address,StockAlert,StockNotification
from .forms  import AddressForm
import razorpay
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest,JsonResponse
from .models import Cart
from Amazonclone.models import StockNotification 
from django.db.models import Q
from .models import UserLocation,Address
from django.http import JsonResponse,HttpResponseNotAllowed
import json
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages

COD_ALLOWED_PINCODES = ['380001', '110001', '560001','380013']

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
    

    addresses = []
    selected_address = None
    if request.user.is_authenticated:
     addresses = Address.objects.filter(user=request.user)
     selected_address = addresses.filter(is_default=True).first()


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

    paginator = Paginator(products, 8)
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
            {'name': 'Crosscut Furniture Wooden Floor Lamp with Shelf (Natural Jute). LED Bulb Included', 'price': '₹2,749', 'img': 'images/lamp.jpg'},
        ]),
        ('Best Sellers', [
            {'name': 'Samsung Galaxy S24 Ultra', 'price': '₹99,700', 'img': 'images/S24Ultra.jpg'},
            {'name': 'Nike Sports Shoes', 'price': '₹11,245', 'img': 'images/nikeshoes.jpg'},
            {'name': 'Portable Mini Cooler Rechargeable Air Conditioner Water Cooler Small AC', 'price': '₹439', 'img': 'images/cooler.jpg'},
            {'name': 'Kamiliant American Tourister Harrier Small,Medium & Large 360 Degree Spinner Suitcase', 'price': '₹5,299', 'img': 'images/suitcase.jpg'},
             
        ]),
        ('Trending Items', [
            {'name': 'Noise Airwave Max5', 'price': '₹4,999', 'img': 'images/Bluetooth.jpg'},
            {'name': "Levi's Jeans", 'price': '₹1,799', 'img': 'images/levisjeans.jpg'},
            {'name': 'SWAROVSKI Women Emily Bracelet, White, Rhodium Plated', 'price': '₹8,290', 'img': 'images/swaroski.jpg'},
            {'name': "Pure Vegan Leather Tote Bag for Women, Fully Embossed, Handbag, Shoulder Bag, Black", 'price': '₹394', 'img': 'images/purse.jpg'},
        ])

    ]

    context = {
        'categories': categories,
        'product_sections': product_sections,
        'deals': [
            {'banner_img': 'images/bg2.jpg'},
            {'banner_img': 'images/bg3.jpg'},
            {'banner_img': 'images/bg1.jpg'},
            {'banner_img': 'images/bg4.jpg'},
        ],
        'deals_of_day': [
            {'name': 'Boat Bluetooth Speaker', 'price': '₹1,299', 'img': 'images/boatspeaker.jpg', 'discount': '35% Off'},
            {'name': 'Fastrack Watch', 'price': '₹2,499', 'img': 'images/fasttrackwatch.jpg', 'discount': '40% Off'},
            {'name': 'Dell Laptop Bag', 'price': '₹999', 'img': 'images/delllaptopbag.jpg', 'discount': '50% Off'},
        ],
        'products': products_page,
        'paginator': paginator,
        'email_warning': email_warning,
        'addresses':addresses,
        'selected_address':selected_address
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

@csrf_exempt
def save_location(request):
    print(">>> save_location VIEW CALLED <<<")

    if request.method == 'POST':
        # First try JSON
        if request.headers.get('Content-Type') == 'application/json':
            try:
                print("Raw JSON request body:", request.body)
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
        else:
            # Fallback: handle form-encoded POST data
            data = request.POST
            print("Form data:", data)

        # Extract latitude and longitude
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return JsonResponse({"status": "error", "message": "Missing coordinates"}, status=400)

        print("✅ Received:", latitude, longitude)
        return JsonResponse({"status": "success", "message": "Location saved"})

    return HttpResponseNotAllowed(['POST'])

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Prevent adding out-of-stock items
    if product.stock <= 0:
        messages.error(request, "This product is out of stock and cannot be added to the cart.")
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        size = request.POST.get('size', '')
        color = request.POST.get('color', '')
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('cart_view')

    return redirect('home')

@login_required
def remove_from_cart(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cart_view')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        cart_item = Cart.objects.filter(user=request.user, product_id=product_id).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()

    return redirect('cart_view')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = 0

    for item in cart_items:
        item.total_price = item.product.price * item.quantity
        subtotal += item.total_price

    estimated_shipping = 49  # example fixed shipping
    total = subtotal + estimated_shipping

    return render(request, 'Amazonclone/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'estimated_shipping': estimated_shipping,
        'total': total
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
    return render(request, 'Amazonclone/profile.html', {'profile': profile})

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
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()

        # Validate username
        if not username:
            messages.error(request, 'Username cannot be empty.')
            return redirect('edit_profile')

        # Check if username already exists (and not the current user)
        if username != user.username and User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Username already taken.')
            return redirect('edit_profile')

        # Save user model
        user.username = username
        user.first_name = name
        user.email = email
        user.save()

        # Save profile model
        profile.phone = phone
        profile.city = city
        profile.address = address
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('view_profile')

    return render(request, 'Amazonclone/edit_profile.html', {
        'profile': profile
    })


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
def set_password(request):
    if request.user.has_usable_password():
        return redirect('home')

    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password set successfully!")
            return redirect('home')
    else:
        form = SetPasswordForm(request.user)

    return render(request, 'Amazonclone/set_password.html', {'form': form})
@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    return render(request, 'Amazonclone/orders.html',{'orders':orders})

@login_required
def order_success(request):
    order_id = request.GET.get('order_id')
    return render(request,"Amazonclone/order_success.html",{"order_id":order_id})

@property
def total_price(self):
    return self.product.price * self.quantity

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Track views once per session
    session_key = f'viewed_product_{product.id}'
    if not request.session.get(session_key, False):
        product.register_view()
        request.session[session_key] = True

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    sizes = [s.strip() for s in product.sizes.split(",")] if product.sizes else []
    colors = [c.strip() for c in product.colors.split(",")] if product.colors else []
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    questions = ProductQuestion.objects.filter(product=product).order_by('-asked_at')

    review_form = ReviewForm()
    question_form = QuestionForm()

    if request.method == 'POST' and request.user.is_authenticated:
     if 'submit_review' in request.POST:
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            # ⭐ Recalculate product rating
            product.update_rating()

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

@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request,'Amazonclone/manage_addresses.html',{'addresses':addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=request.user
            if address.is_default:
                Address.objects.filter(user=request.user,is_default=True).update(is_default=False)
            address.save()

            if address.is_default:
                profile=Profile.objects.get(user=request.user)
                profile.default_address=address
                profile.save()
            return redirect('manage_addresses')
    else:
        form = AddressForm()
    return render(request,'Amazonclone/add_address.html',{'form':form})

@login_required
def edit_address(request, address_id):
    address = Address.objects.get(id=address_id,user=request.user)
    form=AddressForm(request.POST or None,instance=address)
    if form.is_valid():
        form.save()
        return redirect('manage_addresses')
    return render(request,'Amazonclone/edit_address.html',{'form':form})

def set_default_address(request,address_id):
    address=get_object_or_404(Address,id=address_id,user=request.user)
    request.session['selected_address_id']=address.id 
    return redirect('home')

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid amount")

        # Razorpay client setup
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create a Razorpay order
        payment = client.order.create({
            'amount': int(amount * 100),  # Convert to paisa
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create a local order and store the Razorpay order ID
        order = Order.objects.create(
            user=request.user,
            total_price=amount,
            payment_method='Online',
            payment_status='Pending',
            razorpay_order_id=payment['id']  # Save Razorpay order ID
        )

        return render(request,'Amazonclone/payment.html', {
            'payment': payment,
            'order': order,
            'key_id': settings.RAZORPAY_KEY_ID,
            'amount': int(amount * 100),  # Send paisa to JS
            'user': request.user
        })

    return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        order_id = request.POST.get('order_id')  # Razorpay Order ID
        signature = request.POST.get('signature')

        if not all([payment_id, order_id, signature]):
            return JsonResponse({'error': 'Missing payment data'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Signature verification failed'}, status=400)

        # Fetch the correct order
        order = Order.objects.filter(razorpay_order_id=order_id).order_by('-order_date').first()

        if not order:
            return JsonResponse({'error': 'Order not found'}, status=400)

        order.payment_id = payment_id
        order.payment_status = 'Paid'
        order.save()

        send_mail(
            subject='Order Confirmation - Payment Successful',
            message=f'Your order #{order.id} has been successfully placed and paid online.',
            from_email='no-reply@amazonclone.com',
            recipient_list=[order.user.email],
            fail_silently=False
        )

        return JsonResponse({'order_id': order.id})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def cod_order(request):
    if request.method == 'POST':
        pincode = request.POST.get('pincode', '').strip()
        print("COD Order Received - Pincode:", repr(pincode))

        if pincode in COD_ALLOWED_PINCODES:
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Please log in to place an order.'})

            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items:
                return JsonResponse({'error': 'Your cart is empty.'})

            total_price = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                payment_status='Pending',
                payment_method='COD'
            )

            send_mail(
                subject='COD Order Confirmation',
                message=f'Thank you for your order #{order.id}. We’ll deliver it soon!',
                from_email='no-reply@amazonclone.com',
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            return JsonResponse({'redirect_url': '/cod/success/'})

        else:
            return JsonResponse({'error': 'COD not available in your area.'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return HttpResponse("Cart is empty", status=400)

        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        estimated_shipping = 50
        total_amount = subtotal + estimated_shipping

        # Pre-fill address form from user profile
        profile = request.user.profile
        address_form = AddressForm(initial={
            'name': request.user.get_full_name(),
            'phone': profile.phone,
            'address_line': profile.address,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
        })

        return render(request, 'Amazonclone/checkout.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'estimated_shipping': estimated_shipping,
            'amount': total_amount,
            'address_form': address_form,
        })

    return redirect('cart_view')

@login_required
def order_success(request):
    return render(request,'Amazonclone/order_success.html')

def thankyou(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.filter(id=order_id).first()
    return render(request, 'Amazonclone/thankyou.html', {'order': order})

@csrf_exempt
def check_cod_availability(request):
    if request.method == "POST":
        pincode = request.POST.get('pincode', '').strip()
        print("Checking COD for:", repr(pincode))  # Debugging

        if pincode in COD_ALLOWED_PINCODES:
            return JsonResponse({'cod_available': True, 'message': 'COD is available in your area.'})
        else:
            return JsonResponse({'cod_available': False, 'message': 'COD is not available in your area.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def cod_success_view(request):
    return render(request,'Amazonclone/order_success.html')

def send_order_status_email(user,order):
    subject=f"Your Order #{order.id} is {order.status.capitalize()}"
    message=f"Hello {user.username},\n\nYour order witj ID{order.id}is now{order.status.replace('_','').title()}.\n\nThank You!"
    send_mail(subject,message,'yourshop@example.com',[user.email])

@login_required
def notify_me(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    already_exists = StockNotification.objects.filter(user=request.user, product=product, notified=False).exists()
    if not already_exists:
        StockNotification.objects.create(user=request.user,product=product,notified=False)
        messages.success(request,"You'll be notified when this is product is back in stock")
    else:
        messages.info(request,"You are already subscribed for stock updates on this item")
    
    return redirect('product_detail',product_id=product_id)

def check_and_notify_stock(product):
    if product.stock > 0:
        notifications = StockNotification.objects.filter(product=product, notified=False)
        for note in notifications:
            send_mail(
                subject='Item back in stock!',
                message=f'Hi {note.user.username}, the product "{product.name}" is now available!',
                from_email='itspreksha54@gmail.com',
                recipient_list=[note.user.email],
            )
            note.notified = True
            note.save()

@login_required
def update_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        new_stock = int(request.POST.get('stock'))

        old_stock = product.stock
        product.stock = new_stock
        product.save()

        if old_stock == 0 and new_stock > 0:
            check_and_notify_stock(product)

        messages.success(request, 'Stock updated successfully.')
        return redirect('product_detail', product_id=product.id)

    return render(request, 'Amazonclone/update_stock.html', {'product': product})

def product_list(request):
    products = Product.objects.all()

    # Filters
    sort = request.GET.get('sort')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if brand:
        products = products.filter(brand__iexact=brand)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # Sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating_desc':
        products = products.order_by('-rating')

    # Optional: Get unique brand list for the filter dropdown
    brands = Product.objects.values_list('brand', flat=True).distinct()

    return render(request, 'Amazonclone/product_list.html', {
        'products': products,
        'brands': brands,
    })

def product_autocomplete(request):
    query=request.GET.get('term','')
    suggestions=list(Product.objects.filter(name_icontains=query).values_list('name',flat=True)[:10])
    return JsonResponse(suggestions,safe=False)

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        matching_products = Product.objects.filter(Q(name__icontains=query))[:10]
        suggestions = [{'id': p.id, 'name': p.name} for p in matching_products]

    return JsonResponse({'suggestions': suggestions})


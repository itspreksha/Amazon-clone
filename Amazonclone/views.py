from django.shortcuts import render,redirect,get_object_or_404
from .models import Product
from django.core.paginator import Paginator

# Create your views here.
def home(request):
  products=Product.objects.all()

  category=request.GET.get('category')
  search=request.GET.get('search')
  sort=request.GET.get('sort')
  page=request.GET.get('page',1)
  
  if category:
    products=products.filter(category=category)
  
  if search:
    products=products.filter(name__icontains=search)

  if sort=='price_asc':
    products=products.order_by('price')
  elif sort=='price_desc':
     products=products.order_by('-price')
  else:
    products=products.order_by('-created_at')

  paginator=Paginator(products,6)
  products_page=paginator.get_page(page)
  
  categories=[
    {'name': 'Mobiles'},
    {'name': 'Books'},
    {'name': 'Watches'},
    {'name': 'Shoes'},
    {'name': 'Fashion'},
    {'name': 'Electronics'},
    
  ]
  featured_products = [
        {'name': 'iPhone 16', 'price': '₹73,500', 'img': 'images/iphone16.jpg', 'category': 'Mobiles'},
        {'name': 'Harry Potter Book Set', 'price': '₹949', 'img': 'images/harrypotter.jpg', 'category': 'Books'},
        {'name': 'Titan Watch', 'price': '₹1695', 'img': 'images/titanwatch.jpg', 'category': 'Watches'},
        
    ]

  best_sellers = [
        {'name': 'Samsung Galaxy S24 Ultra', 'price': '₹99,700', 'img': 'images/S24Ultra.jpg', 'category': 'Mobiles'},
        {'name': 'Nike Sports Shoes', 'price': '₹11,245', 'img': 'images/nikeshoes.jpg', 'category': 'Shoes'},
    ]

  trending_items = [
        {'name': 'Noise Airwave Max5', 'price': '₹4,999', 'img': 'images/Bluetooth.jpg', 'category': 'Electronics'},
        {'name': 'Levi\'s Jeans', 'price': '₹1,799', 'img': 'images/levisjeans.jpg', 'category': 'Fashion'},
    ]

  deals = [
        {'banner_img': 'images/dealoftheday1.png'},
        {'banner_img': 'images/dealoftheday2.png'},
    ]

  deals_of_day = [
        {'name': 'Boat Bluetooth Speaker', 'price': '₹1,299', 'img': 'images/boatspeaker.jpg', 'discount': '35% Off'},
        {'name': 'Fastrack Watch', 'price': '₹2,499', 'img': 'images/fasttrackwatch.jpg', 'discount': '40% Off'},
        {'name': 'Dell Laptop Bag', 'price': '₹999', 'img': 'images/delllaptopbag.jpg', 'discount': '50% Off'},
    ]

  context = {
        'categories': categories,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'trending_items': trending_items,
        'deals': deals,
        'deals_of_day': deals_of_day,
        'products':products_page,
        'paginator':paginator,
    }
    
  return render(request, 'Amazonclone/home.html', context)
  
def product_detail(request):
    product_id = request.GET.get('id')

    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except product.DoesNotExist:
            return render(request, 'Amazonclone/product_not_found.html', status=404)
        return render(request, 'Amazonclone/product_detail.html', {'product': product})
    else:
        return render(request, 'Amazonclone/product_not_found.html', status=400)


def add_to_cart(request,product_id):
   cart=request.session.get('cart',{})

   if str(product_id) in cart:
      cart[str(product_id)]+=1
   else:
      cart[str(product_id)]=1

   request.session['cart']=cart
   return redirect('cart_view')

def remove_from_cart(request,product_id):
   cart=request.session.get('cart',{})
   if str(product_id) in cart:
      del cart[str(product_id)]
   request.session['cart']=cart
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

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'estimated_shipping': estimated_shipping,
        'total': total,
    }

    return render(request, 'Amazonclone/cart.html', context)

def get_cart_item_count(request):
    cart = request.session.get('cart', {})
    return sum(cart.values())

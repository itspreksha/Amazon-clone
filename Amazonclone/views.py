from django.shortcuts import render,redirect

# Create your views here.
def home(request):
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
    }
    
  return render(request, 'Amazonclone/home.html', context)
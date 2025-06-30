from django.core.mail import send_mail

def check_and_notify_stock(product):
    from .models import StockNotification  # Lazy import to avoid circular import

    if product.stock > 0:
        notifications = StockNotification.objects.filter(product=product, notified=False)
        for note in notifications:
            print(f"📧 Sending email to {note.user.email}")
            send_mail(
                subject='Product is Back in Stock!',
                message=f"Hi {note.user.username}, the product '{product.name}' is now available!",
                from_email='itspreksha54@gmail.com',
                recipient_list=[note.user.email],
                fail_silently=False,
            )
            note.notified = True
            note.save()

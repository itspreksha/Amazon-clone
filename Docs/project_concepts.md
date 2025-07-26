Assignment 1 : Software Design and Testing
Name : Preksha Joshi
Id : 202412029

AmazonClone - Project Concepts

--> Objects,Context and Information

1. Product
#Context-
--> Product listing, detail page, stock updates, price updates.

#Information- 
--> name, description, category, price, stock
--> Dynamic price adjustment based on views
--> Notification system when product is back in stock
--> Related to: Review, ProductQuestion, Cart, OrderItem

2. Profile
#Context-
--> User Profile Management, Order history, Verification

#Information-
--> Phone, City, State, Pincode, Address, Email_verified
--> Default_address, is_blocked

3. OTPVerification
#Context-
--> User registration, password recovery

#Information-
--> OTP, expires_at, verified

4. Order
#Context-
--> Checkout, order tracking, payment

#Information-
--> Status, total_price, payment_id, payment_method, payment_status
--> Related to: OrderItem

5. OrderItem
#Context-
--> Inside an Order

#Information-
--> product_name, price, quantity

6. Review
#Context-
--> product_feedback, star rating display

#Information-
--> rating, comment, created_at
--> related to: product, user

7. ProductQuestion
#Context-
--> Q&A section of product

#Information-
--> Question_text, answer, asked_at, answered_at

8. Address
#Context-
--> Checkout, Profile settings

#Information-
--> name, phone, pincode, address_line, city, state, address_type, is_default

9. Cart
#Context-
--> Before Checkout, product preview

#Information-
--> product, size, color, quantity

10. StockAlert & StockNotification
#Context-
--> When product is restocked

#Information-
--> notified, created_at
--> Triggers email alerts

11. UserLocation
#Context-
--> Location-aware services, City Specific delivery

#Information-
--> latitude, longitude, city, country, updated_at
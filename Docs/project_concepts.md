Assignment 1 : Software Design and Testing
Name : Preksha Joshi
Id : 202412029

Project Title: Amazon Clone – A Scalable E-commerce Platform
This document outlines the key concepts and components used in the Amazon Clone project. The system is described using three sections: Objects, Context, and Information (as per context) to clearly communicate the structure and behavior of the platform.

## Objects : 

User → A person registered on the platform (using Django’s built-in User model)

Profile → Extended user information like phone, address, and OTP

Product → An item listed for sale (with price, stock, specs, etc.)

Cart → Temporary collection of products a user intends to purchase

Order → A confirmed purchase made by the user

OrderItem → Individual item entries in an order

Review → Feedback with rating and comment submitted by users

ProductQuestion → User-submitted product inquiries, optionally answered

Address → Shipping/billing location linked to a user

OTPVerification → Stores and validates OTPs for account verification

StockAlert / StockNotification → Tracks user interest in out-of-stock products

UserLocation → Tracks user’s geolocation (city, country, lat/lon)

## Context :

User signup & verification
→ Involves User, Profile, and OTPVerification

Adding products to cart
→ Involves User, Cart, and Product (with optional size & color)

Placing an order
→ Involves Order, OrderItem, Product, User, and Address

Reviewing a product
→ Involves User, Product, and Review

Asking questions about a product
→ Involves User, Product, and ProductQuestion

Handling payments
→ Involves Order fields like razorpay_order_id, payment_status

Notifying users about restocked items
→ Involves StockNotification, Product, and send_mail

Tracking user location
→ Involves UserLocation and User

Default shipping address selection
→ Involves Profile and Address

## Information (as per context):

User Signup & Verification
username, email, password, otp, is_verified, phone, city, state, pincode

Adding to Cart
user_id, product_id, size, color, quantity

Placing an Order
user_id, order_date, order_items (with product names, prices, quantities),
total_price, payment_method, payment_status, shipping_address

Product Review
rating, comment, image, user_id, product_id, timestamp

Product Questions
question_text, answer, asked_at, answered_at, user_id, product_id

Payments
razorpay_order_id, payment_id, payment_method, payment_status

Stock Notification
product_id, user_id, notified status, email sent timestamp

User Location Tracking
latitude, longitude, city, country, last_updated

Address Management
name, phone, pincode, address_line, city, state, address_type, is_default

# AutomatedFoodOrderingApp in Django
This project is a Django-backend automated food ordering system, where users can register as either customers or cafe administrators. Customers can view menus, add items to their cart, place orders, make payments through the Daraja API (M-Pesa), earn loyalty points, and redeem points for food items. Cafe administrators can manage food items, categories, dining tables, and view daily orders and reviews. Both users and admins receive notifications for important events, such as payments and point redemptions.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Database Models](#database-models)
- [Authentication and Authorization](#authentication-and-authorization)
- [Payment Integration](#payment-integration)
- [Loyalty Points System](#loyalty-points-system)
- [Notifications](#notifications)
- [Order Review System](#order-review-system)
- [Admin Features](#admin-features)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)


# Features
## Customer
- View food menu items categorized by food categories.
- Add multiple food items to the cart.
- Place an order and specify the dining table.
- Make payments using Daraja API (M-Pesa).
- Receive loyalty points for every 100 KSH spent.
- Redeem points for specific food items.
- View order history (paid, unpaid, and redeemed orders).
- Review the order on the same day it was placed.

## Cafeadmin
- Manage food categories (add, edit, delete).
- Manage food items under categories (add, edit, delete).
- Manage special offers.
- Manage dining tables.
- View daily orders (paid, unpaid, and completed).
- Mark orders as completed.
- Receive notifications for payments and point redemptions.
- Create orders for customers directly from the counter.
- View daily customer reviews.

# Tech Stack

- **Python** 3.x with **Django** 5.x
- **restframewor** for API
- **djoser** for user management
- **simplejwt** for json web token authentication
- **PostgreSQL** for the database
- **Celery** with **Redis** for background tasks
- **Daraja API** (M-Pesa) for payment integration



# Setup Instructions
1. Clone the Repository
```
git clone https://github.com/yourusername/food-ordering-system.git
cd food-ordering-system
```
2. Setup the Virtualenvironment
```
python3 -m venv env
source env/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt

```
4. Optional: Set Up PostgreSQL Database, you can use the default sqlite3
```
CREATE DATABASE food_ordering_system;
CREATE USER yourusername WITH PASSWORD 'yourpassword';
ALTER ROLE yourusername SET client_encoding TO 'utf8';
ALTER ROLE yourusername SET default_transaction_isolation TO 'read committed';
ALTER ROLE yourusername SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE food_ordering_system TO yourusername;
```
5. Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```

6. Create Superuser
```
python manage.py createsuperuser
```
7. Run development server
```
python manage.py runserver
```

# Environment variables
Create a .env file at the root of your project and configure the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
DB_NAME=food_ordering_system
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Daraja API credentials
DARAJA_CONSUMER_KEY=your_consumer_key
DARAJA_CONSUMER_SECRET=your_consumer_secret

# Celery and Redis settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

# Database Models
- **User**: Extended with roles (Customer, CafeAdmin).
- **Category**: Food categories (e.g., Drinks, Main Course).
- **FoodItem**: Specific food items under a category.
- **Cart**: Customer’s cart with items.
- **Order**: Tracks customer orders and dining table.
- **OrderItem**: Links each ordered food item to an order.
- **Payment**: Tracks payments made via M-Pesa.
- **LoyaltyPoints**: Manages customer points for rewards.
- **Review**: Tracks customer reviews for orders.
- **SpecialOffer**: Discounts or promotions on food items.
- **DiningTable**: Specifies the dining tables available.


# Authentication and Authorization
- Authentication: Use djoser or django-allauth for user registration and authentication.
- Authorization: Customers and cafeadmins have different permissions for accessing various views and functionalities.
- Custom Permissions: Ensure only cafeadmins can manage the menu, orders, and tables.

# Payment Integration
We use the Daraja API (M-Pesa) for handling mobile payments.

Payment Flow:
Customer places an order.
Payment request is sent to Daraja API.
M-Pesa confirms the payment.
Order is marked as "Paid" upon confirmation.

## Setup:
Follow the official Daraja API documentation to obtain your API keys.
Implement the payment views and handle callbacks securely.

# Loyalty Points System
- Customers earn 1 point for every 100 KSH spent on orders.
- Points can be redeemed for specific food items.
- Points are awarded automatically after a successful payment using Django signals.

# Notifications
- django-notifications-hq is used to send notifications.
- Notifications are sent to both customers and cafeadmins when:
1. Payment is successful.
2. Loyalty points are redeemed.
3. Orders are placed or updated.

# Order Review System
Customers can review their orders, but only on the day the order was placed.
Reviews are linked to specific orders, and cafeadmins can view daily reviews.

# Admin Features
Cafeadmins can:
- Manage food categories and items.
- Manage special offers.
- Track and update order statuses.
- View daily reports on orders and reviews.
- Create orders directly from the counter for walk-in customers.


# API Endpoints
1. **User Registration** registers a new user. Send a POST request to api/auth/users/ with the following JSON payload.

```
{
  "username": "williams",
  "password": "strong_password",
  "email": "williams@example.com"
}

```
Response:
```
{
  "id": "dc2f3863-d708-4ac7-b6c1-7b5a3327fc29",
  "username": "williams",
  "email": "williams@example.com"
}
```

2. **User Login** logs in the user and returns a jwt access and refresh tokens. Send post request to api/auth/jwt/create with the following JSON payload.

```
{
  "username": "williams",
  "password": "strong_password"
}

```

Response:
```
{
  "refresh": "your_refresh_token_here",
  "access": "your_access_token_here"
}

```
3. **User Info** retrieves detail of the currently logged in user. Send a GET request to api/auth/users/me/ with authorization headers.

Response:
```
{
  "id": "dc2f3863-d708-4ac7-b6c1-7b5a3327fc29",
  "username": "williams",
  "email": "williams@example.com"
}
```

4. **Role based redirection** send a GET request to api/account/role-based-redirect/ with authorizarion headers.

Response: if user is admin
```
{
  "role": "cafeadmin",
  "redirect_url": "/api/cafeadmin/"
}
```

Response: if user is customer
```
{
  "role": "customer",
  "redirect_url": "/api/customer/"
}
```
The frontend can check the role attribute and apply the appropriate redirection logic once the login is successfull.Admin users can be redirected to the admin dashboard.
Customer users can be redirected to the customer area.


# Testing
Run the tests using pytest:

```
pytest
```

tests for:
- User authentication and permissions.
- Order placement and payment processing.
- Loyalty points redemption.
- Admin actions and notifications.


# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Contact
For any issues or contributions, please feel free to reach out or open a pull request.

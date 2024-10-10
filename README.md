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
- **restframework** for API
- **djoser** for user management
- **simplejwt** for json web token authentication
- **PostgreSQL** for the database or **sqlite** for default database
- **Celery** with **Redis** for background tasks
- **Redis** for caching
- **Daraja API** (M-Pesa) for payment integration
- **python-decouple** for managing environment variables



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

5. **Swagger Docs** : for swagger documentatio - /api/docs/schema/swagger/

6. **Redoc docs** : for redoc documentation - /api/docs/schema/redoc/

7. **List Categories**
This endpoint returns a list of all available categories. The list can be filtered, searched, and ordered. The cafeadmin must be authenticated to access this endpoint.

Query Parameters:
?name=<name>: Filters categories containing the provided name (case-insensitive).
?search=<term>: Searches for the term within the name or description of categories.
?ordering=<field>: Orders the categories by the specified field (default: created_at).

Example Request: pass authorization headers

```
GET /api/cafeadmin/categories/?name=fruit&search=organic&ordering=-created_at

```
Example Response (if categories exist):
```
[
  {
    "id": "d234f1b4-bd8f-4b7a-a671-332c8ffbddee",
    "name": "Fruits",
    "description": "All kinds of fruits.",
    "created_at": "2024-09-28T12:34:56Z",
    "updated_at": "2024-09-28T12:34:56Z"
  }
]

```

Getting all categories:
Example Request:

```
GET /api/cafeadmin/categories/

```

Response:
```
[
  {
    "id": "ee3985a7-ec99-4f26-ae6c-18ae2e1642c0",
    "name": "updated",
    "description": "Fresh organic vegetables.",
    "created_at": "2024-10-05T17:13:24.062408+03:00",
    "updated_at": "2024-10-05T17:48:59.000216+03:00"
  },
  {
    "id": "2a9848a9-2952-4cba-848a-4fa30945e137",
    "name": "Breakfast",
    "description": "First Meal of the day.",
    "created_at": "2024-10-05T17:15:08.157435+03:00",
    "updated_at": "2024-10-05T17:15:08.157473+03:00"
  }
  ...
]
```
8. **Create a new Category**: allows you to create a new category by providing a unique name and description.
Example Request: with authorization headers

```
POST /api/cafeadmin/categories/

```
Request body:
```
{
  "name": "Vegetables",
  "description": "Fresh organic vegetables."
}

```
Example Response:
```
{
  "id": "e451f734-56a7-4d8b-bdda-234c879fae12",
  "name": "Vegetables",
  "description": "Fresh organic vegetables.",
  "created_at": "2024-10-05T13:45:23Z",
  "updated_at": "2024-10-05T13:45:23Z"
}
```

9. **Retrieve, Update, Delete** a category.
Endpoint: /api/cafeadmin/categories/<uuid>/
Methods: GET, PUT, PATCH, DELETE

GET: Retrieve Category by ID
Fetches details for a specific category.

Example Request:
```
GET /api/cafeadmin/categories/d234f1b4-bd8f-4b7a-a671-332c8ffbddee/

```
Example response:
```
{
  "id": "d234f1b4-bd8f-4b7a-a671-332c8ffbddee",
  "name": "Fruits",
  "description": "All kinds of fruits.",
  "created_at": "2024-09-28T12:34:56Z",
  "updated_at": "2024-09-28T12:34:56Z"
}

```
PUT/PATCH: Update a Category
Allows you to update a category by providing new data. Either a full update (PUT) or partial update (PATCH) is supported.

Request Body (for PUT):
```
{
  "name": "Updated Category",
  "description": "Updated description of the category."
}

```
Response:
```
{
  "id": "d234f1b4-bd8f-4b7a-a671-332c8ffbddee",
  "name": "Updated Category",
  "description": "Updated description of the category.",
  "created_at": "2024-09-28T12:34:56Z",
  "updated_at": "2024-10-05T14:15:23Z"
}

```

DELETE: Remove a Category
Deletes the specified category.

Example Request:
```
DELETE /api/cafeadmin/categories/d234f1b4-bd8f-4b7a-a671-332c8ffbddee/

```

Response:
```
{
  "message": "Category deleted successfully."
}

```
**Filtering, Searching, and Ordering**
**Filtering**
You can filter the list of categories by name using the ?name= query parameter. This filter is case-insensitive and will match any category whose name contains the given value.

Example:
```
GET /api/cafeadmin/categories/?name=fruit
```
**Searching**
Search through the name and description of categories using the ?search= parameter. It will look for the search term in both fields.

Example:
```
GET /api/cafeadmin/categories/?search=organic
```

**Ordering**
You can order the categories by any field using the ?ordering= query parameter. By default, the results are ordered by created_at in ascending order. To order in descending order, prefix the field name with a minus sign (-).

Example:
```
GET /api/cafeadmin/categories/?ordering=-created_at
```

10. **Customer fetching Categories**: customers can fetch existing list of categories by sending  GET request to : /api/customer/categories/

Response:
```
[
  {
    "id": "ee3985a7-ec99-4f26-ae6c-18ae2e1642c0",
    "name": "updated",
    "description": "Fresh organic vegetables.",
    "created_at": "2024-10-05T17:13:24.062408+03:00",
    "updated_at": "2024-10-05T17:48:59.000216+03:00"
  },
  {
    "id": "2a9848a9-2952-4cba-848a-4fa30945e137",
    "name": "Breakfast",
    "description": "First Meal of the day.",
    "created_at": "2024-10-05T17:15:08.157435+03:00",
    "updated_at": "2024-10-05T17:15:08.157473+03:00"
  }
  ...
]
```

To get detailed info about the category and the fooditems under the category, send a GET request to /api/customer/categories/{category_id}/fooditems/

Response:
```
[
  {
    "id": "c1e28951-09bc-470d-a49f-f5d45baf043b",
    "category": "Breakfast",
    "name": "Eggs",
    "price": "40.00",
    "image": "/media/food_images/default.jpg",
    "description": "Eggs for breakfast",
    "created_at": "2024-10-07T13:42:44.297183+03:00",
    "updated_at": "2024-10-07T14:08:32.835961+03:00",
    "is_available": false
  }
  {
    "id": "c1e28951-09bc-470d-a49f-f5d45baf043b",
    "category": "Vegetables",
    "name": "Salad",
    "price": "40.00",
    "image": "/media/food_images/default.jpg",
    "description": "Salad",
    "created_at": "2024-10-07T13:42:44.297183+03:00",
    "updated_at": "2024-10-07T14:08:32.835961+03:00",
    "is_available": false
  }
  ...
]
```

11. **Dinning tables**: endpoints for cafeadmin to manage dinning tables
```
GET /api/cafeadmin/dinning-tables/
POST /api/cafeadmin/dinning-tables/

PATCH /api/cafeadmin/dinning-tables/{id}/
GET /api/cafeadmin/dinning-tables/{id}/
PUT /api/cafeadmin/dinning-tables/{id}/
DELETE /api/cafeadmin/dinning-tables/{id}/
```

12. **Dinning tables**: endpoints for customer to access all dinning tables
```
GET /api/customer/dinning-tables/
```

13. **FoodItems**: endpoints for admin to manage fooditems under a specific category

```
GET /api/cafeadmin/categories/{category_id}/fooditems/
POST /api/cafeadmin/categories/{category_id}/fooditems/

GET /api/cafeadmin/categories/{category_id}/fooditems/{fooditem_id}/
PUT /api/cafeadmin/categories/{category_id}/fooditems/{fooditem_id}/
PATCH /api/cafeadmin/categories/{category_id}/fooditems/{fooditem_id}/
DELETE /api/cafeadmin/categories/{category_id}/fooditems/{fooditem_id}/

```

14. **SpecialOffers**: endpoints for admin to manage specialoffers

```
GET /api/cafeadmin/specialoffers/
POST /api/cafeadmin/specialoffers/{fooditem_id}/

GET /api/cafeadmin/specialoffers/{offer_id}/detail/
PUT /api/cafeadmin/specialoffers/{offer_id}/detail/
PATCH /api/cafeadmin/specialoffers/{offer_id}/detail/
DELETE /api/cafeadmin/specialoffers/{offer_id}/detail/

```

**Customers accessing specialoffers**- send a GET request to:
```
GET /api/customer/specialoffers/
```

15. **Cart and Order Management**- customers adding items to cart, viewing cart, and updating cart(by deleting cart items or by updating cartitem quantity), placing an order, viewing all orders, cancel unpaid orders
```
POST /api/customer/add-to-cart/{fooditem_id}/

GET api/customer/my-cart/

PATCH api/customer/my-cart/{cartitem_id}/
DELETE api/customer/my-cart/{cartitem_id}/

POST api/customer/my-cart/place-order/
GET api/customer/orders/

POST api/customer/orders/{order_id}/cancel/

```

16. **Payment**: payment for orders placed
```
POST api/customer/order/{order_id}/payment/
```

17. **Reviews** customers can add reviews, update reviews, delete reviews, view reviews they have made.

```
GET api/customer/reviews/
POST api/customer/orders/{order_id}/review/

PATCH api/customer/reviews/{order_id}/update/
DELETE api/customer/reviews/{order_id}/delete/
```
Admin can also view customer reviews

```
GET /api/cafeadmin/customer-reviews/

```

18. **Notifications**: endpoints for notifications with filtering, ordering, search
**Customer Notification**
```
GET api/customer/notifications/
GET api/customer/notifications/{notification_id}/
DELETE api/customer/notifications/{notification_id}/

PATCH /api/customer/notifications/mark-as-read/
DELETE /api/customer/notifications/delete/

```

**CafeAdmin Notification**
```
GET api/cafeadmin/notifications/
GET api/cafeadmin/notifications/{notification_id}/
DELETE api/cafeadmin/notifications/{notification_id}/

PATCH /api/cafeadmin/notifications/mark-as-read/
DELETE /api/cafeadmin/notifications/delete/
```

19. **Loyalty points**: customers can view their loyalty points , redeem loyalty points
```
GET api/customer/loyalty-points/

POST api/customer/loyalty-points/{redemption_id}/redeem/

```

20. **Redemption options**: cafeadmin can manage redemption options from this endpoints
```
GET api/cafeadmin/redemptio-options/
POST api/cafeadmin/redemptio-options/

GET api/cafeadmin/redemptio-options/{redemption_id}/
PUT api/cafeadmin/redemptio-options/{redemption_id}/
DELETE api/cafeadmin/redemptio-options/{redemption_id}/

```

Customer can view redemption options via:
```
GET api/customer/redemption-options/
```

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

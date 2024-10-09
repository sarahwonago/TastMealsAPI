from .models import CustomerLoyaltyPoint, Transaction

def award_customer_points(order):
    customer_points = CustomerLoyaltyPoint.objects.get(user=order.user)

    # Award 1 point for every 100 Ksh paid
    points_earned = int(order.total_price // 100)
    
    if points_earned > 0:
        # Update the customer's loyalty points
        customer_points.points += points_earned
        customer_points.save()

        # Create a transaction record
        transaction = Transaction.objects.create(
            customer_loyalty_point=customer_points,
            amount=order.total_price,
            points_earned=points_earned
            )      

    return 1
def calculate_ride_price(distance_km: float) -> float:
    """
    Calculate ride price based on distance.
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        Price in SYP
    """
    BASE_PRICE = 10000  # SYP
    PRICE_PER_KM = 5000  # SYP
    
    return max(BASE_PRICE, distance_km * PRICE_PER_KM)


def calculate_delivery_price(
    distance_km: float,
    driver_pays: bool = False,
    product_amount: float = 0
) -> dict:
    """
    Calculate delivery price including delivery fee and optional product amount.
    
    Args:
        distance_km: Distance in kilometers
        driver_pays: Whether driver pays for the product
        product_amount: Product amount in SYP
        
    Returns:
        Dictionary with delivery_fee and total_cost
    """
    delivery_fee = calculate_ride_price(distance_km)
    total_cost = delivery_fee
    
    if driver_pays and product_amount > 0:
        total_cost += product_amount
    
    return {
        "delivery_fee": delivery_fee,
        "total_cost": total_cost
    }

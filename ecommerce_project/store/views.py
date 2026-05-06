from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Order

# HOME
def home(request):
    products = Product.objects.all()[:4]
    return render(request, 'home.html', {'products': products})


# PRODUCTS PAGE
def products(request):
    items = Product.objects.all()
    return render(request, 'products.html', {'items': items})


# PRODUCT DETAIL
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return render(request, 'product_detail.html', {'product': product})
    except Product.DoesNotExist:
        return redirect('products')


# ADD TO CART
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    try:
        product = Product.objects.get(id=product_id)
        if str(product_id) in cart:
            cart[str(product_id)] += 1
        else:
            cart[str(product_id)] = 1

        request.session['cart'] = cart
        request.session.save()  # Explicitly save the session
        messages.success(request, f'{product.name} added to cart!')
        # Redirect to products to continue shopping
        return redirect('products')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('home')


# CART PAGE
def cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    items_to_remove = []

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            product.qty = qty
            product.total_price = product.price * qty
            total += product.total_price
            products.append(product)
        except Product.DoesNotExist:
            # Mark for removal instead of deleting during iteration
            items_to_remove.append(product_id)

    # Remove invalid products after iteration
    for product_id in items_to_remove:
        del cart[str(product_id)]

    if items_to_remove:
        request.session['cart'] = cart
        request.session.save()

    return render(request, 'cart.html', {
        'products': products,
        'total': total
    })


# REMOVE ITEM
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart')


# UPDATE QUANTITY
def update_cart_quantity(request, product_id):
    if request.method == "POST":
        action = request.POST.get('action')
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            if action == "increase":
                cart[str(product_id)] += 1
            elif action == "decrease":
                if cart[str(product_id)] > 1:
                    cart[str(product_id)] -= 1
                else:
                    del cart[str(product_id)]

        request.session['cart'] = cart

    return redirect('cart')


# CHECKOUT
def checkout(request):
    if request.method == 'POST':
        # Process the order
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        notes = request.POST.get('notes', '')

        # Create the order
        order = Order.objects.create(
            full_name=full_name,
            email=email,
            address=address,
            phone=phone,
            notes=notes
        )

        # Clear the cart
        request.session['cart'] = {}
        request.session.save()

        messages.success(request, 'Order placed successfully!')
        return render(request, 'checkout.html', {'success': True})

    # GET request: show cart items
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            product.qty = qty
            product.total_price = product.price * qty
            total += product.total_price
            products.append(product)
        except Product.DoesNotExist:
            pass

    return render(request, 'checkout.html', {
        'products': products,
        'total': total
    })
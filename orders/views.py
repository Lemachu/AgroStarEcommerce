from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from accounts.models import Account
# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = round(order.order_total, 2),
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Hvala Vam što kupujete kod nas!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = round((2 * total)/100, 2)
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.phone1 = form.cleaned_data['phone1']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20220922
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)     
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def placanje_preuzecem(request, order_num):
    order_number = int(order_num)
    transID = None
    order = Order.objects.get(order_number=order_number)
    cart_item=CartItem.objects.all().filter(user=request.user) 
    for item in cart_item:
        #spremanje naručenih proizvoda u bazu
        price = item.product.price
        naruceno = OrderProduct()
        naruceno.quantity=item.quantity
        naruceno.product_price=price
        naruceno.ordered=True
        naruceno.order=Order.objects.get(id=order.id)
        naruceno.payment=None
        naruceno.product=Product.objects.get(id=item.product.id)
        naruceno.user=Account.objects.get(id=request.user.id)
        naruceno.save()

    try:
        order = Order.objects.get(order_number=order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        order.is_ordered = True
        order.save()

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = 'Preuzećem'

        cart_item=CartItem.objects.all().filter(user=request.user)
        for item in cart_item:
            #brisanje proizvoda iz
            proizvod = Product.objects.get(id=item.product.id)
            proizvod.stock -= item.quantity
            proizvod.save()
            cart_item.delete()
            
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': transID,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist):
        pass

def licno_preuzimanje(request):
    current_user=Account.objects.get(id=request.user.id)
    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    grand_total = 0
    total=0
    quantity=0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = round((2 * total)/100, 2)
    grand_total = total + tax
    data = Order()
    data.user = current_user
    data.first_name = current_user.first_name
    data.last_name = current_user.last_name
    data.phone = current_user.phone_number
    data.email = current_user.email
    data.address_line_1 = 'Lično preuzeće na tržnici'
    data.address_line_2 = ' '
    data.country = ' '
    data.state = ' '
    data.city = ' '
    data.order_note = ' '
    data.order_total = grand_total
    data.tax = tax
    data.ip = request.META.get('REMOTE_ADDR')
    data.save()
    # Generate order number
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr,mt,dt)
    current_date = d.strftime("%Y%m%d") #20220922
    order_number = current_date + str(data.id)
    data.order_number = order_number
    data.save()

    order = Order.objects.get(user=current_user, order_number=order_number)
    cart_item=CartItem.objects.all().filter(user=request.user) 
    for item in cart_item:
        price = item.product.price
        naruceno = OrderProduct()
        naruceno.quantity=item.quantity
        naruceno.product_price=price
        naruceno.ordered=True
        naruceno.order=Order.objects.get(id=order.id)
        naruceno.payment=None
        naruceno.product=Product.objects.get(id=item.product.id)
        naruceno.user=Account.objects.get(id=request.user.id)
        naruceno.save()
    try:
        order = Order.objects.get(order_number=order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        order.is_ordered = True
        order.save()

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        cart_item=CartItem.objects.all().filter(user=request.user)
        for item in cart_item:
            proizvod = Product.objects.get(id=item.product.id)
            proizvod.stock -= item.quantity
            proizvod.save()
            cart_item.delete()
            
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': None,
            'payment': None,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist):
        pass


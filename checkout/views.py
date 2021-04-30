from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from .forms import OrderCreateForm
from django.contrib import messages
from bag.contexts import bag_contents
from django.conf import settings
from shop.models import Product
from .models import Order, OrderItem

import stripe
import json

@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def create_checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'street_address': request.POST['street_address'],
            'postal_code': request.POST['postal_code'],
            'city': request.POST['city'],
            'country': request.POST['country'],
        }
        order_form = OrderCreateForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.paid = True
            order.grand_total = True
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()

                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database."
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            # Save the info to the user's profile if all is well
            # request.session['save_info'] = 'save-info' in request.POST

            """
            confirmation email for submission
            """
            messages.success(request, f'Order successfully processed! \
                Your order number is {order.id}. A confirmation \
                email will be sent to {order.email}.')

            if 'bag' in request.session:
                del request.session['bag']

            return render(request, 'checkout/order/checkout_success.html')
        else:
            messages.error(request, 'There was an error with your form. \
            Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('index'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

    form = OrderCreateForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/order/checkout.html'
    context = {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


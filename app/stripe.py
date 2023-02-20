import stripe
from django.conf import settings
import json
from django.http import JsonResponse

###------------------------------- STRIPE -------------------------------###
stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = settings.YOUR_DOMAIN


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 500


class StripeCreatePayment:
    def create_payment(self, request):
        data = request.data
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data["items"]),
            currency="cad",
            automatic_payment_methods={
                "enabled": True,
            },
        )
        return intent


class CreateCheckoutSessionService:
    def create_checkout_session(self, request):
        prices = stripe.Price.list(
            lookup_keys=[request.POST["lookup_key"]], expand=["data.product"]
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": 1,
                },
            ],
            customer_email=request.user.email,
            mode="subscription",
            success_url=YOUR_DOMAIN + "stripe/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=YOUR_DOMAIN + "stripe/cancel",
        )
        return HttpResponseRedirect(checkout_session.url)


class CreatePortalSessionService:
    def create_portal_session(self, request):
        checkout_session_id = request.user.stripe_session_id
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

        # This is the URL to which the customer will be redirected after they are
        # done managing their billing with the portal.
        return_url = YOUR_DOMAIN + "dashboard"

        portalSession = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=return_url,
        )
        return HttpResponseRedirect(portalSession.url)


class StripeCheckPaymentService:
    def check_payment(self, request):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print(f"{event=}")
            session = event["data"]["object"]
            print(f"{session=}")

            # stripe_user_email = session["customer_details"]["email"]
            stripe_payment_status = session["payment_status"]
            stripe_payment_data = stripe.checkout.Session.list_line_items(
                session["id"], limit=1
            )
            product = stripe_payment_data["data"][0]["description"]
            price_paid = stripe_payment_data["data"][0]["amount_total"] / 100

            if stripe_payment_status == "paid":
                user = User.objects.get(email=session["customer_email"])
                user.active_subscription = True

                if "1 month" in product:
                    subscription_period = 30
                else:
                    subscription_period = 365
                if user.paid_until == None:
                    user.paid_until = timezone.now() + datetime.timedelta(
                        days=subscription_period
                    )
                else:
                    user.paid_until += datetime.timedelta(days=subscription_period)
                user.stripe_session_id = session["id"]
                user.save()

                order = Orders.objects.create(
                    user=user,
                    order_type="Subscription",
                    price=price_paid,
                    payment_status="active",
                    subscription_period=subscription_period,
                    payment_date=timezone.now(),
                )
                order.save()

                email = EmailService()
                email.send_payment_confirmation(user, YOUR_DOMAIN)
                # celery_stop_membership.apply_async(
                #     kwargs={"user_id": user.id}, countdown=user.paid_until
                # )
        return HttpResponse(status=200)

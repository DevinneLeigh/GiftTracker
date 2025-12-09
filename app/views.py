from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q, Prefetch
from decimal import Decimal
from .forms import TemplateFormMixin, RecipientForm, EventForm, WishListForm, ParticipantForm, GiftForm 
from .models import Recipient, Event, Participant, Gift, Budget, WishList
from .utils import *
from .scraper import Scraper

EVENT_IMAGES = {
    "birthday": "birthday.png",
    "wedding": "wedding.png",
    "christmas": "christmas.png",
    "graduation": "graduation.png",
}

def landing(request):
	return render(request, "landing.html")

@login_required(login_url='/landing/')
def index(request):
    user = request.user
    recipients = Recipient.objects.filter(user=user)
    events = Event.objects.filter(user=user).prefetch_related(
        Prefetch(
            'participant_set',
            queryset=compute_totals(
                Participant.objects.select_related('recipient').prefetch_related('gift_set')
            ),
            to_attr='participants_with_totals'
        )
    )
    for e in events:
        participants = e.participant_set.prefetch_related('gift_set').all()
        e.participants_with_totals = compute_totals(participants)


    participants = Participant.objects.select_related('recipient', 'event').all()


    wishlists = WishList.objects.filter(recipient__in=recipients)
    recipient_form = RecipientForm()
    event_form = EventForm()
    event_edit_forms = {e.id: EventForm(instance=e) for e in events}
    recipient_edit_forms = {r.id: RecipientForm(instance=r) for r in recipients}
    recipient_wishlist_status = {r.id: WishList.objects.filter(recipient=r).exists() for r in recipients}
    return render(request, "index.html", {
        "recipients": recipients,
        "events": events,
        "participants": participants,
        "wishlists": wishlists,
        "recipient_wishlist_status": recipient_wishlist_status,
        "recipient_form": recipient_form,
        "event_form": event_form,
        "event_edit_forms": event_edit_forms,
        "recipient_edit_forms": recipient_edit_forms,

    })



# Events
@login_required(login_url='/landing/')
def add_event(request):
    user = request.user
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = user
            event.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))
    else:
        form = EventForm()
    html = render_to_string("partials/event_form.html", {"form": form}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def edit_event(request, id):
    user = request.user
    event = get_object_or_404(Event, id=id, user=user)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))
    else:
        form = EventForm(instance=event)
    html = render_to_string("partials/event_form.html", {"form": form}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def delete_event(request, id):
    user = request.user
    event = get_object_or_404(Event, id=id, user=user)
    if request.method == "POST":
        event.delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))

@login_required(login_url='/landing/')
def view_event(request, id):
    user = request.user
    event = get_object_or_404(Event, id=id, user=user)
    participants = event.participant_set.select_related("recipient").prefetch_related('gift_set').all()
    participants = compute_totals(participants)
    recipients = [p.recipient for p in participants]
    active_tab = request.GET.get("tab")

    return render(request, "view_event.html", {
        "event": event,
        "participants": participants,
        "active_tab": active_tab,
        "recipients": recipients,
    })



# Recipients
@login_required(login_url='/landing/')
def add_recipient(request):
    user = request.user
    if request.method == "POST":
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.user = user
            recipient.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))
    else:
        form = RecipientForm()
    html = render_to_string("partials/recipient_form.html", {"form": form}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def edit_recipient(request, id):
    user = request.user
    recipient = get_object_or_404(Recipient, id=id, user=user)
    if request.method == "POST":
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))
    else:
        form = RecipientForm(instance=recipient)
    html = render_to_string("partials/recipient_form.html", {"form": form}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def delete_recipient(request, id):
    user = request.user
    recipient = get_object_or_404(Recipient, id=id, user=user)
    if request.method == "POST": 
        recipient.delete()
        return redirect(request.META.get("HTTP_REFERER", "index"))
    return redirect(request.META.get("HTTP_REFERER", "index"))




# Participants
@login_required(login_url='/landing/')
def add_participant(request, event_id):
    user = request.user
    event = get_object_or_404(Event, id=event_id, user=user)
    participant = None 

    referer = request.META.get("HTTP_REFERER", "")

    if request.method == "POST":
        form = ParticipantForm(request.POST, user=user, event=event)

        if form.is_valid():
            participant = form.save(commit=False)
            participant.event = event
            participant.save()

            budget_amount = request.POST.get("budget")
            if budget_amount:
                Budget.objects.create(participant=participant, price=budget_amount)
            
            return redirect(referer or reverse("index"))

    else:
        form = ParticipantForm(user=user, event=event)

    html = render_to_string(
        "partials/participant_form.html",
        {"form": form, "participant": participant, "event": Event.objects.filter(user=user)},
        request=request
    )
    return HttpResponse(html)

@login_required(login_url='/landing/')
def edit_participant(request, participant_id):
    user = request.user
    participant = get_object_or_404(Participant, id=participant_id)
    event = participant.event
    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant, user=user, event=event)
        
        if form.is_valid():
            participant = form.save()
            budget_value = request.POST.get("budget")
            if budget_value:
                Budget.objects.update_or_create(
                    participant=participant, defaults={"price": budget_value}
                )
            referer = request.META.get("HTTP_REFERER", "")
            return redirect(referer or reverse("index"))
    else:
        form = ParticipantForm(instance=participant, user=user, event=event)

    html = render_to_string("partials/participant_form.html", {"form": form, "participant": participant}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def delete_participant(request, id):
    user = request.user
    participant = get_object_or_404(Participant, id=id, event__user=user)
    if request.method == "POST": 
        participant.delete()
    referer = request.META.get("HTTP_REFERER", "")
    return redirect(referer or reverse("index"))

@login_required(login_url='/landing/')
def add_wish_list(request, recipient_id):
    user = request.user
    recipient = get_object_or_404(Recipient, id=recipient_id, user=user)

    if request.method == "POST":
        form = WishListForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.recipient = recipient

            posted_name = request.POST.get("product_name")
            posted_price = request.POST.get("product_price")
            posted_image = request.POST.get("product_image")

            if posted_name or posted_price or posted_image:
                if posted_name is not None:
                    item.product_name = posted_name
                if posted_price is not None:
                    item.product_price = posted_price
                if posted_image is not None:
                    item.product_image = posted_image
            else:
                product_data = Scraper(item.item_url).scrape_product()
                if product_data:
                    item.product_name = product_data.get("name") or ""
                    item.product_image = product_data.get("image") or ""
                    item.product_price = product_data.get("price") or ""

            item.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))
    else:
        form = WishListForm()

    # Use the gift_form partial for both if you want the same markup.
    html = render_to_string("partials/gift_form.html", {"form": form, "recipient": recipient}, request=request)
    return HttpResponse(html)


@login_required(login_url='/landing/')
def edit_wish_list(request, wish_id):
    item = get_object_or_404(WishList, id=wish_id)
    recipient = item.recipient

    if request.method == "POST":
        # Directly update the fields from the POST data
        item.product_name = request.POST.get("product_name", item.product_name)
        item.product_price = request.POST.get("product_price", item.product_price)
        item.product_image = request.POST.get("product_image", item.product_image)
        item.save()

        # Redirect back to the recipient's page (or wherever appropriate)
        return redirect(request.META.get("HTTP_REFERER", "index"))

    html = render_to_string(
        "partials/gift_form.html",
        {"gift": item, "edit_mode": True},
        request=request
    )
    return HttpResponse(html)



# def view_wish_list(request, wishlist_id, name):
#     wishlist = get_object_or_404(WishList, id=wishlist_id)

#     recipient = get_object_or_404(Recipient, id=wishlist_id)
#     wishlist_items = recipient.wishlist.all()

#     return render(request, 'view_wish_list.html', {
#         'recipient': recipient,
#         'wishlist_items': wishlist_items,
#     })

@login_required(login_url='/landing/')
def view_wish_list(request, wishlist_id, name):
    """
    wishlist_id is actually the recipient ID in your URLs. We'll get the recipient,
    then fetch all their wishlist items.
    """
    recipient = get_object_or_404(Recipient, id=wishlist_id)
    wishlist_items = recipient.wishlist.all()

    return render(request, 'view_wish_list.html', {
        'recipient': recipient,
        'wishlist_items': wishlist_items,
    })

@login_required(login_url='/landing/')
def delete_wish_list(request, id):
    user = request.user
    item = get_object_or_404(WishList, id=id, recipient__user=user)
    if request.method == "POST":
        item.delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))

@login_required(login_url='/landing/')
def bulk_delete_wish_list(request):
    user = request.user
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        id_list = [int(x) for x in ids.split(",") if x.isdigit()]
        WishList.objects.filter(
            id__in=id_list,
            recipient__user=user
        ).delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))

@login_required(login_url='/landing/')
def add_gift(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    event = participant.event

    if request.method == "POST":
        form = GiftForm(request.POST)
        if form.is_valid():
            gift = form.save(commit=False)
            gift.participant = participant

            # Check for posted edited fields first
            posted_name = request.POST.get("product_name")
            posted_price = request.POST.get("product_price")
            posted_image = request.POST.get("product_image")

            if posted_name or posted_price or posted_image:
                # Only set them if present (allows empty strings)
                if posted_name is not None:
                    gift.product_name = posted_name
                if posted_price is not None:
                    gift.product_price = posted_price
                if posted_image is not None:
                    gift.product_image = posted_image
            else:
                # Fallback: scrape product info
                product_data = Scraper(gift.item_url).scrape_product()
                if product_data:
                    gift.product_name = product_data.get("name") or ""
                    gift.product_image = product_data.get("image") or ""
                    gift.product_price = product_data.get("price") or ""

            gift.save()
            return redirect(f"{reverse('view_event', args=[event.id])}?tab=tab-{participant.id}")

    else:
        form = GiftForm()

    html = render_to_string("partials/gift_form.html", {"form": form, "participant": participant}, request=request)
    return HttpResponse(html)

@login_required(login_url='/landing/')
def edit_gift(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id)
    participant = gift.participant
    event = participant.event

    if request.method == "POST":
        # Directly update the fields you care about
        gift.product_name = request.POST.get("product_name", gift.product_name)
        gift.product_price = request.POST.get("product_price", gift.product_price)
        gift.product_image = request.POST.get("product_image", gift.product_image)
        gift.save()

        return redirect(f"{reverse('view_event', args=[event.id])}?tab=tab-{participant.id}")

    html = render_to_string(
        "partials/gift_form.html",
        {"gift": gift, "edit_mode": True},
        request=request
    )
    return HttpResponse(html)

@login_required(login_url='/landing/')
def delete_gift(request, id):
    item = get_object_or_404(Gift, id=id)
    if request.method == "POST":
        item.delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))



@login_required(login_url='/landing/')
@require_POST
def move_wishlist_to_gifts(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    selected_ids = request.POST.getlist("wishlist_item_ids")
    for item_id in selected_ids:
        wishlist_item = get_object_or_404(WishList, id=item_id)
        Gift.objects.create(
            participant=participant,
            item_url=wishlist_item.item_url,
            product_name=wishlist_item.product_name,
            product_image=wishlist_item.product_image,
            product_price=wishlist_item.product_price
        )
        wishlist_item.delete()
    
    return redirect(reverse("view_event", args=[participant.event.id]))



@login_required(login_url='/landing/')
@require_POST
def scrape_product_ajax(request):
    """
    Shared AJAX endpoint used by the modal to fetch scraped product data
    without saving the DB object yet.
    Expects POST with 'item_url' (form field name).
    Returns JSON: {name, price, image} or {error: "..."}.
    """
    url = request.POST.get("item_url") or request.POST.get("url")
    if not url:
        return JsonResponse({"error": "No URL provided."}, status=400)

    product_data = Scraper(url).scrape_product()
    if not product_data:
        return JsonResponse({"error": "Could not extract product info."}, status=404)

    # normalize price to string for the UI
    price = product_data.get("price") or ""
    # if it's a float, make into simple string
    if isinstance(price, (int, float)):
        price = str(price)

    return JsonResponse({
        "name": product_data.get("name") or "",
        "price": price,
        "image": product_data.get("image") or ""
    })

@login_required(login_url='/landing/')
def event_styles(request, id):
    event = get_object_or_404(Event, id=id)

    event_image = None
    for key, img in EVENT_IMAGES.items():
        if key in event.event.lower():
            event_image = img
            break

    return render(request, "event.html", {
        "event": event,
        "event_image": event_image,
    })


def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')
    else:
        form = UserCreationForm()

    return render(request, "auth/register.html", {"form": form})
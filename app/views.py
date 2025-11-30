from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q, Prefetch
from decimal import Decimal
from .forms import TemplateFormMixin, RecipientForm, EventForm, WishListForm, ParticipantForm
from .models import Recipient, Event, Participant, Gift, Budget, WishList
from .utils import get_default_user, compute_totals, scrape_product

def index(request):
    recipients = Recipient.objects.all()
    events = Event.objects.prefetch_related(
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
    wishlists = WishList.objects.all()
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
def add_event(request):
    user = get_default_user()
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

def edit_event(request, id):
    user = get_default_user()
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

def delete_event(request, id):
    user = get_default_user()
    event = get_object_or_404(Event, id=id, user=user)
    if request.method == "POST":
        event.delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))

def view_event(request, id):
    user = get_default_user()
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
def add_recipient(request):
    user = get_default_user()
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

def edit_recipient(request, id):
    user = get_default_user()
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

def delete_recipient(request, id):
    user = get_default_user()
    recipient = get_object_or_404(Recipient, id=id, user=user)
    if request.method == "POST": 
        recipient.delete()
        return redirect(request.META.get("HTTP_REFERER", "index"))
    return redirect(request.META.get("HTTP_REFERER", "index"))




# Participants
def add_participant(request, event_id):
    user = get_default_user()
    event = get_object_or_404(Event, id=event_id, user=user)
    participant = None 

    referer = request.META.get("HTTP_REFERER", "")

    if request.method == "POST":
        form = ParticipantForm(request.POST)
        form.fields['recipient'].queryset = Recipient.objects.exclude(participant__event=event)

        if form.is_valid():
            participant = form.save(commit=False)
            participant.event = event
            participant.save()

            budget_amount = request.POST.get("budget")
            if budget_amount:
                Budget.objects.create(participant=participant, price=budget_amount)
            
            return redirect(referer or reverse("index"))

    else:
        form = ParticipantForm()
        form.fields['recipient'].queryset = Recipient.objects.exclude(
            participant__event=event
        )

    html = render_to_string(
        "partials/participant_form.html",
        {"form": form, "participant": participant},
        request=request
    )
    return HttpResponse(html)


def edit_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    event = participant.event
    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)
        form.fields['recipient'].queryset = Recipient.objects.exclude(participant__event=event) | Recipient.objects.filter(id=participant.recipient.id)
        
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
        form = ParticipantForm(instance=participant)
        form.fields['recipient'].queryset = Recipient.objects.exclude(participant__event=event) | Recipient.objects.filter(id=participant.recipient.id)

    html = render_to_string("partials/participant_form.html", {"form": form, "participant": participant}, request=request)
    return HttpResponse(html)


def delete_participant(request, id):
    user = get_default_user()
    participant = get_object_or_404(Participant, id=id, event__user=user)
    if request.method == "POST": 
        participant.delete()
    referer = request.META.get("HTTP_REFERER", "")
    return redirect(referer or reverse("index"))



# Wistlists

def add_wish_list(request, recipient_id):
    user = get_default_user()
    recipient = get_object_or_404(Recipient, id=recipient_id, user=user)
    
    if request.method == "POST":
        form = WishListForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.recipient = recipient

            # Scrape product info from URL
            product_data = scrape_product(item.item_url)
            if product_data:
                item.product_name = product_data.get("name") or ""
                item.product_image = product_data.get("image") or ""
                item.product_price = product_data.get("price") or ""

            item.save()
            return redirect(request.META.get("HTTP_REFERER", "index"))

    else:
        form = WishListForm()

    html = render_to_string("partials/wishlist_form.html", {"form": form}, request=request)
    return HttpResponse(html)

def view_wish_list(request, wishlist_id, name):
    wishlist = get_object_or_404(WishList, id=wishlist_id)

    recipient = wishlist.recipient
    wishlist_items = recipient.wishlist.all()

    return render(request, 'view_wish_list.html', {
        'recipient': recipient,
        'wishlist_items': wishlist_items,
    })


def delete_wish_list(request, id):
    user = get_default_user()
    item = get_object_or_404(WishList, id=id, recipient__user=user)
    if request.method == "POST":
        item.delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))

def bulk_delete_wish_list(request):
    user = get_default_user()
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        id_list = [int(x) for x in ids.split(",") if x.isdigit()]
        WishList.objects.filter(
            id__in=id_list,
            recipient__user=user
        ).delete()
    return redirect(request.META.get("HTTP_REFERER", "index"))


# Gifts
def add_gift(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    event = participant.event
    
    if request.method == "POST":
        from .forms import GiftForm 
        form = GiftForm(request.POST)
        if form.is_valid():
            gift = form.save(commit=False)
            gift.participant = participant

            # Scrape product info from URL
            product_data = scrape_product(gift.item_url)
            if product_data:
                gift.product_name = product_data.get("name") or ""
                gift.product_image = product_data.get("image") or ""
                gift.product_price = product_data.get("price") or ""

            gift.save()
            return redirect(f"{reverse('view_event', args=[event.id])}?tab=tab-{participant.id}")
    else:
        from .forms import GiftForm
        form = GiftForm()

    html = render_to_string("partials/gift_form.html", {"form": form, "participant": participant}, request=request)
    return HttpResponse(html)




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



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from .forms import TemplateFormMixin, RecipientForm, EventForm, WishListForm, ParticipantForm
from .models import Recipient, Event, Participant, Gift, Budget, WishList
from .utils import get_default_user, scrape_product

def index(request):
    recipients = Recipient.objects.all()
    events = Event.objects.all()
    participants = Participant.objects.all()
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
    # participants = Participant.objects.filter(event=event)
    participants = event.participant_set.select_related("recipient").all()
    return render(request, "view_event.html", {
        "event": event,
        "participants": participants,
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
            
            return redirect(request.META.get("HTTP_REFERER", "index"))

    else:
        form = ParticipantForm()
        form.fields['recipient'].queryset = Recipient.objects.exclude(participant__event=event)

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
            return redirect(request.META.get("HTTP_REFERER", "index"))
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
    return redirect(request.META.get("HTTP_REFERER", "index"))



# Wistlists
# def add_wish_list(request, recipient_id):
#     user = get_default_user()
#     recipient = get_object_or_404(Recipient, id=recipient_id, user=user)
#     if request.method == "POST":
#         form = WishListForm(request.POST)
#         if form.is_valid():
#             item = form.save(commit=False)
#             item.recipient = recipient
#             item.save()
#             return redirect(request.META.get("HTTP_REFERER", "index"))

#     else:
#         form = WishListForm()
#     html = render_to_string("partials/wishlist_form.html", {"form": form}, request=request)
#     return HttpResponse(html)


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

def view_wish_list(request, recipient_id):
    recipient = get_object_or_404(Recipient, id=recipient_id)
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




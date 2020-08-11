from django.shortcuts import render, redirect
from exchanges.models import Request, PendingSale
from django.contrib.auth.models import User
from held_shares.models import InvestedShare
from decimal import Decimal

# Create your views here.
def send_sell_request(request):
    numShares = int(request.POST.get('numShares', 0))
    price = Decimal(request.POST.get('price', 0))
    id = request.POST.get('id')
    inv_share = InvestedShare.objects.get(id=id)
    if numShares > inv_share.numSharesHeld:
        return redirect('/my_shares/')

    PendingSale.objects.createSale(
        request.user.profile,
        price,
        numShares,
        inv_share
    )
    return render(request, 'success/sent_success.html')

def reject_request(request):
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        sale = PendingSale.objects.get(id=req_id)
        sale.delete()

        return redirect('/my_shares/')
        return render(request, 'my_shares.html')

# def accept_request(request):
#     if request.method == 'POST':
#         req_id = request.POST.get('req')
#         req = Request.objects.get(id=req_id)
#         richer = req.sender
#         buyer = request.user.profile
#         req.receiver = buyer
#         req.salePrice = req.inv_share.share.pricePerShare
#         req.hidden = True
#         if req.numShares == req.inv_share.numSharesHeld:
#             req.inv_share.hidden = True
#         new_share = InvestedShare.objects.create(
#             user = buyer.user,
#             share = req.inv_share.share,
#             numSharesHeld = req.numShares,
#         )
#         req.inv_share.numSharesHeld -= req.numShares
#         req.inv_share.save()
#
#         req.save()
#         return redirect('/my_shares/')
#     else:
#         return render(request, 'my_shares.html')

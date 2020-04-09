from django.shortcuts import render
from .models import Share

# Create your views here.
def shares_list(request):
context = {
'shares': Share.objects_all()
}
return render(request, "shares_list.html", context)

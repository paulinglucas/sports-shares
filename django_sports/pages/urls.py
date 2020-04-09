from django.urls import path
from . import views
from login import views as login_views
from held_shares import views as invest_views
from exchanges import views as exchange_views

app_name = 'pages'

urlpatterns = [
	# main pages
	path('', views.home_view, name='homepage'),
	path('my_shares/', views.my_shares_view, name='my_shares'),
	path('games/', views.games_view, name='games'),
	# login views
	path('login/', login_views.login_view, name="login"),
	path('login_success/', login_views.login_success_view, name="login_success"),
	path('sign_up/', login_views.signup_view, name="sign_up"),
	path('logout_success/', login_views.logout_success_view, name="logout_success"),
	# successfully invested / requested shares
	path('invest_success/', invest_views.add_share_to_investments_view, name="invest_success"),
	path('game_success/', invest_views.game_success_view, name="game_success"),
	path('sent_success/', exchange_views.send_sell_request, name="sell_request"),
	# buy request response options
	path('my_shares/reject', exchange_views.reject_request, name='reject_request'),
	path('my_shares/accept', exchange_views.accept_request, name='accept_request')

]

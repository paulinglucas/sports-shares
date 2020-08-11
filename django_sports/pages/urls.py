from django.urls import path
from . import views
from login import views as login_views
from held_shares import views as invest_views
from exchanges import views as exchange_views
from history import views as history_views

app_name = 'pages'

urlpatterns = [
	# main pages
	path('', views.home_view, name='homepage'),
	path('my_shares/', views.my_shares_view, name='my_shares'),
	# login views
	path('login/', login_views.login_view, name="login"),
	path('login_success/', login_views.login_success_view, name="login_success"),
	path('sign_up/', login_views.signup_view, name="sign_up"),
	path('logout_success/', login_views.logout_success_view, name="logout_success"),
	# successfully invested / requested shares
	path('invest_success/', invest_views.add_share_to_investments_view, name="invest_success"),
	path('sent_success/', exchange_views.send_sell_request, name="sell_request"),
	# buy request response options
	path('my_shares/reject', exchange_views.reject_request, name='reject_request'),
	# user history
	path('user_history/', history_views.user_history_view, name='user_history'),
	path('user_history/user/', history_views.user_view, name='user_view'),
	path('my_shares/my_history/', views.user_history_view, name='personal_history_view'),
	# events
	path('events/<slug:sport>/', views.events_view, name='events'),
	path('events/<slug:sport>/event-<int:id>', views.event_view, name='event_specified'),
	# games
	path('games/', views.games_view, name='games'),
	path('game_success/', invest_views.game_success_view, name="game_success"),
	

]

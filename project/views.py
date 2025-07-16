from django.shortcuts import redirect

def pwa_home_redirect(request):
    return redirect('/finance/transaction/add/')
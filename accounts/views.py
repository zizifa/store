from django.shortcuts import render ,redirect,get_object_or_404
from .forms import RegisterForm,UserForm,ProfileForm
from django.contrib.auth import authenticate
from .models import Accounts ,Profile
from carts.models import CartItem,Cart
from carts.views import _cart_id
from django.contrib import messages ,auth
from django.contrib.auth.decorators import login_required
from .authentication import EmailBackend
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from order.models import Order,OrderProduct

def register(request):
    if request.method=="POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]

            user=Accounts.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,phone_number=phone_number,password=password)#
            user.phone_number=phone_number
            user.save()

            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request,"Registration successful")
            return redirect(f'accounts/login/?command=verification='+email)
    else:
        form=RegisterForm()
    context={
        "form":form,
    }
    return render(request,"register.html",context)

def create_data_of_dashboard(request):
    orders=Order.objects.order_by('-created_at').filter(user_id=request.user.id ,is_ordered=True)
    orders_count=orders.count()
    context={
        "orders_count":orders_count,
        "orders":orders,
    }
    return context

def login(request):
    if request.method=='POST':

        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = EmailBackend.authenticate(request=request, phone_number=phone_number, password=password)
        # phone_number=request.POST['phone_number']
        # print(phone_number)
        # email=request.POST['email']
        # print(email)
        # password=request.POST['password']
        # print(password)
        #
        # #user=auth.authenticate(email=email,phone_number=phone_number,password=password)
        # user=authenticate(request,email=email,password=password)
        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                    """for item in cart_item:
                        item.user=user
                        item.save()"""
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        exsistion_var = item.variations.all()
                        ex_var_list.append(list(exsistion_var))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
                pass
            auth.login(request,user)
            context=create_data_of_dashboard(request=request)
            return render(request, 'dashboard.html',context)
        else:
            messages.error(request,"invalid login")
            return redirect('login')
    return render(request,"signin.html")

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,"you are logged out")
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'resetPassword.html')


@login_required(login_url='login')
def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        "orders":orders,
    }
    return render(request,"my_orders.html",context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile=get_object_or_404(Profile , user=request.user)
    if request.method=="POST":
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=ProfileForm(request.POST,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"your profile has been updated")
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_form=ProfileForm(instance=userprofile)
    context={
        "user_form":user_form,
        "profile_form":profile_form,
    }
    return render(request,"edit_profile.html",context)


@login_required(login_url='login')
def change_password(request):
    if request.method=="POST":
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']

        user=Accounts.objects.get(username__iexact=request.user.username)
        if new_password==confirm_password:
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request,"Password Updated Successfully")
                return redirect('change_password')
            else:
                messages.error(request,"plz enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request,'passwords does not match')
            return redirect('change_password')

    return render(request,'change_password.html')


@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_num=order_id)
    print(order_detail)
    order=Order.objects.get(order_num=order_id)
    total_Price=0
    for i in order_detail:
        total_Price += i.product_price*i.quantity

    context={
        'order_detail':order_detail,
        'order':order,
        'total_Price':total_Price,
    }
    return render(request,'order_details.html',context)
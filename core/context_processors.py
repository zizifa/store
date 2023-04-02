from .models import Category

#یک لیست از category هارو برمیگردونه و لینک میکنه
def menu_link(request):
    links=Category.objects.all()
    return dict(links=links)
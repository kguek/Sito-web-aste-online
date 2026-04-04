from .models import Categoria

def lista_categorie_globali(request):
    return {'categorie_globali': Categoria.objects.all()}
from .models import Categoria

def lista_categorie_globali(request):
    """
    Rende sempre disponibile la variabile 'categorie_globali' in tutti i template,
    senza il bisogno di passarla manualmente nel context di ogni singola View.
    """
    return {'categorie_globali': Categoria.objects.all()}
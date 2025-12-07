from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F
from .models import Material

def library_list(request):
    """Hiển thị danh sách tài liệu"""
    materials = Material.objects.select_related('subject').prefetch_related('authors').all()

    search = request.GET.get('search', '')
    filter_by = request.GET.get('filter', 'all')

     # ADD THIS
    base_template = "student_base.html"
    if request.user.userprofile.role == "tutor":
        base_template = "tutor_base.html"

    if search:
        if filter_by == 'title':
            materials = materials.filter(title__icontains=search)
        elif filter_by == 'subject':
            materials = materials.filter(subject__name__icontains=search)
        elif filter_by == 'author':
            materials = materials.filter(authors__name__icontains=search)
        else:  # all
            materials = materials.filter(
                Q(title__icontains=search) |
                Q(subject__name__icontains=search) |
                Q(authors__name__icontains=search)
            ).distinct()

    return render(request, "library/library.html", {
        "materials": materials,
        "search": search,
        "filter": filter_by,
        "base_template": base_template,
    })
# library/models.py
from django.db import models
from django.core.validators import FileExtensionValidator
from tutoring_sessions.models import Subject

class Author(models.Model):
    """Model cho tác giả"""
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Material(models.Model):
    """Model cho tài liệu"""
    MATERIAL_TYPE_CHOICES = [
        ('book', 'Book'),
        ('paper', 'Research Paper'),
        ('slides', 'Slides'),
        ('notes', 'Lecture Notes'),
        ('guide', 'Study Guide'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=300)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    authors = models.ManyToManyField(Author, related_name='materials')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='book')
    description = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='library_materials/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])],
        blank=True,
        null=True
    )
    external_url = models.URLField(blank=True, null=True, help_text="URL to external resource")
    isbn = models.CharField(max_length=13, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'subject']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def authors_display(self):
        """Hiển thị danh sách tác giả"""
        return ", ".join([author.name for author in self.authors.all()])
    
    def increment_view_count(self):
        """Tăng số lượt xem"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """Tăng số lượt tải"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    @property
    def has_file(self):
        """Kiểm tra có file không"""
        return bool(self.file)
    
    @property
    def has_external_url(self):
        """Kiểm tra có external URL không"""
        return bool(self.external_url)

class MaterialAccess(models.Model):
    """Track user access to materials"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('download', 'Download'),
    ])
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'material', '-accessed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.material.title}"
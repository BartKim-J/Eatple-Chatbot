from django.urls import reverse
from django.db import models
from django_mysql.models import Model

STRING_LENGHT = 255
WORD_LENGHT   = 32

STORE_CATEGORY_CHOICES = [
    ('한식', (
            ('백반', '백반'),
            ('찌개', '찌개'),
        )
    ),
    ('분식', (
            ('김밥', '김밥'),
        )
    ),
    ('중식', (
            ('마라탕', '마라탕'),
        )
    ),
    ('양식', (
        ('스테이크', '스테이크'),
      )
    ),
    ('일식', (
        ('덮밥', '덮밥'),
        ('라면', '라면'),
        ('초밥', '초밥'),
      )
    ),
    ('N/A', 'N/A'),
]

class Store(models.Model):
    # Fields
    store_name        = models.CharField(default="상호", max_length=STRING_LENGHT, help_text="상호")
    store_addr        = models.CharField(default="주소", max_length=STRING_LENGHT, help_text="주소") 
    owner_name        = models.CharField(default="가게주", max_length=WORD_LENGHT, help_text="가게주")
    store_description = models.TextField(default="가게 설명", help_text="가게 설명")

    store_category = models.CharField(
        max_length=WORD_LENGHT,
        choices=STORE_CATEGORY_CHOICES,
        default='N/A',
    )

    store_logo = models.ImageField(blank=True, upload_to="eatplus_chatot_app/DB/logo_img")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metadata
    class Meta: 
        ordering = ['-store_name']

    # Methods
    def as_json(self):
        return dict(
            store_name=self.store_name,
            store_addr=self.store_addr,
            owner_name=self.owner_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.store_name

class Menu(models.Model):
    # Fields
    store            = models.ForeignKey('Store', on_delete=models.CASCADE)

    menu_name        = models.CharField(default="메뉴명", max_length=STRING_LENGHT, help_text="메뉴명")
    menu_price       = models.IntegerField(default=0, help_text="가격") 
    menu_discount    = models.IntegerField(default=0, help_text="가격")
    menu_description = models.TextField(default="설명", help_text="메뉴 설명")

    image = models.ImageField(blank=True, upload_to="eatplus_chatot_app/DB/logo_img")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    class Meta: 
        ordering = ['-store']

    # Methods
    def as_json(self):
        return dict(
            store_name=self.store,
            menu_name =self.menu_name,
            menu_price=self.menu_price,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def getStore(self):
        return self.store

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        self.store_name = "{}".format(self.store)
        return "[ {} ] - {}".format(self.store_name, self.menu_name)

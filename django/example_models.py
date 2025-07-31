from django.db import models
from django.db.models import Q
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.hashers import make_password
from .managers import UserManager
from .crypto import encrypt, decrypt
from django.core.exceptions import ValidationError
import re



# ---------------------------------------------  System's methods ------------------------------------------------------
# method excludes fields from validation
def exclude_fields(fields, exclude: set):
    return [field for field in fields if field.name not in exclude]



# Validators
def validate_string(value):
    if not value or not isinstance(value, str):
        raise ValidationError(message=f'ValidationError [TypeError]')

def validate_only_chars(value):
    if not value.isalpha():
        raise ValidationError(message=f'ValidationError [StringFormatError]')

def validate_string_phrase(value):
    pattern = r'^[0-9a-zA-Zа-яА-ЯёЁ ]+$'
    if not re.fullmatch(pattern, value):
        raise ValidationError(message=f'ValidationError [StringFormatError]')

def validate_string_slug(value):
    pattern = r'^[a-z_]+$'
    if not re.fullmatch(pattern, value):
        raise ValidationError(message=f'ValidationError [StringFormatError]')

def validate_only_digits(value):
    if not value.isdigit():
        raise ValidationError(message=f'ValidationError [StringFormatError]')

def validate_only_valid_chars(value):
    pattern = r'^[0-9a-zA-Zа-яА-ЯёЁ\"\\\\/№\s]+$'
    if not re.fullmatch(pattern, value):
        raise ValidationError(message=f'ValidationError [StringFormatError]')

    return value

# ----------------------------------------------------------------------------------------------------------------------





# ---------------------------------------------- System's models -------------------------------------------------------
class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True

    def clean(self):
        for field in exclude_fields(self._meta.fields, {'id', 'pk'}):
            validators = field.validators
            if validators:
                for validator in validators:
                    try:
                        value = getattr(self, field.name)
                        validator(value)
                    except:
                        raise ValidationError(message='ValidationError')
        super().clean()


    def save(self, *args, **kwargs):
        self.clean()
        super(BaseModel, self).save(*args, **kwargs)



class HostConnect(BaseModel):
    host = models.CharField(blank=False, max_length=254, verbose_name="Хост")
    port = models.CharField(blank=False, max_length=6, verbose_name="Порт")
    username = models.CharField(blank=False, max_length=254, verbose_name="Пользователь")
    password = models.CharField(blank=False, max_length=254, verbose_name="Пароль")

    class Meta:
        verbose_name = "Хост подключения"
        verbose_name_plural = "Хосты подключения"

        db_table = 'host_connect'

        constraints = [
            models.UniqueConstraint(fields=["host"], name='%(class)s_host')
        ]


    def save(self, *args, **kwargs):
        self.password = encrypt(str(self.password))
        super(HostConnect, self).save(*args, **kwargs)

    def __str__(self):
        return "Хост [{}]".format(self.host)



class AppUser(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(blank=False, max_length=100, verbose_name="Логин")
    first_name = models.CharField(blank=False, max_length=100, verbose_name="Имя")
    last_name = models.CharField(blank=False, max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(blank=True, max_length=100, verbose_name="Отчество")
    password = models.CharField(blank=False, max_length=254, verbose_name="Пароль")
    email = models.EmailField(blank=False, max_length=254, verbose_name="Адрес эл.почты")
    date_joined = models.DateTimeField(blank=False, auto_now_add=True, verbose_name="Дата регистрации в системе")
    is_staff = models.BooleanField(default=False, verbose_name="Администратор")
    is_superuser = models.BooleanField(default=False, verbose_name="Суперпользователь")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'middle_name', 'email']

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        db_table = 'application_user'

        constraints = [
            models.UniqueConstraint(fields=["login"], name='%(class)s_login'),
            models.UniqueConstraint(fields=["email"], name='%(class)s_email')
        ]

    def save(self, *args, **kwargs):
        self.password = make_password(str(self.password))
        super(AppUser, self).save(*args, **kwargs)

    def __str__(self):
        mid_name = ''
        if self.middle_name:
            mid_name = f' {self.middle_name}'
        return f'{self.last_name} {self.first_name}{mid_name}'
# ----------------------------------------------------------------------------------------------------------------------





# ---------------------------------------------- App's methods ---------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------





# ---------------------------------------------- App's models ----------------------------------------------------------
class CardType(BaseModel):
    name = models.CharField(blank=False, max_length=100, verbose_name="Тип транспортной карты",
                            validators=[validate_string, validate_string_phrase])
    slug = models.SlugField(blank=False, max_length=25, verbose_name="Метка",
                            validators=[validate_string, validate_string_slug])
    categories = models.ManyToManyField('ApplicationType',
                                        verbose_name="Категории обращений")

    class Meta:
        verbose_name = "Тип транспортной карты"
        verbose_name_plural = "Типы транспортных карт"
        ordering = ['name']

        db_table = 'card_type'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]


    def __str__(self):
        return self.name



class CardStatus(BaseModel):
    name = models.CharField(blank=False, max_length=100, verbose_name="Статус транспортной карты",
                            validators=[validate_string, validate_only_chars])
    slug = models.SlugField(blank=False, max_length=25, verbose_name="Метка",
                            validators=[validate_string, validate_only_chars])

    class Meta:
        verbose_name = "Статус транспортной карты"
        verbose_name_plural = "Статусы транспортных карт"
        ordering = ['name']

        db_table = 'card_status'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]


    @classmethod
    def get_default_pk(cls):
        obj, created = CardStatus.objects.get_or_create(name='В обращении', slug='active')
        return obj.pk


    def __str__(self):
        return f'{self.name}'




class Card(BaseModel):
    number = models.CharField(blank=False, max_length=10, verbose_name="Номер транспортной карты",
                              validators=[validate_string, validate_only_digits])
    card_type = models.ForeignKey('CardType', on_delete=models.PROTECT, verbose_name="Тип транспортной карты")
    card_status = models.ForeignKey('CardStatus', on_delete=models.PROTECT, default=CardStatus.get_default_pk,
                                    verbose_name="Статус транспортной карты")
    blocked = models.BooleanField(default=False, verbose_name="Статус блокировки")

    class Meta:
        verbose_name = "Транспортная карта"
        verbose_name_plural = "Транспортные карты"

        db_table = 'card'

        indexes = [
            models.Index(fields=["number"], name="%(class)s_number_idx")
        ]

        constraints = [
            models.UniqueConstraint(fields=["number"], name='%(class)s_number'),
        ]

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.number}]'



class DocumentCategory(BaseModel):
    name = models.CharField(blank=False, max_length=100, verbose_name="Категория документа",
                            validators=[validate_string, validate_only_chars])
    slug = models.SlugField(blank=False, max_length=3, verbose_name="Метка",
                            validators=[validate_string, validate_only_chars])

    class Meta:
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"
        ordering = ['pk']

        db_table = 'document_category'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]

    def __str__(self):
        return self.name




class DocumentType(BaseModel):
    '''
        'Categories' указывает к каким функциональным категориям относится вид документа.
        Необходимо в "limit_choices_to" параметре в FK полях.
            - документ удостоверяющий личность,
            - школьная справка,
            - справка о признании семьи малоимущей,
            - студенческий билет,
            - документ подтверждающий социальную льготу,
            - документ подтверждающий проживание.
    '''
    name = models.CharField(blank=False, max_length=100, verbose_name="Вид документа",
                            validators=[validate_string, validate_only_chars])
    slug = models.SlugField(blank=False, max_length=25, verbose_name="Метка",
                            validators=[validate_string, validate_only_chars])
    categories = models.ManyToManyField('DocumentCategory',
                                        verbose_name="Функциональные категории документа")

    class Meta:
        verbose_name = "Вид документа"
        verbose_name_plural = "Виды документов"
        ordering = ['pk']

        db_table = 'document_type'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]

    def __str__(self):
        return self.name





class JudicialBody(BaseModel):
    name = models.CharField(blank=False, max_length=254, verbose_name="Наименование судебного органа",
                            validators=[validate_string, validate_only_valid_chars])

    class Meta:
        verbose_name = "Cудебный орган"
        verbose_name_plural = "Судебные органы"
        ordering = ['name']

        db_table = 'judicial_body'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name')
        ]

    def __str__(self):
        return f'{self.name}'




class Client(BaseModel):
    last_name = models.CharField(blank=False, max_length=254, verbose_name="Фамилия",
                                 validators=[validate_string, validate_only_chars])
    first_name = models.CharField(blank=False, max_length=254, verbose_name="Имя",
                                  validators=[validate_string, validate_only_chars])
    middle_name = models.CharField(null=True, blank=True, max_length=254, verbose_name="Отчество")

    doc_type = models.ForeignKey('DocumentType', on_delete=models.PROTECT,
                                 limit_choices_to=Q(categories_slug='i'),
                                 related_name='%(class)s_doc', verbose_name="Документ удостоверяющий личность")
    doc_serie = models.CharField(blank=False, max_length=254, verbose_name="Серия документа",
                                 validators=[validate_string, validate_only_valid_chars])
    doc_number = models.CharField(blank=False, max_length=254, verbose_name="Номер документа",
                                  validators=[validate_string, validate_only_valid_chars])
    doc_date = models.DateField(blank=False, verbose_name="Дата выдачи документа")
    doc_issuedby = models.CharField(blank=False, max_length=254, verbose_name="Документ выдан",
                                    validators=[validate_string, validate_only_valid_chars])

    card_active = models.ForeignKey('Card', on_delete=models.PROTECT, related_name='%(class)s_card_active', verbose_name="Действующая транспортная карта")
    card_old = models.ForeignKey('Card', null=True, blank=True, on_delete=models.PROTECT, related_name='%(class)s_card_old', verbose_name="Cтарая транспортная карта")

    reestr_number = models.CharField(blank=False, max_length=30, verbose_name="Номер реестра",
                                     validators=[validate_string, validate_only_valid_chars])

    class Meta:
        abstract = True

        indexes = [
            models.Index(fields=["last_name"], name="%(class)s_last_name_idx"),
            models.Index(fields=["first_name"], name="%(class)s_first_name_idx"),
            models.Index(fields=["doc_number"], name="%(class)s_doc_number_idx"),
            models.Index(fields=["card_active"], name="%(class)s_card_active_idx"),
            models.Index(fields=["reestr_number"], name="%(class)s_reestr_number_idx")
        ]

        constraints = [
            models.UniqueConstraint(fields=["last_name", "first_name", "doc_serie", "doc_number"], name='%(class)s_info_const')
        ]

    def get_fullname(self):
        res = f'{decrypt(self.last_name)} {decrypt(self.first_name)}'
        if self.middle_name:
            res += f' {decrypt(self.middle_name)}'
        return res.strip()





class Pensioner(Client):
    birth_date = models.DateField(blank=False, verbose_name="Дата рождения")
    sex = models.CharField(blank=False, max_length=4, verbose_name="Пол",
                           validators=[validate_string, validate_only_chars])
    address = models.CharField(blank=False, max_length=254, verbose_name="Адрес проживания",
                               validators=[validate_string, validate_only_valid_chars])
    confirm_addr_doc_type = models.ForeignKey('DocumentType', on_delete=models.PROTECT, related_name='%(class)s_addr_doc',
                                              limit_choices_to=Q(categories_slug='a'),
                                              verbose_name="Вид документа подтверждающего проживание")
    confirm_addr_doc_num = models.CharField(null=True, blank=True, max_length=254,
                                            verbose_name="Номер документа подтверждающего проживание")
    confirm_addr_doc_from = models.DateField(null=True, blank=True, verbose_name="Документ действует от")
    confirm_addr_doc_to = models.DateField(null=True, blank=True, verbose_name="Документ действует до")
    confirm_addr_doc_judicial_body = models.ForeignKey('JudicialBody', null=True, blank=True, on_delete=models.PROTECT,
                                                       verbose_name="Судебный орган")

    class Meta:
        verbose_name = "Клиент (пенсионер)"
        verbose_name_plural = "Клиенты (пенсионеры)"

        db_table = 'client_pensioner'

        indexes = Client.Meta.indexes

        constraints = [
                          models.UniqueConstraint(fields=["doc_serie", "doc_number"],  name='%(class)s_doc_const')
                      ] + Client.Meta.constraints


    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class Beneficiary(Client):
    confirm_benefit_doc_type = models.ForeignKey('DocumentType', on_delete=models.PROTECT, related_name='%(class)s_benefit_doc',
                                              limit_choices_to=Q(categories_slug='l'),
                                              verbose_name="Вид документа подтверждающего льготу")
    confirm_benefit_doc_num = models.CharField(blank=False, max_length=254,
                                               verbose_name="Номер документа подтверждающего льготу",
                                               validators=[validate_string, validate_only_valid_chars])
    confirm_benefit_doc_date = models.DateField(blank=False, verbose_name="Дата выдачи документа")
    lic = models.CharField(blank=False, max_length=20, verbose_name="Лицевой счет",
                           validators=[validate_string, validate_only_digits])
    #  1 - льготник, 0 - сопровождающий
    status_beneficiary = models.BooleanField(default=True, verbose_name="Статус льготника")

    class Meta:
        verbose_name = "Клиент (льготник)"
        verbose_name_plural = "Клиенты (льготник)"

        db_table = 'client_beneficiary'

        constraints = [
            models.UniqueConstraint(fields=["last_name", "first_name", "doc_serie", "doc_number", "status_beneficiary"],
                                    name='%(class)s_info_const')
        ]

        indexes = Client.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class EducationalCategory(BaseModel):
    name = models.CharField(blank=False, max_length=100, verbose_name="Категория образовательной организации",
                            validators=[validate_string, validate_only_chars])
    slug = models.SlugField(blank=False, max_length=3, verbose_name="Метка",
                            validators=[validate_string, validate_only_chars])

    class Meta:
        verbose_name = "Категория образовательной организации"
        verbose_name_plural = "Категории образовательных организаций"
        ordering = ['pk']

        db_table = 'educational_category'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]

    def __str__(self):
        return self.name




class EducationalInstitution(BaseModel):
    '''
        'Category' указывает к какой категории относится образовательная организация.
        Необходимо в "limit_choices_to" параметре в FK полях.:
        s - школа,
        u - ВУЗ,
        c - училище, колледж.
    '''
    name = models.CharField(blank=False, max_length=254, verbose_name="Образовательная организация",
                            validators=[validate_string, validate_only_valid_chars])
    category = models.ForeignKey('EducationalCategory', on_delete=models.PROTECT,
                                 related_name='%(class)s_category',
                                 limit_choices_to=Q(),
                                 verbose_name="Функциональная категория образовательной организации")



    class Meta:
        verbose_name = "Образовательная организация"
        verbose_name_plural = "Образовательные организации"
        ordering = ['name']

        db_table = 'educational_institution'

        indexes = [
                    models.Index(fields=["name"], name="%(class)s_idx")
        ]

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name')
        ]

    def __str__(self):
        return f'{self.name}'





class Student(Client):
    birth_date = models.DateField(blank=False, verbose_name="Дата рождения")
    student_card_num = models.CharField(blank=False, max_length=254, verbose_name="Номер студенческого билета",
                                        validators=[validate_string, validate_only_valid_chars])
    edu_institution = models.ForeignKey('EducationalInstitution', on_delete=models.PROTECT,
                                        related_name='%(class)s_edu_institution',
                                        limit_choices_to=Q(category_slug='u'),
                                        verbose_name="Образовательная организация")

    class Meta:
        verbose_name = "Клиент (студент)"
        verbose_name_plural = "Клиенты (студенты)"

        db_table = 'client_student'

        indexes = [
                    models.Index(fields=["student_card_num"], name="%(class)s_st_card_num_idx")
                  ] + Client.Meta.indexes

        constraints = [
                          models.UniqueConstraint(fields=["student_card_num", "edu_institution"], name='%(class)s_edu_const')
                      ] + Client.Meta.constraints

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class PupilA(Client):
    confirm_benefit_doc_type = models.ForeignKey('DocumentType', on_delete=models.PROTECT,
                                                 related_name='%(class)s_benefit_doc',
                                                 limit_choices_to=Q(categories_slug='p'),
                                                 verbose_name="Вид документа подтверждающего льготу")
    confirm_benefit_doc_num = models.CharField(blank=False, max_length=254,
                                               verbose_name="Номер документа подтверждающего льготу",
                                               validators=[validate_string, validate_only_valid_chars])
    confirm_benefit_doc_date = models.DateField(blank=False, verbose_name="Дата выдачи документа")
    confirm_benefit_doc_edu_organization = models.ForeignKey('EducationalInstitution', on_delete=models.PROTECT,
                                                             related_name='%(class)s_edu_institution',
                                                             limit_choices_to=Q(category_slug='s'),
                                                             verbose_name="Образовательная организация")

    class Meta:
        abstract = True

        indexes = [
                      models.Index(fields=["confirm_benefit_doc_num"], name="%(class)s_benefit_doc_num_idx")
                  ] + Client.Meta.indexes

        constraints = [
                          models.UniqueConstraint(fields=["confirm_benefit_doc_num", "confirm_benefit_doc_edu_organization_id"],
                                                  name='%(class)s_edu_const')
                      ] + Client.Meta.constraints



class Pupil(PupilA):
    class Meta:
        verbose_name = "Клиент (школьник)"
        verbose_name_plural = "Клиенты (школьники)"

        db_table = 'client_pupil'

        indexes = PupilA.Meta.indexes

        constraints = PupilA.Meta.constraints

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class PupilMO(PupilA):
    certificate_num = models.CharField(blank=False, max_length=254, verbose_name="Номер справки (МО семья)",
                                       validators=[validate_string, validate_only_valid_chars])
    certificate_date = models.DateField(blank=False, verbose_name="Дата выдачи справки (МО семья)")
    certificate_date_to = models.DateField(blank=False, verbose_name="Срок действия справки (МО семья)")

    class Meta:
        verbose_name = "Клиент (школьник МО)"
        verbose_name_plural = "Клиенты (школьники МО)"

        db_table = 'client_pupilMO'

        indexes = PupilA.Meta.indexes

        constraints = PupilA.Meta.constraints

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class ApplicationType(BaseModel):
    name = models.CharField(blank=False, max_length=100, verbose_name="Вид обращения",
                            validators=[validate_string, validate_string_phrase])
    slug = models.SlugField(blank=False, max_length=25, verbose_name="Метка",
                            validators=[validate_string, validate_string_slug])

    class Meta:
        verbose_name = "Вид обращения"
        verbose_name_plural = "Виды обращений"
        ordering = ['name']

        db_table = 'application_type'

        constraints = [
            models.UniqueConstraint(fields=["name"], name='%(class)s_name'),
            models.UniqueConstraint(fields=["slug"], name='%(class)s_slug')
        ]

    def __str__(self):
        return f'{self.name}'




class Application(BaseModel):
    application_type = models.ForeignKey('ApplicationType', on_delete=models.PROTECT,
                                                 related_name='%(class)s_app_type', verbose_name="Вид обращения")
    app_card_new = models.CharField(blank=False, max_length=10, verbose_name="Новая транспортная карта",
                                    validators=[validate_string, validate_only_digits])
    app_card_old = models.CharField(null=False, blank=True, max_length=10, default='',
                                    verbose_name="Старая транспортная карта",
                                    validators=[validate_string, validate_only_digits])
    comment = models.TextField(null=False, blank=True, default='', verbose_name="Дополнительные сведения")
    datetime_creation = models.DateTimeField(blank=False, auto_now_add=True, verbose_name="Дата создания обращения")
    user_created = models.ForeignKey('AppUser', on_delete=models.PROTECT, verbose_name="Пользователь")

    class Meta:
        abstract = True

        indexes = [
            models.Index(fields=["app_card_new"], name="%(class)s_new_card_idx"),
            models.Index(fields=["app_card_old"], name="%(class)s_old_card_idx"),
            models.Index(fields=["datetime_creation"], name="%(class)s_date_create_idx")
        ]



class PensionerApp(Application):
    client = models.ForeignKey('Pensioner', on_delete=models.PROTECT, related_name='%(class)s_client', verbose_name="Клиент")

    class Meta:
        verbose_name = "Обращение (пенсионер)"
        verbose_name_plural = "Обращения (пенсионеры)"

        db_table = 'app_pensioner'

        indexes = Application.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class BeneficiaryApp(Application):
    client = models.ForeignKey('Beneficiary', on_delete=models.PROTECT, related_name='%(class)s_client', verbose_name="Клиент")

    class Meta:
        verbose_name = "Обращение (льготник)"
        verbose_name_plural = "Обращения (льготники)"

        db_table = 'app_beneficiary'

        indexes = Application.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class StudentApp(Application):
    client = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='%(class)s_client', verbose_name="Клиент")

    class Meta:
        verbose_name = "Обращение (студент)"
        verbose_name_plural = "Обращения (студент)"

        db_table = 'app_student'

        indexes = Application.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class PupilApp(Application):
    client = models.ForeignKey('Pupil', on_delete=models.PROTECT, related_name='%(class)s_client', verbose_name="Клиент")

    class Meta:
        verbose_name = "Обращение (школьник)"
        verbose_name_plural = "Обращения (школьники)"

        db_table = 'app_pupil'

        indexes = Application.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'




class PupilMOApp(Application):
    client = models.ForeignKey('PupilMO', on_delete=models.PROTECT, related_name='%(class)s_client', verbose_name="Клиент")

    class Meta:
        verbose_name = "Обращение (школьник МО)"
        verbose_name_plural = "Обращения (школьники МО)"

        db_table = 'app_pupilMO'

        indexes = Application.Meta.indexes

    def __str__(self):
        return f'{self._meta.verbose_name.title()} [{self.pk}]'


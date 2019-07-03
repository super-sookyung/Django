from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField


User = settings.AUTH_USER_MODEL

class GeneralPost(models.Model):


    author = models.ForeignKey(
        User, related_name='user_posts', on_delete=models.CASCADE)

    title = models.CharField(verbose_name=_('post title'),
                             null=False, blank=False, max_length=50)

    content = RichTextField(max_length=3000, null=False)

    created = models.DateTimeField(verbose_name=_('post created'),
                                   auto_now_add=True)

    last_edited = models.DateTimeField(verbose_name=_('post edited'),
                                       auto_now=True)

    # image = models.ImageField(upload_to='images/',null=True)

    published = models.BooleanField(default=True) 


    class Meta:
        verbose_name = _('general post')
        verbose_name_plural = _('general posts')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.author} posted {self.title}!'



class Tag(models.Model):
    slug = models.SlugField(verbose_name=_('tag slug'),
                            unique=True, max_length=35)
    name = models.CharField(verbose_name=_('tag name'),
                            max_length=35)
    created_at = models.DateTimeField(auto_now_add=True)
    # 생각해보니 태그로 search하면 post를 최신순으로 띄워야하니 created_at도 필요해서 남겼습니다.

    def __str__(self):
        return self.name

class FilterTagRelation(models.Model):
    general_post = models.ForeignKey(
        GeneralPost, on_delete=models.CASCADE)
  
    
    filter_tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = _('filter tag relation')
        verbose_name_plural = _('filter tag relations')



# Copyright (c) 2025 知识库管理系统. All rights reserved.


from django.db import models
from django.utils import timezone
from rest_framework import serializers
from event.models import SysEvent
from event.models import SysEventRole
from user.models import SysUser



class SysRepository(models.Model):
    # 可见性级别常量
    VISIBILITY_PRIVATE = 1  # 仅自己可见
    VISIBILITY_DEPT = 2     # 部门可见
    VISIBILITY_ALL = 3      # 全员可见
    
    VISIBILITY_CHOICES = (
        (VISIBILITY_PRIVATE, '仅自己'),
        (VISIBILITY_DEPT, '部门'),
        (VISIBILITY_ALL, '全员'),
    )
    
    id = models.AutoField(primary_key=True)
    dept_id = models.IntegerField(default=0, verbose_name="部门id", db_comment="部门id")  # 部门
    user_id = models.IntegerField(default=0, verbose_name="用户名id", db_comment="用户名id")  # 用户名
    event_id = models.IntegerField(default=0, verbose_name="事件id", db_comment="事件id")# 事件id
    event_occur_time = models.DateField(verbose_name="事件发生时间", db_comment="事件发生时间")  # 事件发生时间
    address = models.CharField(max_length=250, verbose_name="发生地点", db_comment="发生地点")  # 发生地点
    is_temp = models.BooleanField(default=False, verbose_name="是否临时保存", db_comment="临时保存标识")
    temp_version = models.IntegerField(default=0, verbose_name="临时版本号", db_comment="临时保存版本计数")
    confirmed = models.BooleanField(default=False, verbose_name="是否已确认", db_comment="确认状态标识")
    status = models.CharField(max_length=20, default="draft", choices=[
        ("draft", "草稿"), ("submitted", "已提交"), ("confirmed", "已确认")
    ], verbose_name="记录状态", db_comment="控制编辑权限的状态")
    
    # 新增：可见性控制字段
    visibility = models.IntegerField(
        default=VISIBILITY_ALL,
        choices=VISIBILITY_CHOICES,
        verbose_name="可见性",
        db_comment="控制记录可见范围：1-仅自己，2-部门，3-全员"
    )

    types = models.IntegerField(default=0, verbose_name="类型", db_comment="类型")  # 类型
    classify = models.IntegerField(default=0, verbose_name="分类", db_comment="分类")  # 分类
    title = models.TextField(verbose_name="标题", db_comment="标题")  # 标题
    content = models.TextField(verbose_name="内容", db_comment="内容")  # 内容
    upvote = models.IntegerField(default=0, verbose_name="点赞数", db_comment="点赞数")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注", db_comment="备注")

    class Meta:
        db_table = "sys_repository"
        ordering = ['-create_time']
        verbose_name = "知识库"
        verbose_name_plural = "知识库"


class RepositoryLike(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(SysRepository, on_delete=models.CASCADE, verbose_name="知识库条目")
    user_id = models.IntegerField(verbose_name="用户ID", db_comment="点赞用户ID")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="点赞时间")
    
    class Meta:
        db_table = "sys_repository_like"
        unique_together = ('repository', 'user_id')  # 确保同一用户对同一条内容只能点赞一次
        verbose_name = "知识库点赞"
        verbose_name_plural = "知识库点赞"


class RepositoryHistory(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(SysRepository, on_delete=models.CASCADE, verbose_name="知识库条目")
    dept_id = models.IntegerField(default=0, verbose_name="部门id", db_comment="部门id")
    user_id = models.IntegerField(default=0, verbose_name="用户名id", db_comment="用户名id")
    event_id = models.IntegerField(default=0, verbose_name="事件id", db_comment="事件id")
    event_occur_time = models.DateField(verbose_name="事件发生时间", db_comment="事件发生时间")
    address = models.CharField(max_length=250, verbose_name="发生地点", db_comment="发生地点")
    types = models.IntegerField(default=0, verbose_name="类型", db_comment="类型")
    classify = models.IntegerField(default=0, verbose_name="分类", db_comment="分类")
    title = models.TextField(verbose_name="标题", db_comment="标题")
    content = models.TextField(verbose_name="内容", db_comment="内容")
    upvote = models.IntegerField(default=0, verbose_name="点赞数", db_comment="点赞数")
    version = models.IntegerField(verbose_name="版本号", db_comment="修改版本号")
    modified_time = models.DateTimeField(auto_now_add=True, verbose_name="修改时间", db_comment="修改时间")
    remarks = models.CharField(max_length=500, null=True, verbose_name="备注", db_comment="备注")
    
    class Meta:
        db_table = "sys_repository_history"
        ordering = ['-modified_time']
        verbose_name = "知识库历史记录"
        verbose_name_plural = "知识库历史记录"


class SysRepositorySerializer(serializers.ModelSerializer):
    # 自定义时间字段序列化（转换为北京时间）
    create_time = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()

    class Meta:
        model = SysRepository
        fields = '__all__'

    def get_create_time(self, obj):
        return timezone.localtime(obj.create_time).strftime("%Y-%m-%d %H:%M:%S") if obj.create_time else ""

    def get_update_time(self, obj):
        return timezone.localtime(obj.update_time).strftime("%Y-%m-%d %H:%M:%S") if obj.update_time else ""


class SysRepositoryComment(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(SysRepository, on_delete=models.CASCADE, related_name='comments', verbose_name="知识库条目")
    user = models.ForeignKey(SysUser, on_delete=models.CASCADE, verbose_name="评论用户")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    reply_to_user_id = models.IntegerField(null=True, blank=True, verbose_name="被回复人ID", db_comment="被回复人用户ID")
    content = models.TextField(verbose_name="评论内容", db_comment="评论内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间", db_comment="评论时间")

    class Meta:
        db_table = "sys_repository_comment"
        ordering = ['-create_time']
        verbose_name = "知识库评论"
        verbose_name_plural = "知识库评论"


class SysRepositoryCommentSerializer(serializers.ModelSerializer):
    # 自定义时间字段序列化
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = SysRepositoryComment
        fields = '__all__'

    def get_create_time(self, obj):
        return timezone.localtime(obj.create_time).strftime("%Y-%m-%d %H:%M:%S") if obj.create_time else ""


# 复盘模型
class RepositoryReview(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(SysRepository, on_delete=models.CASCADE, related_name='reviews', verbose_name="知识库条目")
    reviewer = models.ForeignKey(SysUser, on_delete=models.CASCADE, verbose_name="复盘人")
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="复盘日期")
    
    # 复盘内容字段
    what_happened = models.TextField(verbose_name="发生了什么", help_text="描述事件的实际发生情况")
    what_went_well = models.TextField(verbose_name="做得好的地方", help_text="列出成功和积极的方面")
    what_not_went_well = models.TextField(verbose_name="需要改进的地方", help_text="识别问题和挑战")
    lessons_learned = models.TextField(verbose_name="学到的经验", help_text="从事件中获得的关键经验教训")
    action_items = models.TextField(verbose_name="行动计划", help_text="未来如何改进的具体措施")
    
    # 评分字段
    effectiveness_score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], verbose_name="有效性评分")
    improvement_potential = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], verbose_name="改进潜力评分")
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    
    class Meta:
        db_table = "sys_repository_review"
        ordering = ['-review_date']
        verbose_name = "知识库复盘"
        verbose_name_plural = "知识库复盘"


class RepositoryReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    review_date_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = RepositoryReview
        # 明确指定需要的字段，排除repository以避免嵌套循环引用
        fields = ['id', 'reviewer', 'review_date', 'what_happened', 'what_went_well', 
                 'what_not_went_well', 'lessons_learned', 'action_items', 
                 'effectiveness_score', 'improvement_potential', 'is_active',
                 'reviewer_name', 'review_date_formatted']
    
    def get_reviewer_name(self, obj):
        try:
            user = SysUser.objects.get(id=obj.reviewer_id)
            return user.realname
        except SysUser.DoesNotExist:
            return "未知用户"
    
    def get_review_date_formatted(self, obj):
        return timezone.localtime(obj.review_date).strftime("%Y-%m-%d %H:%M:%S") if obj.review_date else ""


# 知识库图片模型
class RepositoryImage(models.Model):
    id = models.AutoField(primary_key=True)
    repository = models.ForeignKey(SysRepository, on_delete=models.CASCADE, related_name='images', verbose_name="知识库条目")
    image_url = models.CharField(max_length=500, verbose_name="图片URL", db_comment="图片的完整URL地址")
    image_path = models.CharField(max_length=500, verbose_name="图片路径", db_comment="图片在服务器上的相对路径")
    file_size = models.IntegerField(default=0, verbose_name="文件大小", db_comment="图片文件大小（字节）")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间", db_comment="图片上传时间")
    
    class Meta:
        db_table = "sys_repository_image"
        ordering = ['-upload_time']
        verbose_name = "知识库图片"
        verbose_name_plural = "知识库图片"


class RepositoryImageSerializer(serializers.ModelSerializer):
    upload_time = serializers.SerializerMethodField()
    
    class Meta:
        model = RepositoryImage
        fields = '__all__'
    
    def get_upload_time(self, obj):
        return timezone.localtime(obj.upload_time).strftime("%Y-%m-%d %H:%M:%S") if obj.upload_time else ""

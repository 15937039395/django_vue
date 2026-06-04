# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.db import models
from rest_framework import serializers



class SysUser(models.Model):
    """
    系统用户模型类

    用于定义系统用户的基本信息和属性，对应数据库中的sys_user表。
    包含用户的账号信息、个人信息、状态信息等字段。

    Attributes:
        id (AutoField): 用户ID，主键。
        username (CharField): 用户名，最大长度150字符。
        password (CharField): 密码，最大长度255字符，可为空。
        realname (CharField): 用户真实姓名，最大长度150字符。
        nickname (CharField): 用户花名，最大长度150字符。
        gender (IntegerField): 性别，使用GENDER_CHOICES选项，默认为1（男）。
        avatar (CharField): 用户头像URL，最大长度255字符。
        phone (CharField): 手机号，最大长度30字符。
        email (CharField): 邮箱地址，最大长度50字符。
        birthday (DateField): 出生日期。
        dept_id (IntegerField): 所属部门ID，默认为0。
        level_id (IntegerField): 职级ID，默认为0。
        position_id (IntegerField): 岗位ID，默认为0。
        province_code (CharField): 省份编码，最大长度30字符。
        city_code (CharField): 城市编码，最大长度30字符。
        district_code (CharField): 县区编码，最大长度30字符。
        address_info (CharField): 省市区信息描述，最大长度255字符。
        address (CharField): 详细地址，最大长度255字符。
        intro (CharField): 个人简介，最大长度255字符，可为空。
        status (IntegerField): 用户状态，使用STATUS_CHOICES选项，默认为1（正常）。
        login_date (DateTimeField): 最后登录时间，可为空。
        create_time (DateTimeField): 创建时间，可为空。
        update_time (DateTimeField): 更新时间，可为空。
        remark (CharField): 备注信息，最大长度500字符，可为空。
        sort (IntegerField): 排序值，默认为0。
    """
    id = models.AutoField(primary_key=True, verbose_name="用户ID",db_comment="用户ID")
    #用户名
    username = models.CharField(max_length=150, verbose_name="用户名", db_comment="用户名")
    # 密码
    password = models.CharField(null=True, max_length=255, verbose_name="密码", db_comment="密码")
    #用户姓名
    realname = models.CharField(max_length=150, verbose_name="用户姓名", db_comment="用户姓名")
    #用户花名
    nickname = models.CharField(max_length=150, verbose_name="用户花名", db_comment="用户花名")
    # 性别：1-男 2-女 3-保密
    GENDER_CHOICES = (
        (1, "男"),
        (2, "女"),
        (3, "保密"),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1, verbose_name="性别：1-男 2-女 3-保密",db_comment="性别：1-男 2-女 3-保密")
    #用户头像
    avatar = models.CharField(max_length=255, verbose_name="用户头像", db_comment="用户头像")
    #手机号
    phone = models.CharField(max_length=30, verbose_name="手机号", db_comment="手机号")
    #邮箱
    email = models.CharField(max_length=50, verbose_name="用户邮箱", db_comment="用户邮箱")
    #生日
    birthday = models.DateField( verbose_name="出生日期", db_comment="出生日期")
    #部门ID
    dept_id = models.IntegerField(default=0, verbose_name="部门ID", db_comment="部门ID")
    #职级ID
    level_id = models.IntegerField(default=0, verbose_name="职级ID", db_comment="职级ID")
    # 岗位ID
    position_id = models.IntegerField(default=0, verbose_name="岗位ID", db_comment="岗位ID")
    # 省份编码
    province_code = models.CharField(max_length=30, verbose_name="省份编码", db_comment="省份编码")
    # 城市编码
    city_code = models.CharField(max_length=30, verbose_name="城市编码", db_comment="城市编码")
    # 县区编码
    district_code = models.CharField(max_length=30, verbose_name="县区编码", db_comment="县区编码")
    # 省市区信息
    address_info = models.CharField(max_length=255, verbose_name="省市区信息", db_comment="省市区信息")
    # 详细地址
    address = models.CharField(max_length=255, verbose_name="详细地址", db_comment="详细地址")
    # 个人简介
    intro = models.CharField( max_length=255, verbose_name="个人简介", db_comment="个人简介")

    # 状态
    STATUS_CHOICES = (
        (1, "正常"),
        (2, "禁用"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="状态：1-正常 2-禁用",db_comment="状态：1-正常 2-禁用")
    #最后登录时间
    login_date = models.DateTimeField(auto_now=True, verbose_name="最后登录时间",db_comment="最后登录时间")
    # #创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")
    # 更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", db_comment="更新时间")
    # 备注
    remark = models.CharField(max_length=500, verbose_name="备注",db_comment="备注")
    # 排序
    sort = models.IntegerField(default=0, verbose_name="排序", db_comment="排序")

    # 是否可以查看评论人信息：0-否 1-是
    CAN_VIEW_COMMENTER_CHOICES = (
        (0, "否"),
        (1, "是"),
    )
    can_view_commenter = models.IntegerField(choices=CAN_VIEW_COMMENTER_CHOICES, default=0, verbose_name="是否可以查看评论人信息", db_comment="是否可以查看评论人信息")

    class Meta:
        """
           模型元数据配置
           定义模型在数据库中的表名和其他元数据信息
        """
        db_table = "sys_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"用户{self.username}" if hasattr(self, 'username') else f"用户{self.id}"
    
    def set_password(self, raw_password):
        """设置密码时使用Django内置的密码哈希功能"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """检查密码是否正确"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    @property
    def is_active(self):
        """兼容 DRF 的 is_active 属性"""
        return self.status == 1
    
    @property
    def is_authenticated(self):
        """兼容 DRF 的 is_authenticated 属性"""
        return True
    
    @property
    def is_anonymous(self):
        """兼容 DRF 的 is_anonymous 属性"""
        return False


class SysUserSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):

        if hasattr(obj, "children"):
            serializerUserList: list[SysUserSerializer2] = list()
            for sysMenu in obj.children:
                serializerUserList.append(SysUserSerializer2(sysMenu).data)
            return serializerUserList

    class Meta:
        model = SysUser
        fields = '__all__'

class SysUserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = '__all__'
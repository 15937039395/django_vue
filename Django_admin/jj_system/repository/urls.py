# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.urls import path
from repository.views import SearchView,SaveView,ActionView,DeptListView,UserListView,ItemDetailView,LikeView,HistoryView,AssociatedEventsView,CommentListView,CommentSubmitView,UploadImageView,RepositoryImagesView
from repository.views_review import ReviewListView, ReviewSaveView, ReviewDetailView, ReviewUpdateView, ReviewDeleteView

urlpatterns = [
    # 示例：路径映射（根据你的实际视图调整）
    path('search', SearchView.as_view(), name='search'),  # 知识库信息分页查询
    path('save', SaveView.as_view(), name='save'),  # 添加或者修改知识库信息
    path('action', ActionView.as_view(), name='action'),  # 知识库信息操作
    path('dept/list', DeptListView.as_view()),  # 部门列表接口
    path('user/list', UserListView.as_view()),  # 用户列表接口
    path('detail', ItemDetailView.as_view(), name='item_detail'),
    path('like', LikeView.as_view(), name='like'),  # 点赞接口
    path('history', HistoryView.as_view(), name='history'),  # 历史记录接口
    path('associated-events', AssociatedEventsView.as_view(), name='associated_events'),  # 关联事件接口
    path('comment/list', CommentListView.as_view(), name='comment_list'),  # 评论列表接口
    path('comment/submit', CommentSubmitView.as_view(), name='comment_submit'),  # 提交评论接口
    path('upload/image', UploadImageView.as_view(), name='upload_image'),  # 图片上传接口
    path('images', RepositoryImagesView.as_view(), name='repository_images'),  # 知识库图片列表接口
    # 复盘功能接口
    path('review/list', ReviewListView.as_view(), name='review_list'),  # 获取复盘记录列表
    path('review/save', ReviewSaveView.as_view(), name='review_save'),  # 保存复盘记录
    path('review/detail', ReviewDetailView.as_view(), name='review_detail'),  # 获取复盘记录详情
    path('review/update', ReviewUpdateView.as_view(), name='review_update'),  # 更新复盘记录
    path('review/delete', ReviewDeleteView.as_view(), name='review_delete'),  # 删除复盘记录
]
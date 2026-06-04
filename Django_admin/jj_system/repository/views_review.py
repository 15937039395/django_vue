# Copyright (c) 2025 知识库管理系统. All rights reserved.

from django.shortcuts import render
import json
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from repository.models import SysRepository, SysRepositorySerializer, RepositoryReview, RepositoryReviewSerializer
from user.models import SysUser
from rest_framework_simplejwt.tokens import AccessToken


def check_token(request):
    """检查请求中的认证令牌"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    
    # 使用系统相同的JWT验证方法
    try:
        # 使用SimpleJWT的AccessToken来解析
        validated_token = AccessToken(token)
        # 如果能成功解析，说明token有效
        return True
    except Exception:
        # 如果解析失败，说明token无效或已过期
        return False

def get_user_from_token(request):
    """从令牌中获取用户信息"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        # 使用SimpleJWT的AccessToken来解析
        validated_token = AccessToken(token)
        # 从token的payload中获取用户ID
        user_id = validated_token.payload.get('user_id')
        if user_id:
            user = SysUser.objects.get(id=user_id)
            return user
    except Exception:
        return None
    
    return None


class ReviewListView(View):
    """
    获取某个知识库条目的复盘记录（支持分页）
    """
    def get(self, request):
        # 检查认证令牌
        if not check_token(request):
            logger.warning('复盘列表获取失败：缺少或无效的token')
            return JsonResponse({'code': 401, 'msg': '缺少认证token或token无效'})
        
        try:
            repository_id = request.GET.get("id")
            page = int(request.GET.get("page", 1))  # 页码，默认为1
            page_size = int(request.GET.get("page_size", 10))  # 每页大小，默认为10
            
            logger.info(f'尝试获取知识库 {repository_id} 的复盘列表，页码: {page}, 每页: {page_size}')
            
            if not repository_id:
                logger.warning('缺少知识库ID')
                return JsonResponse({'code': 400, 'msg': '缺少知识库ID'})
            
            # 获取复盘记录
            reviews = RepositoryReview.objects.filter(
                repository_id=repository_id,
                is_active=True
            ).select_related('reviewer').order_by('-review_date')
            
            # 计算总数
            total_count = reviews.count()
            logger.info(f'总共找到 {total_count} 条复盘记录')
            
            # 分页处理
            paginator = Paginator(reviews, page_size)
            try:
                paginated_reviews = paginator.page(page)
            except Exception:
                # 页码超出范围时，返回第一页
                paginated_reviews = paginator.page(1)
            
            # 序列化数据
            review_list = []
            for review in paginated_reviews:
                review_data = RepositoryReviewSerializer(review).data
                # 添加复盘人姓名
                try:
                    reviewer = SysUser.objects.get(id=review.reviewer_id)
                    review_data['reviewer_name'] = reviewer.realname
                except SysUser.DoesNotExist:
                    logger.warning(f'复盘人不存在: {review.reviewer_id}')
                    review_data['reviewer_name'] = '未知用户'
                
                review_data['review_date_formatted'] = review.review_date.strftime('%Y-%m-%d %H:%M:%S')
                logger.debug(f'添加复盘记录: {review_data}')
                review_list.append(review_data)
            
            logger.info(f'返回复盘列表，当前页: {page}, 每页: {page_size}, 总数: {total_count}')
            
            return JsonResponse({
                'code': 200,
                'review_list': review_list,
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages
            })
            
        except Exception as e:
            logger.error(f'获取复盘列表失败: {str(e)}', exc_info=True)
            # 即使出现异常，也要返回空列表，而不是错误信息
            return JsonResponse({
                'code': 200,
                'review_list': [],
                'total': 0,
                'page': 1,
                'page_size': 10,
                'total_pages': 0
            })


import logging
logger = logging.getLogger(__name__)

class ReviewSaveView(View):
    """
    保存或更新复盘记录
    """
    def post(self, request):
        # 检查认证令牌
        if not check_token(request):
            logger.warning('认证失败：缺少或无效的token')
            return JsonResponse({'code': 401, 'msg': '缺少认证token或token无效'})
        
        try:
            data = json.loads(request.body.decode("utf-8"))
            logger.info(f'收到复盘保存请求: {data}')
            
            # 验证必需字段
            required_fields = [
                'repository_id', 'what_happened', 'what_went_well', 
                'what_not_went_well', 'lessons_learned', 'action_items',
                'effectiveness_score', 'improvement_potential'
            ]
            
            for field in required_fields:
                if field not in data:
                    logger.warning(f'缺少必要字段: {field}')
                    return JsonResponse({'code': 400, 'msg': f'缺少必要字段: {field}'})
            
            repository_id = data['repository_id']
            reviewer_id = data.get('reviewer_id')  # 前端传入的当前用户ID
            
            logger.info(f'尝试保存复盘: repository_id={repository_id}, reviewer_id={reviewer_id}')
            
            if not reviewer_id:
                logger.warning('缺少复盘人ID')
                return JsonResponse({'code': 400, 'msg': '缺少复盘人ID'})
            
            # 检查知识库条目是否存在
            try:
                repository = SysRepository.objects.get(id=repository_id)
                logger.info(f'找到知识库条目: {repository_id}')
            except SysRepository.DoesNotExist:
                logger.error(f'知识库条目不存在: {repository_id}')
                return JsonResponse({'code': 400, 'msg': '知识库条目不存在'})
            
            # 检查用户是否存在
            try:
                current_user = SysUser.objects.get(id=reviewer_id)
                logger.info(f'找到用户: {reviewer_id}')
            except SysUser.DoesNotExist:
                logger.error(f'用户不存在: {reviewer_id}')
                return JsonResponse({'code': 400, 'msg': '用户不存在'})
            
            # 创建或更新复盘记录
            review = RepositoryReview(
                repository=repository,
                reviewer=current_user,
                what_happened=data['what_happened'],
                what_went_well=data['what_went_well'],
                what_not_went_well=data['what_not_went_well'],
                lessons_learned=data['lessons_learned'],
                action_items=data['action_items'],
                effectiveness_score=data['effectiveness_score'],
                improvement_potential=data['improvement_potential']
            )
            
            review.save()
            logger.info(f'复盘记录保存成功，ID: {review.id}')
            
            return JsonResponse({
                'code': 200,
                'msg': '复盘记录保存成功',
                'review_id': review.id
            })
            
        except json.JSONDecodeError:
            logger.error('JSON格式错误')
            return JsonResponse({'code': 400, 'msg': 'JSON格式错误'})
        except SysUser.DoesNotExist:
            logger.error(f'用户不存在: {reviewer_id}')
            return JsonResponse({'code': 400, 'msg': '用户不存在'})
        except Exception as e:
            logger.error(f'保存复盘记录失败: {str(e)}', exc_info=True)
            return JsonResponse({'code': 500, 'msg': f'保存复盘记录失败: {str(e)}'})


class ReviewDetailView(View):
    """
    获取单个复盘记录详情
    """
    def get(self, request):
        # 检查认证令牌
        if not check_token(request):
            return JsonResponse({'code': 401, 'msg': '缺少认证token或token无效'})
        
        try:
            review_id = request.GET.get("id")
            if not review_id:
                return JsonResponse({'code': 400, 'msg': '缺少复盘记录ID'})
            
            try:
                review = RepositoryReview.objects.select_related('reviewer', 'repository').get(
                    id=review_id,
                    is_active=True
                )
            except RepositoryReview.DoesNotExist:
                return JsonResponse({'code': 404, 'msg': '复盘记录不存在'})
            
            review_data = RepositoryReviewSerializer(review).data
            review_data['reviewer_name'] = review.reviewer.realname
            review_data['repository_title'] = review.repository.title
            review_data['review_date_formatted'] = review.review_date.strftime('%Y-%m-%d %H:%M:%S')
            
            return JsonResponse({
                'code': 200,
                'review_data': review_data
            })
            
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'获取复盘详情失败: {str(e)}'})


class ReviewUpdateView(View):
    """
    更新复盘记录
    """
    def post(self, request):
        # 检查认证令牌
        if not check_token(request):
            return JsonResponse({'code': 401, 'msg': '缺少认证token或token无效'})
        
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            review_id = data.get('id')
            if not review_id:
                return JsonResponse({'code': 400, 'msg': '缺少复盘记录ID'})
            
            try:
                review = RepositoryReview.objects.get(id=review_id)
            except RepositoryReview.DoesNotExist:
                return JsonResponse({'code': 404, 'msg': '复盘记录不存在'})
            
            # 获取当前登录用户
            current_user = get_user_from_token(request)
            if not current_user:
                return JsonResponse({'code': 401, 'msg': '无法获取当前用户信息'})
            
            # 检查权限：只有复盘记录的创建者才能编辑
            if review.reviewer_id != current_user.id:
                return JsonResponse({'code': 403, 'msg': '您没有权限编辑此复盘记录'})
            
            # 更新字段
            updatable_fields = [
                'what_happened', 'what_went_well', 'what_not_went_well',
                'lessons_learned', 'action_items', 'effectiveness_score',
                'improvement_potential'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(review, field, data[field])
            
            review.save()
            
            return JsonResponse({
                'code': 200,
                'msg': '复盘记录更新成功'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON格式错误'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'更新复盘记录失败: {str(e)}'})


class ReviewDeleteView(View):
    """
    删除复盘记录（软删除）
    """
    def post(self, request):
        # 检查认证令牌
        if not check_token(request):
            return JsonResponse({'code': 401, 'msg': '缺少认证token或token无效'})
        
        try:
            data = json.loads(request.body.decode("utf-8"))
            review_id = data.get('id')
            
            if not review_id:
                return JsonResponse({'code': 400, 'msg': '缺少复盘记录ID'})
            
            try:
                review = RepositoryReview.objects.get(id=review_id)
            except RepositoryReview.DoesNotExist:
                return JsonResponse({'code': 404, 'msg': '复盘记录不存在'})
            
            # 获取当前登录用户
            current_user = get_user_from_token(request)
            if not current_user:
                return JsonResponse({'code': 401, 'msg': '无法获取当前用户信息'})
            
            # 检查权限：只有复盘记录的创建者才能删除
            if review.reviewer_id != current_user.id:
                return JsonResponse({'code': 403, 'msg': '您没有权限删除此复盘记录'})
            
            # 软删除
            review.is_active = False
            review.save()
            
            return JsonResponse({
                'code': 200,
                'msg': '复盘记录删除成功'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'msg': 'JSON格式错误'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': f'删除复盘记录失败: {str(e)}'})
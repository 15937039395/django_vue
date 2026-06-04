# Copyright (c) 2025 知识库管理系统. All rights reserved.

import json
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils import timezone
from approval.models import SysApproval, SysApprovalSerializer
from user.models import SysUser
from role.models import SysUserRole


class ApprovalListView(View):
    """审批列表查询"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            page_num = data.get('pageNum', 1)
            page_size = data.get('pageSize', 10)
            status = data.get('status')  # 状态筛选
            
            # 基础查询
            queryset = SysApproval.objects.all().order_by('-create_time')
            
            # 状态筛选
            if status:
                queryset = queryset.filter(status=status)
            
            # 数据权限：普通用户只能看到自己提交的和需要自己审批的
            current_user = request.user
            if current_user.username != 'admin':
                queryset = queryset.filter(
                    applicant_id=current_user.id
                ) | queryset.filter(
                    status=SysApproval.STATUS_PENDING
                )
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_data = paginator.get_page(page_num)
            
            # 序列化
            approval_list = []
            for approval in page_data:
                approval_dict = SysApprovalSerializer(approval).data
                approval_list.append(approval_dict)
            
            return JsonResponse({
                'code': 200,
                'approvalList': approval_list,
                'total': paginator.count
            })
            
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': f'查询失败：{str(e)}'
            })


class ApprovalSubmitView(View):
    """提交审批申请"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            approval_type = data.get('approval_type')
            title = data.get('title')
            content = data.get('content')
            target_id = data.get('target_id')
            target_data = data.get('target_data')
            
            current_user = request.user
            
            # 创建审批记录
            approval = SysApproval.objects.create(
                approval_type=approval_type,
                title=title,
                content=content,
                target_id=target_id,
                target_data=json.dumps(target_data) if target_data else None,
                applicant_id=current_user.id,
                applicant_name=current_user.realname or current_user.username,
                status=SysApproval.STATUS_PENDING
            )
            
            return JsonResponse({
                'code': 200,
                'msg': '审批申请已提交',
                'approval_id': approval.id
            })
            
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': f'提交失败：{str(e)}'
            })


class ApprovalProcessView(View):
    """处理审批（通过/拒绝）"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            approval_id = data.get('id')
            action = data.get('action')  # 'approve' 或 'reject'
            remark = data.get('remark', '')
            
            current_user = request.user
            
            # 获取审批记录
            approval = SysApproval.objects.get(id=approval_id)
            
            # 检查状态
            if approval.status != SysApproval.STATUS_PENDING:
                return JsonResponse({
                    'code': 500,
                    'msg': '该审批已处理，无法重复操作'
                })
            
            # 检查权限（只有管理员可以审批）
            if current_user.username != 'admin':
                # 也可以检查是否是部门经理等
                return JsonResponse({
                    'code': 403,
                    'msg': '您没有审批权限'
                })
            
            # 更新审批状态
            if action == 'approve':
                approval.status = SysApproval.STATUS_APPROVED
                
                # 执行实际操作
                if approval.approval_type == SysApproval.TYPE_USER_DELETE:
                    # 删除用户
                    try:
                        user_ids = json.loads(approval.target_data) if approval.target_data else [approval.target_id]
                        SysUserRole.objects.filter(user_id__in=user_ids).delete()
                        SysUser.objects.filter(id__in=user_ids).delete()
                    except Exception as e:
                        return JsonResponse({
                            'code': 500,
                            'msg': f'执行删除操作失败：{str(e)}'
                        })
                
            elif action == 'reject':
                approval.status = SysApproval.STATUS_REJECTED
            else:
                return JsonResponse({
                    'code': 500,
                    'msg': '无效的操作'
                })
            
            approval.approver_id = current_user.id
            approval.approver_name = current_user.realname or current_user.username
            approval.approve_remark = remark
            approval.approve_time = timezone.now()
            approval.save()
            
            return JsonResponse({
                'code': 200,
                'msg': '审批成功' if action == 'approve' else '已拒绝'
            })
            
        except SysApproval.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '审批记录不存在'
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': f'处理失败：{str(e)}'
            })


class ApprovalCancelView(View):
    """撤销审批申请"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            approval_id = data.get('id')
            
            current_user = request.user
            
            # 获取审批记录
            approval = SysApproval.objects.get(id=approval_id)
            
            # 只能撤销自己提交的且待审批的记录
            if approval.applicant_id != current_user.id:
                return JsonResponse({
                    'code': 403,
                    'msg': '只能撤销自己提交的申请'
                })
            
            if approval.status != SysApproval.STATUS_PENDING:
                return JsonResponse({
                    'code': 500,
                    'msg': '该审批已处理，无法撤销'
                })
            
            approval.status = SysApproval.STATUS_CANCELLED
            approval.save()
            
            return JsonResponse({
                'code': 200,
                'msg': '已撤销申请'
            })
            
        except SysApproval.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '审批记录不存在'
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': f'撤销失败：{str(e)}'
            })

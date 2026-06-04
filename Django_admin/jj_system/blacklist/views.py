# Copyright (c) 2025 知识库管理系统. All rights reserved.


import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError

from blacklist.models import SysBlackList, SysBlacklistSerializer


def success_response(data=None, code=200):
    response = {'code': code}
    if data:
        response.update(data)
    return JsonResponse(response)


def error_response(msg, code=400):
    return JsonResponse({'code': code, 'msg': msg})


class SearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            page_num = int(data['pageNum'])
            page_size = int(data['pageSize'])

            if page_num <= 0 or page_size <= 0 or page_size > 100:
                return error_response("分页参数超出允许范围")

            query = data.get('query', '')

            base_queryset = SysBlackList.objects.filter(name__icontains=query)
            paginator = Paginator(base_queryset, page_size)

            try:
                current_page = paginator.page(page_num)
            except (EmptyPage, PageNotAnInteger):
                return error_response("分页参数无效")

            blacks = list(current_page.object_list.values())
            total = paginator.count

            return success_response({
                'blackList': blacks,
                'total': total
            })

        except (KeyError, ValueError, TypeError) as e:
            return error_response(f'参数错误: {str(e)}')
        except Exception as e:
            return error_response(f'服务器内部错误: {str(e)}')


class SaveView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))

            now = timezone.now()
            if data.get('id') == -1:
                self._create_blacklist(data, now)
            else:
                self._update_blacklist(data, now)

            return success_response()
        except (KeyError, ValueError, TypeError) as e:
            return error_response(f'参数错误: {str(e)}')
        except IntegrityError as e:
            return error_response(f'保存失败，可能存在唯一约束冲突: {str(e)}', code=409)
        except Exception as e:
            return error_response(f'服务器内部错误: {str(e)}')

    def _create_blacklist(self, data, now):
        obj_sysBlacklist = SysBlackList(
            name=data['name'],
            contract_time=data['contract_time'],
            deadline_time=data['deadline_time'],
            types=data['types'],
            status=data['status'],
            amount_type=data['amount_type'],
            amount=data['amount'],
            archival_information=data['archival_information'],
            actual_time=data['actual_time'],
            remark=data['remark'],
            create_time=now
        )
        obj_sysBlacklist.save()

    def _update_blacklist(self, data, now):
        record_id = data.get('id')
        if not record_id:
            raise KeyError("Missing id field")

        try:
            obj_sysBlacklist = SysBlackList.objects.get(id=record_id)
        except ObjectDoesNotExist:
            raise ValidationError("指定ID的数据不存在")

        obj_sysBlacklist.name = data['name']
        obj_sysBlacklist.contract_time = data['contract_time']
        obj_sysBlacklist.deadline_time = data['deadline_time']
        obj_sysBlacklist.types = data['types']
        obj_sysBlacklist.status = data['status']
        obj_sysBlacklist.amount_type = data['amount_type']
        obj_sysBlacklist.amount = data['amount']
        obj_sysBlacklist.archival_information = data['archival_information']
        obj_sysBlacklist.actual_time = data['actual_time']
        obj_sysBlacklist.remark = data['remark']
        obj_sysBlacklist.update_time = now
        obj_sysBlacklist.save()


class ActionView(View):
    def get(self, request):
        try:
            record_id = request.GET.get("id")
            if not record_id:
                return error_response('缺少必要参数 id')

            black_object = SysBlackList.objects.get(id=record_id)
            serialized_data = SysBlacklistSerializer(black_object).data
            return success_response({'blacklist': serialized_data})
        except ObjectDoesNotExist:
            return error_response('未找到对应黑名单信息', code=404)
        except Exception as e:
            return error_response(f'服务器内部错误: {str(e)}')

    def delete(self, request):
        try:
            ids = json.loads(request.body.decode("utf-8"))
            if not isinstance(ids, list) or len(ids) == 0:
                return error_response('无效的删除ID列表')

            valid_ids = [int(i) for i in ids if isinstance(i, (int, str)) and str(i).isdigit()]
            if not valid_ids:
                return error_response('删除ID列表中无有效整数')

            deleted_count, _ = SysBlackList.objects.filter(id__in=valid_ids).delete()
            return success_response({'msg': f'成功删除 {deleted_count} 条记录'})
        except json.JSONDecodeError:
            return error_response('JSON格式错误')
        except Exception as e:
            return error_response(f'删除过程中发生错误: {str(e)}')
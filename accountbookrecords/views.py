import json
from json.decoder         import JSONDecodeError

from django.http          import JsonResponse
from django.views         import View
from django.utils         import timezone
from django.db.models     import Q

from accountbookrecords.models  import AccountBookRecord
from core.utils           import LoginAccess 
from .shorturl            import shortUrl

class AccountBookRecordView(View):
    @LoginAccess
    def post(self, request):
        try:
            data            = json.loads(request.body)
            title           = data['title']
            date            = data['date']
            memo            = data['memo']
            description     = data['description']
            amount          = data['amount']
            balance         = data['balance']
            account_book_id = data['book_id']
            user_id         = request.user.id

            AccountBookRecord.objects.create(
              title           = title,
              date            = date,
              memo            = memo,
              description     = description,
              amount          = amount,
              balance         = balance,
              user_id         = user_id,
              account_book_id = account_book_id

            )
            return JsonResponse({'message':'SUCCESS'}, status=201)
            
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"}, status=400)
    
    @LoginAccess
    def get(self, request):
        
        account_book_id = request.GET.get('book_id')
        user_id         = request.GET.get('user_id')
        
        if account_book_id :
          queries = Q(account_book_id = account_book_id)
          queries = Q(account_book_id__user_id = user_id)

        accountbookrecords = AccountBookRecord.objects.filter(queries)
        
        result = [
        {
            'id'         : accountbookrecord.id,
            'title'      : accountbookrecord.title,
            'date'       : accountbookrecord.date,
            'memo'       : accountbookrecord.memo,
            'description': accountbookrecord.description,
            'amount'     : accountbookrecord.amount,
            'balance'    : accountbookrecord.balance,
            'is_deleted' : accountbookrecord.is_deleted,
            'created_at' : accountbookrecord.created_at,
            'updated_at' : accountbookrecord.updated_at,
          
        } for accountbookrecord in accountbookrecords]

        # shortUrl() 단축URl이 만들어짐
        return JsonResponse({"result":result}, status = 200)

        

    @LoginAccess
    def patch(self, request):
        try:
            data           = json.loads(request.body)
            accountbookrecord_id = data['record_id']
            is_deleted           = data['is_deleted']

            accountbookrecords = AccountBookRecord.objects.get(
              id = accountbookrecord_id, 
              user_id = request.user.id)

            if  is_deleted == False:
                accountbookrecords.is_deleted = False
                accountbookrecords.deleted_at = timezone.now()
                accountbookrecords.save()
                
                return JsonResponse({'is_deleted': accountbookrecords.is_deleted, 'deleted_at':accountbookrecords.deleted_at}, status = 200)
            else :
                return JsonResponse({'message' : "BAD REQUEST"}, status = 400) 

        except AccountBookRecord.DoesNotExist :
          return JsonResponse({'message': 'Book_DoesNotExist'}, status = 400)
        except JSONDecodeError :
          return JsonResponse({'message':'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
          return JsonResponse({'message':'KEY_ERROR'}, status=400)
    
    @LoginAccess
    def put(self, request):
        try:
            data           = json.loads(request.body)
            accountbookrecord_id = data['record_id']


            accountbookrecord   = AccountBookRecord.objects.get(
              user_id      = request.user.id,
              id           = accountbookrecord_id
            )

            accountbookrecord.amount = data['amount']
            accountbookrecord.memo = data['memo']
            accountbookrecord.save()
            
            return JsonResponse({'change_amount': accountbookrecord.amount, 'change_memo': accountbookrecord.memo}, status = 200)

        except AccountBookRecord.DoesNotExist :
          return JsonResponse({'message': 'Book_DoesNotExist'}, status = 400)
        except JSONDecodeError :
          return JsonResponse({'message':'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
          return JsonResponse({'message':'KEY_ERROR'}, status=400)
    


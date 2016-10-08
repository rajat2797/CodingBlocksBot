from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.conf import settings
import requests
import json

# Create your views here.

VERIFY_TOKEN = '8thoctober2016'
PAGE_ACCESS_TOKEN = ''

def index(request):
	return HttpResponse(logg('HI','-'))

def logg(text,symbol='*'):
	print '%s%s%s'%(symbol*10,text,symbol*10)

def handle_postback(fbid,payload):
	pass

def handle_quickreply(fbid,payload):
	pass

def post_fb_msg(fbid,message):
	post_fb_url='https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
	requests.post(post_fb_url,headers={"Content-Type": "application/json"},data=response_msg)

class MyChatBotView(generic.View):
    def get (self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Oops invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message= json.loads(self.request.body.decode('utf-8'))
        logg(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:

                try:
                    if 'postback' in message:
                        handle_postback(message['sender']['id'],message['postback']['payload'])
                        return HttpResponse()
                    else:
                        pass
                except Exception as e:
                    logg(e,symbol='-315-')

                try:
                    if 'quick_reply' in message['message']:
                        handle_quickreply(message['sender']['id'],message['message']['quick_reply']['payload'])
                        return HttpResponse()
                    else:
                        pass

                except Exception as e:
                    logg(e,symbol='-325-')
                
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_fb_msg(sender_id,message_text) 
                except Exception as e:
                    logg(e,symbol='-332-')

        return HttpResponse()
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.conf import settings
from details import v_token, page_token, sheet_id
import requests
import json

# Create your views here.

VERIFY_TOKEN = v_token
PAGE_ACCESS_TOKEN = page_token

def index(request):
	# return HttpResponse(scrape_spreadsheet())
	# return HttpResponse(gen_response_object('21',scrape_spreadsheet(),'course'))
	# return HttpResponse(post_fb_msg('21',''))
	return HttpResponse('HI')

def logg(text,symbol='*'):
	print '%s%s%s'%(symbol*10,text,symbol*10)

def handle_postback(fbid,payload):
	pass

def handle_quickreply(fbid,payload):
	pass

def scrape_spreadsheet():
    url = 'https://spreadsheets.google.com/feeds/list/%s/od6/public/values?alt=json'%sheet_id
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    data=data['feed']['entry']
    arr=[]

    for entry in data:
    	d={}
        for k,v in entry.iteritems():
        	if k.startswith('gsx'):
        		key_name = k.split('$')[1]
        		d[key_name] = entry[k]['$t']

        arr.append(d)

    return arr

def gen_response_object(fbid,spreadsheet_object,item_type = 'course'):
	item_arr = [i for i in spreadsheet_object if i['itemtype'].lower()==item_type.lower()]
	elements=[]
	for i in item_arr:
		sub_item = {

					"title":i['itemname'],
					"item_url":i['itemlink'],
					"image_url":i['itempicture'],
					"subtitle":i['itemdescription'],
					"buttons":[
					  {
					    "type":"web_url",
					    "url":i['itemlink'],
					    "title":"OPEN"
					  },
					  {
					    "type":"element_share"
					  }               
					]

		}
		elements.append(sub_item)

	response_object = {
				"recipient":{
				    "id":fbid
				  },
				  "message":{
				    "attachment":{
				      "type":"template",
				      "payload":{
				        "template_type":"generic",
				        "elements":elements
				      }
				    }
				  }
		}

	return json.dumps(response_object)

def post_fb_msg(fbid,message):
	post_fb_url='https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
	response_msg_object = gen_response_object(fbid,scrape_spreadsheet(),message)
	# return response_msg_object
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
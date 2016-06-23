# coding=utf-8
#----------------------------------------------#
# BifrostBot | Jahus | 2016-06-17              #
#----------------------------------------------#----------------
# Fork from VideoLabelBot 1.2.3
# Change log
# * 2016-06-17 :
#     (0.0.0)               - First code (Alpha)
#     (1.0.0)               - Beta release
#     (1.1.0)               - Added Channel Part with reason
# * 2016-06-18 :
#     (1.2.0)               - Added /enligne command (from Dj4x)
# * 2016-06-23 :
#                           - Cleared code for GitHub
#
bDEBUG = True
__username__ = "~@BridgeToIRC_Bot"
#---------------------------------------------------------------
# IMPORTS
#---------------------------------------------------------------
import json
import requests
import time
import os
requests.packages.urllib3.disable_warnings()
#---------------------------------------------------------------
# DATA
#---------------------------------------------------------------
def load_file_json(file_name):
	with open(file_name, 'r') as _file:
		content = _file.read()
		content_dict = json.loads(content)
		return content_dict
# CONFIG FILES
data_file = {
	"windows": "C:\\Users\\jahus\\AppData\\Roaming\\HexChat\\addons\\BifrostBot_config.json",
	"linux": "/home/foudre/.config/hexchat/addons/BifrostBot_config.json"
}
SYSTEM = "linux"
config = load_file_json(data_file[SYSTEM])
#
#---------------------------------------------------------------
# IRC
#---------------------------------------------------------------
#
__module_name__ = str(config["bot_name"])
__module_version__ = str(config["bot_version"])
__module_description__ = str(config["bot_description"])
import hexchat # HexChat IRC client
telegram_group_for_irc = config["telegram_params"]["telegram_group_for_irc"]
send_to_IRC = True
#---------------------------------------------------------------
# VARIABLES
#---------------------------------------------------------------
__name__ = __module_name__
__version__ = __module_version__
__description__ = __module_description__
print("#---------------------------------------------------------------")
print("# %s version %s, by Jahus & Mohus Softworks." % (__name__, __version__))
print("#---------------------------------------------------------------")
telegram_bot_token = config.get("telegram_params").get("token")
telegram_bot_request = "https://api.telegram.org/bot"
Markdown_chars = {
	"`": {
		"description": "code"
	},
	"*": {
		"description": "bold"
	},
	"_": {
		"description": "italic"
	},
	"[": {
		"description": "link_start"
	}
}
#
#---------------------------------------------------------------
# Telegram :: Classes
#---------------------------------------------------------------
#
# User or Bot
class telegram_classes_User:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.first_name = data_json.get("first_name")
		if "last_name" in data_json:
			self.last_name = data_json.get("last_name")
		else:
			self.last_name = -1
		if "username" in data_json:
			self.username = data_json.get("username")
		else:
			self.username = -1
	def __str__(self):
		r_str = "User #%s | First name: %s" % (self.id, self.first_name)
		if self.last_name != -1:
			r_str += " | Last name: %s" % (self.last_name)
		if self.username != -1:
			r_str += " | Username: @%s" % (self.username)
		return r_str
#
# Group chat
class telegram_classes_GroupChat:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Group chat #%s: ""%s""" % (self.id, self.title)
#
# Supergroup chat
class telegram_classes_SupergroupChat:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Supergroup #%s: ""%s""" % (self.id, self.title)
#
# Channel
class telegram_classes_Channel:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.title = data_json.get("title")
	def __str__(self):
		return "Channel #%s: ""%s""" % (self.id, self.title)
# 
# Types for Message
telegram_types = {
	"text": "T",
	"forward_from": "F",
	"reply_to_message": "R",
	"audio": "A",
	"document": "G",
	"photo": "I",
	"sticker": "S",
	"video": "V",
	"contact": "U",
	"location": "L",
	"new_chat_participant": "cpn",
	"left_chat_participant": "cpl",
	"new_chat_title": "ctn",
	"new_chat_photo": "cin",
	"delete_chat_photo": "cid",
	"group_chat_created": "gcc",
	"supergroup_chat_created": "sgcc",
	"channel_chat_created": "ccc",
	"migrate_to_chat_id": "mtci",
	"migrate_from_chat_id": "mfci"
}
#
class telegram_classes_Message:
	def __init__(self, data_json):
		self.type = ""
		self.message_id = data_json.get("message_id")
		if "from" in data_json:
			self.sender = telegram_classes_User(data_json.get("from"))
		else:
			self.sender = "[N/A]"
		self.date = data_json.get("date")
		# NEW API ELEMENTS (2016-02-05) for channels
		if data_json["chat"]["type"] == "private":
			self.chat = telegram_classes_User(data_json.get("chat"))
			self.chat_type = "private"
		elif data_json["chat"]["type"] == "group":
			self.chat = telegram_classes_GroupChat(data_json.get("chat"))
			self.chat_type = "group"
		elif data_json["chat"]["type"] == "supergroup":
			self.chat = telegram_classes_SupergroupChat(data_json.get("chat"))
			self.chat_type = "supergroup"
		else: #elif
			self.chat = telegram_classes_Channel(data_json.get("chat"))
			self.chat_type = "channel"
		#
		if "forward_from" in data_json:
			self.forward_from = telegram_classes_User(data_json.get("forward_from"))
			if telegram_types.get("forward_from") not in self.type: self.type += telegram_types.get("forward_from")
		if "forward_date" in data_json:
			self.forward_date = data_json.get("forward_date")
		if "reply_to_message" in data_json:
			self.reply_to_message = telegram_classes_Message(data_json.get("reply_to_message"))
			if telegram_types.get("reply_to_message") not in self.type: self.type += telegram_types.get("reply_to_message")
		if "text" in data_json:
			self.text = data_json.get("text")
			if telegram_types.get("text") not in self.type: self.type += telegram_types.get("text")
		if "audio" in data_json:
			self.audio = data_json.get("audio") #TODO: Audio structure
			if telegram_types.get("audio") not in self.type: self.type += telegram_types.get("audio")
		if "document" in data_json:
			self.document = data_json.get("document") #TODO: Document structure
			if telegram_types.get("document") not in self.type: self.type += telegram_types.get("document")
		if "photo" in data_json:
			self.photo = data_json.get("photo") #TODO: Photo structure
			if telegram_types.get("photo") not in self.type: self.type += telegram_types.get("photo")
		if "sticker" in data_json:
			self.sticker = data_json.get("sticker") #TODO: Sticker structure
			if telegram_types.get("sticker") not in self.type: self.type += telegram_types.get("sticker")
		if "video" in data_json:
			self.video = data_json.get("video") #TODO: Video structure
			if telegram_types.get("video") not in self.type: self.type += telegram_types.get("video")
		if "caption" in data_json:
			self.caption = data_json.get("caption")
		if "contact" in data_json:
			self.contact = data_json.get("contact") #TODO: Contact structure
			if telegram_types.get("contact") not in self.type: self.type += telegram_types.get("contact")
		if "location" in data_json:
			self.location = data_json.get("location") #TODO: Location structure
			if telegram_types.get("location") not in self.type: self.type += telegram_types.get("location")
		if "new_chat_participant" in data_json:
			self.new_chat_participant = telegram_classes_User(data_json.get("new_chat_participant"))
			if telegram_types.get("new_chat_participant") not in self.type: self.type += telegram_types.get("new_chat_participant")
		if "left_chat_participant" in data_json:
			self.left_chat_participant = telegram_classes_User(data_json.get("left_chat_participant"))
			if telegram_types.get("left_chat_participant") not in self.type: self.type += telegram_types.get("left_chat_participant")
		if "new_chat_title" in data_json:
			self.new_chat_title = data_json.get("new_chat_title")
			if telegram_types.get("new_chat_title") not in self.type: self.type += telegram_types.get("new_chat_title")
		if "new_chat_photo" in data_json:
			self.new_chat_photo = data_json.get("new_chat_photo") #TODO: Photo structure
			if telegram_types.get("new_chat_photo") not in self.type: self.type += telegram_types.get("new_chat_photo")
		if "delete_chat_photo" in data_json:
			self.delete_chat_photo = data_json.get("delete_chat_photo") # Boolean
			if telegram_types.get("delete_chat_photo") not in self.type: self.type += telegram_types.get("delete_chat_photo")
		if "group_chat_created" in data_json:
			self.group_chat_created = data_json.get("group_chat_created") # Boolean
			if telegram_types.get("group_chat_created") not in self.type: self.type += telegram_types.get("group_chat_created")
		# added 2016-02-05
		if "supergroup_chat_created" in data_json:
			self.supergroup_chat_created = data_json.get("supergroup_chat_created") # Boolean
			if telegram_types.get("supergroup_chat_created") not in self.type: self.type += telegram_types.get("supergroup_chat_created")
		if "channel_chat_created" in data_json:
			self.channel_chat_created = data_json.get("channel_chat_created") # Boolean
			if telegram_types.get("channel_chat_created") not in self.type: self.type += telegram_types.get("channel_chat_created")
		if "migrate_to_chat_id" in data_json:
			self.channel_chat_created = data_json.get("migrate_to_chat_id") # integer
			if telegram_types.get("migrate_to_chat_id") not in self.type: self.type += telegram_types.get("migrate_to_chat_id")
		if "migrate_from_chat_id" in data_json:
			self.channel_chat_created = data_json.get("migrate_from_chat_id") # Boolean
			if telegram_types.get("migrate_from_chat_id") not in self.type: self.type += telegram_types.get("migrate_from_chat_id")
	def __str__(self):
		return "Message #%s at %s. From %s to %s." % (self.message_id, self.date, self.sender, self.chat)
#
class telegram_classes_Update:
	def __init__(self, data_json):
		self.update_id = data_json.get("update_id")
		self.type = ""
		if "message" in data_json:
			self.message = telegram_classes_Message(data_json.get("message"))
			self.type += "m"
		if "inline_query" in data_json:
			self.inline_query = telegram_classes_InlineQuery(data_json.get("inline_query"))
			self.type += "iq"
		if "chosen_inline_result" in data_json:
			self.chosen_inline_result = telegram_classes_ChosenInlineResult(data_json.get("chosen_inline_result"))
			self.type += "ir"
	def __str__(self):
		return "Update #%s | Type: %s" % (self.update_id, self.type)
#
# UPDATE 2016-01-05 InLine query
class telegram_classes_InlineQuery:
	def __init__(self, data_json):
		self.id = data_json.get("id")
		self.sender = telegram_classes_User(data_json.get("from"))
		self.query = data_json.get("query")
		self.offset = data_json.get("offset")
#
class telegram_classes_ChosenInlineResult:
	def __init__(self, data_json):
		self.result_id = data_json.get("result_id")
		self.sender = data_json.get("from")
		self.query = data_json.get("query")
#
#---------------------------------------------------------------
# Telegram :: Bot
#---------------------------------------------------------------
#
telegram_bot_info = None
telegram_bot_offset = 0
#
# Error messages can be formatted with simple Markdown or simple HTML
error_messages = {
	"err_source": [
		"*Error*",
		"_Sorry, I can't do this with these arguments._",
		"Usage: `/command_name <opt1> [opt2]`",
		"Example: `/command_name DOGE BTC`",
		"Another line here"
		],
	"err_source_2": [
		"*Warning*",
		"foo",
		"`boo`",
		"Example: `blah`"
		],
	"api_error": [
		"*Error*",
		"Source returned:"
		]
	}
#
def telegram_bot_get_bot_info():
	global __username__
	if bDEBUG:
		print("** get_bot_info(): getting bot information...")
	global telegram_bot_info
	req = requests.get("%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getMe"))
	if (req.status_code != 200):
		print("** get_bot_info(): Error %s" % req.status_code)
	else:
		req_json = req.json()
		if "ok" in req_json:
			if (req_json.get("ok") == True):
				_me = telegram_classes_User(req_json.get("result"))
				__username__ = _me.username
				telegram_bot_info = _me
				print(telegram_bot_info)
			else:
				print("** get_bot_info(): Error %s" % "There has been an unknown error")
		else:
			print("** get_bot_info(): Error %s" & "There has been an unknown error.")
#
def telegram_bot_get_updates():
	global telegram_bot_offset
	req_data = {
		"offset": telegram_bot_offset + 1,
		"limit": "",
		"timeout": ""
		}
	req = requests.get("%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getUpdates"), req_data)
	if (req.status_code != 200):
		print("** get_updates(): Error %s" % req.status_code)
	else:
		req_json = req.json()
		# print(req_json)
		if "ok" in req_json:
			if (req_json.get("ok") == True):
				# print("-- telegram_bot_get_updates(): Got %s updates." % len(req_json.get("result")))
				for update_json in req_json.get("result"):
					_update = telegram_classes_Update(update_json)
					print("** get_updates(): reading update '%s'..." % _update.update_id)
					if _update.update_id > telegram_bot_offset: telegram_bot_offset = _update.update_id
					# Traiter le message reçu
					if _update.type == "m":
						telegram_bot_read_message(_update.message)
					else:
						telegram_bot_read_inlinequery(_update)
			else:
				print("** get_updates(): Error %s" % "There has been an unknown error")
		else:
			print("** get_updates(): Error %s" & "There has been an unknown error.")
#
def telegram_bot_send_message(chat_id, text, parse_mode = None, disable_web_page_preview = None, reply_to_message_id = None, reply_markup = None):
	req_data = {
		"chat_id": chat_id,
		"text": text
	}
	if bDEBUG: print("** Sending message to chat # %s. Text: %s" % (chat_id, text))
	if parse_mode != None:
		req_data.update([("parse_mode", parse_mode)])
	if disable_web_page_preview != None:
		req_data.update([("disable_web_page_preview", disable_web_page_preview)])
	if reply_to_message_id != None:
		req_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		req_data.update([("reply_markup", reply_markup)])
	req = requests.post(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendMessage"), data = req_data)
	if (req.status_code != 200):
		print("-- answerInlineQuery(): Error %s (::%s)" % (req.status_code, req.content))
	else:
		req_json = req.json()
		# print(req_json)
		#TODO: Verify if send message is equal to received message
#
def telegram_bot_read_message(message):
	# Checking message type
	if telegram_types.get("text") in message.type:
		telegram_bot_handle_message_text(message)
	elif telegram_types.get("new_chat_participant") in message.type:
		telegram_bot_handle_message_chat_participant_new(message)
	elif telegram_types.get("left_chat_participant") in message.type:
		telegram_bot_handle_message_chat_participant_left(message)
	elif telegram_types.get("new_chat_title") in message.type:
		telegram_bot_handle_message_chat_title_new(message)
	elif telegram_types.get("group_chat_created") in message.type:
		telegram_bot_handle_message_group_chat_created(message)
	elif telegram_types.get("photo") in message.type:
		telegram_bot_handle_message_picture(message)
	elif telegram_types.get("channel_chat_created") in message.type:
		telegram_bot_handle_message_channel_chat_created(message)
	elif telegram_types.get("video") in message.type:
		telegram_bot_handle_message_video(message)
	elif telegram_types.get("document") in message.type:
		telegram_bot_handle_message_document(message)
	else:
		print("-- read_message(): Message type unhandled")
#
def telegram_bot_read_inlinequery(Update):
	print("** read_inlinequery(): Reading update...")
	if Update.type == "iq":
		print("--- telegram_bot_read_inlinequery(): Reading inline query...")
		inline_query = Update.inline_query
		sender = inline_query.sender # user that sent the request
		query = inline_query.query # important
		offset = inline_query.offset # not important
		print("---> Query:\n\t#%s: %s" % (inline_query.id, inline_query.query.encode("utf-8")))
		# Add a line to call the main function of your bot with query.split(' ') arguments.
	elif Update.type == "ir":
		print("--- telegram_bot_read_inlinequery(): Reading inline result choice...")
		chosen_inline_result = Update.chosen_inline_result
		# Optional: Add a line to make your bot know what people choose
#
def telegram_bot_sendDocument(chat_id, file_name, reply_to_message_id = None, reply_markup = None, file_name_suppl = '', file_ext = '', mime_type = None, existing_file = False):
	head_data = {
		"chat_id": chat_id
		}
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("document", file_name)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendDocument"), params = head_data)
	else:
		_file = {'document': (file_name + file_name_suppl + file_ext, open(file_name + file_ext, 'rb'))}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendDocument"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("-- sendDocument(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("-- sendDocument(): Success\nAnswer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.document["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_sendPhoto(chat_id, photo, existing_file = False, caption = None, reply_to_message_id = None, reply_markup = None):
	head_data = {
		"chat_id": chat_id
		}
	if caption != None:
		head_data.update([("caption", caption)])
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("photo", photo)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendPhoto"), params = head_data)
	else:
		_file = {'photo': (photo, open(photo, 'rb'), "image/jpeg")}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendPhoto"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("** sendPhoto(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("** sendPhoto(): Success\n*** Answer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.photo[-1]["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_sendVideo(chat_id, video, existing_file = False, duration = None, caption = None, reply_to_message_id = None, reply_markup = None):
	head_data = {
		"chat_id": chat_id
		}
	if bDEBUG: # remove this if you have correct video files sent as videos (not files)
		if duration == None: duration = 5
	if duration != None:
		head_data.update([("duration", duration)])
	if caption != None:
		head_data.update([("caption", caption)])
	if reply_to_message_id != None:
		head_data.update([("reply_to_message_id", reply_to_message_id)])
	if reply_markup != None:
		head_data.update([("reply_markup", reply_markup)])
	if existing_file:
		head_data.update([("video", video)])
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendVideo"), params = head_data)
	else:
		_file = {'video': (video, open(video, 'rb'))}
		req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/sendVideo"), params = head_data, files = _file)
	if (req.status_code != 200):
		print("** sendVideo(): Error %s\n*** %s" % (req.status_code, req.content))
		return None
	else:
		req_json = req.json()
		if bDEBUG: print("** sendVideo(): Success\n*** Answer:%s" % ("%s" % req_json).encode("utf-8"))
		returned_message = telegram_classes_Message(req_json["result"])
		return {"file_id": returned_message.video["file_id"], "message_id": returned_message.message_id}
#
def telegram_bot_answerInlineQuery(inline_query_id, results, cache_time = None, is_personal = None, next_offset = None):
	req_data = {
		"inline_query_id": int(inline_query_id),
		"results": json.dumps(results)
		}
	if cache_time != None:
		req_data.update([("cache_time", cache_time)])
	if is_personal != None:
		req_data.update([("is_personal", is_personal)])
	if next_offset != None:
		req_data.update([("next_offset", next_offset)])
	print("-- telegram_bot_answerInlineQuery()\n\tData = %s" % req_data)
	req = requests.post(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/answerInlineQuery"), data = req_data)
	if (req.status_code != 200):
		print("-- answerInlineQuery(): Error %s (::%s)" % (req.status_code, req.content))
	else:
		req_json = req.json()
		print("** answerInlineQuery():\n\tRequest sent. Result: %s" % req_json)
		#TODO: True is returned on success.
#
def telegram_bot_createInlineQueryResult_article(id, title, message_text, parse_mode = None, disable_web_page_preview = None, url = None, hide_url = None, description = None, thumb_url = None, thumb_width = None, thumb_height = None):
	type = "article"
	r = {
		"type": type,
		"id": id,
		"title": title,
		"message_text": message_text
		}
	if parse_mode != None:
		r.update([("parse_mode", parse_mode)])
	if disable_web_page_preview != None:
		r.update([("disable_web_page_preview", disable_web_page_preview)])
	if url != None:
		r.update([("url", url)])
	if hide_url != None:
		r.update([("hide_url", hide_url)])
	if description != None:
		r.update([("description", description)])		
	if thumb_url != None:
		r.update([("thumb_url", thumb_url)])
	if thumb_width != None:
		r.update([("thumb_width", thumb_width)])
	if thumb_height != None:
		r.update([("thumb_height", thumb_height)])
	return r
#---------------------------------------------------------------
# Message handles
#---------------------------------------------------------------
def telegram_bot_handle_message_text(message):
	_to = ""; _from = ""
	_text = message.text
	if message.sender.id != message.chat.id:
		_to = "@%s" % message.chat.title
	if telegram_types.get("forward_from") in message.type:
		_from = " [fwd: %s]" % message.forward_from.first_name
		if _text[0] == "<":
			_from = " [fwd: %s]" % _text[1:].split(">")[0]
			_text = ' '.join(_text[1:].split(">")[1:])[1:]
	print("[#%s]\t<%s(%s)%s%s> %s" % (message.message_id, message.sender.first_name.encode("utf-8"), message.sender.id, _to.encode("utf-8"), _from, _text.encode("UTF-8")))
	# Telegram bridge (to IRC)
	Telegram_to_IRC(message.sender, message.chat.id, message.text, _from=_from)
	# Handle commands
	# user / chat / command / arguments(full_text)
	if len(_text) > 2 and _text[0] == "/":
		if _to == "":
			# Privé
			_command = _text[1:].split()[0]
			_args = _text[1:].split()[1:]
			print("--- Private command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
			telegram_bot_command_user(_command, _args, message.sender, message.message_id)
		elif ("@" + telegram_bot_info.username.lower()) in _text.lower():
			# Groupe + Hilight
			# /command@MyBot
			_bot_username = _text[1:].split('@')[1][:len(telegram_bot_info.username)].lower()
			#print("_bot_username = %s" % _bot_username)
			if _bot_username.lower() == telegram_bot_info.username.lower():
				_command = _text[1:].split('@')[0]
				_args = (" ".join(_text[1:].split('@')[1:])[len(_bot_username):]).split()
				print("--- Group command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
				telegram_bot_command_user(_command, _args, message.sender, message.message_id, message.chat)
		else:
			# Group /without hilight
			# /command [args]
			_command = _text[1:].split()[0]
			_args = _text[1:].split()[1:]
			print("--- Group command is: %s | With args: %s" % (_command.encode("utf-8"), ((' '.join(_args)).encode("utf-8")).split()))
			telegram_bot_command_user(_command, _args, message.sender, message.message_id, message.chat)
#
def telegram_bot_handle_message_chat_participant_new(message):
	print("[#%s]\t** %s joined group %s" % (message.message_id, message.new_chat_participant.first_name, message.chat.title.encode("utf-8")))
	if message.new_chat_participant.id != telegram_bot_info.id:
		telegram_bot_send_message(message.chat.id, "Hello, %s." % message.new_chat_participant.first_name, reply_to_message_id = message.message_id)
	else:
		telegram_bot_send_message(message.chat.id, "Salut tout le monde ! [chat #%s]" % message.chat.id, reply_to_message_id = message.message_id)
def telegram_bot_handle_message_chat_participant_left(message):
	print("[#%s]\t** %s left group %s" % (message.message_id, message.left_chat_participant.first_name, message.chat.title.encode("utf-8")))
	if message.left_chat_participant.id != telegram_bot_info.id:
		telegram_bot_send_message(message.chat.id, "Bye, %s." % message.left_chat_participant.first_name, reply_to_message_id = message.message_id)
def telegram_bot_handle_message_chat_title_new(message):
	print("[#%s]\t** Group %s changed title to ""%s""" % (message.message_id, message.chat.id, message.new_chat_title.encode("utf-8")))
def telegram_bot_handle_message_group_chat_created(message):
	print("[#%s]\t** Group chat ""%s"" created" % (message.message_id, message.chat.title.encode("utf-8")))
	#telegram_bot_send_message(message.chat.id, "Salut tout le monde !")
# Added 2016-02-05
def telegram_bot_handle_message_channel_chat_created(message):
	print("[#%s]\t** Channel chat ""%s"" created" % (message.message_id, message.chat.title.encode("utf-8")))
	#telegram_bot_send_message(message.chat.id, "Salut tout le monde !")
#
def telegram_bot_handle_message_audio(message):
	print("Sorry, I can't hear audio for now.")
#
def telegram_bot_handle_message_video(message):
	if bDEBUG: telegram_bot_send_message(message.chat.id, "*Video* received.", parse_mode = "Markdown", reply_to_message_id = message.message_id)
	if message.chat_type == "private":
		user_id = message.chat.id
		# Video Label Bot
		if user_id in config["telegram_params"]["admins"]:
			VideoLabelBot(message, isVideo = True)
#
def telegram_bot_handle_message_document(message):
	if bDEBUG: telegram_bot_send_message(message.chat.id, "*File* received.", parse_mode = "Markdown", reply_to_message_id = message.message_id)
	if message.chat_type == "private":
		user_id = message.chat.id
		# Video Label Bot
		if user_id in config["telegram_params"]["admins"]:
			VideoLabelBot(message)
#
# Remove markdown characters
def Markdown_RemoveChars(string):
	Markdown_chars = {
		"`": {
			"description": "code"
		},
		"*": {
			"description": "bold"
		},
		"_": {
			"description": "italic"
		},
		"[": {
			"description": "link_start"
		}
	}
	_string = string
	for char in Markdown_chars.keys():
		_string = _string.replace(char, "\\%s" % char)
	return _string
#
#
def telegram_bot_getFile(file_id):
	head_data = {
		"file_id": file_id
		}
	req = requests.get(url = "%s%s%s" % (telegram_bot_request, telegram_bot_token, "/getFile"), params = head_data)
	if (req.status_code != 200):
		print("-- getFile(): Error %s (::%s)" % (req.status_code, req.content))
		return {"success": False, "reason": "Error %s" % req.status_code}
	else:
		req_json = req.json()
		if bDEBUG: print("** getFile():\n\tResult: %s" % req_json)
		req_json_result = req_json["result"]
		_file_id = req_json_result["file_id"]
		_file_size = None
		_file_path = None
		if "file_size" in req_json_result: _file_size = req_json_result["file_size"]
		if "file_path" in req_json_result: _file_path = req_json_result["file_path"]
		# TODO: Check if file_id is the same as requested
		# TODO: Add file_size to returned answer on success
		if not _file_path:
			return {"success": False, "reason": "No file returned. Can't download. Sorry"}
		else:
			return {"success": True, "file_path": _file_path}
#
def telegram_bot_handle_message_picture(message):
	print("Sorry, I can't see pictures for now.")
def telegram_bot_handle_message_sticker(message):
	print("Sorry, I don't care about stickers for now.")
def telegram_bot_handle_message_contact(message):
	print("Sorry, I have nothing to do with this contact for now.")
def telegram_bot_handle_message_location(message):
	print("Sorry, I can't change location, nor look at it for now.")
def telegram_bot_handle_message_chat_photo_new(message):
	print("Sorry, I can't see chat photos for now.")
def telegram_bot_handle_message_chat_photo_delete(message):
	print("Sorry, I don't care about photos for now.")
#
def telegram_bot_command_about(context, original_message_id):
	# Fournit le texte d'à propos
	telegram_bot_send_message(context, "@%(username)s\n*%(name)s* version %(version)s\nBy @Jahus.\n_This is a bridge between a telegram group chat and an IRC channel. No special command is required. Just talk._" % {"username": __username__, "name": __name__, "version": __version__}, reply_to_message_id = original_message_id, parse_mode="Markdown")
#
def telegram_bot_command_user(msg, args, user, original_message_id, chat = None):
	if chat == None: chat = user
	cmd = msg.split()[0]
	if bDEBUG: print("Received command '%s' with arguments '%s'." % (cmd, args))
	if cmd.lower() == "about":
		telegram_bot_command_about(chat.id, original_message_id)
	if cmd.lower() == "keskifichou":
		telegram_bot_send_message(chat.id, "Une vraie chaudasse !", reply_to_message_id = original_message_id)
	if cmd.lower() == "enligne":
		get_irc_channel_users(user, chat, original_message_id)
#
#---------------------------------------------------------------
# Functions
#---------------------------------------------------------------
#
def DownloadFile(url, name = None, name_alt = None):
	# This function is a legacy from Get500pxBot
	print("* DownloadFile(): Downloading file '%s'..." % url.encode("utf-8"))
	if name != None:
		_FileName = name
	elif name_alt != None:
		_FileName = name_alt
	else:
		_FileName = url.split('/')[-1]
	try:
		# Downloading file...
		req = requests.get(url = url, stream = True)
		try:
			with open(_FileName, 'wb') as _File:
				for chunk in req.iter_content(chunk_size = 512):
					if chunk:
						_File.write(chunk)
			print("* DownloadFile(): File downloaded.")
			return {"success": True, "file_path": _FileName}
		except:
			try:
				with open(name_alt, 'wb') as _File:
					for chunk in req.iter_content(chunk_size = 512):
						if chunk:
							_File.write(chunk)
					print("* DownloadFile(): File downloaded.")
					return {"success": True, "file_path": name_alt}
			except:
				print("* DownloadFile(): ERROR Can't create destination file.")
				return {"success": False, "reason": "Can't create destination file."}
	except:
		print("* DownloadFile(): ERROR Can't download file.")
		return {"success": False, "reason": "Can't download file."}
#
#--------------------------------------------------------------
# HOOKS
#--------------------------------------------------------------
#
# Channel messsages
def trig_chan(word, word_eol, userdata):
	# Strip input word
	for i in range(len(word)):
		word[i] = hexchat.strip(word[i], -1, 3)
	# Telegram bridge
	IRC_to_Telegram(hexchat.get_context(), word[0], word[1])
	return hexchat.EAT_NONE
hexchat.hook_print("Channel Message", trig_chan)
#
# Hilight in channels
def trig_hilight(word, word_eol, userdata):
	# STRIP word
	for i in range(len(word)):
		word[i] = hexchat.strip(word[i], -1, 3)
	# Telegram bridge
	IRC_to_Telegram(hexchat.get_context(), word[0], word[1])
hexchat.hook_print("Channel Msg Hilight", trig_hilight)
#
def trig_user_join(word, word_eol, userdata):
	print("-- trig_user_join(): word = '%s'" % word)
	user_nick = word[0]
	channel = word[1]
	user_host = word[2]
	# Telegram bridge
	if channel.lower() in config["irc_params"]["irc_channels_for_telegram"]:
		telegram_bot_send_message(config["irc_params"]["irc_channels_for_telegram"][channel.lower()], "** *%s* (`%s`) has joined `%s`" % (user_nick, user_host, channel), parse_mode = "Markdown")
hexchat.hook_print("Join", trig_user_join)
#
def trig_user_part(word, word_eol, userdata):
	print("-- trig_user_part(): word = '%s'" % word)
	user_nick = word[0]
	user_host = word[1]
	channel = word[2]
	# Telegram bridge
	if channel.lower() in config["irc_params"]["irc_channels_for_telegram"]:
		telegram_bot_send_message(config["irc_params"]["irc_channels_for_telegram"][channel.lower()], "** *%s* (`%s`) has left `%s`" % (user_nick, user_host, channel), parse_mode = "Markdown")
hexchat.hook_print("Part", trig_user_part)
#
def trig_user_part_reason(word, word_eol, userdata):
	print("-- trig_user_part(): word = '%s'" % word)
	user_nick = word[0]
	user_host = word[1]
	channel = word[2]
	reason = word[3]
	# Telegram bridge
	if channel.lower() in config["irc_params"]["irc_channels_for_telegram"]:
		telegram_bot_send_message(config["irc_params"]["irc_channels_for_telegram"][channel.lower()], "** *%s* (`%s`) has left `%s` (Reason: _%s_)" % (user_nick, user_host, channel, reason), parse_mode = "Markdown")
hexchat.hook_print("Part with reason", trig_user_part_reason)
#
def trig_user_quit(word, word_eol, userdata):
	print("-- trig_user_quit(): word = '%s'" % word)
	user_nick = word[0]
	user_quit_reason = word[1]
	user_host = word[2]
	channel = hexchat.get_context().get_info("channel")
	print("-- trig_user_quit(): channel = %s" % channel)
	# Telegram bridge
	if channel.lower() in config["irc_params"]["irc_channels_for_telegram"]:
		telegram_bot_send_message(config["irc_params"]["irc_channels_for_telegram"][channel.lower()], "** *%s* (`%s`) has quit (Reason: _%s_)" % (user_nick, user_host, user_quit_reason), parse_mode = "Markdown")
hexchat.hook_print("Quit", trig_user_quit)
#
#---------------------------------------------------------------
# Bifrost Bridge
#---------------------------------------------------------------
def IRC_to_Telegram(current_context, user, text_to_send):
	if current_context.get_info("channel").lower() in config["irc_params"]["irc_channels_for_telegram"]:
		_text_to_send = text_to_send
		for char in Markdown_chars.keys():
			_text_to_send = _text_to_send.replace(char, "\\%s" % char)
		telegram_bot_send_message(config["irc_params"]["irc_channels_for_telegram"][current_context.get_info("channel").lower()], "`<`*%s*`>` %s" % (user, _text_to_send), parse_mode = "Markdown")
#
def Telegram_to_IRC(message_sender, chat_id, message_text, _from = ""):
	_multi_line_text = message_text.split('\n')
	# Anti-flood system:
	if len(_multi_line_text) > 4:
		_multi_line_text = _multi_line_text[:min(3, len(_multi_line_text))]
		_multi_line_text.append("[... and more on Telegram.]")
		if bDEBUG: print("** Telegram_to_IRC:\n\t'_multi_line_text' = %s" % _multi_line_text)
	if (str(chat_id) in telegram_group_for_irc):
		current_context = hexchat.find_context(channel = telegram_group_for_irc.get(str(chat_id)))
		for _line in _multi_line_text:
			current_context.command("msg %s <%s%s> %s" % (current_context.get_info("channel"), message_sender.first_name.encode("utf-8"), _from.encode("utf-8"), _line.encode("utf-8")))
#
def get_irc_channel_users(user, chat, original_message_id):
	if str(chat.id) in config["telegram_params"]["telegram_group_for_irc"]:
		current_context = hexchat.find_context(channel = config["telegram_params"]["telegram_group_for_irc"][str(chat.id)])
		cc_users = current_context.get_list("users")
		cc_users_nicks_pack = [("-- `%s`" % (i.nick)) for i in cc_users]
		if len(cc_users_nicks_pack) == 0:
			telegram_bot_send_message(user.id, "The channel is... void?!")
		else:
			telegram_bot_send_message(user.id, "List of users on channel `%s` as you requested:\n%s." % (current_context.get_info("channel"), " ;\n".join(cc_users_nicks_pack)), parse_mode="Markdown")
	else:
		telegram_bot_send_message(chat.id, "Sorry %s, you are not on a bridged group." % user.first_name, reply_to_message_id=original_message_id, parse_mode="Markdown")
#
#--------------------------------------------------------------
# TIMERS
#--------------------------------------------------------------
timer_telegram = None
timer_telegram_first = None
timer_telegram_timeout = config["telegram_params"]["timeout"]
timer_telegram_timeout_first = config["telegram_params"]["timeout_first"]
#
def _timeout_telegram(userdata):
	if timer_telegram_first is None:
		try:
			telegram_bot_get_updates()
		except:
			if bDEBUG: print("** Telegram interface :: Can't get updates | Error from _timeout_telegram()")
			log_print("** Telegram interface :: Can't get updates | Error from _timeout_telegram()")
	return 1
timer_telegram = hexchat.hook_timer(timer_telegram_timeout*1000, _timeout_telegram)
#
def _timeout_telegram_first(userdata):
	global timer_telegram_first
	try:
		telegram_bot_get_bot_info()
	except:
		if bDEBUG: print("** Telegram interface :: Can't get bot info | Error from script call to telegram_bot_get_bot_info()")
		log_print("** Telegram interface :: Can't get bot info | Error from script call to telegram_bot_get_bot_info()")
	hexchat.unhook(timer_telegram_first)
	timer_telegram_first = None
	return 1
timer_telegram_first = hexchat.hook_timer(timer_telegram_timeout_first*1000, _timeout_telegram_first)
#
#---------------------------------------------------------------
# Functions
#---------------------------------------------------------------
def log_print(text):
	for admin in config["telegram_params"]["admins"]:
		telegram_bot_send_message(admin, text, disable_web_page_preview = True)
#
#---------------------------------------------------------------
#
if not send_to_IRC: telegram_bot_get_bot_info()
print("EoF@offset: %s" % telegram_bot_offset)
#EOF
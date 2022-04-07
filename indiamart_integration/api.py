from __future__ import unicode_literals
import frappe
from frappe.utils import today
from frappe import _
import json
import requests

@frappe.whitelist()
def add_source_lead():
	if not frappe.db.exists("Lead Source","India Mart"):
		doc=frappe.get_doc(dict(
			doctype = "Lead Source",
			source_name = "India Mart"
		)).insert(ignore_permissions=True)
		if doc:
			frappe.msgprint(_("Lead Source Added For India Mart"))
	else:
		frappe.msgprint(_("India Mart Lead Source Already Available"))

@frappe.whitelist()
def sync_india_mart_lead(from_date,to_date):
	try:
		india_mart_setting = frappe.get_doc("IndiaMart Setting","IndiaMart Setting")
		if (not india_mart_setting.url
			or not india_mart_setting.mobile_no
			or not india_mart_setting.key):
				frappe.throw(
					msg=_('URL, Mobile, Key mandatory for Indiamart API Call. Please set them and try again.'),
					title=_('Missing Setting Fields')
				)
		req = get_request_url(india_mart_setting)
		res = requests.post(url=req)
		if res.text:
			count = 0
			for row in json.loads(res.text):
				if not row.get("Error_Message")==None:
					frappe.throw(row["Error_Message"])
				else:
					doc = add_lead(row)
					if doc:
						count += 1
			if not count == 0:
				frappe.msgprint(_("{0} Lead Created").format(count))

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("India Mart Sync Error"))

def get_request_url(india_mart_setting):
	req = str(india_mart_setting.url)+str(india_mart_setting.mobile_no)+'/GLUSR_MOBILE_KEY/'+str(india_mart_setting.key)+'/Start_Time/'+str(india_mart_setting.from_date)+'/End_Time/'+str(india_mart_setting.to_date)+'/'
	return req

@frappe.whitelist()
def cron_sync_lead():
	india_mart_setting = frappe.get_doc("IndiaMart Setting","IndiaMart Setting")
	if not india_mart_setting.enabled:
		return
	try:
		sync_india_mart_lead(today(),today())
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("India Mart Sync Error"))

@frappe.whitelist()
def add_lead(lead_data):
	qtype_map = {'P' : 'Indiamart – Call', 'B' : 'Indiamart – Buy Lead', 'W' : 'Indiamart – Direct'}
	try:
		if not frappe.db.exists("Lead",{"india_mart_id":lead_data["QUERY_ID"]}):
			doc = frappe.get_doc(dict(
				# doctype="Lead",
				# title = lead_data['GLUSR_USR_COMPANYNAME'] if lead_data['GLUSR_USR_COMPANYNAME'] else lead_data['SENDERNAME'],
				# lead_name = lead_data["SENDERNAME"],
				# email_id = lead_data["SENDEREMAIL"],
				# mobile_no = lead_data["MOB"][-10:],
				# company_name = lead_data['GLUSR_USR_COMPANYNAME'],
				# address_line1 = lead_data['ENQ_ADDRESS'],
				# city = lead_data['ENQ_CITY'],
				# state = lead_data['ENQ_STATE'],
				# notes = lead_data['ENQ_MESSAGE'] + '\n' + lead_data['PRODUCT_NAME'] + '\n' + lead_data['ENQ_CALL_DURATION'] + '\n' + lead_data['ENQ_RECEIVER_MOB'] + '\n' + lead_data['EMAIL_ALT'] + '\n' + lead_data['QUERY_ID'],
				# phone = lead_data['MOBILE_ALT'],
				# status = 'Lead',
				# source = qtype_map[lead_data["QTYPE"]]
				
				doctype="Lead",
				lead_name=lead_data["SENDERNAME"],
				email_address=lead_data["SENDEREMAIL"],
				phone=lead_data["MOB"][-10:],
				requirement=lead_data["SUBJECT"],
				india_mart_id=lead_data["QUERY_ID"],
				source="India Mart" 
				          
			)).insert(ignore_permissions = True)
			return doc
	except Exception as e:
		frappe.log_error(frappe.get_traceback())




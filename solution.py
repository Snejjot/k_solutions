import datetime
import hashlib
import os
from urllib.parse import urlencode

import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "XYZ")



@app.route("/", methods=["GET"])
def main():
	"""
	Render initial view
	:return: render html template
	"""
	return render_template("main.html")


@app.route("/formpost", methods=["POST"])
def formpost():
	"""
	Receives form in request and provide payment rules on this basis
	:return: http response object
	"""
	if (len(request.form["paymentValue"]) > 1):
		redirectLink = "empty"
		#  Logfile write payment (В ореальном мире этот лог нужно писать еще и при подтверждении оплаты)
		with open("logs.txt", "a") as logFile:
			logFile.write('\n'+str(request.form['currency']) + ',' +
			              str(request.form['paymentValue']) + ',' +
			              str(datetime.datetime.now()) + ',' +
			              str(request.form['description'].strip()) + ',' +
			              str(dataDefault["shop_order_id"])
			              )
		
		try:
			if (request.form["currency"] == "EUR"):
				data = {"amount": str(request.form["paymentValue"]),
				        "currency": currency["EUR"]
				        }
				data.update(dataDefault)
				requestData = requestCreate(data)
				requestData["description"] = request.form["description"].strip()
				return redirect(urls["Pay"]+"?" + urlencode(requestData))
			elif (request.form["currency"] == "USD"):
				data = {"payer_currency": currency["USD"],
				        "shop_amount":str(request.form["paymentValue"]),
				        "shop_currency":currency["USD"],
				        }
				data.update(dataDefault)
				requestData = requestCreate(data)
				response = requests.post(urls["Bill"], json=requestData)
				redirectLink = response.json()["data"]["url"]
			
			elif (request.form["currency"] == "RUB"):
				data = {"amount": str(request.form["paymentValue"]),
				        "currency": currency["RUB"],
				        "payway": "payeer_rub",
				        }
				data.update(dataDefault)
				requestData = requestCreate(data)
				response = requests.post(urls["Invoice"], json=requestData)
				redirectLink = response.json()["data"]["data"]["referer"]
		except Exception as e:
			pass
	else:
		Message = "Сумма к оплате не указана"
		return render_template("main.html", {"Message": Message})
	
	return redirect(redirectLink)


def hashGeneretor(inputString):
	"""
	Create hash from input string sequence
	:param inputString:
	:return: hash
	"""
	return hashlib.sha256(inputString.encode('utf-8')).hexdigest()

def requestCreate(data):
	"""
	Generates a sorted dict for request
	:param data:
	:return: dict with required for request data
	"""
	sorted_string = ""
	requestData = {}
	for key in sorted(data):
		sorted_string = sorted_string + ("" if len(sorted_string) == 0 else ":") + str(data[key])
		requestData[key] = data[key]
	hashingSequence = (sorted_string + secret)
	hash = hashGeneretor(hashingSequence)
	requestData.update({"sign":hash})
	return requestData


dataDefault = {"shop_id": "5",
               # IN REAL LIFE ORDER WILL DIFFER EVERY TIME - I REALIZE IT.
               "shop_order_id": 123465
               }

secret = "SecretKey01"

currency = {"EUR":978, "USD": 840, "RUB": 643}

urls = {"Pay": "https://pay.piastrix.com/ru/pay",
        "Bill": "https://core.piastrix.com/bill/create",
        "Invoice": "https://core.piastrix.com/invoice/create"
        }

keys = {
	"Pay":["amount", "currency","shop_id","shop_order_id"],
	"Bill":["payer_currency", "shop_amount", "shop_currency", "shop_id", "shop_order_id"],
	"Invoice": ["amount","currency","payway","shop_id","shop_order_id"]
}
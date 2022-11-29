from flask import Flask, jsonify, request
import access_secret
import threading

app = Flask(__name__)


@app.route('/fparty', methods=['POST'])
def infra():
    # app.logger.info(request.form)
    request_form = request.form
    response_url = request_form.get('response_url')
    with app.app_context():
        print ("Checking")
        impl = threading.Thread(target=access_secret.token_validation, args=[request_form, response_url])
        impl.start()
        app.logger.info('Started processing in the background')
        response = {
            "response_type": "in_channel",
            "text": f"Hey {request_form['user_name']}! Processing your request, please wait."
        }
        return jsonify(response)

@app.errorhandler(405)
def fourofive(error):
    return "Not authorized"


@app.errorhandler(404)
def fourofour(error):
    return "Not authorized"


if __name__ == "__main__":
    print ("Hello")
    app.run(host='0.0.0.0', port=8080)

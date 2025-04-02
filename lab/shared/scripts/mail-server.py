from flask import Flask, jsonify, request
import os

server = Flask(__name__)

@server.route('/send-email', methods=['POST'])

# Function that creates a vulnerable email server, that returns error messages containing informations about the fields 
# needed to correctly send an email with it and about how the user input is parsed
def send_email():
    sender = request.form.get('sender')
    rec = request.form.get('recipient')
    subj = request.form.get('subject')
    msg = request.form.get('message')

    # Error messages if one of the fields is missing
    if not sender: return jsonify({"error": "Missing field: sender!"}), 400
    if not rec: return jsonify({"error": "Missing field: recipient!"}), 400
    if not subj: return jsonify({"error": "Missing field: subject!"}), 400
    if not msg: return jsonify({"error": "Missing field: message!"}), 400

    cmd = f'echo "{msg}" | mail -s "{subj}" -a "From:{sender}" {rec}'
    try:
        result = os.system(cmd)
        if result != 0:
            return jsonify({"error": f"Failed to send email. Command: {cmd}"}), 500 # error message revealing how the input is parsed
        return jsonify({"success": f"Email sent to {rec}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)
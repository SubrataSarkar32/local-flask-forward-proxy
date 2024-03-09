from flask import Flask, jsonify, request, Response
# from flask_cors import CORS
import requests

app = Flask(__name__)
# CORS(app)

target_url = 'https://pagamesssddr.com'

@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath=''):
    try:
        # Make a request to localhost:11434 with the specified path
        target_url_with_path = f'{target_url}/{subpath}'
        print(request.get_data())
        response = requests.request(
            method=request.method,
            url=target_url_with_path,
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        #region exlcude some keys in :res response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']  # NOTE we here exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref. https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
        headers          = [
                                (k,v) for k,v in response.raw.headers.items()
                                if k.lower() not in excluded_headers
                            ]
        #endregion exlcude some keys in :res response

        # Build the response
        # resp = jsonify(response.json())
        # resp.status_code = response.status_code

        # # Set CORS headers
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        # resp.headers['Access-Control-Allow-Headers'] = '*'
        # return resp
        response1 = Response(response.content, response.status_code, headers)
        return response1

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
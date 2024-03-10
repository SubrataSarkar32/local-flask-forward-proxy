from flask import Flask, jsonify, request, Response
# from flask_cors import CORS
import requests
import re
import httpx
import asyncio
import ssl

app = Flask(__name__)
# CORS(app)

target_url_list = ["pagamesssddr.com", "jellyfin.local"]
# target_url = 'https://pagamesssddr.com'
proxy_url = 'http://localhost:5000'  # Change this to match your proxy server's URL

@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath=''):
    try:
        # # Make a request to localhost:11434 with the specified path
        if proxy_url in subpath:
            subpath = subpath.split(proxy_url)[-1]
        if "/" in subpath:
            if subpath.split("/")[1] not in target_url_list:
                raise ValueError(subpath.split("/")[1]+ " Not allowed by proxy")
            target_url_with_path = f'https:/{subpath}'
        else:
            if not(subpath in target_url_list):
                raise ValueError(subpath + " Not allowed by proxy")
            target_url_with_path = f'https://{subpath}'
        print(request.get_data())
        # response = requests.request(
        #     method=request.method,
        #     url=target_url_with_path,
        #     headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
        #     data=request.get_data(),
        #     cookies=request.cookies,
        #     allow_redirects=False
        # )

        # Forward the request using httpx
        async def forward_request(target_url_with_path):
            async with httpx.AsyncClient(http2=True, verify=False) as client:
                # Forward the incoming request method, URL, headers, and data
                response = await client.request(
                    method=request.method,
                    url=target_url_with_path,
                    headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
                    data=request.get_data(),
                    cookies=request.cookies
                )
                # Return the response from the target server
                return response, response.content, response.status_code, response.headers.items()

        # Run the event loop to execute the forward_request coroutine
        response, content, status_code, headers = asyncio.run(forward_request(target_url_with_path))

        #region exlcude some keys in :res response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']  # NOTE we here exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref. https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
        headers          = [
                                (k,v) for k,v in headers
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
        response1 = Response(content, status_code, headers)
        # Replace occurrences of target_url with proxy_url in the response content
        content_type = response.headers.get('Content-Type', '')
        if (content_type.startswith('text/html') or 
           content_type.startswith('text/css') or 
           content_type.startswith('text/javascript') or 
           content_type.startswith('image/jpeg')):
            response1.data = re.sub(target_url.encode(), proxy_url.encode(), response.content)

        return response1

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
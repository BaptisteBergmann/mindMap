#!/bin/sh
# curl http://127.0.0.1:5000/my-map/is # Should return error
# curl -X POST http://127.0.0.1:5000/ -H 'content-type: application/json' -d '{"id": "my-map"}'
# curl -X POST http://127.0.0.1:5000/my-map -H 'content-type: application/json' -d '{"path": "i/like/saweie", "text": "1"}' # Should return error
# curl -X POST http://127.0.0.1:5000/my-map -H 'content-type: application/json' -d '{"path": "i", "text": "2"}'
# curl -X POST http://127.0.0.1:5000/my-map -H 'content-type: application/json' -d '{"path": "i/like", "text": "33"}'
# curl -X GET http://127.0.0.1:5000/my-map/i/like -H 'content-type: application/json'
curl http://127.0.0.1:5000/my-map/id
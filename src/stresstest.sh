while true; do 
  curl -X POST http://localhost:5000/command \
  -H "Content-Type: application/json" \
  -d '{"command":"login nyxx"}' 
  sleep 1
done
from src.gr_tradinggame.coding.server import GameServer

server = GameServer('<MYNGROKTOKEN>')  # see https://dashboard.ngrok.com/get-started/your-authtoken
server.run()

import logging
import valve.source.a2s
from .models import Server

logger = logging.getLogger(__name__)

SERVER_ADDRESS = ('ip', port)  # Укажите ваш адрес и порт


def update_server_status(sid):
    try:
        logger.info(f"Connecting to server with SID {sid}...")

        with valve.source.a2s.ServerQuerier(SERVER_ADDRESS) as server:
            info = server.info()
            players = server.players()

            logger.info("Server Info: %s", info)
            logger.info("Players List: %s", players)

            player_count = len(players)
            max_players = info['max_players']

            # Проверяем, существует ли сервер с таким SID
            server_obj = Server.objects.get(sid=sid)
            server_obj.players = player_count
            server_obj.max_players = max_players
            server_obj.save()

            logger.info(f"Server {server_obj.name} updated: Players {player_count}/{max_players}")

    except Server.DoesNotExist:
        logger.error(f"Server with SID {sid} not found!")
    except Exception as e:
        logger.error(f"Error updating server status: {e}")

let ws;

class SocketService {

    static init(webscoket) {
        ws = webscoket;
    }

    static sendMessage(message) {
        ws.send(message);
    }
}

module.exports = { SocketService };
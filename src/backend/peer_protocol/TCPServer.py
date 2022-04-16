import asyncio
from asyncio import StreamReader, StreamWriter

class TCPServer:
    PORT_RANGE = range(6880, 6889 + 1)

    def __init__(self):
        self._server = None
        self.port = None


    async def start(self):
        for port in TCPServer.PORT_RANGE:
            try:
                self._server = await asyncio.start_server(self.client_connected, host="0.0.0.0", port=port)
            except Exception as e:
                # TODO log
                print(e)
            else:
                self.port = port
                print('WORKING ON PORT', port)
                break

    async def stop(self):
        if self._server == None:
            return
        
        self._server.close()
        await self._server.wait_closed()
    
    def client_connected(self, reader: StreamReader, writer: StreamWriter):
        print('\033[91m' + 'CLIENT CONNECTED' * 100 + '\033[0m')


if __name__ == '__main__':
    async def run():
        server = TCPServer()
        await server.start()
    
    asyncio.run(run())
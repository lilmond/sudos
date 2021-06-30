import threading
import socket
import socks
import ssl

class Sudos(object):
    def __init__(self, url):
        self.url = url
    
    @staticmethod
    def spliturl(url):
        try:
            url = url.strip()
            
            try:
                protocol, host = url.split("://", 1)
            except ValueError:
                raise Exception("Missing or invalid URL protocol")
            
            try:
                host, path = host.split("/", 1)
            except ValueError:
                path = ""
            
            try:
                host, port = host.split(":", 1)
            except ValueError:
                port = 80
            
            try:
                path, parameters = path.split("?", 1)
            except ValueError:
                parameters = ""
            
            try:
                port = int(port)
            except ValueError:
                raise Exception("Invalid URL port value")
                
            path = f"/{path}"
            parameters = f"{parameters}"
            
            url_dict = {
                "protocol": protocol,
                "host": host,
                "port": port,
                "path": path,
                "parameters": parameters
            }
            
            return url_dict
        except Exception as e:
            raise Exception(e)
            pass
    
    def connect(self, url):
        try:
            url = Sudos.spliturl(url)
        except Exception as e:
            raise Exception(e)
            pass

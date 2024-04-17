import socket


# Получаем локальный IPv4 адрес
def get_ip():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip
    except socket.gaierror as e:
        try:
            # Получаем локальный IPv6 адрес
            local_ip = socket.gethostbyname(socket.gethostname())
            return local_ip
        except socket.gaierror as e:
            return 'Хорошо шифруется'

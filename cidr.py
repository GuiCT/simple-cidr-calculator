import re # Regex

# Pattern utilizado para verificar formato de IP
pattern = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}$")
# Não verifica os valores dos octetos, apenas se o formato em si é válido

# Separa um ip no formato válido em octetos e CIDR
def separate_ip(ip : str):
    octetos = ip.split(".")
    octetos[3], cidr = octetos[3].split("/")
    octetos = [int(oc) for oc in octetos]
    cidr = int(cidr)
    return octetos, cidr

# Escreve um ip no formato válido a partir dos octetos
def group_ip(octets):
    outstr = "{}.{}.{}.{}".format(
            octets[0],
            octets[1],
            octets[2],
            octets[3]
            )
    return outstr

# Escreve ip como um inteiro de 32 bits
def ip_as_binary(octets):
    asbinary = (
            (octets[0] << 24) +
            (octets[1] << 16) +
            (octets[2] << 8) +
            (octets[3])
            )
    return asbinary

def ip_from_binary(ip):
    octets = list([None] * 4)
    octets[0] = ip >> 24
    octets[1] = (ip & 0b00000000111111110000000000000000) >> 16
    octets[2] = (ip & 0b00000000000000001111111100000000) >> 8
    octets[3] = (ip & 0b00000000000000000000000011111111)
    return octets

# Verifica se o input é válido, tanto em formato quanto em valores
def check_ip_address(inputstr : str) -> bool:
    if pattern.match(inputstr):
        values = list([None] * 5) # Inicializando lista
        values[0:4], values[4] = separate_ip(inputstr)
        # Verificando cada valor
        letters = 'wxyz'
        for i in range(4):
            if (values[i] < 0) or (values[i] > 255):
                raise ValueError('O valor de ' + letters[i] + ' não é válido.')
                return False
        # CIDR
        if (values[4] < 1) or (values[4] > 31):
            raise ValueError('O valor de n não é válido.')
            return False
    else:
        raise ValueError('Formato da string não é válido.')
        return False
    return True

# Realiza um prompt pedindo pelo endereço IP, checa se o formato é válido.
def get_ip_address():
    inputstr = input('Insira um endereço IP: ')
    if check_ip_address(inputstr):
        return inputstr

def calculate_from_ip(ip):
    # Separando octetos e CIDR
    octetos, cidr = separate_ip(ip)
    # Escrevendo ip como um inteiro de 32 bits
    ip_binario = ip_as_binary(octetos)
    # Escrevendo máscara de subredes como inteiro de 32 bits
    mascara_sub_rede = '1' * cidr + '0' * (32 - cidr)
    mascara_sub_rede = int(mascara_sub_rede, 2)
    # Endereço de rede
    end_rede = ip_binario & mascara_sub_rede
    # End de broadcast
    end_broadcast = ip_binario | (~mascara_sub_rede)
    # Inicio e fim do range
    range_start = end_rede + 1
    range_end = end_broadcast - 1
    # Retornando cada um dos valores calculados
    return (end_rede, end_broadcast, mascara_sub_rede, range_start, range_end)


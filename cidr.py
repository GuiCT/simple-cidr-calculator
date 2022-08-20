import re  # Regex
from ctypes import c_uint32  # Unsigned int utilizado para garantir
# o funcionamento do bitwise NOT

# Pattern utilizado para verificar formato de IP
pattern = re.compile(
    r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}$")
# Não verifica os valores dos octetos, apenas se o formato em si é válido
# Valor mínimo e máximo do CIDR
CIDR_MIN = 1
CIDR_MAX = 30

# Separa um ip no formato válido em octetos e CIDR


def separate_ip(ip: str) -> tuple[list[int], int]:
    # Separando octetos
    octetos = ip.split(".")
    # Separando último octeto do CIDR
    octetos[3], cidr = octetos[3].split("/")
    # Transformando octetos e CIDR em inteiros
    octetos = [int(oc) for oc in octetos]
    cidr = int(cidr)
    return octetos, cidr

# Escreve um ip no formato válido a partir dos octetos


def group_ip(octets: list[int]) -> str:
    # [192, 168, 0, 1] -> '192.168.0.1'
    outstr = "{}.{}.{}.{}".format(
        octets[0],
        octets[1],
        octets[2],
        octets[3]
    )
    return outstr

# Escreve ip como um inteiro de 32 bits


def ip_as_binary(octets: list[int]) -> int:
    # [192, 168, 0, 1] -> 11000000101010000000000000000001
    asbinary = (
        (octets[0] << 24) +
        (octets[1] << 16) +
        (octets[2] << 8) +
        (octets[3])
    )
    return asbinary


def ip_from_binary(ip: int) -> list[int]:
    # 11000000101010000000000000000001 -> [192, 168, 0, 1]
    octets = list([None] * 4)
    octets[0] = ip >> 24
    octets[1] = (ip & 0b00000000111111110000000000000000) >> 16
    octets[2] = (ip & 0b00000000000000001111111100000000) >> 8
    octets[3] = (ip & 0b00000000000000000000000011111111)
    return octets

# Verifica se o input é válido, tanto em formato quanto em valores


def check_ip_address(inputstr: str) -> bool:
    if pattern.match(inputstr):
        values = list([None] * 5)  # Inicializando lista
        values[0:4], values[4] = separate_ip(inputstr)
        # Verificando cada valor
        letters = 'wxyz'
        for i in range(4):
            if (values[i] < 0) or (values[i] > 255):
                raise ValueError(
                    'O valor de ' + letters[i] + ' deve estar entre 0 e 255')
        # CIDR
        if (values[4] < CIDR_MIN) or (values[4] > CIDR_MAX):
            raise ValueError('O valor de n deve estar entre 1 e 30')
    else:
        raise ValueError('Formato da string não é válido.')
    return True

# Realiza um prompt pedindo pelo endereço IP, checa se o formato é válido.


def get_ip_address() -> str:
    inputstr = input('Insira um endereço IP (w.x.y.z/n): ')
    if check_ip_address(inputstr):
        return inputstr


def calculate_from_ip(ip: str) -> dict:
    # Variável de retorno, dicionário contendo os valores calculados
    ret = dict()
    # Separando octetos e CIDR
    octetos, cidr = separate_ip(ip)
    # Escrevendo ip como um inteiro de 32 bits
    ip_binario = ip_as_binary(octetos)
    # Escrevendo máscara de subredes como inteiro de 32 bits
    mascara_sub_rede = '1' * cidr + '0' * (32 - cidr)  # Escreve como string
    ret['mascara_sub_rede'] = int(mascara_sub_rede, 2)  # Realiza parse
    ret['mascara_wildcard'] = c_uint32(
        ~ret['mascara_sub_rede']).value  # Bitwise NOT na
    # máscara de sub-rede retorna a máscara wildcard.
    # Endereço de rede
    ret['end_rede'] = ip_binario & ret['mascara_sub_rede']
    # End de broadcast
    ret['end_broadcast'] = ip_binario | ret['mascara_wildcard']
    # Inicio e fim do range
    ret['range'] = dict()
    ret['range']['start'] = ret['end_rede'] + 1
    ret['range']['end'] = ret['end_broadcast'] - 1
    # Quantidade de hosts disponíveis
    ret['qnt_hosts'] = 2**(32 - cidr) - 2
    return ret


while True:
    try:
        inputstr = get_ip_address()
        infos = calculate_from_ip(inputstr)
        print(
            f'''Valor inserido: {inputstr}
================================================================================
Endereço de rede: {group_ip(ip_from_binary(infos['end_rede']))}
Endereço de broadcast: {group_ip(ip_from_binary(infos['end_broadcast']))}
Máscara de sub-rede: {group_ip(ip_from_binary(infos['mascara_sub_rede']))}
Máscara de wildcard: {group_ip(ip_from_binary(infos['mascara_wildcard']))}
Range: {group_ip(ip_from_binary(infos['range']['start']))} - {group_ip(ip_from_binary(infos['range']['end']))}
Quantidade de hosts disponíveis: {infos['qnt_hosts']}
================================================================================
''')
    except ValueError as e:
        print('IP inserido é inválido: ' + str(e))
    except KeyboardInterrupt:
        print('\nVolte sempre :)')
        quit()

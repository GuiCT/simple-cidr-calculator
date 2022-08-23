# Atividade 3 - Cálculo de Endereço IPV4
# Disciplina: Redes de Computadores I
# Aluno: Guilherme Cesar Tomiasi

import re  # Regex
from ctypes import c_uint32  # Unsigned int utilizado para garantir
# o funcionamento do bitwise NOT

# Pattern utilizado para verificar formato de IP
pattern = re.compile(
    r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}$")
# Não verifica os valores dos octetos, apenas se o formato em si é válido

# Valor mínimo e máximo do CIDR
CIDR_MIN = 0
CIDR_MAX = 32

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
    # Realizando bit shift em cada octeto para assumirem as posições
    # desejadas. Após isso, todos eles são somados para obter o valor
    # final em binário (representado como inteiro pelo Python).
    return asbinary


def ip_from_binary(ip: int) -> list[int]:
    # 11000000101010000000000000000001 -> [192, 168, 0, 1]
    octets = list([None] * 4)
    # Realizando bit shift para a direita para obter o valor
    # de cada octeto separadamente. Também é necessário aplicar uma
    # máscara AND para cada um deles.
    octets[0] = ip >> 24
    octets[1] = (ip & 0b00000000111111110000000000000000) >> 16
    octets[2] = (ip & 0b00000000000000001111111100000000) >> 8
    octets[3] = (ip & 0b00000000000000000000000011111111)
    return octets

# Verifica se o input é válido, tanto em formato quanto em valores


def check_ip_address(inputstr: str) -> bool:
    # Verifica se a string obedece ao Regex definido no início do script
    if pattern.match(inputstr):
        values = list([None] * 5)  # Inicializando lista
        # Recebendo octetos e CIDR
        values[0:4], values[4] = separate_ip(inputstr)
        # Verificando cada valor
        letters = 'wxyz'
        for i in range(4):
            # Se octeto não está no intervalo correto, um erro é lançado
            if (values[i] < 0) or (values[i] > 255):
                raise ValueError(
                    'O valor de ' + letters[i] + ' deve estar entre 0 e 255')
        # CIDR, se não estiver no intervalo correto, um erro é lançado
        if (values[4] < CIDR_MIN) or (values[4] > CIDR_MAX):
            raise ValueError(f'O valor de n deve estar entre {CIDR_MIN} e {CIDR_MAX}')
    # Caso a string não obedecer ao Regex, o formato da mesma é inválido
    else:
        raise ValueError('Formato da string não é válido.')
    # Caso não ocorrer nenhum erro, tudo ocorreu bem
    return True

# Realiza um prompt pedindo pelo endereço IP, checa se o formato é válido.


def get_ip_address() -> str:
    # Input sem checagem
    inputstr = input('Insira um endereço IP (w.x.y.z/n): ')
    # Verifica se é válido, caso sim é retornado
    if check_ip_address(inputstr):
        return inputstr


# Obtendo os valores desejados (endereço de rede, broadcast,  ...) a partir
# de uma string contendo o endereço IP e o CIDR


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
    # Aqui é necessário utilizar c_uint32 pois o bitwise NOT retorna o complemento
    # de 2 do valor inteiro, caso não utilizado um valor unsigned.
    # Endereço de rede
    ret['end_rede'] = ip_binario & ret['mascara_sub_rede']
    # End de broadcast
    ret['end_broadcast'] = ip_binario | ret['mascara_wildcard']
    # Inicio e fim do range
    # Se o CIDR for 31 ou 32, o range é ignorado, visto que não há hosts válidos
    if cidr < 31:
        ret['range'] = dict()
        ret['range']['start'] = ret['end_rede'] + 1
        ret['range']['end'] = ret['end_broadcast'] - 1
    # Quantidade de hosts disponíveis
    ret['qnt_hosts'] = max(2**(32 - cidr) - 2, 0)  # Não pode ser negativo
    return ret


# Função composta que transforma IP armazenado em um inteiro de 32 bits
# em um IP formatado como string, utiliza duas funções apresentadas anteriormente.
def ip_int_to_str(ip): return group_ip(ip_from_binary(ip))


while True:
    # Bloco try...except verifica se o formato inserido é válido
    try:
        # Obtém IP e valida
        inputstr = get_ip_address()
        # Obtém informações a partir do valor inserido
        infos = calculate_from_ip(inputstr)
        # Imprime informações na tela
        print(
            f'''Valor inserido: {inputstr}
================================================================================
Endereço de rede: {ip_int_to_str(infos['end_rede'])}
Endereço de broadcast: {ip_int_to_str(infos['end_broadcast'])}
Máscara de sub-rede: {ip_int_to_str(infos['mascara_sub_rede'])}
Máscara de wildcard: {ip_int_to_str(infos['mascara_wildcard'])}
Quantidade de hosts disponíveis: {infos['qnt_hosts']}''')
        # Verifica se há range, se sim, é impresso
        if 'range' in infos:
            print(
                f'''Range: {ip_int_to_str(infos['range']['start'])} - {ip_int_to_str(infos['range']['end'])}''')
        # Fim do print
        print('================================================================================')
    # Caso haja algum problema com o input, o mesmo é impresso na tela
    except ValueError as e:
        print('IP inserido é inválido: ' + str(e))
    # Fim do script
    except KeyboardInterrupt:
        print('\nVolte sempre :)')
        quit()

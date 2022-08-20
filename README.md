# IP CIDR Calculator

Calcula informações de um determinado IP com valor da máscara CIDR (1 - 30)

# Input

O formato inserido deve obedecer ao padrão: 'w.x.y.z/n', com:
- w,x,y,z entre 0 e 255
- n entre 1 e 30

# Output

O script calcula:
- IP de Rede
- IP de Broadcast
- Máscara de sub-rede
- Máscara de wildcard
- Range[início] - Range[fim]
- Quantidade de hosts disponíveis na sub-rede em questão 

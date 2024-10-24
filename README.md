# Sistema centralizado de comunicação com sensores IoT

## Trabalho de Sistemas Distribuídos 
### Allan Toledo & João Padilha

Desenvolvimento de um sistema de comunicação em tempo real com sensores.

Funcionamento:
Os clientes criam uma conexão TCP/IP com o servidor na porta 8001.
O servidor adiciona a conexão do cliente na lista de conexões.

Os sensores utilizam protocolo UDP e enviam dados para o servidor.
Quando o servidor recebe os dados de um sensor, ele percorre a lista de clientes enviando para multiplos clientes.

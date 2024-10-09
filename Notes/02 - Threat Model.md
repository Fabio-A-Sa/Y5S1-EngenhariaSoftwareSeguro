# Threat Model

## Concepts

- `Vulnerability`: falhas que podem resultar em danos;
- `Threats`: potencial violação de segurança de um recurso ou conjunto de recursos; 
- `Exploitation`: utilização das vulnerabilidades para alterar as propriedades de segurança CIA num sistema;
- `Attack`: exploração da vulnerabilidade;
- `Contermeasure`: prevenção, deteção ou minimização do risco;

## TM Steps

- `Vision`: caracterização do sistema em cenários, requisitos, comportamentos esperados;
- `Diagram`: representação do sistema em modelo UML ou DFG (data flow diagram);
- `Identify Threads`: externas às *trust boundaries*, using STRIDE methodology;
- `Mitigate`: 
- `Validate`: 

## STRIDE

- `S`poofing - fazer-se passar por outra entidade;
- `T`ampering - modificação de dados ou código;
- `R`epudiation - impedir alguém que diga que não fez determinada ação;
- `I`nformation disclosure - expor informação a alguém que não estava autorizada a vê-la;
- `D`enial of Service - degradação dos serviços para os utilizadores finais;
- `E`levation of privilege - ganhar capacidades no sistema sem autorização para tal;


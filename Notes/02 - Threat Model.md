# Threat Model

## Concepts

- `Vulnerability`: falhas que podem resultar em danos;
- `Threats`: potencial violação de segurança de um recurso ou conjunto de recursos; 
- `Exploitation`: utilização das vulnerabilidades para alterar as propriedades de segurança CIA num sistema;
- `Attack`: exploração da vulnerabilidade;
- `Contermeasure`: prevenção, deteção ou minimização do risco;

## Threat Modeling Steps

- `Vision`: caracterização do sistema em cenários, requisitos, comportamentos esperados;
- `Diagram`: representação do sistema em modelo UML ou DFG (data flow diagram);
- `Identify Threads`: externas às *trust boundaries*, using STRIDE methodology;
- `Mitigate`: Analisando por exemplo as attack trees (é a threat decomposta por sectores e elementos);
- `Validate`: Verificar se todas as possíveis threats foram cobertas e analisadas;

## STRIDE

- `S`poofing - fazer-se passar por outra entidade;
- `T`ampering - modificação de dados ou código;
- `R`epudiation - impedir alguém que diga que não fez determinada ação;
- `I`nformation disclosure - expor informação a alguém que não estava autorizada a vê-la;
- `D`enial of Service - degradação dos serviços para os utilizadores finais;
- `E`levation of privilege - ganhar capacidades no sistema sem autorização para tal;

STRIDE deve ser aplicado a todos os elementos do diagrama resultante do procesos de Threat Model.

## DREAD Evaluation

DREAD é uma framework usada para avaliar o risco de um potencial ataque:

- Damage
- Reproducibility
- Exploitability
- Affected Users
- Discoverability
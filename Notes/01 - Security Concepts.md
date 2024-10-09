# Security Concepts

## Computer Security

A proteção usada para automatizar sistemas de modo a preservar o **CIA**:

- `Confidentiality`: a informação não é percebida por entidades não autorizadas;
- `Integrity`: a informação é só modificada por pessoas autorizadas;
- `Availability`: o sistema funciona adequadamente e o serviço está presente para pessoas autorizadas;

Além disso, são importantes os conceitos:

- `Authenticity`: propriedade de ser genuíno, verificado e confiável;
- `Accountability`: o sistema mantém logs de todas as atividades para futura análise;
- `Policy`: descrição do que é ou não permitido;
- `Mechanism`: procedimento para forçar a policy a ser cumprida;
- `Attack tree`: branching hierárquica que representa um conjunto de potenciais vulnerabilidades;

## Fundamental Security Design Principles

Só alguns de vários exemplos:

- Economu of Mechanisms / Keep it Simple;
- Fail-safe default;
- Zero Trust;
- Opening design;
- Design by contract;
- Separation Privileges;
- Least Privilege;
- Isolation;
- Encapsulation;
- Modularity;
- Layering / Defense in depth;

## Lack of security impacts

- `High`: catastrófico com efeito adverso para as operações, assets e indivíduos;
- `Moderate`: efeito sério com degradação;
- `Low`: efeito limitado, apenas alguma degradação ou perda;

## Network Attacks

### Passive

Por exemplo o `eavesdropping`, que não afecta os assets na rede mas consegue:

- Analisar o tráfego na rede;
- Encontrar e explorar as mensagens trocadas;
- É difícil de detectar porque não há alteração dos dados;
- Pode ser prevenido usando encriptação;

### Active

Exemplos de ataques ativos (que modificam assets) na rede:

- `Replay`: retransmissão para tentar um efeito não autorizado;
- `Masquerade`: tenta  uma entidade diferente no canal de comunicação;
- `Modification of messages`;
- `Denial of service`: inibir a utilização normal do serviço;


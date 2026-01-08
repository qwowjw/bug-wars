# Ant Simulator - Arquitetura

Este projeto segue uma arquitetura modular com foco em testabilidade, manutenção e escalabilidade.

- core: engine e gerenciamento de cenas
- entities: modelos de domínio (Ant, Nest, Colony)
- systems: lógica do jogo (movimento, seleção, animação)
- rendering: renderizadores de sprites e UI
- input: abstração de eventos
- utils: utilitários reaproveitáveis
- config: configurações globais

Cada módulo possui responsabilidades bem definidas e pode ser testado isoladamente.

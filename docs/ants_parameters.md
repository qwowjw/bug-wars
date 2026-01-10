# Parâmetros e Tipos de Formigas

Este documento descreve os parâmetros a serem usados para implementar comportamento e combate das formigas, seguido por descrições das espécies e inimigos mencionados.

## Parâmetros essenciais (para implementar agora)

- **Armadura**: reduz a penetração de dano físico; valor numérico que subtrai do dano recebido antes da aplicação de modificadores.
- **Resistência a veneno**: reduz dano contínuo (DoT) e chance/eficácia de efeitos químicos.
- **Alcance**: distância de ataque (melee pequena, alcance para picadas/injeções).
- **Dano por segundo (DPS)**: saída média de dano por segundo; para ataques com DoT separar dano inicial e dano ao longo do tempo.
- **Efeito especial**: tipo de efeito aplicado (ex.: imobilização, desmembramento, queimadura, envenenamento) e duração.
- **Agressividade**: probabilidade de iniciar combate ao detectar inimigo (valor 0-1).
- **Tempo de produção**: tempo em segundos/unidades para produzir uma unidade dessa formiga na colônia.
- **Velocidade**: velocidade de movimento em unidades/segundo.
- **Chance de crítico**: probabilidade de causar dano aumentado em um ataque (valor 0-1) e multiplicador de crítico.

## Como usar esses parâmetros

- Cada formiga deve expor um dicionário/struct com os campos acima.
- Ataques químicos devem testar primeiro *Penetração de Armadura* vs *Armadura* para dano físico, e aplicar *Resistência a veneno* para DoT/efeitos químicos.
- *Efeito especial* deve incluir: tipo, chance de aplicação, duração e intensidade.

## Espécies / Unidades (descrições)

### Formigas potes de mel
- **Função**: unidades de armazenamento/recursos vivas.
- **Características**: abdômen distendido que aumenta capacidade de carga; mobilidade reduzida quando cheias.
- **Parâmetros relevantes**: alta capacidade de carga (meta), baixa velocidade, tempo de produção médio, baixa agressividade.

### Formigas cortadeiras quénquén
- **Função**: coletoras e com casta militar (soldados e operárias).
- **Características**: 4 pares de espinhos nas costas; soldados maiores que operárias.
- **Comportamento de ataque**: soldados mordem na cabeça (alto dano único), operárias seguram patas (reduzem mobilidade inimiga — efeito de imobilização curta).
- **Parâmetros relevantes**: soldados: alta armadura relativa, maior DPS e tamanho, menor velocidade; operárias: chance de aplicar imobilização, maior velocidade e capacidade de corte/coleta.

### Formigas faraó
- **Função**: pequenas e numerosas; infiltração e dano localizado.
- **Características**: 1,5–2 mm, cor amarela/marrom claro; ferrão (podem picar), dois nós na cintura, peças bucais fortes.
- **Comportamento de ataque**: ataques em massa com picadas; dano baixo por unidade, mas em grupo podem causar DoT por injeção química.
- **Parâmetros relevantes**: baixa armadura, alta furtividade/detecção baixa, alta agressividade quando ameaçadas, tempo de produção baixo.

## Inimigas independentes

### Formigas de correição
- **Função**: predadoras nômades que atacam em grupos.
- **Características**: não vivem em formigueiros, super numerosas, dominam por número; atacam picando.
- **Comportamento**: bônus quando em terreno aberto e quando em grande número; penalidade quando isoladas.
- **Parâmetros relevantes**: alta mobilidade, baixo DPS individual, bônus de sinergia de enxame (futuro), chance média de aplicar veneno/DoT.

### Formigas argentinas
- **Função**: invasoras agressivas com recrutamento rápido.
- **Características**: extremamente agressivas e numerosas; injetam produtos químicos; podem desmembrar inimigos.
- **Comportamento**: recrutamento rápido (reduz tempo de produção por reforço), alta agressividade, chance elevada de efeitos graves (desmembramento).
- **Parâmetros relevantes**: baixa/média armadura, alta agressividade, alto número por produção, efeito químico com chance de desmembramento.

### Formigas de fogo (vermelhas)
- **Função**: unidades ofensivas com ferrões venenosos e efeito de queimadura.
- **Características**: maiores que as argentinas (≈2x), ferrões com veneno; dano de queima persistente e efeito de área.
- **Comportamento**: ataques causam DoT de queimadura; ataque em área (AOE) com alcance ligeiramente maior.
- **Parâmetros relevantes**: DPS com componente inicial + DoT, chances de aplicar queimadura, área de efeito, maior armadura/força que argentinas.

## Observações sobre mecânicas de combate

- **Penetração de armadura vs Armadura**: ataques físicos calculam dano efetivo = max(0, dano - (armadura - penetração)). Produtos químicos ignoram parcialmente a armadura conforme parâmetro de penetração química.
- **DoT**: implementar como instâncias que aplicam dano por tick, afetadas por resistência a veneno/químicos.
- **Efeitos especiais**: devem expirar por duração e poder ter interações (ex.: imobilização reduz velocidade, desmembramento reduz DPS e velocidade de ataque).

## Ideias / Parâmetros futuros (documentar e planejar)

- **Inteligência de enxame**: bônus de combate quando unidades amigas estiverem próximas (stacking ou diminishing returns).
- **Sinergia de casta**: bônus específicos quando soldados e operárias agem coordenadas.
- **Moral / coesão**: resistência a fugir/dispersionar sob dano massivo.
- **Detecção**: raio de percepção, com modificadores de terreno/iluminação.
- **Custo de recursos**: custo em alimento/material para produzir cada tipo de unidade.
- **Capacidade de carga**: quanto cada unidade pode carregar (relevante para coletoras e potes de mel).
- **Consumo de alimento**: manutenção periódica por unidade para simular economia da colônia.

## Mapeamento rápido para implementação (exemplo de struct)

```
AntType {
  name: string,
  armor: float,
  poison_resistance: float,
  range: float,
  dps: float,
  special_effect: {type, chance, duration, intensity},
  aggressiveness: float,
  production_time: float,
  speed: float,
  crit_chance: float,
  crit_multiplier: float
}
```

---

Arquivo criado para orientar implementação e futuras extensões. Atualize conforme balanceamento e novas mecânicas.

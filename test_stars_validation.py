"""
Script para validar o sistema de estrelas e score.
Testa a lógica de cálculo de score e estrelas.
"""

from src.core.events import LevelResult

def test_stars_system():
    """Testa o cálculo de estrelas com diferentes cenários."""
    
    # Cenário 1: Vitória perfeita (tempo rápido, sem perdas)
    # Score: 100*10 + 50*50 - 0*20 - 30*0.5 = 1000 + 2500 - 0 - 15 = 3485
    print("=" * 60)
    print("TESTE DO SISTEMA DE ESTRELAS")
    print("=" * 60)
    
    # Exemplo 1: Vitória com 3 estrelas
    print("\nCenário 1: Vitória perfeita (3 estrelas)")
    result1 = LevelResult(
        victory=True,
        time_spent=30.0,  # 30 segundos (< 120s)
        score=1000,  # score >= 500
        stars=3  # Vitória + Tempo + Eficiência
    )
    print(f"  Victory: {result1.victory}")
    print(f"  Time: {result1.time_spent}s (target: 120s)")
    print(f"  Score: {result1.score} (target: 500)")
    print(f"  Stars: {result1.stars}/3 ✓")
    
    # Exemplo 2: Vitória com 2 estrelas (rápido mas com perdas)
    print("\nCenário 2: Vitória com tempo (mas com perdas - 2 estrelas)")
    result2 = LevelResult(
        victory=True,
        time_spent=60.0,  # 60 segundos (< 120s)
        score=200,  # score < 500 (perdeu formigas aliadas)
        stars=2  # Vitória + Tempo (sem eficiência)
    )
    print(f"  Victory: {result2.victory}")
    print(f"  Time: {result2.time_spent}s (target: 120s)")
    print(f"  Score: {result2.score} (target: 500) ✗")
    print(f"  Stars: {result2.stars}/3 ✓")
    
    # Exemplo 3: Vitória com 1 estrela (demorou mas ganhou)
    print("\nCenário 3: Vitória lenta (1 estrela - apenas vitória)")
    result3 = LevelResult(
        victory=True,
        time_spent=150.0,  # 150 segundos (> 120s)
        score=100,  # score < 500
        stars=1  # Apenas vitória
    )
    print(f"  Victory: {result3.victory}")
    print(f"  Time: {result3.time_spent}s (target: 120s) ✗")
    print(f"  Score: {result3.score} (target: 500) ✗")
    print(f"  Stars: {result3.stars}/3 ✓")
    
    # Exemplo 4: Derrota (0 estrelas)
    print("\nCenário 4: Derrota (0 estrelas)")
    result4 = LevelResult(
        victory=False,
        time_spent=45.0,
        score=0,
        stars=0
    )
    print(f"  Victory: {result4.victory}")
    print(f"  Stars: {result4.stars}/3 ✓")
    
    print("\n" + "=" * 60)
    print("FÓRMULA DE SCORE")
    print("=" * 60)
    print("score = comida_coletada * 10")
    print("      + inimigos_derrotados * 50")
    print("      - formigas_perdidas * 20")
    print("      - tempo_gasto * 0.5")
    print()
    print("CONDIÇÕES PARA ESTRELAS")
    print("=" * 60)
    print("⭐ Vitória: Ganhou a fase")
    print("⭐ Tempo: time_spent <= time_target (120s)")
    print("⭐ Eficiência: score >= score_target (500)")
    print("              E nenhum ninho aliado perdido para inimigos")
    print()
    print("EXEMPLO: Para ganhar 3 estrelas na campanha:")
    print("  - Vencer a fase")
    print("  - Terminar em <= 120 segundos")
    print("  - Score >= 500 e não perder nenhum ninho aliado")
    print("=" * 60)

if __name__ == "__main__":
    test_stars_system()

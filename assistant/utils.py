import os
from openai import OpenAI
from dashboard.utils import get_user_dashboard_data

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_ai_prompt(user):
    """
    Gera o texto (prompt) que será enviado à IA com base nos dados do dashboard.
    Inclui contexto sobre foco, hábitos digitais e impacto ambiental.
    """
    data = get_user_dashboard_data(user)

    prompt = f"""
    Você é o assistente FocusGreen 🌿 — um guia de bem-estar digital e sustentabilidade.
    Sua missão é analisar os hábitos digitais do usuário e transformar dados em conselhos inspiradores,
    mostrando o impacto ambiental do tempo de tela e incentivando o uso mais consciente da tecnologia.

    🔹 Dados reais do usuário:
    - Data: {data['today']}
    - Tempo total de uso hoje: {data['daily']['total']} minutos
    - Tempo produtivo: {data['daily']['prod']} minutos
    - Tempo não produtivo (avaliado para impacto ambiental): {data['daily']['nao_prod']} minutos
    - Média diária de uso na semana: {data['weekly']['avg_daily']} minutos
    - Tendência de foco: {data['trend']['trend_label']} ({data['trend']['focus_change_pct']}%)
    - Dias consecutivos dentro da meta de foco: {data['meta']['streak']}
    - Meta diária de minutos não produtivos: {data['meta']['goal_nao_prod']} min
    - CO₂ digital diário estimado: {data['daily']['co2']} g
    - CO₂ digital semanal estimado: {data['weekly']['co2']} g

    🔸 O que você deve gerar:
    Crie um insight educativo, com até 5 frases, contendo:
    1. Um resumo do desempenho **do dia e da semana**, com comparações simples ("melhor que ontem", "um pouco acima da média", etc.).
    2. Uma **dica prática e personalizada** para melhorar o equilíbrio digital (ex: pausas conscientes, blocos de foco, reduzir apps não produtivos).
    3. Uma **curiosidade ecológica realista** que traduza o CO₂ emitido pelo tempo não produtivo em algo tangível, como:
    - energia para acender uma lâmpada por alguns minutos,
    - número de recargas de celular,
    - percurso curto de carro, etc.
    (Você pode criar comparações educativas e simbólicas — sem precisar ser exata, mas plausível).
    4. Um **incentivo positivo e encorajador**, destacando progresso, consistência ou o valor de pequenas melhorias.

    🔹 Regras de tom e estilo:
    - Use uma linguagem natural, motivadora e leve — pareça um mentor amigo, não um relatório.
    - Adicione emojis para tornar o texto mais imersivo ao insight
    - Evite listas, números exatos demais e formatações técnicas.
    - Nunca critique: se o dia foi ruim, transforme em oportunidade de aprendizado.
    - Mostre o impacto do tempo não produtivo, mas sem culpa, focando em consciência e ação.
    - Mantenha o texto contínuo, com fluidez e emoção.
    """


    return prompt.strip()


def get_ai_insight(user):
    """
    Envia o prompt para a API da OpenAI e retorna o texto de resposta.
    """
    prompt = build_ai_prompt(user)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um coach digital chamado FocusGreen 🌿 que incentiva hábitos sustentáveis e foco equilibrado."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=180
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Erro ao gerar insight da IA:", e)
        return "Não foi possível gerar o insight da IA no momento. Tente novamente mais tarde 🌱."

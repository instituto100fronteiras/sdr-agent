
"""
Templates de mensagem para o SDR Agent.
Placeholders disponíveis: {nome}, {empresa}, {setor}
"""

TEMPLATES = {
    "A": (
        "Olá {nome}, tudo bem?\n\n"
        "Sou o Ivair, consultor da Revista 100fronteiras aqui na Tríplice Fronteira. "
        "Estou entrando em contato pois vi o destaque da {empresa} no setor de {setor} "
        "e acredito que temos uma oportunidade de visibilidade interessante para vocês.\n\n"
        "Você teria um minuto para eu te explicar como podemos destacar a {empresa} na região?"
    ),
    "B": (
        "Oi {nome}, como vai?\n\n"
        "Acompanho o trabalho da {empresa} em {setor} e vejo muita sinergia com o público "
        "de leitores da 100fronteiras (Brasil, Paraguai e Argentina).\n\n"
        "Gostaria de compartilhar uma ideia para posicionar ainda mais sua marca na fronteira. "
        "Podemos conversar rapidamente?"
    ),
    "C": (
        "Olá {nome}, boa tarde!\n\n"
        "Ivair aqui da 100fronteiras. Estava analisando o mercado de {setor} e a "
        "{empresa} me chamou atenção.\n\n"
        "Estamos com um projeto especial para empresas líderes do seu segmento. "
        "Faz sentido conversarmos sobre como atrair mais clientes qualificados?"
    )
}

def get_template(template_id: str) -> str:
    """Retorna o template pelo ID (A, B, ou C)."""
    return TEMPLATES.get(template_id.upper())

def format_message(template_id: str, nome: str, empresa: str, setor: str) -> str:
    """Preenche o template com os dados do lead."""
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template '{template_id}' não encontrado.")
    
    return template.format(
        nome=nome,
        empresa=empresa,
        setor=setor
    )

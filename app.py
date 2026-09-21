from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Portais por Unidade da Federação (UF)
#
# "confianca" indica o quanto o link foi checado:
#   - "verificado": conferido com o conteúdo real da página (não é só um chute
#     de URL baseado em busca) e a página bate com o serviço esperado.
#   - "inferido": encontrado em busca / fonte confiável (domínio oficial
#     .jus.br ou instituto de protesto), mas o conteúdo específico da página
#     não pôde ser confirmado ao vivo (bloqueio anti-robô, site fora do ar no
#     momento da checagem, etc). Vale a pena conferir manualmente antes de
#     usar em produção com clientes.
#   - "nao_encontrado": não achei um portal oficial confiável. Nesse caso o
#     app não mostra um link "chutado" — mostra um botão de busca no Google.
# Última checagem: 2026-09-21.
# ---------------------------------------------------------------------------

UFS = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
]

# Certidão Distribuidor Cível Estadual (1ª instância) — portal do TJ de cada UF
TJ_ESTADUAL = {
    "AC": {"link": "https://certidoes.tjac.jus.br/", "confianca": "verificado"},
    "AL": {"link": "https://www2.tjal.jus.br/esaj/portal.do?servico=820100", "confianca": "inferido"},
    "AP": {"link": None, "confianca": "nao_encontrado", "nota": "Sistema é o 'Tucujuris' do TJAP, mas não consegui confirmar a URL exata do formulário."},
    "AM": {"link": "https://www.tjam.jus.br/index.php/serv-certidoes", "confianca": "verificado"},
    "BA": {"link": "https://portalcertidoes.tjba.jus.br/#/primeirograu", "confianca": "verificado"},
    "CE": {"link": "https://sirece.tjce.jus.br/sirece-web/nova/solicitacao.jsf", "confianca": "verificado"},
    "DF": {"link": "https://www.tjdft.jus.br/carta-de-servicos/servicos/certidoes/emitir-nada-consta", "confianca": "verificado"},
    "ES": {"link": "https://sistemas.tjes.jus.br/certidaonegativa/sistemas/certidao/CERTIDAOPESQUISA.cfm", "confianca": "inferido"},
    "GO": {"link": "https://projudi.tjgo.jus.br/CertidaoNegativaPositivaPublica", "confianca": "verificado"},
    "MA": {"link": "https://www.tjma.jus.br/midia/pje/pagina/hotsite/503530/certidoes", "confianca": "inferido"},
    "MT": {"link": "https://sec.tjmt.jus.br/emitir-certidao-de-primeiro-grau", "confianca": "inferido"},
    "MS": {"link": "https://www5.tjms.jus.br/servicos/certidoes/", "confianca": "inferido"},
    "MG": {"link": "https://www.tjmg.jus.br/portal-tjmg/processos/certidao-judicial/", "confianca": "inferido"},
    "PA": {"link": "https://portal-certidao.tjpa.jus.br/", "confianca": "inferido"},
    "PB": {"link": "https://app.tjpb.jus.br/certo/paginas/publico/areaPublica.jsf", "confianca": "verificado"},
    "PR": {"link": "https://www.tjpr.jus.br/certidao-de-1-grau", "confianca": "verificado"},
    "PE": {"link": "https://certidoesunificadas.app.tjpe.jus.br/", "confianca": "verificado"},
    "PI": {"link": None, "confianca": "nao_encontrado", "nota": "O link encontrado parecia ser de certidão de 2ª instância, não do distribuidor de 1ª instância."},
    "RJ": {"link": "https://www3.tjrj.jus.br/CJE/certidao/judicial/", "confianca": "verificado"},
    "RN": {"link": None, "confianca": "nao_encontrado", "nota": "O TJRN descontinuou a emissão pelo site: hoje é feita pelo aplicativo oficial 'Justiç@RN'."},
    "RS": {"link": "https://www.tjrs.jus.br/novo/processos-e-servicos/servicos-processuais/emissao-de-antecedentes-e-certidoes/", "confianca": "inferido"},
    "RO": {"link": "https://www.tjro.jus.br/certidao-unificada/certidaoPublicaEmitir", "confianca": "inferido"},
    "RR": {"link": "https://balcaovirtual.tjrr.jus.br/servicos", "confianca": "inferido"},
    "SC": {"link": "https://www.tjsc.jus.br/web/judicial/certidoes-de-primeiro-grau-comarcas", "confianca": "verificado"},
    "SP": {"link": "https://esaj.tjsp.jus.br/sco/abrirCadastro.do", "confianca": "verificado"},
    "SE": {"link": "https://certidao-online.tjse.jus.br/app/solicitacao/", "confianca": "verificado"},
    "TO": {"link": "https://app.tjto.jus.br/certidao/Home/Inicio", "confianca": "verificado"},
}

# Certidão de Protesto — central estadual (quando existe uma unificada)
PROTESTO_ESTADUAL = {
    "AC": {"link": None, "confianca": "nao_encontrado"},
    "AL": {"link": None, "confianca": "nao_encontrado"},
    "AP": {"link": None, "confianca": "nao_encontrado"},
    "AM": {"link": "https://cartoriosdeprotestoam.org.br/", "confianca": "verificado"},
    "BA": {"link": "https://protestoba.com.br/", "confianca": "inferido"},
    "CE": {"link": "https://site.ieptbce.com.br/protesto/", "confianca": "inferido", "nota": "Página parece direcionar aos cartórios individuais, sem emissão unificada online."},
    "DF": {"link": "https://cartoriosdeprotestodf.com.br/solicitar-certidao/", "confianca": "verificado"},
    "ES": {"link": None, "confianca": "nao_encontrado"},
    "GO": {"link": "https://www.cartoriosdeprotestogo.com.br/", "confianca": "verificado", "nota": "O próprio site alerta sobre domínios falsos/clonados — confira o endereço com atenção."},
    "MA": {"link": "https://protestoma.com.br/", "confianca": "verificado"},
    "MT": {"link": "https://www.cartoriosdeprotestomt.com.br/", "confianca": "verificado"},
    "MS": {"link": "https://protestoms.org.br/", "confianca": "verificado"},
    "MG": {"link": "https://protestomg.com.br/", "confianca": "verificado"},
    "PA": {"link": "https://protestopa.com.br/", "confianca": "verificado"},
    "PB": {"link": "https://protestoparaiba.com.br/", "confianca": "verificado", "nota": "Direciona ao tabelião da comarca ou à pesquisa nacional (cenprotnacional.org.br), sem emissão unificada própria."},
    "PR": {"link": "https://paranaprotesto.com.br/", "confianca": "verificado"},
    "PE": {"link": None, "confianca": "nao_encontrado"},
    "PI": {"link": None, "confianca": "nao_encontrado"},
    "RJ": {"link": "https://www.cartoriosdeprotestorj.com.br/certidao-protesto", "confianca": "verificado"},
    "RN": {"link": "https://www.cartoriosdeprotestorn.com.br/", "confianca": "verificado", "nota": "Direciona aos cartórios individuais, sem emissão unificada própria."},
    "RS": {"link": "https://www.protestors.com.br/", "confianca": "verificado", "nota": "A emissão em si é feita pelo portal nacional CENPROT (site.cenprotnacional.org.br)."},
    "RO": {"link": "https://www.protestorondonia.com.br/", "confianca": "verificado"},
    "RR": {"link": None, "confianca": "nao_encontrado"},
    "SC": {"link": "https://cartoriosdeprotestosc.com.br/", "confianca": "inferido"},
    "SP": {"link": "https://protestosp.com.br/certidao-de-protesto", "confianca": "verificado"},
    "SE": {"link": None, "confianca": "nao_encontrado"},
    "TO": {"link": "https://cratocantins.com.br/", "confianca": "inferido", "nota": "No momento da checagem, a página indicava ambiente de testes/homologação."},
}

# Justiça Federal: cada UF pertence a um TRF (Tribunal Regional Federal).
# O TRF6 (criado em 2023) cobre só Minas Gerais; o TRF1 perdeu MG nessa divisão.
UF_PARA_TRF = {
    "AC": "trf1", "AM": "trf1", "AP": "trf1", "BA": "trf1", "DF": "trf1", "GO": "trf1",
    "MA": "trf1", "MT": "trf1", "PA": "trf1", "PI": "trf1", "RO": "trf1", "RR": "trf1", "TO": "trf1",
    "RJ": "trf2", "ES": "trf2",
    "SP": "trf3", "MS": "trf3",
    "PR": "trf4", "RS": "trf4", "SC": "trf4",
    "AL": "trf5", "CE": "trf5", "PB": "trf5", "PE": "trf5", "RN": "trf5", "SE": "trf5",
    "MG": "trf6",
}

TRF_LINKS = {
    "trf1": {"link": "https://sistemas.trf1.jus.br/certidao/#/solicitacao", "confianca": "inferido", "nome": "TRF da 1ª Região"},
    "trf2": {"link": "https://certidoes.trf2.jus.br/certidoes/#/principal/solicitar", "confianca": "verificado", "nome": "TRF da 2ª Região"},
    "trf3": {"link": "https://web.trf3.jus.br/certidao-regional/", "confianca": "verificado", "nome": "TRF da 3ª Região"},
    "trf4": {"link": "https://www.trf4.jus.br/trf4/processos/certidao/index.php", "confianca": "verificado", "nome": "TRF da 4ª Região"},
    "trf5": {"link": "https://certidoes.trf5.jus.br/certidoes2022/", "confianca": "verificado", "nome": "TRF da 5ª Região"},
    "trf6": {"link": "https://sistemas.trf6.jus.br/certidao/#/solicitacao", "confianca": "inferido", "nome": "TRF da 6ª Região"},
}


def link_trf_para_uf(uf):
    trf_key = UF_PARA_TRF.get(uf)
    if not trf_key:
        return {"link": None, "confianca": "nao_encontrado"}
    dado = dict(TRF_LINKS[trf_key])
    dado["trf"] = trf_key
    return dado


# ---------------------------------------------------------------------------
# Base de Dados das Ações. Documentos com "fonte_link" têm o link resolvido
# dinamicamente conforme a UF escolhida (ver /api/portais e /api/checklist).
# Documentos com "link_emissao" fixo são de âmbito nacional (não mudam por UF).
# ---------------------------------------------------------------------------

ACOES_IMOBILIARIAS = {
    "despejo": {
        "titulo": "Ação de Despejo por Falta de Pagamento",
        "categoria": "Locação Imobiliária",
        "documentos": [
            {
                "id": "doc_1",
                "nome": "RG e CPF do Locador (Autor)",
                "categoria": "Qualificação",
                "obrigatorio": True,
                "dica": "Documento pessoal com foto ou CNH atualizada."
            },
            {
                "id": "doc_2",
                "nome": "Contrato de Locação Assinado",
                "categoria": "Contratual",
                "obrigatorio": True,
                "dica": "Verificar se há assinatura das testemunhas ou validação digital."
            },
            {
                "id": "doc_3",
                "nome": "Certidão Distribuidor Cível (1ª Instância TJ)",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Emissão gratuita no portal do Tribunal de Justiça do estado do imóvel.",
                "fonte_link": "tj_estadual"
            },
            {
                "id": "doc_4",
                "nome": "Certidão Negativa de Débitos Federais e Dívida Ativa",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Validade de 180 dias. Emitida no site da Receita Federal (âmbito nacional, não muda por estado).",
                "link_emissao": "https://servicos.receita.fazenda.gov.br/Servicos/certidao/"
            },
            {
                "id": "doc_5",
                "nome": "Certidão Negativa de Débitos Trabalhistas (CNDT)",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Emitida gratuitamente pelo Tribunal Superior do Trabalho (âmbito nacional, não muda por estado).",
                "link_emissao": "https://www.tst.jus.br/certidao1"
            },
            {
                "id": "doc_6",
                "nome": "Matrícula do Imóvel Atualizada (RGI)",
                "categoria": "Cartório de Imóveis",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "A certidão de ônus e ações reais precisa ter menos de 30 dias de emissão (âmbito nacional via ONR).",
                "link_emissao": "https://registradores.onr.org.br/"
            },
            {
                "id": "doc_7",
                "nome": "Planilha / Demonstrativo dos Aluguéis em Atraso",
                "categoria": "Provas",
                "obrigatorio": True,
                "dica": "Incluir correção monetária, juros de 1% a.m. e multa prevista em contrato."
            }
        ]
    },
    "usucapiao": {
        "titulo": "Ação de Usucapião Urbano",
        "categoria": "Propriedade Imobiliária",
        "documentos": [
            {
                "id": "doc_101",
                "nome": "Documentos de Identificação do Possuidor",
                "categoria": "Qualificação",
                "obrigatorio": True,
                "dica": "Se casado(a), certidão de casamento e documentos do cônjuge."
            },
            {
                "id": "doc_102",
                "nome": "Certidão Distribuidor Cível (Estadual)",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Emitida em nome do autor e dos antecessores na posse (últimos 10/15 anos).",
                "fonte_link": "tj_estadual"
            },
            {
                "id": "doc_103",
                "nome": "Certidão Negativa da Justiça Federal (TRF)",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Para comprovar ausência de ações possessórias federais. O tribunal (TRF) muda conforme o estado.",
                "fonte_link": "trf"
            },
            {
                "id": "doc_104",
                "nome": "Certidão Negativa dos Cartórios de Protesto",
                "categoria": "Certidões Negativas",
                "tipo": "certidao",
                "obrigatorio": True,
                "alerta": "Certidão de consulta de protestos em nome dos possuidores.",
                "fonte_link": "protesto_estadual"
            },
            {
                "id": "doc_105",
                "nome": "Planta e Memorial Descritivo do Imóvel",
                "categoria": "Documentos Técnicos",
                "obrigatorio": True,
                "alerta": "Deve conter ART/RRT quitada e assinatura do profissional técnico."
            }
        ]
    }
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/acoes', methods=['GET'])
def listar_acoes():
    resumo = [{"key": key, "titulo": data["titulo"]} for key, data in ACOES_IMOBILIARIAS.items()]
    return jsonify(resumo)


@app.route('/api/checklist/<tipo_acao>', methods=['GET'])
def obter_checklist(tipo_acao):
    acao = ACOES_IMOBILIARIAS.get(tipo_acao)
    if not acao:
        return jsonify({"error": "Ação imobiliária não encontrada"}), 404
    return jsonify(acao)


@app.route('/api/portais', methods=['GET'])
def obter_portais():
    """Retorna toda a base de UFs/portais para o front-end resolver os links
    dinamicamente quando o usuário escolhe o estado do imóvel."""
    trf_por_uf = {uf: link_trf_para_uf(uf) for uf, _ in UFS}
    return jsonify({
        "ufs": [{"sigla": sigla, "nome": nome} for sigla, nome in UFS],
        "tj_estadual": TJ_ESTADUAL,
        "protesto_estadual": PROTESTO_ESTADUAL,
        "trf_por_uf": trf_por_uf,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
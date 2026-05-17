import streamlit as st
import requests
import pandas as pd
import json

# ==============================================================================
# CONFIGURAÇÃO DEVE SER A PRIMEIRA CHAMADA DO STREAMLIT
# ==============================================================================
# Define o layout e as configurações básicas da página
st.set_page_config(
    page_title="Dashboard Log Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes da API
API_URL = "http://127.0.0.1:8000"
ANALYZE_ENDPOINT = f"{API_URL}/analyze/"
TOKEN_ENDPOINT = f"{API_URL}/token"

def render_login_page():
    """Renderiza uma página de login bonita e centralizada."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container com bordas e sombra simulada para dar um aspecto de "card"
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>🛡️ Secure Log Analyzer</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Central de Inteligência Cibernética</p>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 Nome de Usuário", placeholder="Ex: admin")
                password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
                
                submitted = st.form_submit_button("Entrar no Sistema", type="primary", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.warning("⚠️ Preencha usuário e senha!")
                    else:
                        with st.spinner("Autenticando na API..."):
                            try:
                                response = requests.post(TOKEN_ENDPOINT, data={"username": username, "password": password})
                                if response.status_code == 200:
                                    st.session_state["token"] = response.json().get("access_token")
                                    st.success("✅ Acesso Liberado!")
                                    st.rerun()
                                else:
                                    st.error("❌ Credenciais inválidas.")
                            except Exception as e:
                                st.error(f"🔌 Erro de conexão com o servidor. A API está rodando?")

def analyze_logs(firewall_file, auth_file):
    """
    Envia os arquivos de log para a API HTTP via POST.
    
    Tenta enviar tanto o firewall_file quanto o auth_file se existirem.
    Retorna o JSON da resposta ou None em caso de erro.
    """
    files = {}
    
    # Verifica quais arquivos o usuário anexou e prepara o formato multipart/form-data
    if firewall_file is not None:
        files["firewall_log"] = (firewall_file.name, firewall_file.getvalue(), firewall_file.type)
        
    if auth_file is not None:
        files["auth_log"] = (auth_file.name, auth_file.getvalue(), auth_file.type)

    if not files:
        st.warning("Por favor, faça upload de pelo menos um arquivo de log.")
        return None

    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"

    try:
        # st.spinner exibe uma animação enquanto a requisição à API é feita
        with st.spinner("Enviando dados para análise na API..."):
            response = requests.post(ANALYZE_ENDPOINT, files=files, headers=headers, timeout=30)
            
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Erro de Autenticação. Verifique seu login.")
            return None
        else:
            st.error(f"Erro na API (Status Code: {response.status_code}): {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Falha na conexão. A API está rodando? Verifique se o uvicorn foi iniciado na porta 8000.")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao conectar à API: {e}")
        return None

def draw_results(report_data):
    """
    Exibe os resultados da análise na interface de forma visual.
    Lê o JSON retornado pela API e monta métricas, tabelas e gráficos.
    """
    st.success("Análise concluída com sucesso!")
    
    # 1. Visão Geral (Métricas)
    st.header("📊 Visão Geral")
    col1, col2, col3 = st.columns(3)
    
    # Tratamento com `.get()` na raiz do JSON de reposta
    stats = report_data.get("statistics", {})
    general = report_data.get("summary", {})
    
    col1.metric("Eventos Analisados", general.get("total_events", 0))
    col2.metric("IPs Únicos", stats.get("unique_ips", 0))
    col3.metric("IPs Suspeitos (Totais)", len(report_data.get("top_suspicious_ips", [])))

    st.markdown("---")

    # 2. Informações de Suspeitos
    st.header("🚨 IPs Mais Suspeitos")
    suspicious_ips = report_data.get("top_suspicious_ips", [])
    
    if suspicious_ips:
        # Convertemos a lista de dicionários para um DataFrame do Pandas para exibir numa tabela mais bonita
        df_ips = pd.DataFrame(suspicious_ips)
        st.dataframe(df_ips, use_container_width=True)
    else:
        st.info("Nenhum IP classificado como suspeito na análise.")
        
    st.markdown("---")
    
    # 3. Análise Geográfica (Mapas e Gráficos)
    st.header("🌍 Análise Geográfica")
    geo_data = report_data.get("geographic_analysis", [])
    
    if geo_data:
        df_geo = pd.DataFrame(geo_data)
        
        # O streamlit map precisa das colunas como latitude e longitude (ou lat/lon)
        # Filtramos apenas os registros que tem latitude e longitude mapeadas
        if 'latitude' in df_geo.columns and 'longitude' in df_geo.columns:
            # Pegando as coordenadas reais e formatando para o mapa
            df_map = df_geo[['latitude', 'longitude']].dropna()
            df_map.columns = ['lat', 'lon'] # streamit st.map reconhece automaticamente lat/lon
            
            col_map, col_chart = st.columns(2)
            
            with col_map:
                st.subheader("Mapa de Origem dos IPs")
                st.map(df_map)
                
            with col_chart:
                st.subheader("Distribuição por País")
                # Conta a ocorrência de cada país para montar um gráfico
                if 'country' in df_geo.columns:
                    country_counts = df_geo['country'].value_counts()
                    st.bar_chart(country_counts)
        else:
            st.warning("Dados de latitude e longitude não encontrados na resposta da API.")
    else:
        st.info("Nenhuma informação geográfica disponível. Verifique se o geographic.py gerou resultados válidos.")
        
    st.markdown("---")
    
    # 4. Retorno Bruto (Para desenvolvedores/auditoria)
    with st.expander("Ver JSON completo retornado pela API"):
        st.json(report_data)

def main():
    """
    Função principal que monta a interface.
    """
    # Verifica o estado da sessão antes de renderizar qualquer coisa da aplicação principal
    if "token" not in st.session_state:
        render_login_page()
        st.stop()
        
    # ==========================================
    # ÁREA LOGADA (DASHBOARD)
    # ==========================================
    # Título principal da página logada
    st.title("🛡️ Log Analyzer Cyber")
    st.markdown("Bem-vindo ao dashboard interativo. Utilize as ferramentas ao lado para subir seus dados.")
    
    # Cria uma barra lateral
    with st.sidebar:
        st.header("👤 Perfil")
        st.success("Logado com sucesso.")
        st.button("Sair (Logout)", on_click=lambda: st.session_state.pop("token") and st.rerun(), type="secondary", use_container_width=True)
        
        st.markdown("---")
        st.header("📁 Upload de Arquivos")
        st.markdown("Insira seus relatórios exportados abaixo (tamanho máx: 100MB).")
        
        # Widgets para o upload de arquivos
        firewall_file = st.file_uploader("Upload Firewall Log", type=['csv', 'json'])
        auth_file = st.file_uploader("Upload Auth Log", type=['csv', 'json'])
        
        analyze_button = st.button("🚀 Analisar Logs", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("💡 *Dica: Você pode testar subindo os arquivos que estão na pasta `data/` do projeto.*")

    # Verifica se o usuário clicou no botão "Analisar Logs"
    if analyze_button:
        if not firewall_file and not auth_file:
            st.error("⚠️ Envie primeiro pelo menos um arquivo de log na barra lateral.")
        else:
            # Chama a função que faz o post para a API
            result_json = analyze_logs(firewall_file, auth_file)
            
            if result_json:
                # Desenha os gráficos e tabelas com as informações
                draw_results(result_json)
            else:
                st.info("Aguardando correção para processar.")

# ==============================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    main()
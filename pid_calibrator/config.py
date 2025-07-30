def defaults():
    """
    Retorna um dict com as configurações padrão:
      - CONNECTION_URI: URI de conexão MAVLink
      - UPDATE_INTERVAL_MS: intervalo (ms) entre cada atualização de gráfico
      - PARAM_REQUEST_TIMEOUT: timeout (s) na requisição de parâmetros
      - MAX_DATA_LENGTH: quantos pontos manter em memória para cada eixo
      - WINDOW_SECONDS: tamanho, em segundos, da janela de tempo no eixo X
    """
    return {
        'CONNECTION_URI':      "udp:0.0.0.0:14550",
        'UPDATE_INTERVAL_MS':  50,
        'PARAM_REQUEST_TIMEOUT': 1,
        'MAX_DATA_LENGTH':     1000,
        'WINDOW_SECONDS':      10.0,
    }

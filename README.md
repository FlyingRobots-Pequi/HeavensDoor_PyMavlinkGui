# HeavensDoor_PyMavlinkGui (PX4 PID Calibrator)

Um visualizador e calibrador de controladores PID para drones rodando PX4, desenvolvido em Python com Tkinter e Matplotlib. Permite monitorar em tempo real os setpoints e valores reais dos controladores de taxa, atitude, velocidade e posição, organizados em abas.

## 📂 Estrutura do Repositório

```
├── main.py                    # Ponto de entrada da aplicação
├── pid_calibrator/            # Pacote principal
│   ├── __init__.py            # Inicialização do pacote e exportação de API
│   ├── config.py              # Configurações e constantes padrão
│   ├── mavlink_client.py      # Wrapper de conexão Mavlink e leitura de mensagens
│   ├── plotter.py             # Lógica de armazenamento e atualização dos gráficos
│   └── ui.py                  # Interface Tkinter com notebooks e canvases
└── README.md                  # Este arquivo de documentação
```

## 🚀 Recursos

- Conexão automatizada via MAVLink (UDP por padrão em `udp:0.0.0.0:14550`)
- Exibição de parâmetros do PX4 em Treeview
- Abas separadas para cada controlador:
  - **Rate Controller**: roll, pitch e yaw (velocidades angulares)
  - **Attitude Controller**: roll, pitch e yaw (ângulos) via quaternion
  - **Velocity Controller**: componentes horizontal e vertical da velocidade
  - **Position Controller**: componentes horizontal e vertical da posição
- Gráficos em tempo real com janela de tempo configurável

## ⚙️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/px4-pid-calibrator.git
   cd px4-pid-calibrator
   ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

> **Observação:** No Linux, certifique-se de instalar o pacote do Tkinter:
> ```bash
> sudo apt-get install python3-tk
> ```

## 🎬 Uso

1. Inicie o PX4 ou conecte o simulador (ex: PX4 SITL).
2. Execute a aplicação:
   ```bash
   python3 main.py
   ```
3. Na janela principal:
   - Informe a URI de conexão MAVLink (padrão `udp:0.0.0.0:14550`).
   - Clique em **Connect**.
   - Aguarde o heartbeat e carregamento dos parâmetros.
   - Navegue pelas abas de controladores e observe os gráficos de setpoint (azul) vs. medido (laranja).

## 🧩 Configurações

Todas as constantes e valores padrão estão em `pid_calibrator/config.py`. Você pode alterar:

| Chave                   | Descrição                                         | Valor Padrão         |
|-------------------------|---------------------------------------------------|----------------------|
| `CONNECTION_URI`        | URI para conexão MAVLink                          | `udp:0.0.0.0:14550`  |
| `UPDATE_INTERVAL_MS`    | Intervalo (ms) entre atualizações de gráfico      | `50`                 |
| `PARAM_REQUEST_TIMEOUT` | Timeout (s) na requisição de parâmetros           | `1`                  |
| `MAX_DATA_LENGTH`       | Máximo de pontos mantidos na memória              | `1000`               |
| `WINDOW_SECONDS`        | Tamanho da janela de tempo exibida no eixo X (s)  | `10.0`               |

Obs: para que o QGC e o app rodem junto com a simulação, use no QGC o ip do pc e a porta 18570, no app mantenha o localhost (127.0.0.0 ou 0.0.0.0) e a porta 14540 

## 🛠️ Personalização

- Para adicionar novos controladores ou métricas, edite `pid_calibrator/ui.py`:
  - Atualize o dicionário `controllers` com o ID e as abas-filho.
  - Ajuste o parsing de mensagens em `_update_loop()` no mesmo arquivo.
- Para mudar estilos dos gráficos (cores, linhas, escalas), modifique `plotter.py` ou o setup do Matplotlib em `ui.py`.

## ❓ Problemas Comuns

- **Tkinter não encontrado**: instale `python3-tk` no seu sistema.
- **Sem heartbeat**: verifique se o PX4/SITL está rodando e enviando dados na porta correta.
- **Linhas não aparecem**: cheque se as mensagens MAVLink corretas estão sendo publicadas (`ATTITUDE_TARGET`, `ATTITUDE`, `POSITION_TARGET_LOCAL_NED`, `LOCAL_POSITION_NED`).

## 🤝 Contribuição

Pull requests são bem-vindos! Siga o modelo:
1. Fork deste repositório
2. Crie uma branch com sua feature (`git checkout -b minha-feature`)
3. Commit com mensagens claras (`git commit -m "Adiciona X"`)
4. Push para a branch (`git push origin minha-feature`)
5. Abra um Pull Request

## 📄 Licença

E la tem essa bagaça
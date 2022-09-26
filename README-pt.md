# ProfitSwitch for HiveOS

Esse projeto visa realizar a troca da moeda minerada no HiveOS para a que está com a maior rentabilidade de acordo com o site Whattomine (https://whattomine.com/).

A partir da Rig disponível no HiveOS, ele monta os valores referentes de hashrate e consumo de acordo com a quantidade de placas encontradas no HiveOS utilizando os valores padrões conforme o Whattomine. Caso deseja alterar os valores é possível configurar uma URL para buscar com valores de hasrate e consumo.

## Instalação
Para a execução é necessário ter instalado o python versão 3.8 ou maior.

Pode-se tanto instalar na RIG do HiveOS, extraindo os arquivos em uma pasta e rodar de tempos em tempos conforme configurado no crontab, ou executando o script para instalação.

```
wget -O - https://raw.githubusercontent.com/pkelbern/profitswitch/main/install.sh | bash
```

Ao executar o script de instalação, será criado um arquivo para executar a verificação a cada 1 hora. Caso deseje alterar ou excluir o arquivo, ele se encontra em `/etc/cron.d/profitswitch`. Para testar a instalação, execute o comando:
```
/usr/bin/python3 /usr/profitswitch/profitswitch.py
```

## Configurações disponíveis:

### hiveosapi.txt
Arquivo com o Personal Token de acesso a api da HiveOS. Disponível na url:
```
https://id.hiveon.com/auth/realms/id/account/sessions
```

### whattomine.txt (opcional)
Caso deseje que não seja montado automaticamente os dados do whattomine para a sua rig, é possível colocar a url do whattomine para acessar as informações. Para gerar a url, configure o whattomine e clique no botão JSON. Depois, copia a URL gerada para esse arquivo.

### config.json (opcional)
O arquivo config.json pode ser configurado conforme abaixo.

| Chave  | Tipo | Descricao do Valor |
| --- | --- | --- |
| farmid  | opcional  | Busca o ID da FARM no HiveOS, caso não esteja configurado, irá buscar o configurado no arquivo `/hive-config/rig.conf`. Se ambos não existem, busca a primeira FARM disponível |
| rigid  | opcional  | Busca o ID da RIG no HiveOS, caso não esteja configurado, irá buscar o configurado no arquivo `/hive-config/rig.conf`. Se ambos não existem, busca a primeira RIG da primeira FARM disponível |
| cost  | opcional  | Custo em USD/kWh, valor padrão de `0.1`. Pode ser configurado também no HiveOS nas opções de configuração da Farm |
| switch  | opcional  | Caso esteja com `false`, não será realizada a troca do flight sheet |
| verbose  | opcional  | Mostra na tela os valores das moedas de acordo com o site Whattomine |

### flightsheets.json (opcional)
O arquivo flightsheets.json pode ser configurado com as moedas para realizar a troca do flight sheets no HiveOS.

| Chave  | Tipo | Descricao do Valor |
| --- | --- | --- |
| "sigla"  | opcional  | Informa que para a moeda com a "sigla", qual a flight sheet deve-se usar, caso esteja com `false`, ignora qualquer flight sheet |

### algomap.json
Json com o mapeamento de algoritmo para moeda no Whattomine.

### gpumap.json 
Json com o mapeamento de GPU no HiveOS com o Whattomine.

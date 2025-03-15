# AGATA - Arquitetura para Gerenciamento Automático de Tarefas de Aprendizado Federado 

O objetivo deste artefato é exemplificar o uso da ferramenta AGATA através de dois experimentos: 

* O primeiro experimento inicializa os microsserviços do servidor e, em seguida, cria e inicializa uma tarefa simples de aprendizado no servidor, executado na máquina local. Depois, ocorre a inicialização dos microsserviços do cliente na mesma máquina. Com isso, ocorre a trasferência automática da tarefa para o cliente.

* O segundo experimento se diferencia do primeiro ao inicializar uma tarefa com erro (E) e outra correta (C). O cliente, após ocorrer um erro em E, automaticamente troca a tarefa para C.

Em ambos os casos, os resultados são apresentados nos arquivos `experiments/events.json`, `experiments/exp_*_raw_times` e `logs_*/*`.

# Estrutura do README.md



# Selos considerados

Os 4 selos são considerados:

* Artefatos Disponíveis (SeloD);
* Artefatos Funcionais (SeloF);
* Artefatos Sustentáveis (SeloS); e
* Experimentos Reprodutíveis (SeloR).

# Informações básicas

Os experimentos foram executados em diferentes máquinas físicas e virtuais, com as seguintes especificações:
* VM com 4 CPUs, 8GB de memória RAM e Debian 12, instanciadas em um servidor com CPU Intel Xeon E5-2650, 8 núcleos e 16 threads, 2,80GHz e 32GB de RAM. 
* PC com Intel i9-10900, CPU de 2.80 GHz, 20 threads, 32GB de RAM, e Ubuntu 20.04.
* Notebook com Intel i5-8250U , CPU de 3.40 GHz, 8 threads, 8GB de RAM, e Ubuntu 20.04.

Uma vez que em todas as configurações não foi observada nenhuma dificuldade com desempenho, assume-se a execução é garantida sob as seguintes condições:
* Sistema Operacional Ubuntu 20.04 ou Debian 12
* CPU mínima: Intel i5 de 8ª Geração
* Memória mínima: 8GB

# Dependências

Os requisitos são:
* Python 3.12.7 
* Conda (miniconda3)
* Docker 24.0.7

# Preocupações com segurança

A execução dos experimentos não apresentam para os revisores riscos de segurança **conhecidos pelos autores**. Por prevenção, uma vez que alguns processos expõem portas de rede, recomenda-se a execução em uma rede local segura.

Em **casos de modificação do código por parte do usuário**, para além do tutorial apresentado neste artefato, os autores se isentam de riscos da segurança.

# Instalação

Crie um ambiente conda:

```bash
conda create -n agata python=3.12.7
```

Ative o ambiente conda toda vez que um terminal for aberto para rodar os experimentos:
```bash
conda activate agata
```

Instale as dependências dentro do ambiente conda:
```bash
conda install pip
pip install -r requirements.txt
```

INICIAR MICROSSERVIÇOS BÁSICOS NA MÃO

# Teste mínimo

Esta seção deve apresentar um passo a passo para a execução de um teste mínimo.
Um teste mínimo de execução permite que os revisores consigam observar algumas funcionalidades do artefato. 
Este teste é útil para a identificação de problemas durante o processo de instalação.

# Experimentos

Antes de executar o primeiro experimento, garanta a finalização de qualquer processo Python anteriormente iniciado neste artefato. Não se preocupe que contêineres serão finalziados e os bancos de dados serão deletados pelos scripts dos experimentos. O mais importante é que nenhum micorsserviço Python esteja iniciado, para evitar conflitos de porta de rede, por exemplo.

## Experimento 1 

Para executar o primeiro experimento, descrito no início deste artefato, execute
```bash
bash experiments/exp1.sh
```

A permissão de superusuário será pedida para executar o Docker. O experimento demora certa de 4 minutos. O revisor pode acompanhar no terminal a impressão do andamento do experimento. Os resultados mais interessantes são:
* O arquivo `experiments/events.json` apresenta, em ordem de momento de execução, as principais etapas necessárias para a execução da tarefa de aprendizado federado, bem como a estampa de tempo correspondente e o componente onde ocorrem
* O arquivo `experiments/exp1_raw_times` resume o tempo para as operações mais importantes

## Experimento 2

Para executar o primeiro experimento, descrito no início deste artefato, execute
```bash
bash experiments/exp2.sh
```

Analogamente, observe os arquivos `experiments/events.json` e `experiments/exp2_raw_times`

# LICENSE

```
MIT License

Copyright (c) 2024 Grupo de Teleinformática e Automação (GTA)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

# Documentação

```bash
cd docs
sphinx-build -M html source build
python3 -m http.server -d build/html 7777
```

Acesse `http:\\localhost:7777` para visualizar a documentação no formato Sphinx

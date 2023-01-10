# Star Jeans Company
###### [Visualizar projeto](https://luiz-maycon-star-jeans-company-streamlit-app-ihraje.streamlit.app)

## 1.0 Contexto do Negócio
Depois de vários negócios bem sucedidos, dois sócios brasileiros estão planejando entrar no mercado de moda dos EUA com um modelo de negócio do tipo E-commerce.

A idéia inicial é começar com apenas um produto para um público específico. No caso, o produto seria calças jeans para o público masculino. O objetivo é manter o custo de operação baixo e escalar a medida que forem conseguindo clientes.

Porém, mesmo com o produto de entrada e a audiência definidos, os dois companheiros não têm experiência nesse mercado e, portanto, não sabem definir coisas básicas como preço, o tipo de calça e o material para a fabricação de cada peça.

Assim, eles decidiram contratar uma consultoria de Análise de Dados para responder tais questões antes de iniciarem o desenvolvimento das peças na recém fundada Star Jeans Company¹.

Dentre as suas principais concorrentes estão H&M, Macy 's, Levi's, Zara e Polo.

###### ¹A Star Jeans, assim como toda a situação problema, é fictícia, sendo criada apenas para ajudar no contexto de análise de dados do projeto.

## 2.0 Questões do Negócio
Abaixo estão as perguntas feitas à equipe de dados:

**2.1** Qual o melhor preço de venda para as calças?

**2.2** Quais tipos de calças e suas cores para o produto inicial?

**2.3** Quais as matérias-primas necessárias para confeccionar as calças?

## 3.0 Dados
Os dados foram coletados diretamente do website da H&M, conforme será explicado mais adiante. A seguir está uma breve descrição destes:
| COLUNA          | DESCRIÇÃO                           |
|-----------------|-------------------------------------|
| product_id      | Identificador do produto            |
| style_id        | Identificador do estilo do produto  |
| color_id        | identificador da cor do produto     |
| product_name    | Nome                                |
| product_color   | cor                                 |
| fit             | Modelo                              |
| product_price   | Preço                               |
| size_number     | Comprimento                         |
| size_model      | Largura                             |
| cotton          | Presença de algodão na composição   |
| polyester       | Presença de poliéster na composição |
| spandex         | Presença de spandex na composição   |
| scrapy_datetime | Data que o dado foi coletado        |

## 4.0 Premissas
**4.1** Cores que possuem a palavra “denim”, como a cor “light_denim_blue”, tiveram tal palavra removida dado que denim é o tecido das calças jeans. Dessa forma, o exemplo citado se tornaria “light_blue”.

**4.2** As colunas size_number e size_model foram desconsideradas e, assim, removidas do dataframe.

**4.3** As colunas correspondentes a composição do produto (cotton, polyester e spandex) foram considerados como binários - possui ou não possui algodão, por exemplo.

## 5.0 Planejamento da Solução
**5.1 Produto Final**

Tem-se, então, a causa raíz do problema que é o fato da empresa está entrando no mercado de varejo de moda dos EUA sem ter expertise para escolher e precificar os seus produtos. O próximo objetivo é pensar em como entregar as respostas para as perguntas solicitadas de forma que a construção seja guiada por tal modelo.

A maneira escolhida foi utilizar médias dos preços de possíveis concorrentes para criar tabelas e/ou gráficos e apresentá-los em um dashboard no Streamlit (biblioteca disponível em Python) que pode ser acessado no link logo no início deste artigo.

**5.2 Processo**

Identificando a causa raíz do problema e tendo um modelo para o produto final em mente, o próximo é dividir todo o processo em tarefas sequenciais:
- Definir as colunas da base de dados, isto é, os dados que serão coletados;
- Coletar os dados do website de um ou mais concorrentes da Star Jeans usando webscraping;
- Fazer a limpeza dos dados coletados;
- Armazenar os dados em um banco de dados;
- Fazer o agendamento do processo de ETL gerado;
- Analisar os dados armazenados;
- Criar a visualização do produto final;
- Entregar o produto final.

**5.3 Ferramentas**
- Python 3.8.0
- Jupyter Notebook
- Pycharm
- Processo de ETL
- Beautiful Soup
- Cron Job
- SQLite
- Streamlit e Streamlit Cloud
- Estatística descritiva
- Git e Github

## 6.0 Engenharia
**6.1 Coleta de dados**

Webscraping pode ser definido simplesmente como extrair dados de websites, e essa é a técnica mais apropriada para o presente projeto. Foi escolhida a página Men’s Jeans do site da H&M (https://www2.hm.com/en_us/men/products/jeans.html) como fonte de dados e a ferramenta utilizada foi a biblioteca Beautiful Soup. A seguir está um exemplo da forma como os dados chegaram:
| COLUNA          | DADO                                                                   |
|-----------------|------------------------------------------------------------------------|
| product_id      | 1024256002                                                             |
| fit             | Slim Fit                                                               |
| product_name    | Slim Jeans                                                             |
| product_price   | $19.99                                                                 |
| product_color   | Light denim blue                                                       |
| style_id        | 1024256                                                                |
| color_id        | 002                                                                    |
| size            | The model is 189cm/6'2" and wears a size 31/32                         |
| composition     | Shell: Cotton 99%, Spandex 1% Pocket lining: Polyester 65%, Cotton 35% |
| scrapy_datetime | 2022-12-23 15:01:33                                                    |

**6.2 Limpeza de dados**

O trabalho de limpeza foi feito principalmente através das bibliotecas Pandas e Numpy e técnicas de Regex. O maior desafio aqui estava na coluna composition, onde as informações vieram em uma única string e acabaram sendo transformadas nas três colunas cotton, polyester e spandex. Segue um exemplo após a limpeza:
| COLUNA          | DADO                |
|-----------------|---------------------|
| product_id      | 1024256002          |
| fit             | slim_fit            |
| product_name    | slim_jeans          |
| product_price   | 19.99               |
| product_color   | light_denim_blue    |
| style_id        | 1024256             |
| color_id        | 002                 |
| size_model      | 189                 |
| size_number     | 31/32               |
| cotton          | 0.99                |
| polyester       | 0.65                |
| spandex         | 0.01                |
| scrapy_datetime | 2022-12-23 15:01:33 |

**6.3 Design de ETL**

Após a coleta e a limpeza, foi feito o armazenamento dos dados em um banco de dados, o que finalizou a construção do processo de ETL. O banco de dados utilizado foi o SQLite e foi acessado dentro das próprias IDE’s (ambiente de desenvolvimento integrado) que estavam sendo utilizadas, Jupyter Notebook e PyCharm, sem a necessidade de um SGBD (sistema de gerenciamento de banco de dados) separado.

Dessa forma, a imagem logo abaixo expõe como ficou o design de ETL, sendo que: o job 1 representa o acesso ao site da H&M e à sua vitrine de calças jeans masculinas; o job 2 o acesso à cada produto da página - importante pontuar que foi feita paginação para que fossem pegas todas as páginas - e, em seguida, à cada variação de cor desse produto; o job 3 se trata da limpeza de dados; e o job 4 do armazenamentos dos dados limpos no banco de dados.

![](/img/etl_architecture_design.png)

Para que o ETL funcionasse diariamente sem a necessidade de alguém rodar o código, foi feito o agendamento utilizando o Cron Job, um agendador de tarefas. Com isso, o ETL ficou rodando automaticamente às 10h de segunda a sexta.

Por fim, foi criado um arquivo de log para monitorar o ETL enquanto estivesse em execução. O log foi criado utilizando o logging, mais uma biblioteca em python, e ele ajuda a identificar mais facilmente um erro, caso ocorra. O log informa o link de cada produto conforme estes forem sendo coletados e também quando cada um dos jobs é finalizado.

## 7.0 Análise
Para finalmente responder as questões feitas pelos donos do negócio, foram primeiro formuladas cinco hipóteses que serviram para guiar a análise. Abaixo estão os principais insights gerados.

**7.1 Principais Insights**

**1- Cerca de 80% das calças são das cores blue ou black (ou suas derivadas).**

![](/img/insight01.png)

**2- Calças de cores blue ou black possuem preços médios 21% abaixo da cor mais cara e 15% acima da mais barata.**

![](/img/insight02.png)

**3- Um único fit, o regular_fit, representa quase 30% da quantidade total de calças à venda.**

![](/img/insight03.png)

**4- Mais ou menos metade (50%) das calças possuem poliéster em sua composição.**

![](/img/insight04.png)

**5- O preço médio das calças que possuem poliéster é praticamente igual ao preço médio das que não possuem.**

![](/img/insight05.png)

**7.2 Respondendo as questões**

Relembrando:

- Qual o melhor preço de venda para as calças?
- Quais tipos de calças e suas cores para o produto inicial?
- Quais as matérias-primas necessárias para confeccionar as calças?

Primeiro foi verificado que mais de 80% das calças são das cores azul ou black e, logo, a análise foi levada para as variáveis dessas duas cores. Essa foi a classificação por quantidade de calças medida em porcentagem do grupo:

| COR        | PORCENTAGEM |
|------------|-------------|
| blue       | 24.83       |
| light_blue | 24.15       |
| black      | 19.39       |
| dark_blue  | 17.01       |
| pale_blue  | 3.40        |

Em relação aos modelos, foi descoberto na geração de insights a classificação por quantidade. Agora tem-se também por preço médio:

| FIT         | MEAN PRICE |
|-------------|------------|
| loose_fit   | 39.99      |
| relaxed_fit | 34.33      |
| slim_fit    | 32.31      |
| skinny_fit  | 27.71      |
| regular_fit | 27.13      |

Aqui já se conclui que o modelo regular_fit é o ideal pois possui o menor preço médio e a maior quantidade de calças à venda, enquanto que o loose_fit foi completamente descartado por ser exatamente o oposto. Quanto às cores, escolher apenas uma talvez não seja a melhor opção, de forma que ter pelo menos blue e black deve ser considerado.

Dessa forma, foram criados três casos, os quais foram trazidos abaixo apresentando o preço médio por cada opção e o total - estes podem ser visualizados também no dashboard.

- **Caso 01**

Este é o caso mais simples e prático para a empresa começar suas atividades, trazendo unicamente o modelo regular_fit e as cores black e blue. Os outros dois casos acrescentam variedade, mas também dificuldade, de forma que caberá aos empreendedores decidirem o que podem fazer no momento.

| DESCRIPTION       | MEAN PRICE |
|-------------------|------------|
| regular_fit black | 26.55      |
| regular_fit blue  | 30.63      |
| total             | 28.79      |

- **Caso 02**

Já este outro traz o mesmo fit e aumenta a variedade das cores, sendo acrescentadas light_blue e dark_blue, a segunda e quarta cores mais vendidas, respectivamente.

| DESCRIPTION            | MEAN PRICE |
|------------------------|------------|
| regular_fit black      | 26.55      |
| regular_fit blue       | 30.63      |
| regular_fit dark_blue  | 27.79      |
| regular_fit light_blue | 26.24      |
| total                  | 27.99      |

- **Caso 03**

Por fim, nesta última opção foi trazido mais variedade em modelos, as cores voltam a ser apenas black e blue, porém agora presentes também no skinny_fit. Este é um tipo de calça mais ajustada ao corpo, um contraponto às tradicionais calças retas. Em termos de quantidade disponíveis, o skinny_fit está levemente abaixo do slim_fit (que é um modelo meio termo entre regular e skinny), mas os preços da primeira são consideravelmente mais baixo, o que vai ao encontro do pretendido pelos donos da Star Jeans.

| DESCRIPTION       | MEAN PRICE |
|-------------------|------------|
| regular_fit black | 26.55      |
| regular_fit blue  | 30.63      |
| skinny_fit black  | 31.66      |
| skinny_fit blue   | 26.28      |
| total             | 28.49      |

Quanto a composição, sabe-se que 100% das calças possuem algodão e spandex e cerca de metade delas possuem poliéster. Entretanto, a situação muda bastante quando olhamos para modelos específicos, de modo que no regular_fit apenas 34% possuem poliéster, enquanto que no skinny_fit 83% possuem. Outro ponto interessante é que o médio das calças com poliéster do primeiro modelo é 16% menor que as que não possuem; já para o segundo, os preços são praticamente iguais.

Pensando nisso, os casos acima consideram tanto as calças que possuem quanto as que não possuem poliéster. Isso porque: I) embora a demanda por tal componente seja menor no regular_fit, há um desconto muito bom nos preços; e II) embora quase não haja alteração nos preços do skinny_fit, o componente é essencial no atendimento à sua demanda.

Assim sendo, os materiais que irão compor as calças serão algodão em sua grande maioria e spandex e poliéster em quantidades bem menores.

## 8.0 Conclusão
A decisão orientada à dados está ganhando tanta amplitude a ponto de se tornar quase impossível de ser ignorada, chegando a deixar em desvantagem empresas ou empreendedores que não a utilizam. E é em direção a essa afirmação que o presente projeto vai.

Com o uso da análise dados, empreendedores sem experiência em determinado ramo de negócios conseguiram ter em mãos conclusões talvez equivalentes à intuição de homens com anos de expertise. Sem contar que essa é apenas uma das várias formas de se usar a análise de dados.

Para o analista, além de ampla aptidão para com as ferramentas de tecnologia e estatística, é necessário um bom pensamento analítico e entendimento de negócio, tanto conhecimento (para esse caso em específico) de varejo, quanto de e-commerce e do ramo da moda em si.

Ademais, este projeto segue uma forma cíclica de construção, de modo que há sempre possíveis próximos passos para caso uma futura nova versão seja feita.

## 9.0 Próximos Passos
- Utilizar a ferramenta Selenium para fazer o webscraping;
- Utilizar a ferramenta Apache Airflow para trabalhar com o agendamento e os jobs;
- Coletar dados de outras fontes além do website da H&M;
- Incluir os fatores de tamanho das calças à análise.

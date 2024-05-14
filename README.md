# gatobot
Bot para postar fotos de gato no Twitter (que agora também posta foto de cachorro)

## Atualizações com endpoint v2
Devido à última atualização, algumas funcionalidades do endpoint v1.1 do API do Twitter não funcionam mais, sendo necessário utilizar o v2. Infelizmente, a versão free do v2 não têm algumas funcionalidades disponíveis, como o "tweet_lookup" para procurar outros posts de gato para curtir e compartilhar. Mesmo assim, é possivel utilizar uma mistura das funcionalidades do v1, como upar imagens com "media_upload" e do v2 para postar com "create_tweet". Por fim, as funcionalidades de postar imagens e texto ainda funcionam, só não é possível procurar outros tweets.

## wtf???

Assim como meus outros dois bots do twitter (nasa e corona), esse daqui vai postar conteúdo automatizado para postar foto de gatos e cachorros toda hora (leia-se uma vez por hora), isso mesmo que você leu, além de umas coisinhas mais.

## de onde vêm os gato

Utilizando o API do https://thecatapi.com/

## de onde vêm os dog

API do https://dog.ceo/dog-api/

## tem também os gato fake

Gatos gerados por uma GAN do https://thesecatsdonotexist.com/

## agora tem os status http

Pra cada status http existe sua versão gato: https://http.cat e sua versão dog: https://http.dog

## legendas geradas pelo API do Gemini
Estou utilizando a AI do Google, o [Gemini API](https://deepmind.google/technologies/gemini/#introduction), para gerar tweets baseados nas imagens.

## e as # de gato (descontinuado porque a função de tweet lookup só na versão paga)

Adicionei a funcionalidade de dar RT e like em hashtags como #CatsOfTwitter, além de seguir a pessoa que postou. Os filtros são procurar só media (pra impedir de acabar encontrando algum tweet aleatório que tenha só usado a # pra engajamento), procurar o post original e não algum RT do original (impedindo assim que o bot siga a pessoa errada) e filtrar imagens sensíveis (nudez, etc.).

## esqueci de falar dos fatos sobre gatos
essa é simples, ele entra em contato com o catfact.ninja e procura alguma curiosidade sobre gatos que contenha menos de 280 caracteres pra postar.

## adicionei também umas propagandas (funciona, mas descontinuado porque ninguém comprou nada em 1 ano)

Já que estou nessa, resolvi entrar no mercado afiliado de venda de produtos de pet (gatobot está com quase 5 mil idosos aposentados seguindo suas fotos de gato), então a cada hora ele vai escolher um dos produtos da lista e postar a propaganda pra ver se alguém compra (e a gente ganha alguma coisa com isso, né?). Por enquanto é relativamente simples, tem um txt chamado "products" que tem um link por linha, o hepper.py escolhe uma dessas linhas cada vez que roda e posta o link no fim da frase geral, próxima coisa a se fazer é criar outro txt com frases diferentes, pra ele não ficar postando sempre a mesma frase antes da propaganda.

## cadê o bot

Se quiserem ver no que deu é só procurarem o [Boturi](https://twitter.com/boturitter)

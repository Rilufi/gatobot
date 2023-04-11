# gatobot
Bot para postar fotos de gato no Twitter (que agora também posta foto de cachorro)

## wtf???

Assim como meus outros dois bots do twitter (nasa e corona), esse daqui vai postar conteúdo automatizado, mas com a diferença que usará o próprio workflow do Github pra... postar foto de gatos e cachorros toda hora (leia-se uma vez por hora), isso mesmo que você leu (na verdade esse bot já posta fotos de animais, mas só 3 vezes ao dia e todos de uma database feita com fotos do Flickr, vou tentar expandir isso com o Github já que o local de onde o bot roda não consegue ter acesso à nenhum API externo com imagens de gato ((ou eu que não consigo usar)) ).

## de onde vêm os gato

Utilizando o API do https://thecatapi.com/

## de onde vêm os dog

API do https://dog.ceo/dog-api/

## tem também os gato fake (descontinuado porque o site caiu)

Gatos gerados por uma GAN do https://thiscatdoesnotexist.com/

## agora tem os status http

Pra cada status http existe sua versão gato: https://http.cat e sua versão dog: https://http.dog

## e as # de gato

Adicionei a funcionalidade de dar RT e like em hashtags como #CatsOfTwitter, além de seguir a pessoa que postou. Os filtros são procurar só media (pra impedir de acabar encontrando algum tweet aleatório que tenha só usado a # pra engajamento), procurar o post original e não algum RT do original (impedindo assim que o bot siga a pessoa errada) e filtrar imagens sensíveis (nudez, etc.).

## adicionei também umas propagandas

Já que estou nessa, resolvi entrar no mercado afiliado de venda de produtos de pet (gatobot está com quase 5 mil idosos aposentados seguindo suas fotos de gato), então a cada hora ele vai escolher um dos produtos da lista e postar a propaganda pra ver se alguém compra (e a gente ganha alguma coisa com isso, né?). Por enquanto é relativamente simples, tem um txt chamado "products" que tem um link por linha, o hepper.py escolhe uma dessas linhas cada vez que roda e posta o link no fim da frase geral, próxima coisa a se fazer é criar outro txt com frases diferentes, pra ele não ficar postando sempre a mesma frase antes da propaganda.

## cadê o bot

Se quiserem ver no que deu é só procurarem o [Boturi](https://twitter.com/boturitter)

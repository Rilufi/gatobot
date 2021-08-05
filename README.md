# gatobot
Bot para postar fotos de gato no Twitter (que agora também posta foto de cachorro)

## wtf???

Assim como meus outros dois bots do twitter (nasa e corona), esse daqui vai postar conteúdo automatizado, mas com a diferença que usará o próprio workflow do Github pra... postar foto de gatos e cachorros toda hora (leia-se uma vez por hora), isso mesmo que você leu (na verdade esse bot já posta fotos de animais, mas só 3 vezes ao dia e todos de uma database feita com fotos do Flickr, vou tentar expandir isso com o Github já que o local de onde o bot roda não consegue ter acesso à nenhum API externo com imagens de gato ((ou eu que não consigo usar)) ).

## de onde vêm os gato

Utilizando o API do https://thecatapi.com/

## de onde vêm os dog

API do https://dog.ceo/dog-api/

## e tem também os gato fake

Gatos gerados por uma GAN do https://thiscatdoesnotexist.com/

## e as # de gato

Adicionei a funcionalidade de dar RT e like na #CatsOfTwitter, além de seguir a pessoa que postou. Os filtros são procurar só media (pra impedir de acabar encontrando algum tweet aleatório que tenha só usado a # pra engajamento) e procurar o post original e não algum RT do original (impedindo assim que o bot siga a pessoa errada) por enquanto ele só fica em uma hashtag, mas deixei comentado lá caso queira colocar mais na lista queries = [].

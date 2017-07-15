# coding: utf8
from __future__ import unicode_literals


STOP_WORDS = set("""
	
a, a cada, a menos que, a quem, a respeito, a respeito de, a seguir, abaixo, aberto, abertura, abre, abrir, acabar, acabou, achado, achar, acima, acontece, acreditam, acrescentou, adicional, adjetivo, adotou, afeta, afetados, afetando, afetou, agora, agradar, agradece, agradecer, agrupados, agrupamento, ah, ainda, ajudar, algo, algum, algum dia, alguma, algumas, alguns, alguém, alto, além, além de, além disso, ambas, ambos, amplamente, ano, anos, anotou, anterior, anteriormente, antes, anunciar, ao contrário, ao invés de, ao lado, ao lado de, ao longo, ao longo de, ao mesmo, ao redor de, aparente, aparentemente, apenas, apesar, apoiado, apontado, apontar, apreciar, apresenta, apresentado, apresentando, apresentar, apresentou, aprofundamento, apropriado, após, aquela, aquelas, aquele, aqueles, aqui, aqui está, aquilo, arrumar, as, assim, associada, ato, através, através de, atrás, atualmente, até, auto, aí, à, às, área, áreas, ao, aos, aquela, aquelas, aquele, aqueles, aquilo, acerca, adeus, agora, ali, além, ano, anos, apoia, apoio, apontar, após, área, assim, através

baixo, baixos, bastante, bem sucedido, bens, bilhão, bilhões, bom, breve, brevemente, bem, boa

cada, cada vez, cada vez mais, cancelar, caneca, capaz, capaz de, cara, caro, casa, casca, caso, casos, causa, causar, causas, caída, cedo, cem, centena, cerca de, certa, certamente, certo, chamar, chaves, chorar, cinco, cincoenta, cinquenta, claramente, claro, clique, coisa, coisas, colocar, coloca, colocados, colocar, com, com certeza, começa, começando, começar, começo, começou, como, como está, completa, comprar, comprimento, computador, conformidade, conhece, conhecida, conhecido, consegue, conseguir, conseguiu, consequentemente, consertar, conseuindo, considerando, considerar, conta, contar, contendo, conter, continua, continuar, contra, contudo, contêm, copiar, correr, correspondente, correto, correu, corrigir, cuja, cujas, cujo, cujos, curso, cópia, caminho, cento, cima, coisa, comprido, comprida, conselho, contra, corrente, custa, cá

dada, dados, dali, dando, dar, data, daí, de, de acordo, de alguma forma, de antemão, de boas-vindas, de lado, de novo, de outra forma, de qualquer forma, de qualquer maneira, de volta, de zero, debaixo, definitivamente, deixar que, dela, delas, dele, deles, demais, dentro, depois, depois do que, derramou, descrevem, descrito, desde, desejo, desfazer, despedida, desta, detalhe, deu, deve, deve ter, deveria ter, devido, dez, diante, diferenciar, diferente, diferentemente, diferir, diretamente, disparar, disponível, dispostos, disse, disso, distante, diz, dizem, dizendo, dizer, do lado de fora, do que, dobro, doente, dois, donde, doze, duas vezes, durante, durar, duvidosos, dá, da, das, do, dos, de, daquela, daquele, debaixo, dentro, desligada, desligado, dessa, desse, desta, deste, deve, devem, deverá, dezenove, dezesseis, dezessete, dezoito, dia, diante, direita, doze, duas, dá, dão dúvida

e, egos, ela, ela está, ela mesma, ela própria, ela é, elas, ele, ele está, ele mesmo, ele próprio, ele é, eles, eles estão, eles são, em, em algum lugar, em cima, em direção a, em grande parte, em meio a, em outro lugar, em particular, em qualquer lugar, em relação a, em seguida, em segundo lugar, em todo, em todos os lugares, em torno, em vez, em vez de, embaixo, embora, eminentemente, encontra, encontrar, encontraram, enfrenta, enquanto, entre, entretanto, então, enviados, era, eram, escondeu, especialmente, especificado, especificamente, especificando, especificar, específico, espero, espessas, estado, estados, estamos, estando, estar, esta, estas, estava, este, estes, este meio, esteve, estou, está, estão, etc, eu estou, eu mesmo, eu próprio, eu sou, eu tenho, eu tinha, ex, exatamente, exceto, exemplo, experimentar, experimentou, é, era, eram, essa, essas, esse, esses, estava, estavam, esteja, estejam, estejamos, estive, estivemos, estiver, estivera, estiveram, estiverem, estivesse, estivessem, estivéramos, estivéssemos, estou, está, estávamos, estão, eu, és, estará, estiveste, estivestes

foi, fomos, for, fora, foram, forem, fosse, fossem, fui, fôramos, fôssemos, fato, fatos, faz, fazendo, fazer, feita, feito, fez, fim, final, finais, foi, fora, foram, forma, formas, fornece, forneceu, fortemente, frente, frequentemente, funcionar, funcionou, falta, fará, favor, fazeis, fazem, fazemos, fazes, fazia, faço, fez, foste, fostes

ganhou, geral, geralmente, global, gostar, gostava, gostou, grande, gritar, grupo, grupos, grande, grandes
 
hoje, homens, homepage, html, http, há, haja, hajam, hajamos, havemos, havia, hei, houve, houvemos, houver, houvera, houveram, houverem, houveria, houveriam, houvermos, houverá, houverão, houveríamos, houvesse, houvessem, houvéramos, houvéssemos, hão, horas

ido, ignorado, ignorou, imediatamente, imediato, importante, importância, improvável, independentemente, indica, indicada, indicado, indicam, indo, infelizmente, inferior, inferiores, inferno, informação, início, iniciando, iniciar, iniciou, inteira, inteiramente, interessados, interessante, interesse, interesses, interna, internet, interno, invenção, início, ir, irá, isso, isto

jovem, juntar, junto, juntos, juros, já

km

lado, lados, lar, largura, legenda, levado, levando, levar, levemente, linha, livre, local, logo, logo após, longe, longo, lugar, lugares, lá, límpido, lhe, lhes, ligado

maior, maioria, maiorias, mais, mais alto, mais antigo, mais jovens, mais longe, mais longo, mais recente, mal, maneira, maneiras, manter, mantido, mantém, mas, máximo, me, meio, melhor, membro, membros, menor, menos, meramente, mercadorias, mesmo, mesmo modo, mesmos, mês, meses, metade, meu, meus, mexer, mil, milhão, milhões, mina, minha, minhas, minuciosa, minuciosamente, modo, modos, moinho, momento, montante, mostra, mostrados, mostrando, mostrar, mostrou, mover, muda, mudar, muita, muitas, muitas vezes, muito, muitos, mundial, mundo, mas, mesma, mesmas, muito, muita, muitos, muitas

na, nas, no, nos, na medida, nada, necessariamente, necessitar, necessário, nem, nenhum, nenhum lugar, nenhuma, nesse sentido, ninguém, no, no entanto, no exterior, nome, nomeadamente, normalmente, nossa, nossas, nosso, nossos, notou, nova, novamente, nove, noventa, novo, nunca, nunca mais, não, não deve, não devia, não era, não eram, não estava, não estavam, não está, não estão, não foi, não foram, não ousa, não pode, não poderia, não são, não tem, não teve, não tinha, não vai, não é, nós, nós mesmos, nós próprios, número, números, num, numa, não, nós, naquela, naquele, naquelas, naqueles, nessa, nesse, nesta, neste, noite, nome, nos,, nova, novas, novos, nove, nuns, nível

o, o homem, o maior, o mais alto, o que, o que é, o suficiente, obrigado, obstante, obter, obteve, obtido, obtém, obviamente, oi, oitenta, oito, ok, olha, olhando, olhar, olá, omitido, onde, onde está, onde quer que, onze, oposto, ordenando, ordenou, orgulhoso, os, ou, ousa, outra coisa, outro, outros, obra, obrigada, oitava, oitavo, ontem, os,outra, outras

palavras, para, para a, para baixo, para cima, para dentro, para fora, para onde, para que não, para trás, parar, paraíso, parece, parecem, parecendo, parecer, parecia, parte, partes, partir, particularmente, passado, pede, pedido, pedidos, pedindo, pedir, pediu, pelo qual, pena, pensa, pensamento, pensamentos, pensar, pequeno, pergunta, perguntando, perguntar, perguntou, permite que, permitem que, perto de, pesquisa, pode, pode ter, poderia, poderia ter, ponta, ponto, pontos, por, por exemplo, por isso, por todo, por vezes, porque, porquê, portanto, porém, positivo, possivelmente, possível, potencialmente, pouco, posição, precisando, precisar, predominantemente, preenchimento, presente, presumivelmente, primeira, primeiras, primeiro, primeiros, principalmente, problema, produtos, produz, produzindo, produzir, projeto, promove, promoveu, prontamente, provavelmente, provável, próprio, próprios, próximo, próximo de, página, páginas, põe, pelo, pela, pelas, pelos, por, porquê, perto, primeira, primeiro, próprio, próxima, próximo, próximos, próximas,  puderam, pôde, põe, põem, posso, povo, pouca, poucas, pouco, poucos, possivelmente

qual, qualquer, qualquer que seja, qualquer um, quando, quarenta, quarto, quartos, quase, quatro, que, que querem, que é, quem, quem está, quem quer que, quem quer que seja, quem é, querer, querer dizer, queria, querida, querido, quinta, quinto, quinze, que, quem, quanto, quarta, quarto, quatro, quer, querem, quero, questão, quieto, quinta, quinto, quinze, quê

rapidamente, raramente, razoavelmente, realmente, recente, recentemente, rede, relacionadas, relativamente, reservados, respectivamente, respeita, resultando, resultou, rodada, romance, rosto, relação

sabe, saber, sabia, saudações, se, segue, seguido, seguinte, segunda, segundo, segundos, seis, sem, sempre, sempre que, sendo, sensato, sentiu, separado, separaram, ser, seres, seriamente, serra, sessenta, sete, setenta, seu, seus, seção, shows, significa, significar, significativa, significativamente, sim, sincera, sistema, sob, sobre, somente, somos, sou, soube, sozinho, sua, suas, sub, substancialmente, suficientemente, sugerem, superior, surge, surgem, são, seja, sejam, sejamos, sem, ser, serei, seremos, seria, seriam, será, serão, seríamos, só, sei, seis, sete, sexta, sexto, sistema, sois, somos, sou sétima, sétimo

tais, tal, talvez, também, tem, tende, tendes, tendo, tentar, tentaram, tentativa, tentativas, tentou, ter, terceira, termina, terminou, terrivelmente, teste, teve, texto, tinha, tipo, toda, toda vez que, todo mundo, todos, tomado, tomando, tomar, tomou, torna-se, tornando-se, tornar-se, tornou-se, total, totalmente, trabalhar, trabalha, trabalhando, trabalho, trabalhos, trabalhou, transforma, trilhões, trinta, três, tu, tudo, tão, te, temos, tenha, tenho, teremos, teria, teriam, terá, terão, teríamos, teu, teus, tua,tuas, teve, tinha, tinham, tive, tivemos, tiver, tivera, tiveram, tiverem, tivermos, tivesse, tivessem, tivéramos, tivéssemos, tem, têm, tínhamos, tanta, tanto, tarde, terceiro, tiveste, tivestes,  toda, todas, todo, todo, todos, treze, tão

ultimamente, um, um pouco, uma, uma vez, umas, uniformemente, unir, uns, usado, usando, usar, uso, usos, utilidade, última, último, útil, usa

vai, vais, valor, vamos, vazio, veio, velho, vem, vens, vendo, ver, versus, vez, vezes, vinte, vir, vira, viragem, virar, virou, visto, viu, você, você está, você mesmo, você próprio, você é, vocês mesmos, vocês próprios, voltada, vontade, vários, você, vocês, veja, verdade, verdadeiro, verdadeira, viagem, viagens, vindo, vós, vos, vosso, vossos, vossa, vossas, várias, vários, vão, vêm

web, webpage, website

zero

""".split())

# Guia de Comandos do EventListener

Este guia descreve os comandos de teclado e mouse utilizados no `EventListener` para interagir com a cena.

## Comandos de Teclado

### `R` - Modo de Rotação
- **Pressionar**: Ativa o modo de rotação.
- **Soltar**: Desativa o modo de rotação.

### `T` - Modo de Translação
- **Pressionar**: Ativa o modo de translação.
- **Soltar**: Desativa o modo de translação.

### `C` - Modo de Cisalhamento (temporariamente desabilitado)
- **Pressionar**: Ativa o modo de cisalhamento (comentado no código original, pode ser habilitado se necessário).
- **Soltar**: Desativa o modo de cisalhamento.

### `F1` a `F6` - Posições de Predefinição
- **Pressionar**: Define a posição da câmera para uma das predefinições configuradas.

### `O` - Visão Geral
- **Pressionar**: Alterna a tela de visão geral.
- **Pressionar novamente**: Desabilita a tela

### `P` - Visibilidade da Barra Lateral
- **Pressionar**: Alterna a visibilidade da barra lateral.

### `DELETE` - Deletar Objeto Selecionado
- **Pressionar**: Deleta o objeto atualmente selecionado na cena.

## Comandos de Mouse

### Botão Esquerdo (1)
- **Pressionar**: Seleciona um objeto na cena. Se `Shift` estiver pressionado, permite múltipla seleção.
- **Soltar**: Libera o objeto selecionado.

### Botão Direito (3)
- **Pressionar**: Inicia a movimentação da câmera.
- **Soltar**: Para a movimentação da câmera.

### Scroll (4 e 5)
- **Rolar para cima (4)**: Aproxima a câmera ou aplica transformação (rotação, translação, escala) no objeto selecionado.
- **Rolar para baixo (5)**: Afasta a câmera ou aplica transformação (rotação, translação, escala) no objeto selecionado.

## Modificadores de Teclado

### `Ctrl`
- **Pressionado**: Modifica o comportamento do scroll para rotação/translação/escala no eixo X.

### `Shift`
- **Pressionado**: Modifica o comportamento do scroll para rotação/translação/escala no eixo Y.

### `Alt`
- **Pressionado**: Modifica o comportamento do scroll para rotação/translação/escala no eixo Z.

## Outros Eventos

### Movimento do Mouse
- **Movimento**: Atualiza a posição da câmera com base na posição atual do mouse.

### Saída do Programa
- **Evento**: `pygame.QUIT` fecha o programa.

Esses comandos são gerenciados pela classe `EventListener` para fornecer uma interface interativa ao usuário para manipular a cena e os objetos nela contidos.

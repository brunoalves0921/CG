
# Modelador 3D em Python

Este projeto consiste em um modelador 3D desenvolvido em Python utilizando OpenGL. O projeto abrange a criação, manipulação e visualização de diversos modelos 3D, com foco em iluminação, texturização e interação do usuário.

![CENA](cg.png)

## Objetivos

- Renderizar diferentes objetos 3D como cone, cubo, esfera, objetos .obj etc.
- Implementar técnicas de iluminação e texturização.
- Permitir a manipulação dos objetos 3D através de uma interface interativa.
- Demonstrar conceitos de computação gráfica em um ambiente de desenvolvimento prático.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

- `main.py`: Ponto de entrada principal do projeto.
- `objects/`: Contém os scripts para diferentes objetos 3D como cone, cubo, cilindro, etc.
- `OBJFileLoader/`: Scripts para carregamento e visualização de arquivos OBJ.
  - `objloader.py`: Carregador de arquivos OBJ.
  - `objviewer.py`: Visualizador de arquivos OBJ.
- `utils/`: Scripts utilitários para a cena, câmera, transformações e eventos.
  - `camera.py`: Gerencia a câmera da cena.
  - `event_listener.py`: Gerencia os eventos de interação do usuário.
  - `scene.py`: Gerencia a cena e os objetos contidos nela.
  - `transform.py`: Gerencia as transformações dos objetos.
  - `sidebar.py`: Gerencia de forma intuitiva a criação de novos objetos na cena e adição de texturas.

## Dependências

O projeto requer as seguintes dependências:

- Python 3.x
- PyOpenGL
- NumPy
- PyGame

Certifique-se de ter essas dependências instaladas em seu ambiente antes de executar o projeto.

## Executando o Projeto

Para executar o projeto, siga as etapas abaixo:

1. Certifique-se de ter o Python instalado em seu sistema.
2. Execute o arquivo `main.py` para iniciar a aplicação.
3. Utilize as teclas e o mouse para interagir com os objetos 3D renderizados na tela.

## Funcionalidades

- **Renderização de Objetos 3D**: Renderiza diferentes modelos 3D como cone, cubo, esfera, etc.
- **Iluminação e Texturização**: Implementa técnicas de iluminação e texturização para melhorar a visualização dos objetos.
- **Interação do Usuário**: Permite ao usuário manipular os objetos através do teclado e mouse.
- **Carregamento de Arquivos OBJ**: Suporta o carregamento e visualização de modelos 3D a partir de arquivos OBJ.

## Imagens do Projeto

### Sombras
[![Sombras](sombras.png)](sombras.png)

### Textura
[![Textura](texture.png)](textura.png)

### Luz
[![Luz](light.png)](luz.png)

### Menu
[![Menu](menu.png)](menu.png)

### Viewport
[![Viewport](viewport.png)](viewport.png)

## Guia de Comandos do EventListener

Este guia descreve os comandos de teclado e mouse utilizados no EventListener para interagir com a cena.

### Comandos de Teclado

- **R - Modo de Rotação**
  - Pressionar: Ativa o modo de rotação.
  - Soltar: Desativa o modo de rotação.
- **T - Modo de Translação**
  - Pressionar: Ativa o modo de translação.
  - Soltar: Desativa o modo de translação.
- **C - Modo de Cisalhamento (temporariamente desabilitado)**
  - Pressionar: Ativa o modo de cisalhamento (comentado no código original, pode ser habilitado se necessário).
  - Soltar: Desativa o modo de cisalhamento.
- **F1 a F6 - Posições de Predefinição**
  - Pressionar: Define a posição da câmera para uma das predefinições configuradas.
- **O - View Port**
  - Pressionar: Habilita/Desabilita a viewport.
- **M - Visibilidade do menu de criação**
  - Pressionar: Habilita/Desabilita o menu interativo.
- **P - Projeções**
  - Pressionar: Alterna entre os modos de projeções (Perspectiva / Ortográfica / Oblíqua).
- **L - Sombras**
  - Pressionar: Habilita/Desabilita a visualização das sombras em planos.
- **DELETE - Deletar Objeto Selecionado**
  - Pressionar: Deleta o objeto atualmente selecionado na cena.

### Comandos de Mouse

- **Botão Esquerdo**
  - Pressionar: Seleciona / Desceleciona um objeto na cena. Se Shift estiver pressionado, permite múltipla seleção.
- **Botão Direito**
  - Pressionar: Inicia a movimentação da câmera.
  - Soltar: Para a movimentação da câmera.
- **Scroll **
  - Rolar para cima: Aproxima a câmera ou aplica transformação (rotação, translação, escala) no objeto selecionado.
  - Rolar para baixo: Afasta a câmera ou aplica transformação (rotação, translação, escala) no objeto selecionado.

### Modificadores de Teclado

- **Ctrl**
  - Pressionado: Modifica o comportamento do scroll para rotação/translação/escala no eixo X.
- **Shift**
  - Pressionado: Modifica o comportamento do scroll para rotação/translação/escala no eixo Y.
- **Alt**
  - Pressionado: Modifica o comportamento do scroll para rotação/translação/escala no eixo Z.

### Outros Eventos

- **Movimento do Mouse**
  - Movimento: Atualiza a posição da câmera com base na posição atual do mouse.
- **Saída do Programa**
  - Evento: `pygame.QUIT` fecha o programa (Pode ser utilizando apertando ESC ou clicando no X).

Esses comandos são gerenciados pela classe `EventListener` para fornecer uma interface interativa ao usuário para manipular a cena e os objetos nela contidos.

## Autor

Jorge Bruno Costa Alves

Universidade Federal do Ceará - Campus Quixadá.


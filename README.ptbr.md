# Agentes de IA em Profundidade: Princípios de Design e Prática de Engenharia

[![PDF](https://img.shields.io/badge/PDF-Download-success.svg)](#livro-eletrônico) [![Leitura online](https://img.shields.io/badge/🌐_Leitura_online-bojieli.github.io-success?style=flat-square)](https://bojieli.github.io/ai-agent-book/astro/pt-BR/) [![Stars](https://img.shields.io/github/stars/bojieli/ai-agent-book?style=social)](https://github.com/bojieli/ai-agent-book) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Languages](https://img.shields.io/badge/Traduções-15%20idiomas-informational.svg)](#livro-eletrônico)

[中文](README.md) · [English](docs/en/README.md) · [Español](docs/es/README.md) · [Bahasa Indonesia](docs/id/README.md) · [العربية](docs/ar/README.md) · [繁體中文（台灣）](docs/zh-TW/README.md) · [Русский](docs/ru/README.md) · [Tiếng Việt](docs/vi/README.md) · [தமிழ்](docs/ta/README.md) · [日本語](docs/ja/README.md) · [Türkçe](docs/tr/README.md) · [한국어](docs/ko/README.md) · [Magyar](docs/hu/README.md) · [עברית](README.he.md) · **Português (Brasil)** ← atual

> 📥 **[Download do PDF / EPUB](#livro-eletrônico)** (recomendado) — as edições em PDF e EPUB oferecem a melhor experiência de leitura. Também é possível [ler online](https://bojieli.github.io/ai-agent-book/astro/pt-BR/) com navegação completa, alternância entre idiomas e destaques e notas.

**Agente = LLM + Contexto + Ferramentas** — o livro é construído em torno desta fórmula e apresenta, em dez capítulos, os princípios e a prática de engenharia de agentes de IA.

> 📚 **O livro irmão _AI Infra em Profundidade: Análise Quantitativa e Design de Sistemas_ agora é open source** — leia em [github.com/bojieli/ai-infra-book](https://github.com/bojieli/ai-infra-book)
>
> Desenvolver boas aplicações baseadas em modelos também exige entender a infraestrutura sobre a qual elas rodam. O livro irmão trata da AI Infra por trás do treinamento e da inferência: onde ficam os parâmetros e o estado do contexto, como a computação é executada e como vários aceleradores trabalham juntos.

> 📢 **Mudanças da versão 2.0 em relação à 1.4:** a versão 2.0 unifica a parte "Interação Assíncrona" do antigo capítulo 4 com o conteúdo sobre "Agentes Multimodais" do antigo capítulo 9, reorganizando-os como o novo capítulo 6, "Interação: Expansão dos Espaços de Observação e Ação". Os antigos capítulos 6 ("Avaliação de Agentes"), 7 ("Pós-treinamento de Modelos") e 8 ("Evolução Contínua de Agentes") foram deslocados em um capítulo cada, passando a ser, respectivamente, os capítulos 7, 8 e 9.
>
> Se você tem um PDF antigo, recomendamos [baixar a versão mais recente do PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-ptbr.pdf). A nova edição também inclui diversas correções e ajustes de conteúdo; confie apenas na versão mais recente.

A tradução completa para português do Brasil foi produzida por [Leonardo F. Nascimento](https://github.com/leofn) (LABHD-UFBA) com assistência de IA (GPT-5.6 Sol), revisão estrutural automatizada e glossário técnico. A tradução do texto das figuras (SVG) foi contribuída por [Líbna Raffaely](https://github.com/LibnaRaffaely).

## Livro eletrônico

- **Português (Brasil)** — tradução comunitária de [Leonardo F. Nascimento](https://github.com/leofn): [PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-ptbr.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-ptbr.epub)
- **Original em chinês**: [PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.epub)

## Sumário

| Capítulo | Tópico | Leitura |
| :--: | --- | :--: |
| — | Introdução | [Ler](book-ptbr/introduction.ptbr.md) |
| 1 | Primeiros passos com agentes de IA | [Ler](book-ptbr/chapter1.ptbr.md) |
| 2 | Engenharia de contexto | [Ler](book-ptbr/chapter2.ptbr.md) |
| 3 | Memória do usuário e base de conhecimento | [Ler](book-ptbr/chapter3.ptbr.md) |
| 4 | Ferramentas | [Ler](book-ptbr/chapter4.ptbr.md) |
| 5 | Agente de código e geração de código | [Ler](book-ptbr/chapter5.ptbr.md) |
| 6 | Interação: expansão dos espaços de observação e ação | [Ler](book-ptbr/chapter6.ptbr.md) |
| 7 | Avaliação de agentes | [Ler](book-ptbr/chapter7.ptbr.md) |
| 8 | Pós-treinamento de modelos | [Ler](book-ptbr/chapter8.ptbr.md) |
| 9 | Evolução contínua de agentes | [Ler](book-ptbr/chapter9.ptbr.md) |
| 10 | Colaboração multiagente | [Ler](book-ptbr/chapter10.ptbr.md) |
| — | Posfácio | [Ler](book-ptbr/afterword.ptbr.md) |
| — | Respostas das questões de reflexão | [Ler](book-ptbr/reference-answers.ptbr.md) |

A documentação dos experimentos que acompanham o livro ainda não foi traduzida para português do Brasil. O código dos experimentos e as instruções em inglês ou chinês estão disponíveis nas pastas `chapter1/` a `chapter10/`.

## Build local

Para gerar o PDF são necessários Pandoc, XeLaTeX, ElegantBook, librsvg e as fontes incluídas no TeX Live:

```bash
cd book-ptbr
bash build_pdf.sh
```

Após gerar o PDF, é possível gerar e validar o EPUB a partir da raiz do repositório:

```bash
./build_epub.sh ptbr
```

O código-fonte da edição em português do Brasil está na pasta [`book-ptbr/`](book-ptbr/). O conteúdo é atualizado continuamente e pode diferir da edição chinesa original.

## ❓ Perguntas frequentes

**P: Existe PDF / EPUB? Preciso compilar por conta própria?**
Não. A seção [Livro eletrônico](#livro-eletrônico) traz os links de download em PDF / EPUB (as edições nos 15 idiomas estão listadas no [README em inglês](docs/en/README.md)), sempre apontando para o build mais recente do branch main; também é possível [ler online](https://bojieli.github.io/ai-agent-book/). Só é preciso compilar se você quiser alterar o texto e refazer a diagramação.

**P: Que conhecimentos prévios são necessários para ler o livro?**
A seção "Pré-requisitos" da introdução explica em detalhes: saber ler e modificar código Python de complexidade média; já ter usado produtos de LLM como ChatGPT e Claude; ter familiaridade com pelo menos uma ferramenta de programação assistida por IA (Claude Code, Codex, Cursor etc.); conhecer noções básicas de engenharia de software, como linha de comando, Git, JSON e APIs REST. Exceto pelo pós-treinamento do capítulo 8, o livro exige muito pouco de matemática e aprendizado de máquina.

**P: É muito conteúdo e eu esqueço logo depois de ler. Como assimilar?**
Não leia apenas o texto. O caminho recomendado é pôr a mão na massa com os experimentos de cada capítulo — não lendo o código que acompanha o livro, mas entendendo os princípios de design apresentados e, com a ajuda de um coding agent, reimplementando tudo do zero, observando a saída e investigando o que não sai como esperado. As questões para reflexão no fim de cada capítulo também são uma boa autoavaliação. Para um percurso mais sistemático, veja o [guia de estudo](docs/en/LEARNING.md) (em inglês). Um leitor resumiu bem: primeiro leia o livro até ele ficar fino, depois até ficar grosso, depois até ficar fino de novo.

**P: Preciso entender o código dos experimentos linha por linha?**
Não. Todo o código que acompanha o livro foi gerado por coding agents a partir do texto, e o próprio autor não o lê linha por linha. O essencial é pensar com clareza a arquitetura, os componentes centrais e os princípios de design; depois, deixe a IA escrever o código, rodar os testes e corrigir bugs — a pessoa fica responsável pelo design inicial e pela aceitação final.

**P: As questões para reflexão têm respostas de referência?**
Sim: [`book-ptbr/reference-answers.ptbr.md`](book-ptbr/reference-answers.ptbr.md) (original em chinês: [`book/reference-answers.md`](book/reference-answers.md), [versão online](https://bojieli.github.io/ai-agent-book/book/reference-answers/)). São apenas referências, não gabaritos; opiniões diferentes são bem-vindas nas Discussions.

**P: Que projeto prático posso construir depois de terminar o livro?**
Recomendamos construir do zero um coding agent no estilo do Claude Code ou do Codex: os capítulos 1–5 bastam para produzir um coding agent utilizável; os capítulos 7 e 9 ajudam a montar um conjunto de avaliação e a melhorá-lo continuamente a partir dos casos de falha; o capítulo 8 intervém no próprio modelo; os capítulos 6 e 10 acrescentam formas de interação como voz e Computer Use, além de colaboração multiagente. As etapas de engenharia — avaliação, observabilidade, confiabilidade — podem começar pelos experimentos de avaliação do capítulo 7: monte primeiro um pequeno conjunto de avaliação com uma dúzia de tarefas para o seu agente e depois itere sobre os casos de falha.

**P: Onde faço perguntas e participo das discussões?**
- Erratas do texto, bugs nos experimentos, problemas de tradução: abra uma [Issue](https://github.com/bojieli/ai-agent-book/issues) indicando o capítulo, a seção e a frase original.
- Dúvidas de leitura, discussão das questões para reflexão, troca de experiências, indicação de materiais: use o [GitHub Discussions](https://github.com/bojieli/ai-agent-book/discussions).

**P: Encontrei um erro e quero corrigir. Como faço?**
Pull Requests são bem-vindos. A versão em chinês, [`book/`](book/), é a fonte canônica, e os demais idiomas são sincronizados a partir dela: ao alterar o texto, basta modificar a versão em chinês e explicar no PR; as traduções são sincronizadas em conjunto após o merge. Veja os [Pull Requests](https://github.com/bojieli/ai-agent-book/pulls) do repositório.

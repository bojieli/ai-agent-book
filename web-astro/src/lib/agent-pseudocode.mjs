// A lexical grammar for the book's API walkthrough and message trajectories,
// which are pseudocode rather than executable JavaScript/JSON programs.
export const agentPseudocode = {
  name: 'agent-pseudocode',
  scopeName: 'source.agent-pseudocode',
  patterns: [
    { name: 'comment.line.number-sign', match: '(?:#|←).*$' },
    {
      name: 'string.quoted.double',
      begin: '"',
      end: '"',
      patterns: [{ name: 'constant.character.escape', match: '\\\\.' }],
    },
    {
      name: 'string.quoted.single',
      begin: "'",
      end: "'",
      patterns: [{ name: 'constant.character.escape', match: '\\\\.' }],
    },
    {
      name: 'support.type.property-name.json',
      match: '\\b[A-Za-z_][A-Za-z_0-9]*(?=\\s*:)',
    },
    { name: 'constant.numeric', match: '\\b\\d+(?:\\.\\d+)?\\b' },
    { name: 'punctuation.section', match: '[{}\\[\\]]' },
    { name: 'punctuation.separator', match: '[:,]' },
  ],
};

// Mixed Markdown/XML instructions and the book’s procedural walkthrough.
export const agentInstructions = {
  name: 'agent-instructions',
  scopeName: 'text.agent-instructions',
  patterns: [
    { name: 'entity.name.tag', match: '</?[A-Za-z_][^>]*>' },
    { name: 'markup.heading', match: '^#{1,6} .*$' },
    { name: 'entity.name.function', match: '^Step \\d+:.*$' },
    { name: 'keyword.control', match: '→|↓' },
  ],
};

// Explanatory transcripts and traces: color only meaningful labels and values.
export const bookExample = {
  name: 'book-example',
  scopeName: 'text.book-example',
  patterns: [
    { name: 'comment.line', match: '(?:#|←).*$' },
    {
      name: 'entity.name.function',
      match: '^(?:User|Agent|Extracted memories|Query tokens|Final ranking):',
    },
    { name: 'comment.block', match: '^\\s*\\[calls .+\\]$' },
    {
      name: 'entity.name.type',
      match:
        '\\((?:preference|dietary restriction|loyalty program|recent activity)\\)',
    },
    { name: 'entity.name.tag', match: '\\bdoc_\\d+\\b' },
    {
      name: 'variable.other',
      match: '\\b(?:TF|IDF|df|BM25 contribution|doc length)(?==)',
    },
    { name: 'string.quoted.double', begin: '"', end: '"' },
    { name: 'constant.numeric', match: '\\b\\d+(?:\\.\\d+)?\\b' },
    { name: 'keyword.operator', match: '→|>|=' },
  ],
};

export const bookTree = {
  name: 'book-tree',
  scopeName: 'text.book-tree',
  patterns: [
    { name: 'comment.line', match: '#.*$' },
    { name: 'entity.name.filename', match: '[a-zA-Z_][\\w/-]*/|viking://' },
    { name: 'punctuation.separator', match: '[├└─│]+' },
  ],
};

// Localized interaction traces: event IDs, element tags, and action sequences.
export const bookInteraction = {
  name: 'book-interaction',
  scopeName: 'text.book-interaction',
  patterns: [
    { name: 'entity.name.tag', match: '</?[A-Za-z_][^>]*>' },
    { name: 'entity.name.function', match: '\\b[A-Za-z_][A-Za-z_0-9]*(?=\\()' },
    { name: 'entity.name.tag', match: '^\\[[^\\]\\n]+\\]' },
    ...bookExample.patterns,
  ],
};

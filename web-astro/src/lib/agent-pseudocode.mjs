// A lexical grammar for the book's API walkthrough and message trajectories,
// which are pseudocode rather than executable JavaScript/JSON programs.
export const agentPseudocode = {
  name: 'agent-pseudocode',
  scopeName: 'source.agent-pseudocode',
  patterns: [
    { name: 'comment.line.number-sign', match: '#.*$' },
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

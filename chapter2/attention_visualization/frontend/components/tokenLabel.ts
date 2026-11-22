// Keep decoded token positions visible when a UTF-8 character spans tokens.
export function tokenLabel(token: string): string {
  if (token === '') return '↳';
  if (token.trim() === '') return '␣';
  return token;
}

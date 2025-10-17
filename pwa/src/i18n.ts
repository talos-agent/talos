import { detectLocale } from './geo';
export const defaultLocale = detectLocale() || 'pt-BR';
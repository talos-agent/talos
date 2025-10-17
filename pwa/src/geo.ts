export function detectLocale(): string | null {
  // 1. Browser lang
  const browser = navigator.language;  // 'pt-BR'
  // 2. Tor latency-based geo (country=br) – no GPS
  const torCountry = (window as any).TorCountry || 'br';
  return torCountry === 'br' ? 'pt-BR' : browser;
}
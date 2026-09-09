import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { useLocation, useOutlet } from 'react-router-dom';

/** Keep previously visited route components mounted so local UI state survives navigation. */
export default function KeepAliveOutlet() {
  const location = useLocation();
  const outlet = useOutlet();
  const cache = useRef(new Map<string, ReactNode>());
  const key = location.pathname;

  if (outlet && !cache.current.has(key)) cache.current.set(key, outlet);

  useEffect(() => {
    // The current outlet is cached during render; this effect intentionally keeps all
    // visited pages mounted. Authentication/logout still remounts the whole layout.
  }, [key]);

  return <>{Array.from(cache.current.entries()).map(([route, element]) => (
    <div key={route} style={{ display: route === key ? 'block' : 'none', height: '100%' }}>
      {element}
    </div>
  ))}</>;
}

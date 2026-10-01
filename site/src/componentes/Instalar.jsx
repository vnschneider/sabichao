import { useEffect, useState } from "react";
import { Check, Copy } from "@phosphor-icons/react";
import { INSTALACAO } from "../conteudo.js";
import "./Instalar.css";

function sistemaProvavel() {
  const ua = navigator.userAgent;
  return /Mac|Linux|X11/.test(ua) && !/Android|iPhone|iPad/.test(ua) ? "unix" : "windows";
}

export default function Instalar({ aoCopiar }) {
  const [so, setSo] = useState("windows");
  const [copiado, setCopiado] = useState(null);

  useEffect(() => setSo(sistemaProvavel()), []);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(INSTALACAO[so].comando);
      setCopiado("ok");
      aoCopiar?.();
    } catch {
      setCopiado("falhou");
    }
    setTimeout(() => setCopiado(null), 2200);
  }

  return (
    <div className="instalar">
      <div className="instalar-abas" role="tablist" aria-label="Sistema operacional">
        {Object.entries(INSTALACAO).map(([id, info]) => (
          <button
            key={id}
            role="tab"
            id={`aba-${id}`}
            aria-selected={so === id}
            aria-controls="instalar-painel"
            onClick={() => setSo(id)}
          >
            {info.rotulo}
          </button>
        ))}
      </div>
      <div className="instalar-painel" id="instalar-painel" role="tabpanel" aria-labelledby={`aba-${so}`}>
        <code className="instalar-comando">{INSTALACAO[so].comando}</code>
        <button className="botao botao-primario instalar-copiar" onClick={copiar}>
          {copiado === "ok" ? <Check size={18} weight="bold" /> : <Copy size={18} weight="bold" />}
          {copiado === "ok" ? "Copiado" : "Copiar"}
        </button>
      </div>
      <p className="instalar-dica" aria-live="polite">
        {copiado === "falhou" ? "Nao consegui copiar sozinho. Selecione o comando e copie." : INSTALACAO[so].dica}
      </p>
    </div>
  );
}
